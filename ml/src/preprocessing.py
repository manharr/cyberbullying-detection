"""
Modular Natural Language Processing (NLP) Preprocessing Pipeline.
Implements Stages A through F:
- Stage A: Text cleaning & normalization (HTML, URLs, mentions, whitespace)
- Stage B: Tokenization (NLTK word_tokenize with fallback)
- Stage C: Stop-word filtering (with preservation of negation terms)
- Stage D: Lemmatization (NLTK WordNetLemmatizer with POS mapping)
- Stage E: Stemming (PorterStemmer)
- Stage F: Vectorization helper for TF-IDF
Provides full step-by-step inspection for the educational NLP Laboratory interface.
"""

import re
import string
from typing import List, Dict, Any, Optional
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import word_tokenize

# Ensure resources are available
for resource in ["punkt", "stopwords", "wordnet", "omw-1.4"]:
    try:
        nltk.download(resource, quiet=True)
    except Exception:
        pass

# Negation words that carry critical semantic context for toxicity & cyberbullying
NEGATION_WORDS = {
    "no", "not", "nor", "neither", "never", "none", "nobody", "nowhere",
    "nothing", "hardly", "scarcely", "barely", "cannot", "n't", "dont",
    "wont", "isnt", "arent", "wasnt", "werent", "havent", "hasnt", "hadnt"
}


class TextCleaner:
    """Stage A: Text normalization, cleaning, and sanitization."""
    
    HTML_REGEX = re.compile(r"<[^>]+>")
    URL_REGEX = re.compile(r"https?://\S+|www\.\S+")
    MENTION_REGEX = re.compile(r"@[\w_]+")
    IP_REGEX = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
    MULTISPACE_REGEX = re.compile(r"\s+")

    @classmethod
    def clean(cls, text: Optional[str]) -> str:
        if not text or not isinstance(text, str):
            return ""

        # Normalize whitespace
        text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")

        # Remove HTML tags
        text = cls.HTML_REGEX.sub(" ", text)

        # Strip URLs and mentions (anonymize / reduce noise)
        text = cls.URL_REGEX.sub(" ", text)
        text = cls.MENTION_REGEX.sub(" ", text)
        text = cls.IP_REGEX.sub(" ", text)

        # Lowercase text
        text = text.lower()

        # Keep alphanumeric, apostrophes (for negations like don't), and basic sentence punctuation
        # Replace non-standard characters with spaces
        text = re.sub(r"[^a-z0-9'\s!\?]", " ", text)

        # Collapse repeated spaces
        text = cls.MULTISPACE_REGEX.sub(" ", text).strip()
        return text


class TokenizerModule:
    """Stage B: Tokenization."""

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        if not text:
            return []
        try:
            tokens = word_tokenize(text)
        except Exception:
            # Fallback regex tokenizer
            tokens = re.findall(r"\b[\w']+\b|[!?]", text)
        return tokens


class StopWordsFilter:
    """Stage C: Stop-word filtering with negation preservation."""

    def __init__(self, preserve_negations: bool = True):
        self.preserve_negations = preserve_negations
        try:
            base_sw = set(stopwords.words("english"))
        except Exception:
            base_sw = {
                "the", "a", "an", "in", "on", "of", "to", "for", "with", "at",
                "by", "from", "up", "about", "into", "through", "after", "is",
                "am", "are", "was", "were", "be", "been", "being", "have", "has",
                "had", "do", "does", "did", "and", "but", "if", "or", "because",
                "as", "until", "while", "that", "this", "these", "those"
            }

        if self.preserve_negations:
            # Exclude negations from stopwords so they are NOT removed
            self.stop_words = base_sw - NEGATION_WORDS
        else:
            self.stop_words = base_sw

    def filter(self, tokens: List[str]) -> List[str]:
        return [
            token for token in tokens
            if token.lower() not in self.stop_words and token not in string.punctuation
        ]


