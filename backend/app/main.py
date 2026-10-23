"""
FastAPI application for Cyberbullying Detection & Severity Analysis.
Provides RESTful endpoints for single analysis, batch CSV processing, dashboard analytics,
model comparison, explainability, NLP educational diagnostics, and human moderation.
"""

import os
import io
import csv
import json
import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.database.db import (
    init_db, insert_analysis, get_analysis_by_id, list_analyses,
    delete_analysis, get_dashboard_statistics, list_moderation_queue,
    update_moderation_item, record_feedback
)
from backend.app.schemas.analysis import (
    AnalyzeRequest, AnalyzeResponse, BatchAnalyzeResponse, BatchAnalyzeItem,
    ModerationUpdateRequest, FeedbackRequest, NlpLabRequest
)
from backend.app.services.nlp_service import nlp_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize database schema on startup
init_db()

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="Advanced MCA NLP Project: Cyberbullying Detection & Severity Analysis API"
)

# Configure development CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Returns application health and model readiness status."""
    return {
        "status": "online",
        "app_title": settings.app_title,
        "models_loaded": nlp_service.is_loaded,
        "database_connected": os.path.exists(settings.db_path)
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_single_comment(req: AnalyzeRequest):
    """Analyzes a single comment for cyberbullying toxicity, category scores, severity, and explanations."""
    if not nlp_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="NLP model artifacts not loaded. Please train models first using `python ml/src/train.py`."
        )

    prediction = nlp_service.predict_comment(req.comment_text)

    # Persist in SQLite database if requested
    saved_id = None
    if req.auto_save:
        record = insert_analysis(
            comment_text=req.comment_text,
            is_toxic=prediction["is_toxic"],
            confidence=prediction["confidence"],
            primary_class=prediction["primary_class"],
            estimated_severity=prediction["severity"]["level"],
            severity_label=prediction["severity"]["label"],
            category_scores=prediction["category_scores"],
            influential_words=prediction["influential_words"]
        )
        saved_id = record["id"]

    prediction["id"] = saved_id
    return prediction


@app.post("/api/analyze/batch", response_model=BatchAnalyzeResponse)
async def analyze_batch_csv(
    file: UploadFile = File(...),
    text_column: str = Query("comment_text", description="Name of the text column in the CSV")
):
    """Processes uploaded CSV files in batches, generating toxicity classifications and severity ratings."""
    if not nlp_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="NLP model artifacts not loaded."
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    try:
        text_stream = io.StringIO(content.decode("utf-8", errors="replace"))
        reader = csv.DictReader(text_stream)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {str(e)}")

    if not reader.fieldnames or text_column not in reader.fieldnames:
        # Fallback: check if 'text' or first column exists
        available_cols = reader.fieldnames or []
        fallback_col = None
        for cand in ["comment_text", "text", "comment", "message", "content"]:
            if cand in available_cols:
                fallback_col = cand
                break
        if not fallback_col and len(available_cols) > 0:
            fallback_col = available_cols[0]

        if not fallback_col:
            raise HTTPException(
                status_code=400,
                detail=f"Column '{text_column}' not found. Available columns: {available_cols}"
            )
        text_column = fallback_col

    results = []
    errors = []
    toxic_cnt = 0
    non_toxic_cnt = 0

    for idx, row in enumerate(reader):
        if idx >= settings.max_batch_size:
            errors.append({"row": idx, "error": f"Max batch limit of {settings.max_batch_size} reached."})
            break

        comment = row.get(text_column, "").strip()
        if not comment:
            continue

        try:
            pred = nlp_service.predict_comment(comment)
            if pred["is_toxic"]:
                toxic_cnt += 1
            else:
                non_toxic_cnt += 1

            # Auto persist batch items
            insert_analysis(
                comment_text=comment,
                is_toxic=pred["is_toxic"],
                confidence=pred["confidence"],
                primary_class=pred["primary_class"],
                estimated_severity=pred["severity"]["level"],
                severity_label=pred["severity"]["label"],
                category_scores=pred["category_scores"],
                influential_words=pred["influential_words"],
                auto_flag_moderation=True
            )

            results.append(BatchAnalyzeItem(
                row_index=idx + 1,
                comment_text=comment,
                is_toxic=pred["is_toxic"],
                confidence=pred["confidence"],
                estimated_severity=pred["severity"]["level"],
                severity_label=pred["severity"]["label"],
                category_scores=pred["category_scores"]
            ))
        except Exception as e:
            errors.append({"row": idx + 1, "error": str(e)})

    return BatchAnalyzeResponse(
        total_processed=len(results),
        total_toxic=toxic_cnt,
        total_non_toxic=non_toxic_cnt,
        results=results,
        errors=errors
    )


