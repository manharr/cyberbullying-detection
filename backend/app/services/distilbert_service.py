"""
DistilBERT Service for optional deep learning inference and toxicity threshold tuning.
Provides lazy-loaded Transformer inference without impacting default Linear SVM pipeline.
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional

from backend.app.core.config import settings
from ml.src.distilbert_model import DistilBertClassifier
from ml.src.severity import calculate_severity

logger = logging.getLogger(__name__)

DISTILBERT_ARTIFACT_DIR = os.path.join(settings.artifacts_dir, "distilbert")
ACADEMIC_DISCLAIMER = (
    "Academic Notice: This classification detects toxic or abusive language within an individual comment "
    "using an optional fine-tuned DistilBERT transformer. It does NOT independently establish a pattern "
    "of repeated cyberbullying, legal culpability, or the overall context of an interpersonal dispute."
)


class DistilBertService:
    """Manages lazy-loading, inference, and threshold tuning for DistilBERT."""

    def __init__(self):
        self.model = None
        self.is_loaded = False
        self.meta = {}

    def is_available(self) -> bool:
        """Checks if fine-tuned DistilBERT artifacts exist on disk."""
        meta_file = os.path.join(DISTILBERT_ARTIFACT_DIR, "model_meta.json")
        return os.path.exists(meta_file)

    def load_artifacts(self) -> bool:
        """Loads DistilBERT weights and tokenizer into memory on demand."""
        if self.is_loaded:
            return True

        if not self.is_available():
            logger.warning(
                f"DistilBERT artifacts not found at {DISTILBERT_ARTIFACT_DIR}. "
                "Please run `python ml/src/benchmark_distilbert.py` to train and evaluate DistilBERT."
            )
            return False

        try:
            logger.info("Loading DistilBERT service artifacts into memory...")
            self.model = DistilBertClassifier.load_from_dir(DISTILBERT_ARTIFACT_DIR)
            meta_file = os.path.join(DISTILBERT_ARTIFACT_DIR, "model_meta.json")
            with open(meta_file, "r", encoding="utf-8") as f:
                self.meta = json.load(f)
            self.is_loaded = True
            logger.info("DistilBERT service loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load DistilBERT artifacts: {e}")
            self.is_loaded = False
            return False

    def predict_comment(
        self,
        text: str = "",
        threshold: Optional[float] = None,
        nlp_fallback_service = None,
        comment_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classifies comment using fine-tuned DistilBERT with threshold tuning.
        """
        target_text = comment_text if comment_text is not None else text
        if not self.is_loaded:
            success = self.load_artifacts()
            if not success:
                raise RuntimeError("DistilBERT is not loaded. Train first with `python ml/src/benchmark_distilbert.py`.")

        t_start = time.time()
        applied_thr = threshold if threshold is not None else getattr(self.model, "threshold", 0.50)

        # 1. DistilBERT Inference
        probs = self.model.predict_proba(target_text)
        prob_toxic = float(probs[1])
        is_toxic = bool(prob_toxic >= applied_thr)
        latency_ms = round((time.time() - t_start) * 1000, 2)

        # 2. Multi-label Category Scores (utilizing auxiliary models if available for severity)
        cat_scores = {
            "toxic": round(prob_toxic, 4),
            "severe_toxic": round(prob_toxic * 0.4, 4),
            "obscene": round(prob_toxic * 0.5, 4),
            "threat": round(prob_toxic * 0.25, 4),
            "insult": round(prob_toxic * 0.45, 4),
            "identity_hate": round(prob_toxic * 0.2, 4)
        }

        # If fallback service has multilabel models loaded, use their category estimates
        influential = []
        if nlp_fallback_service and nlp_fallback_service.is_loaded:
            try:
                clean_text = nlp_fallback_service.vectorizer.transform([text])
                for cat in ["severe_toxic", "obscene", "threat", "insult", "identity_hate"]:
                    clf = nlp_fallback_service.multilabel_models.get(cat)
                    if clf and hasattr(clf, "predict_proba"):
                        cat_scores[cat] = round(float(clf.predict_proba(clean_text)[0][1]), 4)
                if nlp_fallback_service.explainer:
                    influential = nlp_fallback_service.explainer.explain_comment(text, clean_text, top_k=8)
            except Exception as e:
                logger.debug(f"Auxiliary category enrichment skipped: {e}")

        # 3. Severity Calculation
        confidence = round(prob_toxic if is_toxic else (1.0 - prob_toxic), 4)
        severity_info = calculate_severity(
            is_toxic=is_toxic,
            confidence=confidence,
            category_scores=cat_scores,
            influential_words=influential
        )

        return {
            "comment_text": text,
            "is_toxic": is_toxic,
            "confidence": confidence,
            "primary_class": "Toxic" if is_toxic else "Non-toxic",
            "severity": severity_info,
            "category_scores": cat_scores,
            "influential_words": influential,
            "academic_disclaimer": ACADEMIC_DISCLAIMER,
            "model_used": "DistilBERT (Transformer - Optional)",
            "applied_threshold": round(applied_thr, 3),
            "inference_latency_ms": latency_ms
        }

    def get_threshold_tuning_data(self) -> Dict[str, Any]:
        """Returns threshold tuning curve data if available."""
        tuning_file = os.path.join(DISTILBERT_ARTIFACT_DIR, "threshold_tuning.json")
        if os.path.exists(tuning_file):
            with open(tuning_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["is_available"] = True
                return data
        return {"is_available": False, "optimal_threshold": 0.50, "threshold_curve": []}


distilbert_service = DistilBertService()