class LemmatizerModule:
    """Stage D: Lemmatization using WordNet."""

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    @staticmethod
    def _get_wordnet_pos(treebank_tag: str):
        """Map POS tag to first character lemmatize() accepts."""
        if treebank_tag.startswith("J"):
            return wordnet.ADJ
        elif treebank_tag.startswith("V"):
            return wordnet.VERB
        elif treebank_tag.startswith("N"):
            return wordnet.NOUN
        elif treebank_tag.startswith("R"):
            return wordnet.ADV
        else:
            return wordnet.NOUN

    def lemmatize(self, tokens: List[str], use_pos: bool = False) -> List[str]:
        if not tokens:
            return []

        if not use_pos:
            return [self.lemmatizer.lemmatize(t) for t in tokens]

        try:
            tagged = nltk.pos_tag(tokens)
            return [
                self.lemmatizer.lemmatize(token, self._get_wordnet_pos(tag))
                for token, tag in tagged
            ]
        except Exception:
            return [self.lemmatizer.lemmatize(t) for t in tokens]


class StemmerModule:
    """Stage E: Stemming using PorterStemmer."""

    def __init__(self):
        self.stemmer = PorterStemmer()

    def stem(self, tokens: List[str]) -> List[str]:
        return [self.stemmer.stem(t) for t in tokens]


class NLPPipeline:
    """
    Unified end-to-end NLP Preprocessing pipeline.
    Offers configurable stages and detailed step-by-step diagnostic breakdown.
    """

    def __init__(
        self,
        mode: str = "lemmatization",  # 'raw', 'clean_only', 'stopwords', 'lemmatization', 'stemming'
        preserve_negations: bool = True
    ):
        self.mode = mode
        self.preserve_negations = preserve_negations
        self.cleaner = TextCleaner()
        self.tokenizer = TokenizerModule()
        self.sw_filter = StopWordsFilter(preserve_negations=preserve_negations)
        self.lemmatizer = LemmatizerModule()
        self.stemmer = StemmerModule()

    def transform_text(self, text: str) -> str:
        """Transforms a raw string into a preprocessed space-joined token string."""
        if not text or not isinstance(text, str):
            return ""

        cleaned = self.cleaner.clean(text)
        if self.mode == "clean_only":
            return cleaned

        tokens = self.tokenizer.tokenize(cleaned)
        filtered = self.sw_filter.filter(tokens)

        if self.mode == "stopwords":
            return " ".join(filtered)
        elif self.mode == "stemming":
            stems = self.stemmer.stem(filtered)
            return " ".join(stems)
        else:  # default: lemmatization
            lemmas = self.lemmatizer.lemmatize(filtered)
            return " ".join(lemmas)

    def inspect_pipeline_steps(self, text: str) -> Dict[str, Any]:
        """
        Executes all stages sequentially and returns intermediate representations
        for the interactive educational NLP laboratory.
        """
        raw = text if isinstance(text, str) else ""
        cleaned = self.cleaner.clean(raw)
        tokens = self.tokenizer.tokenize(cleaned)
        filtered = self.sw_filter.filter(tokens)
        lemmas = self.lemmatizer.lemmatize(filtered, use_pos=True)
        stems = self.stemmer.stem(filtered)

        # Removed stopwords explanation
        removed_sw = [
            t for t in tokens
            if t.lower() in self.sw_filter.stop_words
        ]
        preserved_neg = [
            t for t in tokens
            if t.lower() in NEGATION_WORDS
        ]

        return {
            "stage_a_raw": raw,
            "stage_a_cleaned": cleaned,
            "stage_b_tokens": tokens,
            "stage_b_token_count": len(tokens),
            "stage_c_filtered_tokens": filtered,
            "stage_c_removed_stopwords": list(set(removed_sw)),
            "stage_c_preserved_negations": list(set(preserved_neg)),
            "stage_d_lemmatized": lemmas,
            "stage_e_stemmed": stems,
            "final_processed_text": " ".join(lemmas)
        }


# Default pipeline instance for production inference
default_nlp_pipeline = NLPPipeline(mode="lemmatization", preserve_negations=True)
