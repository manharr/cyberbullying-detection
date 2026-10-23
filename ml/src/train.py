"""
Model Training and Comparison Pipeline.
Trains traditional ML models:
1. Logistic Regression (class_weight='balanced')
2. Linear Support Vector Machine (LinearSVC with calibration)
3. Multinomial Naive Bayes (alpha=0.1)
Also trains multi-label classifiers for 6 toxicity sub-categories.

Strict adherence to data discipline:
- Vectorizer is fitted strictly on the training set only.
- Validation set is used for model comparison and selection.
- Held-out test set is evaluated ONLY once on the selected best model.
- All metrics (Accuracy, Precision, Recall, Macro/Weighted F1, Confusion Matrix, Timing) are saved to reports.
"""

import os
import sys
import time
import json
import logging
import argparse
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ml.src.dataset_loader import discover_dataset, inspect_dataset, load_dataset, create_train_val_test_splits, TARGET_COLUMNS
from ml.src.preprocessing import default_nlp_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../artifacts"))
REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../reports"))
os.makedirs(ARTIFACTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def evaluate_predictions(y_true, y_pred, y_prob=None, train_time=0.0, eval_time=0.0) -> Dict[str, Any]:
    """Calculates comprehensive evaluation metrics."""
    acc = accuracy_score(y_true, y_pred)
    prec_macro = precision_score(y_true, y_pred, average="macro", zero_division=0)
    rec_macro = recall_score(y_true, y_pred, average="macro", zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    # Per-class metrics
    prec_per_class = precision_score(y_true, y_pred, average=None, zero_division=0).tolist()
    rec_per_class = recall_score(y_true, y_pred, average=None, zero_division=0).tolist()
    f1_per_class = f1_score(y_true, y_pred, average=None, zero_division=0).tolist()

    cm = confusion_matrix(y_true, y_pred).tolist()

    return {
        "accuracy": round(float(acc), 4),
        "precision_macro": round(float(prec_macro), 4),
        "recall_macro": round(float(rec_macro), 4),
        "f1_macro": round(float(f1_macro), 4),
        "f1_weighted": round(float(f1_weighted), 4),
        "class_0_non_toxic": {
            "precision": round(float(prec_per_class[0]), 4),
            "recall": round(float(rec_per_class[0]), 4),
            "f1": round(float(f1_per_class[0]), 4),
        },
        "class_1_toxic": {
            "precision": round(float(prec_per_class[1]), 4),
            "recall": round(float(rec_per_class[1]), 4),
            "f1": round(float(f1_per_class[1]), 4),
        },
        "confusion_matrix": {
            "tn": int(cm[0][0]),
            "fp": int(cm[0][1]),
            "fn": int(cm[1][0]),
            "tp": int(cm[1][1])
        },
        "training_time_seconds": round(float(train_time), 3),
        "prediction_time_seconds": round(float(eval_time), 3)
    }


def run_training_pipeline(sample_size: int = 40000, random_state: int = 42):
    """Executes the complete end-to-end model training workflow."""
    logger.info("Starting MCA NLP Cyberbullying Model Training Pipeline...")
    start_all = time.time()

    # 1. Dataset Discovery & Inspection
    csv_path, status = discover_dataset(".")
    if not csv_path:
        raise FileNotFoundError(f"Cannot train: {status}")
    logger.info(f"Using dataset from: {csv_path}")

    inspection_report = inspect_dataset(csv_path, os.path.join(REPORTS_DIR, "dataset_inspection.json"))

    # 2. Load dataset with stratified sampling if specified
    df = load_dataset(csv_path, sample_size=sample_size, random_state=random_state)
    logger.info(f"Loaded {len(df)} records. Toxic class ratio: {df['toxic'].mean():.4f}")

    # 3. Create splits (Train 70%, Val 15%, Test 15%)
    train_df, val_df, test_df = create_train_val_test_splits(
        df, val_size=0.15, test_size=0.15, stratify_col="toxic", random_state=random_state
    )

    # 4. Preprocess texts using modular NLPPipeline
    logger.info("Preprocessing train, val, and test texts...")
    t0 = time.time()
    train_clean = [default_nlp_pipeline.transform_text(t) for t in train_df["comment_text"]]
    val_clean = [default_nlp_pipeline.transform_text(t) for t in val_df["comment_text"]]
    test_clean = [default_nlp_pipeline.transform_text(t) for t in test_df["comment_text"]]
    logger.info(f"Preprocessing completed in {time.time() - t0:.2f} seconds.")

    y_train = train_df["toxic"].values
    y_val = val_df["toxic"].values
    y_test = test_df["toxic"].values

    # 5. Fit TF-IDF Vectorizer STRICTLY on training data
    logger.info("Fitting TF-IDF Vectorizer on training data only...")
    vectorizer = TfidfVectorizer(
        max_features=12000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2
    )
    X_train = vectorizer.fit_transform(train_clean)
    X_val = vectorizer.transform(val_clean)
    X_test = vectorizer.transform(test_clean)
    logger.info(f"TF-IDF matrix shape: {X_train.shape}")

    # Save vectorizer artifact
    vectorizer_path = os.path.join(ARTIFACTS_DIR, "tfidf_vectorizer.joblib")
    joblib.dump(vectorizer, vectorizer_path)
    logger.info(f"Saved vectorizer to {vectorizer_path}")

    # 6. Train candidate models
    models = {
        "Logistic Regression": LogisticRegression(
            C=1.5,
            class_weight="balanced",
            max_iter=1000,
            random_state=random_state
        ),
        "Linear SVM": CalibratedClassifierCV(
            LinearSVC(C=0.8, class_weight="balanced", random_state=random_state, max_iter=2000),
            cv=3
        ),
        "Naive Bayes": MultinomialNB(alpha=0.1)
    }

    model_evaluations = {}
    trained_model_objects = {}

    for name, clf in models.items():
        logger.info(f"Training {name}...")
        t_start = time.time()
        clf.fit(X_train, y_train)
        t_train = time.time() - t_start

        # Validation prediction
        t_eval_start = time.time()
        y_val_pred = clf.predict(X_val)
        t_eval = time.time() - t_eval_start

        metrics = evaluate_predictions(y_val, y_val_pred, train_time=t_train, eval_time=t_eval)
        model_evaluations[name] = metrics
        trained_model_objects[name] = clf
        logger.info(f"{name} Validation Macro F1: {metrics['f1_macro']}, Toxic F1: {metrics['class_1_toxic']['f1']}")

    # Save individual model artifacts
    joblib.dump(trained_model_objects["Logistic Regression"], os.path.join(ARTIFACTS_DIR, "model_lr.joblib"))
    joblib.dump(trained_model_objects["Linear SVM"], os.path.join(ARTIFACTS_DIR, "model_svm.joblib"))
    joblib.dump(trained_model_objects["Naive Bayes"], os.path.join(ARTIFACTS_DIR, "model_nb.joblib"))

    # 7. Model Selection: Choose best based on Macro F1 on validation set
    best_name = max(model_evaluations.keys(), key=lambda k: model_evaluations[k]["f1_macro"])
    best_model = trained_model_objects[best_name]
    logger.info(f"Selected best model: '{best_name}' with Macro F1: {model_evaluations[best_name]['f1_macro']}")
    joblib.dump(best_model, os.path.join(ARTIFACTS_DIR, "best_model.joblib"))

    # 8. Evaluate best model on HELD-OUT test set (NEVER tuned on!)
    logger.info(f"Evaluating best model ({best_name}) on held-out test set...")
    t_test_eval_start = time.time()
    y_test_pred = best_model.predict(X_test)
    t_test_eval = time.time() - t_test_eval_start
    test_metrics = evaluate_predictions(y_test, y_test_pred, eval_time=t_test_eval)

    # 9. Train multi-label classifiers for 6 categories
    logger.info("Training multi-label category classifiers (toxic, severe_toxic, obscene, threat, insult, identity_hate)...")
    multilabel_models = {}
    for cat in TARGET_COLUMNS:
        y_cat_train = train_df[cat].values
        # Use Logistic Regression with balanced weighting
        clf_cat = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=random_state)
        clf_cat.fit(X_train, y_cat_train)
        multilabel_models[cat] = clf_cat
        logger.info(f"Trained classifier for category: {cat}")

    joblib.dump(multilabel_models, os.path.join(ARTIFACTS_DIR, "multilabel_classifiers.joblib"))

    # 10. Save Reports
    comparison_report = {
        "validation_comparison": model_evaluations,
        "selected_best_model": best_name,
        "selection_criteria": "Highest Macro F1-score and class-1 (toxic) recall balance on validation split",
        "dataset_sample_size": len(df),
        "split_counts": {
            "train": len(train_df),
            "val": len(val_df),
            "test": len(test_df)
        }
    }
    with open(os.path.join(REPORTS_DIR, "model_comparison.json"), "w", encoding="utf-8") as f:
        json.dump(comparison_report, f, indent=2)

    test_report = {
        "best_model_name": best_name,
        "held_out_test_metrics": test_metrics,
        "held_out_test_samples": len(test_df),
        "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(REPORTS_DIR, "test_evaluation.json"), "w", encoding="utf-8") as f:
        json.dump(test_report, f, indent=2)

    metadata = {
        "dataset_path": csv_path,
        "sample_size": sample_size,
        "training_duration_seconds": round(time.time() - start_all, 2),
        "vectorizer_vocab_size": len(vectorizer.vocabulary_),
        "categories_supported": TARGET_COLUMNS,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(REPORTS_DIR, "training_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info("Training pipeline finished successfully! Artifacts and reports generated.")
    return comparison_report, test_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train MCA NLP Cyberbullying Models")
    parser.add_argument("--sample-size", type=int, default=40000, help="Stratified sample size for fast training")
    args = parser.parse_args()
    run_training_pipeline(sample_size=args.sample_size)