@app.get("/api/history")
def get_history(
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    is_toxic: Optional[bool] = None,
    severity: Optional[int] = None,
    search: Optional[str] = None
):
    """Retrieves paginated analysis history from SQLite."""
    return list_analyses(
        limit=limit,
        offset=offset,
        filter_toxic=is_toxic,
        filter_severity=severity,
        search=search
    )


@app.get("/api/history/{analysis_id}")
def get_history_by_id(analysis_id: int):
    """Retrieves a single historical analysis with influential word details."""
    item = get_analysis_by_id(analysis_id)
    if not item:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return item


@app.delete("/api/history/{analysis_id}")
def delete_history_item(analysis_id: int):
    """Deletes an analysis record."""
    deleted = delete_analysis(analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"status": "deleted", "id": analysis_id}


@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    """Returns aggregated metrics computed strictly from the SQLite database."""
    return get_dashboard_statistics()


@app.get("/api/model/metrics")
def get_model_metrics():
    """Returns evaluation metrics on the held-out test split."""
    test_eval_file = os.path.join(settings.reports_dir, "test_evaluation.json")
    metadata_file = os.path.join(settings.reports_dir, "training_metadata.json")

    if not os.path.exists(test_eval_file):
        raise HTTPException(
            status_code=404,
            detail="Evaluation reports missing. Please run `python ml/src/train.py`."
        )

    with open(test_eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    meta_data = {}
    if os.path.exists(metadata_file):
        with open(metadata_file, "r", encoding="utf-8") as f:
            meta_data = json.load(f)

    return {
        "evaluation": eval_data,
        "metadata": meta_data
    }


@app.get("/api/model/comparison")
def get_model_comparison():
    """Returns model benchmark comparisons and preprocessing ablation findings."""
    model_comp_file = os.path.join(settings.reports_dir, "model_comparison.json")
    preproc_comp_file = os.path.join(settings.reports_dir, "preprocessing_experiments.json")

    if not os.path.exists(model_comp_file):
        raise HTTPException(
            status_code=404,
            detail="Model comparison report missing. Run training pipeline first."
        )

    with open(model_comp_file, "r", encoding="utf-8") as f:
        models_data = json.load(f)

    preproc_data = {}
    if os.path.exists(preproc_comp_file):
        with open(preproc_comp_file, "r", encoding="utf-8") as f:
            preproc_data = json.load(f)

    return {
        "model_comparison": models_data,
        "preprocessing_experiments": preproc_data
    }


@app.get("/api/explain/global")
def get_global_explanations(top_n: int = Query(25, ge=5, le=100)):
    """Returns global feature importance weights from learned linear model parameters."""
    if not nlp_service.is_loaded or not nlp_service.explainer:
        raise HTTPException(status_code=503, detail="Explainer not initialized.")
    return nlp_service.explainer.get_global_feature_importance(top_n=top_n)


@app.post("/api/nlp/laboratory")
def inspect_nlp_lab(req: NlpLabRequest):
    """Processes text through all discrete preprocessing stages for interactive educational display."""
    return nlp_service.inspect_nlp_laboratory(req.text)


@app.get("/api/evaluation/errors")
def get_error_analysis():
    """Returns False Positive and False Negative empirical cases on test set."""
    error_file = os.path.join(settings.reports_dir, "error_analysis.json")
    if not os.path.exists(error_file):
        raise HTTPException(status_code=404, detail="Error analysis report missing.")
    with open(error_file, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/evaluation/fairness")
def get_fairness_analysis():
    """Returns identity subgroup bias evaluation report."""
    fairness_file = os.path.join(settings.reports_dir, "fairness_analysis.json")
    if not os.path.exists(fairness_file):
        raise HTTPException(status_code=404, detail="Fairness report missing.")
    with open(fairness_file, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/moderation/queue")
def get_moderation_queue(status: Optional[str] = None):
    """Returns cases flagged for human review."""
    return list_moderation_queue(status=status)


@app.patch("/api/moderation/{item_id}")
def update_moderation(item_id: int, req: ModerationUpdateRequest):
    """Updates status of a moderation queue item."""
    updated = update_moderation_item(item_id, req.status, req.reviewer_notes)
    if not updated:
        raise HTTPException(status_code=404, detail="Moderation item not found.")
    return {"status": "updated", "id": item_id, "action": req.status}


@app.post("/api/feedback")
def submit_feedback(req: FeedbackRequest):
    """Records user accuracy feedback and label corrections."""
    fid = record_feedback(
        analysis_id=req.analysis_id,
        is_accurate=req.is_accurate,
        suggested_label=req.suggested_label,
        comments=req.user_comments
    )
    return {"status": "success", "feedback_id": fid}
