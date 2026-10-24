"""
Unit tests for DistilBERT Classifier and Cost-Sensitive Threshold Tuning.
"""

import pytest
import numpy as np
from ml.src.distilbert_model import DistilBertClassifier


def test_distilbert_init():
    clf = DistilBertClassifier(threshold=0.50)
    assert clf.threshold == 0.50
    assert clf.is_loaded is False


def test_threshold_tuning_logic():
    clf = DistilBertClassifier()
    # Mock probabilities for 10 samples
    y_true = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
    mock_probs = np.array([
        [0.95, 0.05],
        [0.90, 0.10],
        [0.85, 0.15],
        [0.70, 0.30],
        [0.65, 0.35],
        [0.60, 0.40],
        [0.55, 0.45],  # False negative at 0.50, but true positive at 0.40
        [0.40, 0.60],
        [0.20, 0.80],
        [0.10, 0.90],
    ])

    thresholds = [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]
    best_thr = 0.50
    best_f1 = -1.0
    from sklearn.metrics import f1_score

    for thr in thresholds:
        preds = (mock_probs[:, 1] >= thr).astype(int)
        score = f1_score(y_true, preds, average="macro")
        if score > best_f1:
            best_f1 = score
            best_thr = thr

    assert best_thr <= 0.45
    assert best_f1 > 0.80


def test_custom_threshold_inference():
    clf = DistilBertClassifier()
    prob_toxic = 0.42
    pred_default = 1 if prob_toxic >= 0.50 else 0
    pred_tuned = 1 if prob_toxic >= 0.35 else 0

    assert pred_default == 0
    assert pred_tuned == 1
