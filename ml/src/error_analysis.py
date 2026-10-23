"""
Error Analysis Module for Cyberbullying & Toxicity Detection.
Identifies and categorizes:
- False Positives (Clean comments erroneously flagged as toxic)
- False Negatives (Toxic/abusive comments missed by the classifier)
- Negation challenges, slang, sarcastic subtleties, and context length issues.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List
import pandas as pd
import joblib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ml.src.dataset_loader import discover_dataset, load_dataset, create_train_val_test_splits
from ml.src.preprocessing import default_nlp_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../artifacts"))
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../reports"))


def run_error_analysis(sample_size: int = 15000) -> Dict[str, Any]:
    """Evaluates false positives and false negatives on held-out test data."""
    logger.info("Executing Error Analysis on held-out test records...")
    
    vec_path = os.path.join(ARTIFACTS_DIR, "tfidf_vectorizer.joblib")
    model_path = os.path.join(ARTIFACTS_DIR, "best_model.joblib")

    if not os.path.exists(vec_path) or not os.path.exists(model_path):
        raise FileNotFoundError("Model artifacts not found. Run train.py first.")

    vectorizer = joblib.load(vec_path)
    model = joblib.load(model_path)

    csv_path, _ = discover_dataset(".")
    df = load_dataset(csv_path, sample_size=sample_size, random_state=42)
    _, _, test_df = create_train_val_test_splits(df, val_size=0.15, test_size=0.15, random_state=42)

    test_clean = [default_nlp_pipeline.transform_text(t) for t in test_df["comment_text"]]
    X_test = vectorizer.transform(test_clean)
    y_test = test_df["toxic"].values
    y_pred = model.predict(X_test)

    # Calculate probabilities if available
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_test)[:, 1]
    else:
        probs = [0.5 if p == 1 else 0.0 for p in y_pred]

    test_df = test_df.copy()
    test_df["prediction"] = y_pred
    test_df["confidence"] = [round(float(p), 4) for p in probs]

    # False Positives: Ground Truth = 0, Predicted = 1
    fp_mask = (y_test == 0) & (y_pred == 1)
    fp_df = test_df[fp_mask]

    # False Negatives: Ground Truth = 1, Predicted = 0
    fn_mask = (y_test == 1) & (y_pred == 0)
    fn_df = test_df[fn_mask]

    fp_examples = []
    for _, row in fp_df.head(10).iterrows():
        fp_examples.append({
            "id": str(row["id"]),
            "text": str(row["comment_text"])[:200] + ("..." if len(str(row["comment_text"])) > 200 else ""),
            "actual_label": 0,
            "predicted_label": 1,
            "confidence": float(row["confidence"]),
            "error_type": "False Positive",
            "possible_cause": "Contains taboo words, vehement disagreement, or identity terms without abusive intent."
        })

    fn_examples = []
    for _, row in fn_df.head(10).iterrows():
        fn_examples.append({
            "id": str(row["id"]),
            "text": str(row["comment_text"])[:200] + ("..." if len(str(row["comment_text"])) > 200 else ""),
            "actual_label": 1,
            "predicted_label": 0,
            "confidence": float(row["confidence"]),
            "error_type": "False Negative",
            "possible_cause": "Obfuscated insults, subtle cyberbullying, sarcastic mocking, or colloquial phrasing."
        })

    error_summary = {
        "total_test_evaluated": len(test_df),
        "false_positive_count": int(fp_mask.sum()),
        "false_positive_rate": round(float(fp_mask.sum()) / max(int((y_test == 0).sum()), 1), 4),
        "false_negative_count": int(fn_mask.sum()),
        "false_negative_rate": round(float(fn_mask.sum()) / max(int((y_test == 1).sum()), 1), 4),
        "fp_examples": fp_examples,
        "fn_examples": fn_examples,
        "failure_modes": [
            {
                "pattern": "Negation Inversion",
                "description": "Sentences like 'I do not want to insult you' may be misflagged due to presence of the root word 'insult'.",
                "mitigation": "Preserving negation words during stop-word removal and utilizing unigram+bigram TF-IDF features."
            },
            {
                "pattern": "Sarcasm & Subtle Bullying",
                "description": "Passive-aggressive bullying without overt profanity or slurs is frequently missed by bag-of-words classifiers.",
                "mitigation": "Requires contextual transformer representations (e.g. DistilBERT) or conversational thread history."
            },
            {
                "pattern": "Colloquial Reappropriation",
                "description": "Friendly banter or reclamation of reclaimed terms among close peers is misclassified as toxic.",
                "mitigation": "Incorporating user moderation queue review before taking punitive actions."
            }
        ]
    }

    report_path = os.path.join(REPORTS_DIR, "error_analysis.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(error_summary, f, indent=2)
    logger.info(f"Saved error analysis report to {report_path}")

    return error_summary


if __name__ == "__main__":
    run_error_analysis()
