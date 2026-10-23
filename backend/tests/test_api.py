"""
FastAPI Integration Tests using FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["models_loaded"] is True
    assert data["database_connected"] is True


def test_analyze_comment_non_toxic():
    response = client.post("/api/analyze", json={
        "comment_text": "Good luck with your exam, you studied hard and will do well!",
        "auto_save": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_toxic"] is False
    assert data["primary_class"] == "Non-toxic"
    assert data["severity"]["level"] == 0
    assert "academic_disclaimer" in data


def test_analyze_comment_toxic():
    response = client.post("/api/analyze", json={
        "comment_text": "You are a stupid idiot and I hate you!",
        "auto_save": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_toxic"] is True
    assert data["primary_class"] == "Toxic"
    assert data["severity"]["level"] >= 1
    assert len(data["influential_words"]) > 0


def test_dashboard_stats_endpoint():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_analyses" in data
    assert "toxic_count" in data


def test_model_metrics_endpoint():
    response = client.get("/api/model/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "evaluation" in data
    assert "held_out_test_metrics" in data["evaluation"]


def test_model_comparison_endpoint():
    response = client.get("/api/model/comparison")
    assert response.status_code == 200
    data = response.json()
    assert "model_comparison" in data
    assert "preprocessing_experiments" in data


def test_nlp_laboratory_endpoint():
    response = client.post("/api/nlp/laboratory", json={
        "text": "Bullies are <b>not</b> going to defeat us @school!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "stage_a_cleaned" in data
    assert "stage_b_tokens" in data
    assert "stage_c_filtered_tokens" in data
    assert "stage_d_lemmatized" in data
    assert "stage_e_stemmed" in data


def test_moderation_queue_endpoint():
    response = client.get("/api/moderation/queue")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_error_and_fairness_endpoints():
    res_err = client.get("/api/evaluation/errors")
    assert res_err.status_code == 200
    assert "fp_examples" in res_err.json()

    res_fair = client.get("/api/evaluation/fairness")
    assert res_fair.status_code == 200
    assert "identity_subgroups" in res_fair.json()
