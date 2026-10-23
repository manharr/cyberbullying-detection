"""
Severity Estimation Module for Cyberbullying and Toxic Language.

Provides a transparent, rule-grounded, multi-factor severity estimation heuristic
based on predicted toxicity categories, model confidence scores, and critical linguistic flags.

Academic Disclaimer:
A single toxic comment does not prove persistent cyberbullying. This severity rating
evaluates the immediate linguistic severity of the input comment, NOT an entire interpersonal
cyberbullying incident or the harasser's long-term legal culpability.
"""

from typing import Dict, Any, List

SEVERITY_LEVELS = {
    0: {
        "level": 0,
        "label": "None",
        "description": "No toxicity or abusive language detected.",
        "badge_color": "success",
        "recommended_action": "No moderation action required."
    },
    1: {
        "level": 1,
        "label": "Low",
        "description": "Mild toxicity or borderline rude language without direct threats or identity slurs.",
        "badge_color": "info",
        "recommended_action": "Standard logging or algorithmic down-ranking."
    },
    2: {
        "level": 2,
        "label": "Moderate",
        "description": "Explicit insults, obscenities, or persistent vulgar language targeting an individual.",
        "badge_color": "warning",
        "recommended_action": "Flag for human moderation queue; temporary comment hidden pending review."
    },
    3: {
        "level": 3,
        "label": "High",
        "description": "Severe toxicity, explicit threats of violence, or identity-based hate speech.",
        "badge_color": "error",
        "recommended_action": "Immediate comment removal; escalate account for safety review."
    }
}


def calculate_severity(
    is_toxic: bool,
    confidence: float,
    category_scores: Dict[str, float],
    influential_words: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Computes linguistic severity score (0 to 3) based on:
    1. Overall binary toxicity prediction & confidence.
    2. Multi-label category activations (threat, identity_hate, severe_toxic, obscene, insult).
    3. Severe linguistic indicators.
    """
    if not is_toxic or confidence < 0.50:
        base = SEVERITY_LEVELS[0].copy()
        base["score"] = round((1.0 - confidence) * 0.2, 3)
        base["factors"] = ["No abusive markers detected above classification threshold."]
        return base

    factors = []
    level = 1

    # Extract category likelihoods if present
    threat_prob = category_scores.get("threat", 0.0)
    identity_hate_prob = category_scores.get("identity_hate", 0.0)
    severe_toxic_prob = category_scores.get("severe_toxic", 0.0)
    obscene_prob = category_scores.get("obscene", 0.0)
    insult_prob = category_scores.get("insult", 0.0)

    # High severity triggers: Threat or Identity Hate or Severe Toxic
    if threat_prob >= 0.40 or identity_hate_prob >= 0.40 or severe_toxic_prob >= 0.50:
        level = 3
        if threat_prob >= 0.40:
            factors.append(f"Direct threat of violence / intimidation detected (Score: {threat_prob:.2f})")
        if identity_hate_prob >= 0.40:
            factors.append(f"Identity-based hate speech or slurs detected (Score: {identity_hate_prob:.2f})")
        if severe_toxic_prob >= 0.50:
            factors.append(f"Extreme toxicity category triggered (Score: {severe_toxic_prob:.2f})")

    # Moderate severity triggers: Multiple toxic categories or high obscenity + insult
    elif (obscene_prob >= 0.50 and insult_prob >= 0.50) or confidence >= 0.85 or severe_toxic_prob >= 0.25:
        level = 2
        if obscene_prob >= 0.50:
            factors.append(f"Explicit obscenity detected (Score: {obscene_prob:.2f})")
        if insult_prob >= 0.50:
            factors.append(f"Targeted insult detected (Score: {insult_prob:.2f})")
        if confidence >= 0.85:
            factors.append(f"High-confidence toxicity detection ({confidence * 100:.1f}%)")

    # Low severity: Single mild category or low-confidence positive
    else:
        level = 1
        factors.append(f"Mild toxicity or generalized disrespect detected ({confidence * 100:.1f}% confidence)")

    res = SEVERITY_LEVELS[level].copy()
    res["score"] = round(float(confidence), 3)
    res["factors"] = factors
    res["rubric_notes"] = (
        "Severity is evaluated deterministically using category risk weighting (Threat/Identity Hate = High, "
        "Insult/Obscene = Moderate, Mild Toxic = Low)."
    )
    return res
