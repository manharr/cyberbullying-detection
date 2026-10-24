"""
Pydantic data validation schemas for the Cyberbullying Detection & Severity API.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    comment_text: str = Field(..., min_length=1, max_length=5000, description="The comment text to classify")
    auto_save: bool = Field(default=True, description="Whether to persist analysis to database")
    model: Optional[str] = Field(default="linear_svm", description="Classifier selection: 'linear_svm' (default) or 'distilbert'")
    threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Optional custom toxicity decision threshold")


class InfluentialWord(BaseModel):
    word: str
    tfidf_value: float
    model_weight: float
    contribution: float
    polarity: str


class SeverityDetail(BaseModel):
    level: int
    label: str
    description: str
    badge_color: str
    recommended_action: str
    score: float
    factors: List[str]


class AnalyzeResponse(BaseModel):
    id: Optional[int] = None
    comment_text: str
    is_toxic: bool
    confidence: float
    primary_class: str
    severity: SeverityDetail
    category_scores: Dict[str, float]
    influential_words: List[InfluentialWord]
    academic_disclaimer: str
    created_at: Optional[str] = None
    model_used: Optional[str] = Field(default="Linear SVM (Champion)", description="Model used for prediction")
    applied_threshold: Optional[float] = Field(default=None, description="Applied decision threshold")
    inference_latency_ms: Optional[float] = Field(default=None, description="Inference latency in ms")


class BatchAnalyzeItem(BaseModel):
    row_index: int
    comment_text: str
    is_toxic: bool
    confidence: float
    estimated_severity: int
    severity_label: str
    category_scores: Dict[str, float]


class BatchAnalyzeResponse(BaseModel):
    total_processed: int
    total_toxic: int
    total_non_toxic: int
    results: List[BatchAnalyzeItem]
    errors: List[Dict[str, Any]]


class ModerationItem(BaseModel):
    id: int
    analysis_id: Optional[int]
    comment_text: str
    flagged_reason: str
    severity_level: int
    status: str
    reviewer_notes: Optional[str]
    reviewed_at: Optional[str]
    created_at: str


class ModerationUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(APPROVED|REMOVED|ESCALATED)$")
    reviewer_notes: Optional[str] = None


class FeedbackRequest(BaseModel):
    analysis_id: int
    is_accurate: bool
    suggested_label: Optional[str] = None
    user_comments: Optional[str] = None


class NlpLabRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class NlpLabResponse(BaseModel):
    stage_a_raw: str
    stage_a_cleaned: str
    stage_b_tokens: List[str]
    stage_b_token_count: int
    stage_c_filtered_tokens: List[str]
    stage_c_removed_stopwords: List[str]
    stage_c_preserved_negations: List[str]
    stage_d_lemmatized: List[str]
    stage_e_stemmed: List[str]
    tfidf_active_terms: List[Dict[str, Any]]
