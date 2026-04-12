"""Preprocessing utilities for Q1 text classification."""

from __future__ import annotations

import re
from html import unescape

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


class TextPreprocessor:
    """Simple configurable text normalization pipeline."""

    def __init__(self, config):
        self.lowercase = config.preprocess.lowercase
        self.remove_html = config.preprocess.remove_html
        self.remove_special = config.preprocess.remove_special
        self.remove_stopwords = config.preprocess.remove_stopwords
        self.max_length = config.preprocess.max_length

    def __call__(self, text: str) -> str:
        cleaned = unescape(text or "")
        if self.remove_html:
            cleaned = re.sub(r"<[^>]+>", " ", cleaned)

        cleaned = cleaned.replace("\n", " ").replace("\r", " ")
        if self.lowercase:
            cleaned = cleaned.lower()

        if self.remove_special:
            pattern = r"[^a-z0-9\s']" if self.lowercase else r"[^A-Za-z0-9\s']"
            cleaned = re.sub(pattern, " ", cleaned)

        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        tokens = cleaned.split()

        if self.remove_stopwords:
            tokens = [token for token in tokens if token not in ENGLISH_STOP_WORDS]

        if self.max_length:
            tokens = tokens[: self.max_length]

        return " ".join(tokens)
