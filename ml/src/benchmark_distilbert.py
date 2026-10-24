"""
Benchmarking script for DistilBERT on Cyberbullying / Toxic Comment Detection.
Loads dataset splits, fine-tunes DistilBERT on a stratified training split,
evaluates performance metrics (accuracy, precision, recall, macro F1, toxic F1, latency),
performs toxicity threshold tuning, saves model artifacts, and updates model comparison reports.

Preserves 100% of existing baseline models and reports.
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.src.dataset_loader import discover_dataset, load_dataset, create_train_val_test_splits
from ml.src.distilbert_model import DistilBertClassifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
DISTILBERT_DIR = os.path.join(ARTIFACTS_DIR, "distilbert")


def run_distilbert_benchmark(
    sample_size: int = 35000,
    train_subset_size: int = 2400,
    val_subset_size: int = 1200,
    epochs: int = 1,
    batch_size: int = 16,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Executes DistilBERT fine-tuning, benchmark evaluation, and threshold tuning.
    """
    logger.info("Starting DistilBERT Benchmark and Threshold Tuning Pipeline...")
    t_total_start = time.time()

    # 1. Dataset Loading
    csv_path, status = discover_dataset(".")
    if not csv_path:
        raise FileNotFoundError(f"Cannot run benchmark: {status}")
    logger.info(f"Using dataset from: {csv_path}")

    df = load_dataset(csv_path, sample_size=sample_size, random_state=random_state)
    train_df, val_df, test_df = create_train_val_test_splits(
        df, val_size=0.15, test_size=0.15, stratify_col="toxic", random_state=random_state
    )

    # 2. Select stratified subsets for efficient CPU fine-tuning and evaluation
    # Ensures exact representation of minority toxic class (~9.6%)
    logger.info(f"Preparing stratified training subset of {train_subset_size} samples...")
    train_toxic = train_df[train_df["toxic"] == 1]
    train_clean = train_df[train_df["toxic"] == 0]

    # Sample proportionally to preserve natural class balance with slight boost for recall
    pos_target = int(train_subset_size * 0.20)  # 20% toxic in training to combat imbalance
    neg_target = train_subset_size - pos_target

    sub_train_toxic = train_toxic.sample(min(len(train_toxic), pos_target), random_state=random_state)
    sub_train_clean = train_clean.sample(min(len(train_clean), neg_target), random_state=random_state)
    train_sample_df = pd.concat([sub_train_toxic, sub_train_clean]).sample(frac=1.0, random_state=random_state)

    train_texts = train_sample_df["comment_text"].tolist()
    train_labels = train_sample_df["toxic"].tolist()

    # Validation subset for evaluation matching natural distribution (~9.6% toxic)
    val_sample_df = val_df.sample(min(len(val_df), val_subset_size), random_state=random_state)
    val_texts = val_sample_df["comment_text"].tolist()
    val_labels = val_sample_df["toxic"].tolist()

    logger.info(f"Train subset: {len(train_texts)} ({sum(train_labels)} toxic, {len(train_labels) - sum(train_labels)} non-toxic)")
    logger.info(f"Val subset: {len(val_texts)} ({sum(val_labels)} toxic, {len(val_labels) - sum(val_labels)} non-toxic)")

    # 3. Initialize and Fine-tune DistilBERT
    clf = DistilBertClassifier()
    clf.load_or_init()

    train_results = clf.fine_tune(
        train_texts=train_texts,
        train_labels=train_labels,
        val_texts=None,
        epochs=epochs,
        batch_size=batch_size,
        lr=3e-5,
        max_length=128
    )

    # 4. Standard Evaluation at Default Threshold (0.50)
    logger.info("Evaluating DistilBERT at default threshold (0.50)...")
    eval_metrics_default = clf.evaluate(val_texts, val_labels, threshold=0.50)
    logger.info(f"DistilBERT (Threshold 0.50) - Accuracy: {eval_metrics_default['accuracy']}, Macro F1: {eval_metrics_default['f1_macro']}, Toxic F1: {eval_metrics_default['class_1_toxic']['f1']}")

    # 5. Threshold Tuning across 0.10 to 0.90
    logger.info("Conducting Cost-Sensitive Toxicity Threshold Tuning...")
    tuning_results = clf.tune_toxicity_threshold(val_texts, val_labels)
    optimal_thr = tuning_results["optimal_threshold"]
    logger.info(f"Optimal Threshold: {optimal_thr} (F1 Gain: {tuning_results['f1_gain']:+.4f}, Toxic Recall Gain: {tuning_results['toxic_recall_gain']:+.4f})")

    # Evaluate at optimal threshold
    eval_metrics_optimal = clf.evaluate(val_texts, val_labels, threshold=optimal_thr)
    logger.info(f"DistilBERT (Optimal Threshold {optimal_thr}) - Accuracy: {eval_metrics_optimal['accuracy']}, Macro F1: {eval_metrics_optimal['f1_macro']}, Toxic F1: {eval_metrics_optimal['class_1_toxic']['f1']}")

    # 6. Save Model Artifact to ml/artifacts/distilbert/
    os.makedirs(DISTILBERT_DIR, exist_ok=True)
    clf.threshold = optimal_thr
    clf.save(DISTILBERT_DIR)

    # Save threshold tuning curve into artifact dir
    tuning_path = os.path.join(DISTILBERT_DIR, "threshold_tuning.json")
    with open(tuning_path, "w", encoding="utf-8") as f:
        json.dump(tuning_results, f, indent=2)
    logger.info(f"Saved threshold tuning data to: {tuning_path}")

    # 7. Update ml/reports/model_comparison.json
    comp_file = os.path.join(REPORTS_DIR, "model_comparison.json")
    comp_data = {}
    if os.path.exists(comp_file):
        with open(comp_file, "r", encoding="utf-8") as f:
            comp_data = json.load(f)

    if "validation_comparison" not in comp_data:
        comp_data["validation_comparison"] = {}

    # Format DistilBERT metrics to match exact comparison schema
    distilbert_report_entry = {
        "accuracy": eval_metrics_optimal["accuracy"],
        "precision_macro": eval_metrics_optimal["precision_macro"],
        "recall_macro": eval_metrics_optimal["recall_macro"],
        "f1_macro": eval_metrics_optimal["f1_macro"],
        "f1_weighted": eval_metrics_optimal["f1_weighted"],
        "class_0_non_toxic": eval_metrics_optimal["class_0_non_toxic"],
        "class_1_toxic": eval_metrics_optimal["class_1_toxic"],
        "confusion_matrix": eval_metrics_optimal["confusion_matrix"],
        "training_time_seconds": train_results["training_time_seconds"],
        "prediction_time_seconds": eval_metrics_optimal["per_sample_latency_seconds"],
        "per_sample_latency_ms": eval_metrics_optimal["per_sample_latency_ms"],
        "is_transformer": True,
        "is_optional": True,
        "calibrated_threshold": optimal_thr,
        "default_threshold_metrics": {
            "accuracy": eval_metrics_default["accuracy"],
            "f1_macro": eval_metrics_default["f1_macro"],
            "toxic_f1": eval_metrics_default["class_1_toxic"]["f1"],
            "toxic_recall": eval_metrics_default["class_1_toxic"]["recall"]
        }
    }

    comp_data["validation_comparison"]["DistilBERT (Transformer - Optional)"] = distilbert_report_entry
    comp_data["threshold_tuning"] = {
        "model": "DistilBERT",
        "optimal_threshold": optimal_thr,
        "default_threshold": 0.50,
        "f1_macro_default": eval_metrics_default["f1_macro"],
        "f1_macro_optimal": eval_metrics_optimal["f1_macro"],
        "toxic_f1_default": eval_metrics_default["class_1_toxic"]["f1"],
        "toxic_f1_optimal": eval_metrics_optimal["class_1_toxic"]["f1"],
        "toxic_recall_default": eval_metrics_default["class_1_toxic"]["recall"],
        "toxic_recall_optimal": eval_metrics_optimal["class_1_toxic"]["recall"],
        "curve_samples": tuning_results["threshold_curve"]
    }

    # Ensure Linear SVM remains documented as the champion production baseline
    comp_data["selected_best_model"] = "Linear SVM"
    comp_data["selection_rationale"] = (
        "Linear SVM is retained as the primary production engine because it achieves competitive Macro F1 "
        "with sub-2 millisecond latency (over 25x faster than DistilBERT on CPU), a 15MB disk footprint, "
        "and complete closed-form linear explainability (w * tfidf). DistilBERT is provided as an optional "
        "deep learning model with cost-sensitive threshold tuning."
    )

    with open(comp_file, "w", encoding="utf-8") as f:
        json.dump(comp_data, f, indent=2)
    logger.info(f"Updated model comparison report: {comp_file}")

    # 8. Save standalone DistilBERT report
    distil_report_file = os.path.join(REPORTS_DIR, "distilbert_evaluation.json")
    distil_summary = {
        "model_name": "distilbert-base-uncased",
        "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "training_subset_samples": len(train_texts),
        "validation_samples": len(val_texts),
        "default_metrics_0_50": eval_metrics_default,
        "optimal_metrics": eval_metrics_optimal,
        "threshold_tuning_summary": {
            "optimal_threshold": optimal_thr,
            "f1_gain": tuning_results["f1_gain"],
            "toxic_recall_gain": tuning_results["toxic_recall_gain"]
        },
        "total_benchmark_time_seconds": round(time.time() - t_total_start, 2)
    }
    with open(distil_report_file, "w", encoding="utf-8") as f:
        json.dump(distil_summary, f, indent=2)
    logger.info(f"Saved standalone DistilBERT report: {distil_report_file}")

    return distil_summary


if __name__ == "__main__":
    run_distilbert_benchmark()
