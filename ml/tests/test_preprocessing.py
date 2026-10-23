"""
Unit tests for NLP preprocessing stages (Stages A through E).
"""

import pytest
from ml.src.preprocessing import (
    TextCleaner, TokenizerModule, StopWordsFilter,
    LemmatizerModule, StemmerModule, NLPPipeline, NEGATION_WORDS
)


def test_text_cleaner():
    cleaner = TextCleaner()
    raw = "<p>Check this out: https://example.com @user123! BAD WORDS! 192.168.1.1</p>"
    cleaned = cleaner.clean(raw)
    assert "bad words" in cleaned
    assert "https://" not in cleaned
    assert "@user123" not in cleaned
    assert "192.168.1.1" not in cleaned


def test_tokenizer():
    text = "hello world, don't hate!"
    tokens = TokenizerModule.tokenize(text)
    assert len(tokens) >= 4
    assert "hello" in tokens
    assert "hate" in tokens


def test_stopwords_filter_preserves_negations():
    sw_filter = StopWordsFilter(preserve_negations=True)
    tokens = ["this", "is", "not", "a", "good", "movie", "no", "never"]
    filtered = sw_filter.filter(tokens)
    # Check that negations are preserved
    assert "not" in filtered
    assert "no" in filtered
    assert "never" in filtered
    # Non-negation stopwords are removed
    assert "this" not in filtered
    assert "is" not in filtered


def test_lemmatizer():
    lemmatizer = LemmatizerModule()
    words = ["bullies", "running", "better"]
    lemmas = lemmatizer.lemmatize(words, use_pos=False)
    assert "bully" in lemmas


def test_stemmer():
    stemmer = StemmerModule()
    words = ["connected", "connecting", "connection"]
    stems = stemmer.stem(words)
    assert all(s == "connect" for s in stems)


def test_nlp_pipeline_step_by_step():
    pipeline = NLPPipeline(mode="lemmatization", preserve_negations=True)
    report = pipeline.inspect_pipeline_steps("You are <b>not</b> smart @person!")
    assert "stage_a_cleaned" in report
    assert "stage_b_tokens" in report
    assert "stage_c_filtered_tokens" in report
    assert "stage_d_lemmatized" in report
    assert "stage_e_stemmed" in report
    assert "not" in report["stage_c_preserved_negations"]
