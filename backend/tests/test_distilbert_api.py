"""
Unit and integration tests for DistilBERT optional routing and threshold tuning API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_analyze_linear_svm_default_unchanged():
    """Verify that default model routing to Linear SVM remains 100% backward compatible."""
    response = client.post("/api/analyze", json={
        "comment_text": "You are a total clown and should delete your account.",
        "auto_save": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_toxic"] is True
    assert data["primary_class"] == "Toxic"
    assert data["severity"]["level"] >= 1
    assert "model_used" in data or "influential_words" in data


def test_analyze_explicit_linear_svm():
    """Verify explicit model='linear_svm' request."""
    response = client.post("/api/analyze", json={
        "comment_text": "Great work on this open source library, very helpful!",
        "auto_save": False,
        "model": "linear_svm"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_toxic"] is False
    assert data["primary_class"] == "Non-toxic"


def test_threshold_tuning_endpoint():
    """Verify /api/model/threshold-tuning endpoint behaves cleanly."""
    response = client.get("/api/model/threshold-tuning")
    assert response.status_code == 200
    data = response.json()
    assert "is_available" in data
    if data["is_available"]:
        assert "optimal_threshold" in data
        assert "threshold_curve" in data
        assert len(data["threshold_curve"]) > 0


def test_model_comparison_endpoint_includes_benchmark_data():
    """Verify /api/model/comparison returns model comparison data."""
    response = client.get("/api/model/comparison")
    assert response.status_code == 200
    data = response.json()
    assert "model_comparison" in data
    assert "validation_comparison" in data["model_comparison"]
    assert "selected_best_model" in data["model_comparison"]
    # Linear SVM must remain documented as the selected champion
    assert data["model_comparison"]["selected_best_model"] == "Linear SVM"


def test_analyze_distilbert_optional():
    """Verify optional model='distilbert' routing with custom threshold."""
    response = client.post("/api/analyze", json={
        "comment_text": "Thank you for the wonderful tutorial!",
        "auto_save": False,
        "model": "distilbert",
        "threshold": 0.65
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_toxic"] is False
    assert data["primary_class"] == "Non-toxic"
    assert data["model_used"] == "DistilBERT (Transformer - Optional)"
    assert data["applied_threshold"] == 0.65
    assert "inference_latency_ms" in data
