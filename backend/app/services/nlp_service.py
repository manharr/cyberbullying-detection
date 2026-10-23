"""
Inference and NLP Service for model evaluation, category scoring, and explainability.
Loads model artifacts once at backend startup to ensure low latency.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import joblib

from backend.app.core.config import settings
from ml.src.preprocessing import default_nlp_pipeline
from ml.src.explain import ModelExplainer
from ml.src.severity import calculate_severity

logger = logging.getLogger(__name__)

TARGET_COLUMNS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

ACADEMIC_DISCLAIMER = (
    "Academic Notice: This classification detects toxic or abusive language within an individual comment "
    "using supervised statistical NLP models. It does NOT independently establish a pattern of repeated cyberbullying, "
    "legal culpability, or the overall context of an interpersonal dispute."
)


class NLPModelService:
    """Manages loaded artifacts, vectorization, multi-label scoring, and explainability."""

    def __init__(self):
        self.vectorizer = None
        self.best_model = None
        self.lr_model = None
        self.multilabel_models = {}
        self.explainer = None
        self.is_loaded = False
        self.load_artifacts()

    def load_artifacts(self):
        """Loads trained artifacts from ml/artifacts/."""
        vec_path = os.path.join(settings.artifacts_dir, "tfidf_vectorizer.joblib")
        best_path = os.path.join(settings.artifacts_dir, "best_model.joblib")
        lr_path = os.path.join(settings.artifacts_dir, "model_lr.joblib")
        multi_path = os.path.join(settings.artifacts_dir, "multilabel_classifiers.joblib")

        missing = []
        for p, name in [
            (vec_path, "TF-IDF Vectorizer"),
            (best_path, "Best Model"),
            (lr_path, "Logistic Regression"),
            (multi_path, "Multi-label Classifiers")
        ]:
            if not os.path.exists(p):
                missing.append(f"{name} ({os.path.basename(p)})")

        if missing:
            logger.warning(
                f"Model artifacts not found: {', '.join(missing)}. "
                "Please run `python ml/src/train.py` to train models and generate artifacts."
            )
            self.is_loaded = False
            return

        try:
            self.vectorizer = joblib.load(vec_path)
            self.best_model = joblib.load(best_path)
            self.lr_model = joblib.load(lr_path)
            self.multilabel_models = joblib.load(multi_path)
            self.explainer = ModelExplainer(self.vectorizer, self.lr_model)
            self.is_loaded = True
            logger.info("All NLP model artifacts loaded successfully into memory.")
        except Exception as e:
            logger.error(f"Failed to load model artifacts: {e}")
            self.is_loaded = False

    def predict_comment(self, text: str) -> Dict[str, Any]:
        """Classifies a single comment, computes categories, severity, and word explanations."""
        if not self.is_loaded:
            raise RuntimeError(
                "NLP models are not loaded. Train models first using `python ml/src/train.py`."
            )

        # 1. Preprocessing
        clean_text = default_nlp_pipeline.transform_text(text)
        if not clean_text.strip():
            # If text had only symbols/empty
            return {
                "comment_text": text,
                "is_toxic": False,
                "confidence": 0.05,
                "primary_class": "Non-toxic",
                "severity": calculate_severity(False, 0.05, {}, []),
                "category_scores": {c: 0.01 for c in TARGET_COLUMNS},
                "influential_words": [],
                "academic_disclaimer": ACADEMIC_DISCLAIMER
            }

        # 2. Vectorization
        X = self.vectorizer.transform([clean_text])

        # 3. Best Model Prediction
        y_pred = int(self.best_model.predict(X)[0])
        is_toxic = bool(y_pred == 1)

        # Confidence calculation
        if hasattr(self.best_model, "predict_proba"):
            probs = self.best_model.predict_proba(X)[0]
            confidence = round(float(probs[1] if is_toxic else probs[0]), 4)
        elif hasattr(self.best_model, "decision_function"):
            df_val = float(self.best_model.decision_function(X)[0])
            prob_pos = 1.0 / (1.0 + np.exp(-df_val))
            confidence = round(float(prob_pos if is_toxic else (1.0 - prob_pos)), 4)
        else:
            confidence = 0.85

        # 4. Multi-label Category Scores
        cat_scores = {}
        for cat in TARGET_COLUMNS:
            clf = self.multilabel_models.get(cat)
            if clf and hasattr(clf, "predict_proba"):
                prob = float(clf.predict_proba(X)[0][1])
                cat_scores[cat] = round(prob, 4)
            elif clf and hasattr(clf, "decision_function"):
                df_val = float(clf.decision_function(X)[0])
                prob = 1.0 / (1.0 + np.exp(-df_val))
                cat_scores[cat] = round(float(prob), 4)
            else:
                cat_scores[cat] = 0.0

        # 5. Local Explainability
        influential = self.explainer.explain_comment(clean_text, X, top_k=8)

        # 6. Severity Estimation
        severity_info = calculate_severity(
            is_toxic=is_toxic,
            confidence=confidence,
            category_scores=cat_scores,
            influential_words=influential
        )

        return {
            "comment_text": text,
            "is_toxic": is_toxic,
            "confidence": confidence,
            "primary_class": "Toxic" if is_toxic else "Non-toxic",
            "severity": severity_info,
            "category_scores": cat_scores,
            "influential_words": influential,
            "academic_disclaimer": ACADEMIC_DISCLAIMER
        }

    def inspect_nlp_laboratory(self, text: str) -> Dict[str, Any]:
        """Executes transparent step-by-step diagnostic inspection for education."""
        pipeline_steps = default_nlp_pipeline.inspect_pipeline_steps(text)

        # Attach active TF-IDF features if vectorizer is ready
        active_terms = []
        if self.is_loaded and self.vectorizer:
            X = self.vectorizer.transform([pipeline_steps["final_processed_text"]])
            coo = X.tocoo()
            feature_names = self.vectorizer.get_feature_names_out()
            for idx, val in zip(coo.col, coo.data):
                active_terms.append({
                    "term": feature_names[idx],
                    "tfidf_weight": round(float(val), 4)
                })
            active_terms.sort(key=lambda x: x["tfidf_weight"], reverse=True)

        pipeline_steps["tfidf_active_terms"] = active_terms
        return pipeline_steps


nlp_service = NLPModelService()
