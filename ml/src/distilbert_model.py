"""
DistilBERT Transformer Model for Cyberbullying and Toxic Language Detection.
Provides optional deep learning classification, evaluation, latency benchmarking,
and cost-sensitive toxicity threshold tuning.

Isolates all Transformer functionality to prevent any impact on classical baseline models.
"""

import os
import time
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification
)

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "distilbert-base-uncased"


class TextDataset(Dataset):
    """PyTorch Dataset for tokenized text inputs."""
    def __init__(self, encodings: Dict[str, Any], labels: Optional[List[int]] = None):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.encodings["input_ids"])

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


class DistilBertClassifier:
    """
    Modular wrapper for fine-tuned or pre-trained DistilBERT sequence classification.
    Runs on CPU or CUDA automatically.
    """
    def __init__(
        self,
        model_name_or_path: str = DEFAULT_MODEL_NAME,
        device: Optional[str] = None,
        threshold: float = 0.50
    ):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.model_name_or_path = model_name_or_path
        self.tokenizer = None
        self.model = None
        self.is_loaded = False
        self.threshold = float(threshold)

    def load_or_init(self):
        """Loads tokenizer and sequence classification model."""
        if self.is_loaded:
            return

        logger.info(f"Loading DistilBERT from '{self.model_name_or_path}' on device '{self.device}'...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name_or_path,
            num_labels=2
        )
        self.model.to(self.device)
        self.model.eval()
        self.is_loaded = True
        logger.info("DistilBERT model and tokenizer initialized successfully.")

    def fine_tune(
        self,
        train_texts: List[str],
        train_labels: List[int],
        val_texts: Optional[List[str]] = None,
        val_labels: Optional[List[int]] = None,
        epochs: int = 1,
        batch_size: int = 16,
        lr: float = 3e-5,
        max_length: int = 128
    ) -> Dict[str, Any]:
        """
        Fine-tunes DistilBERT with weighted cross-entropy to handle class imbalance.
        Designed for efficient execution on CPU / GPU.
        """
        self.load_or_init()
        self.model.train()

        # Tokenization
        logger.info(f"Tokenizing {len(train_texts)} training samples...")
        train_encodings = self.tokenizer(
            train_texts,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        )
        train_dataset = TextDataset(train_encodings, train_labels)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        # Compute positive class weight for imbalanced training
        num_pos = max(1, sum(train_labels))
        num_neg = max(1, len(train_labels) - num_pos)
        pos_weight = float(num_neg / num_pos)
        class_weights = torch.tensor([1.0, min(pos_weight, 5.0)], dtype=torch.float).to(self.device)
        criterion = torch.nn.CrossEntropyLoss(weight=class_weights)

        optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr, weight_decay=0.01)

        t_start = time.time()
        logger.info(f"Starting DistilBERT fine-tuning for {epochs} epoch(s)...")

        for epoch in range(epochs):
            total_loss = 0.0
            for step, batch in enumerate(train_loader):
                optimizer.zero_grad()
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)

                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                loss = criterion(outputs.logits, labels)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / max(1, len(train_loader))
            logger.info(f"Epoch {epoch + 1}/{epochs} - Average Loss: {avg_loss:.4f}")

        training_time = time.time() - t_start
        self.model.eval()

        val_metrics = {}
        if val_texts and val_labels:
            val_metrics = self.evaluate(val_texts, val_labels, max_length=max_length)

        return {
            "training_time_seconds": round(training_time, 3),
            "epochs": epochs,
            "train_samples": len(train_texts),
            "final_loss": round(avg_loss, 4),
            "validation_metrics": val_metrics
        }

    def predict_proba(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        max_length: int = 128
    ) -> np.ndarray:
        """
        Computes calibrated class probabilities for input texts.
        Returns np.ndarray of shape (N, 2): [prob_non_toxic, prob_toxic].
        """
        self.load_or_init()
        single_input = isinstance(texts, str)
        if single_input:
            texts = [texts]

        self.model.eval()
        all_probs = []

        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                inputs = self.tokenizer(
                    batch_texts,
                    truncation=True,
                    padding=True,
                    max_length=max_length,
                    return_tensors="pt"
                )
                input_ids = inputs["input_ids"].to(self.device)
                attention_mask = inputs["attention_mask"].to(self.device)

                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()
                all_probs.append(probs)

        probs_arr = np.vstack(all_probs)
        return probs_arr[0] if single_input else probs_arr

    def predict(
        self,
        texts: Union[str, List[str]],
        threshold: Optional[float] = None,
        max_length: int = 128
    ) -> Union[int, np.ndarray]:
        """
        Binary prediction using specified or default decision threshold.
        """
        thr = threshold if threshold is not None else self.threshold
        probs = self.predict_proba(texts, max_length=max_length)

        if isinstance(texts, str):
            prob_toxic = float(probs[1])
            return 1 if prob_toxic >= thr else 0
        else:
            probs_toxic = probs[:, 1]
            return (probs_toxic >= thr).astype(int)

    def evaluate(
        self,
        texts: List[str],
        labels: List[int],
        threshold: float = 0.50,
        batch_size: int = 32,
        max_length: int = 128
    ) -> Dict[str, Any]:
        """
        Calculates accuracy, macro precision/recall/F1, toxic F1, confusion matrix, and latency.
        """
        t_start = time.time()
        probs = self.predict_proba(texts, batch_size=batch_size, max_length=max_length)
        eval_time = time.time() - t_start

        y_true = np.array(labels)
        y_pred = (probs[:, 1] >= threshold).astype(int)

        acc = accuracy_score(y_true, y_pred)
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
            y_true, y_pred, average="macro", zero_division=0
        )
        p_class, r_class, f1_class, _ = precision_recall_fscore_support(
            y_true, y_pred, average=None, zero_division=0
        )
        _, _, f1_weighted, _ = precision_recall_fscore_support(
            y_true, y_pred, average="weighted", zero_division=0
        )

        cm = confusion_matrix(y_true, y_pred)
        per_sample_latency = (eval_time / max(1, len(texts)))

        return {
            "accuracy": round(float(acc), 4),
            "precision_macro": round(float(p_macro), 4),
            "recall_macro": round(float(r_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
            "f1_weighted": round(float(f1_weighted), 4),
            "class_0_non_toxic": {
                "precision": round(float(p_class[0]), 4),
                "recall": round(float(r_class[0]), 4),
                "f1": round(float(f1_class[0]), 4)
            },
            "class_1_toxic": {
                "precision": round(float(p_class[1]), 4),
                "recall": round(float(r_class[1]), 4),
                "f1": round(float(f1_class[1]), 4)
            },
            "confusion_matrix": {
                "tn": int(cm[0][0]),
                "fp": int(cm[0][1]),
                "fn": int(cm[1][0]),
                "tp": int(cm[1][1])
            },
            "applied_threshold": round(float(threshold), 3),
            "prediction_time_seconds": round(float(eval_time), 4),
            "per_sample_latency_seconds": round(float(per_sample_latency), 5),
            "per_sample_latency_ms": round(float(per_sample_latency * 1000), 2)
        }

    def tune_toxicity_threshold(
        self,
        texts: List[str],
        labels: List[int],
        thresholds: Optional[List[float]] = None,
        target_metric: str = "f1_macro"
    ) -> Dict[str, Any]:
        """
        Conducts grid search over decision thresholds to find the optimal threshold for toxic classification.
        Demonstrates the power of cost-sensitive threshold calibration on imbalanced data.
        """
        if thresholds is None:
            thresholds = [round(x, 2) for x in np.arange(0.10, 0.95, 0.05)]

        probs = self.predict_proba(texts)
        y_true = np.array(labels)
        probs_toxic = probs[:, 1]

        curve = []
        best_threshold = 0.50
        best_score = -1.0

        for thr in thresholds:
            y_pred = (probs_toxic >= thr).astype(int)
            acc = accuracy_score(y_true, y_pred)
            p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
                y_true, y_pred, average="macro", zero_division=0
            )
            p_class, r_class, f1_class, _ = precision_recall_fscore_support(
                y_true, y_pred, average=None, zero_division=0
            )

            toxic_prec = float(p_class[1])
            toxic_rec = float(r_class[1])
            toxic_f1 = float(f1_class[1])

            metric_val = f1_macro if target_metric == "f1_macro" else toxic_f1

            entry = {
                "threshold": round(thr, 2),
                "accuracy": round(float(acc), 4),
                "precision_macro": round(float(p_macro), 4),
                "recall_macro": round(float(r_macro), 4),
                "f1_macro": round(float(f1_macro), 4),
                "toxic_precision": round(toxic_prec, 4),
                "toxic_recall": round(toxic_rec, 4),
                "toxic_f1": round(toxic_f1, 4)
            }
            curve.append(entry)

            if metric_val > best_score:
                best_score = metric_val
                best_threshold = thr

        default_metrics = next((c for c in curve if abs(c["threshold"] - 0.50) < 1e-3), curve[0])
        optimal_metrics = next((c for c in curve if abs(c["threshold"] - best_threshold) < 1e-3), curve[0])

        return {
            "target_metric": target_metric,
            "optimal_threshold": round(float(best_threshold), 2),
            "optimal_metrics": optimal_metrics,
            "default_metrics_at_0_50": default_metrics,
            "f1_gain": round(float(optimal_metrics["f1_macro"] - default_metrics["f1_macro"]), 4),
            "toxic_recall_gain": round(float(optimal_metrics["toxic_recall"] - default_metrics["toxic_recall"]), 4),
            "threshold_curve": curve
        }

    def save(self, save_dir: str):
        """Saves fine-tuned model and tokenizer to disk."""
        os.makedirs(save_dir, exist_ok=True)
        self.load_or_init()
        self.model.save_pretrained(save_dir)
        self.tokenizer.save_pretrained(save_dir)
        meta = {
            "model_type": "DistilBERT",
            "base_model": self.model_name_or_path,
            "default_threshold": self.threshold,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(os.path.join(save_dir, "model_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        logger.info(f"Saved DistilBERT model artifact to: {save_dir}")

    @classmethod
    def load_from_dir(cls, load_dir: str, device: Optional[str] = None):
        """Loads a saved DistilBERT artifact from disk."""
        instance = cls(model_name_or_path=load_dir, device=device)
        instance.load_or_init()
        meta_file = os.path.join(load_dir, "model_meta.json")
        if os.path.exists(meta_file):
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
                instance.threshold = meta.get("default_threshold", 0.50)
        return instance
