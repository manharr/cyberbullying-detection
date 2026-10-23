"""
Tests for SQLite Database CRUD operations.
"""

import os
import pytest
from backend.app.database.db import (
    init_db, insert_analysis, get_analysis_by_id,
    list_analyses, delete_analysis, get_dashboard_statistics,
    list_moderation_queue, update_moderation_item, record_feedback
)


def setup_module():
    init_db()


def test_insert_and_get_analysis():
    record = insert_analysis(
        comment_text="You are an amazing and helpful mentor!",
        is_toxic=False,
        confidence=0.98,
        primary_class="Non-toxic",
        estimated_severity=0,
        severity_label="None",
        category_scores={"toxic": 0.02},
        influential_words=[{"word": "helpful", "contribution": -0.5, "polarity": "non-toxic"}],
        auto_flag_moderation=False
    )
    assert record is not None
    assert record["id"] is not None
    assert record["is_toxic"] is False
    assert record["estimated_severity"] == 0

    fetched = get_analysis_by_id(record["id"])
    assert fetched is not None
    assert fetched["comment_text"] == "You are an amazing and helpful mentor!"


def test_moderation_flagging():
    # Insert severe comment
    record = insert_analysis(
        comment_text="I will hurt and attack you tomorrow!",
        is_toxic=True,
        confidence=0.95,
        primary_class="Toxic",
        estimated_severity=3,
        severity_label="High",
        category_scores={"threat": 0.90, "toxic": 0.95},
        influential_words=[{"word": "attack", "contribution": 1.2, "polarity": "toxic"}],
        auto_flag_moderation=True
    )
    assert record["estimated_severity"] == 3

    # Check moderation queue has it
    queue = list_moderation_queue(status="PENDING")
    assert len(queue) > 0
    item = next((q for q in queue if q["analysis_id"] == record["id"]), None)
    assert item is not None
    assert item["severity_level"] == 3

    # Update moderation
    updated = update_moderation_item(item["id"], "REMOVED", "Violates safety policy")
    assert updated is True


def test_dashboard_stats():
    stats = get_dashboard_statistics()
    assert "total_analyses" in stats
    assert "toxic_count" in stats
    assert "severity_distribution" in stats
    assert stats["total_analyses"] >= 1


def test_feedback_and_delete():
    record = insert_analysis(
        comment_text="Temporary comment for deletion test",
        is_toxic=False,
        confidence=0.8,
        primary_class="Non-toxic",
        estimated_severity=0,
        severity_label="None",
        category_scores={},
        influential_words=[]
    )
    fid = record_feedback(record["id"], is_accurate=True, suggested_label="Non-toxic", comments="Good")
    assert fid > 0

    del_res = delete_analysis(record["id"])
    assert del_res is True
    assert get_analysis_by_id(record["id"]) is None
