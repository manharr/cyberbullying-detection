"""
Unit tests for model loading, inference, severity, and explainability.
"""

import os
import pytest
import joblib
from ml.src.explain import ModelExplainer
from ml.src.severity import calculate_severity, SEVERITY_LEVELS
from ml.src.preprocessing import default_nlp_pipeline

ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../artifacts"))


def test_artifacts_exist():
    required_files = [
        "tfidf_vectorizer.joblib",
        "best_model.joblib",
        "model_lr.joblib",
        "model_svm.joblib",
        "model_nb.joblib",
        "multilabel_classifiers.joblib"
    ]
    for rf in required_files:
        assert os.path.exists(os.path.join(ARTIFACTS_DIR, rf)), f"Missing artifact: {rf}"


def test_model_inference():
    vec = joblib.load(os.path.join(ARTIFACTS_DIR, "tfidf_vectorizer.joblib"))
    model = joblib.load(os.path.join(ARTIFACTS_DIR, "best_model.joblib"))

    clean_text = default_nlp_pipeline.transform_text("Thank you for your constructive guidance and help!")
    X = vec.transform([clean_text])
    pred = model.predict(X)[0]
    assert pred == 0  # Non-toxic


def test_severity_rubric():
    # Case 1: Non-toxic
    sev_0 = calculate_severity(is_toxic=False, confidence=0.15, category_scores={}, influential_words=[])
    assert sev_0["level"] == 0

    # Case 2: Threat / High severity
    sev_3 = calculate_severity(
        is_toxic=True,
        confidence=0.92,
        category_scores={"threat": 0.85, "toxic": 0.95},
        influential_words=[]
    )
    assert sev_3["level"] == 3

    # Case 3: Moderate severity
    sev_2 = calculate_severity(
        is_toxic=True,
        confidence=0.88,
        category_scores={"obscene": 0.70, "insult": 0.75},
        influential_words=[]
    )
    assert sev_2["level"] == 2


def test_explainer():
    vec = joblib.load(os.path.join(ARTIFACTS_DIR, "tfidf_vectorizer.joblib"))
    model = joblib.load(os.path.join(ARTIFACTS_DIR, "model_lr.joblib"))
    explainer = ModelExplainer(vec, model)

    global_imp = explainer.get_global_feature_importance(top_n=5)
    assert len(global_imp["top_toxic_indicators"]) == 5
    assert len(global_imp["top_non_toxic_indicators"]) == 5

    clean = default_nlp_pipeline.transform_text("idiot fool nonsense")
    X = vec.transform([clean])
    local_exp = explainer.explain_comment(clean, X, top_k=3)
    assert len(local_exp) > 0
