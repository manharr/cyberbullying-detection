"""
Unit tests for dataset discovery, validation, and splitting.
"""

import os
import pytest
import pandas as pd
from ml.src.dataset_loader import (
    discover_dataset, inspect_dataset,
    EXPECTED_COLUMNS, TARGET_COLUMNS, create_train_val_test_splits
)


def test_discover_dataset():
    csv_path, msg = discover_dataset(".")
    assert csv_path is not None, f"Discovery failed: {msg}"
    assert os.path.exists(csv_path)
    assert csv_path.lower().endswith("train.csv")


def test_dataset_schema():
    csv_path, _ = discover_dataset(".")
    report = inspect_dataset(csv_path, save_report_path=None)
    assert report["total_records"] > 0
    assert report["expected_columns_present"] is True
    for col in EXPECTED_COLUMNS:
        assert col in report["columns"]
    for cat in TARGET_COLUMNS:
        assert cat in report["label_distributions"]


def test_train_val_test_splits():
    # Mock dataframe
    dummy_data = {
        "id": [str(i) for i in range(100)],
        "comment_text": [f"test comment {i}" for i in range(100)],
        "toxic": [1 if i % 5 == 0 else 0 for i in range(100)]
    }
    df = pd.DataFrame(dummy_data)
    train_df, val_df, test_df = create_train_val_test_splits(df, val_size=0.15, test_size=0.15, stratify_col="toxic", random_state=42)

    assert len(train_df) + len(val_df) + len(test_df) == 100
    assert abs(len(train_df) - 70) <= 2
    # Strict separation
    train_ids = set(train_df["id"])
    val_ids = set(val_df["id"])
    test_ids = set(test_df["id"])
    assert train_ids.isdisjoint(val_ids)
    assert train_ids.isdisjoint(test_ids)
    assert val_ids.isdisjoint(test_ids)
