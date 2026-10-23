"""
Dataset discovery, loading, and validation module.
Inspects the workspace, validates Kaggle Jigsaw Toxic Comment Classification Challenge data,
and produces structured dataset inspection reports.
"""

import os
import zipfile
import json
import logging
from typing import Dict, Any, Tuple, Optional
import pandas as pd
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "id",
    "comment_text",
    "toxic",
    "severe_toxic",
    "obscene",
    "threat",
    "insult",
    "identity_hate"
]

TARGET_COLUMNS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]


def discover_dataset(search_dir: str = ".") -> Tuple[Optional[str], str]:
    """
    Searches for train.csv or train.csv.zip in search_dir and subdirectories.
    Safely extracts train.csv.zip if needed without overwriting or escaping workspace.
    Returns (resolved_csv_path, discovery_status_message).
    """
    search_dir = os.path.abspath(search_dir)
    candidate_csv = None
    candidate_zip = None

    # First search for existing uncompressed train.csv
    for root, _, files in os.walk(search_dir):
        # Skip node_modules and .git
        if "node_modules" in root or ".git" in root or ".gemini" in root:
            continue
        for f in files:
            if f.lower() == "train.csv":
                candidate_csv = os.path.join(root, f)
                break
        if candidate_csv:
            break

    if candidate_csv:
        logger.info(f"Discovered existing dataset CSV at: {candidate_csv}")
        return candidate_csv, f"Found extracted CSV: {os.path.basename(candidate_csv)}"

    # Search for ZIP archive
    for root, _, files in os.walk(search_dir):
        if "node_modules" in root or ".git" in root or ".gemini" in root:
            continue
        for f in files:
            if f.lower() == "train.csv.zip":
                candidate_zip = os.path.join(root, f)
                break
        if candidate_zip:
            break

    if candidate_zip:
        logger.info(f"Discovered ZIP archive at: {candidate_zip}. Extracting safely...")
        extract_to = os.path.join(search_dir, "data")
        os.makedirs(extract_to, exist_ok=True)
        with zipfile.ZipFile(candidate_zip, 'r') as zip_ref:
            # Check for path traversal vulnerabilities
            for member in zip_ref.namelist():
                filename = os.path.basename(member)
                if not filename:
                    continue
                # resolve path
                target_path = os.path.abspath(os.path.join(extract_to, filename))
                if not target_path.startswith(os.path.abspath(search_dir)):
                    raise RuntimeError("Zip archive contains unsafe relative path")
                if filename.lower() == "train.csv":
                    zip_ref.extract(member, extract_to)
                    extracted_csv = os.path.join(extract_to, member)
                    return extracted_csv, f"Extracted from {os.path.basename(candidate_zip)}"

    return None, "Dataset train.csv or train.csv.zip not found in workspace"


def inspect_dataset(csv_path: str, save_report_path: Optional[str] = "ml/reports/dataset_inspection.json") -> Dict[str, Any]:
    """
    Inspects and validates dataset schema, record counts, nulls, and label distributions.
    Saves an inspection report.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset file not found at: {csv_path}")

    df = pd.read_csv(csv_path)
    total_records = len(df)
    cols = df.columns.tolist()

    missing_cols = [c for c in EXPECTED_COLUMNS if c not in cols]
    has_all_expected = len(missing_cols) == 0

    null_counts = {col: int(df[col].isnull().sum()) for col in cols}
    label_distributions = {}
    for col in TARGET_COLUMNS:
        if col in cols:
            count = int(df[col].sum())
            pct = round((count / total_records) * 100, 3) if total_records > 0 else 0
            label_distributions[col] = {
                "positive_count": count,
                "negative_count": total_records - count,
                "positive_percentage": pct
            }

    # Binary toxic target analysis
    toxic_positive = label_distributions.get("toxic", {}).get("positive_count", 0)
    toxic_imbalance_ratio = round((total_records - toxic_positive) / toxic_positive, 2) if toxic_positive > 0 else 0

    report = {
        "file_path": os.path.abspath(csv_path),
        "total_records": total_records,
        "columns": cols,
        "expected_columns_present": has_all_expected,
        "missing_columns": missing_cols,
        "null_counts": null_counts,
        "label_distributions": label_distributions,
        "binary_toxic_imbalance_ratio": toxic_imbalance_ratio,
        "dataset_name": "Jigsaw Toxic Comment Classification Challenge",
        "primary_text_column": "comment_text",
        "primary_target_column": "toxic"
    }

    if save_report_path:
        os.makedirs(os.path.dirname(save_report_path), exist_ok=True)
        with open(save_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Saved dataset inspection report to {save_report_path}")

    return report


def load_dataset(
    csv_path: Optional[str] = None,
    sample_size: Optional[int] = None,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Loads dataset, drops null comment texts, fills missing text with empty string.
    Optionally performs stratified sampling to ensure rapid local iteration while maintaining exact label ratio.
    """
    if csv_path is None:
        csv_path, msg = discover_dataset()
        if not csv_path:
            raise FileNotFoundError(f"Could not load dataset: {msg}")

    df = pd.read_csv(csv_path)
    df["comment_text"] = df["comment_text"].fillna("").astype(str)

    if sample_size and sample_size < len(df):
        logger.info(f"Performing stratified sampling of {sample_size} records from {len(df)} total...")
        # Stratify by toxic column
        df, _ = train_test_split(
            df,
            train_size=sample_size,
            stratify=df["toxic"],
            random_state=random_state
        )
        df = df.reset_index(drop=True)

    return df


def create_train_val_test_splits(
    df: pd.DataFrame,
    val_size: float = 0.15,
    test_size: float = 0.15,
    stratify_col: str = "toxic",
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Creates reproducible, strictly separated train, validation, and held-out test splits.
    Held-out test split is preserved strictly for final model evaluation, never for tuning.
    """
    # First split off held-out test
    train_val_df, test_df = train_test_split(
        df,
        test_size=test_size,
        stratify=df[stratify_col],
        random_state=random_state
    )

    # Now split train and validation
    relative_val_size = val_size / (1.0 - test_size)
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=relative_val_size,
        stratify=train_val_df[stratify_col],
        random_state=random_state
    )

    logger.info(f"Dataset split sizes: Train={len(train_df)}, Val={len(val_df)}, Held-out Test={len(test_df)}")
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)


if __name__ == "__main__":
    csv_file, status = discover_dataset(".")
    print(f"Dataset discovery status: {status}")
    if csv_file:
        rep = inspect_dataset(csv_file)
        print(f"Total rows: {rep['total_records']}, Columns: {rep['columns']}")
        print("Label distributions:", json.dumps(rep["label_distributions"], indent=2))
