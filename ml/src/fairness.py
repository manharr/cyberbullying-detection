"""
Fairness and Unintended Bias Assessment Module.
Examines potential disparate impact and false positive disparity across identity mentions
(e.g., race, religion, sexual orientation, gender).

Academic Reference:
Dixon et al., "Measuring and Mitigating Unintended Bias in Text Classification" (AIES 2018).
Evaluates whether benign comments mentioning demographic terms are disproportionately flagged as toxic.
"""

import os
import sys
import re
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

IDENTITY_GROUPS = {
    "Sexual Orientation": ["gay", "lesbian", "homosexual", "queer"],
    "Religion": ["muslim", "jewish", "christian", "islam", "atheist"],
    "Race / Ethnicity": ["black", "white", "asian", "latino", "hispanic"],
    "Gender": ["woman", "man", "transgender", "female", "male"]
}


def run_fairness_assessment(sample_size: int = 15000) -> Dict[str, Any]:
    """Computes subgroup error rates and false positive disparities."""
    logger.info("Executing Fairness & Algorithmic Bias Assessment...")

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

    test_df = test_df.copy()
    test_df["prediction"] = y_pred

    # Global FPR
    global_non_toxic = (y_test == 0)
    global_fp = (y_test == 0) & (y_pred == 1)
    global_fpr = round(float(global_fp.sum()) / max(int(global_non_toxic.sum()), 1), 4)

    group_results = {}

    for category, terms in IDENTITY_GROUPS.items():
        term_pattern = r"\b(" + "|".join(terms) + r")\b"
        matches_mask = test_df["comment_text"].str.contains(term_pattern, case=False, regex=True)
        subgroup_df = test_df[matches_mask]

        if len(subgroup_df) > 0:
            sub_y = subgroup_df["toxic"].values
            sub_pred = subgroup_df["prediction"].values

            sub_non_toxic = (sub_y == 0)
            sub_fp = (sub_y == 0) & (sub_pred == 1)
            sub_fpr = round(float(sub_fp.sum()) / max(int(sub_non_toxic.sum()), 1), 4)

            group_results[category] = {
                "terms_tracked": terms,
                "total_matched_comments": len(subgroup_df),
                "non_toxic_count": int(sub_non_toxic.sum()),
                "false_positive_count": int(sub_fp.sum()),
                "subgroup_fpr": sub_fpr,
                "fpr_disparity_ratio": round(sub_fpr / max(global_fpr, 0.0001), 2)
            }
        else:
            group_results[category] = {
                "terms_tracked": terms,
                "total_matched_comments": 0,
                "subgroup_fpr": 0.0,
                "fpr_disparity_ratio": 1.0
            }

    fairness_report = {
        "global_false_positive_rate": global_fpr,
        "identity_subgroups": group_results,
        "academic_assessment": (
            "Empirical fairness analysis reveals unintended bias: models trained on uncurated internet discussions "
            "often show higher False Positive Rates on benign comments mentioning protected identity groups. "
            "This happens because toxic comments frequently pair identity words with harassment, causing linear models "
            "to assign slightly positive coefficients to demographic terms. Mitigation requires counterfactual data "
            "augmentation and human-in-the-loop moderation before punitive enforcement."
        ),
        "ethical_limitations": [
            "Toxicity prediction does not measure internal intent or personal malice.",
            "Subgroup keyword matching approximates identity discourse but cannot capture nuanced identity context.",
            "Algorithmic filtering should never be used as the sole grounds for disciplinary action without human review."
        ]
    }

    report_path = os.path.join(REPORTS_DIR, "fairness_analysis.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(fairness_report, f, indent=2)
    logger.info(f"Saved fairness assessment report to {report_path}")

    return fairness_report


if __name__ == "__main__":
    run_fairness_assessment()
