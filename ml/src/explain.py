"""
Model-compatible explainability module for text classification.
Provides:
1. Global feature importance using trained linear model coefficients (Logistic Regression / Linear SVM).
2. Local term-level attribution explaining specific comment predictions via linear additive contributions.
"""

from typing import List, Dict, Any, Tuple
import numpy as np


class ModelExplainer:
    """Explains linear model predictions using learned coefficient weights."""

    def __init__(self, vectorizer, model):
        self.vectorizer = vectorizer
        self.model = model
        self.feature_names = np.array(vectorizer.get_feature_names_out())

        # Extract coefficients
        if hasattr(model, "coef_"):
            coef = model.coef_
            if coef.ndim > 1 and coef.shape[0] == 1:
                self.coefficients = coef[0]
            else:
                self.coefficients = coef.ravel()
        elif hasattr(model, "feature_log_prob_"):
            # For Naive Bayes: log prob difference between class 1 and class 0
            self.coefficients = model.feature_log_prob_[1] - model.feature_log_prob_[0]
        else:
            self.coefficients = np.zeros(len(self.feature_names))

    def get_global_feature_importance(self, top_n: int = 25) -> Dict[str, List[Dict[str, Any]]]:
        """Returns top N words most indicative of toxicity and non-toxicity."""
        sorted_indices = np.argsort(self.coefficients)

        # Most negative coefficients -> Non-toxic indicators
        non_toxic_indices = sorted_indices[:top_n]
        non_toxic_features = [
            {"word": self.feature_names[idx], "weight": round(float(self.coefficients[idx]), 4)}
            for idx in non_toxic_indices
        ]

        # Most positive coefficients -> Toxic indicators
        toxic_indices = sorted_indices[::-1][:top_n]
        toxic_features = [
            {"word": self.feature_names[idx], "weight": round(float(self.coefficients[idx]), 4)}
            for idx in toxic_indices
        ]

        return {
            "top_toxic_indicators": toxic_features,
            "top_non_toxic_indicators": non_toxic_features
        }

    def explain_comment(
        self,
        processed_text: str,
        tfidf_vector,
        top_k: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Calculates local linear feature contribution for the specific input:
        contribution = tfidf_value * model_coefficient
        """
        if not processed_text:
            return []

        # Vector is 1 x V sparse matrix
        coo = tfidf_vector.tocoo()
        contributions = []

        for idx, val in zip(coo.col, coo.data):
            word = self.feature_names[idx]
            weight = float(self.coefficients[idx])
            impact = float(val * weight)
            contributions.append({
                "word": word,
                "tfidf_value": round(float(val), 4),
                "model_weight": round(weight, 4),
                "contribution": round(impact, 4),
                "polarity": "toxic" if impact > 0 else "non-toxic"
            })

        # Sort by absolute contribution descending
        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        return contributions[:top_k]
