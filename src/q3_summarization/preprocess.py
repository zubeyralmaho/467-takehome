"""Preprocessing helpers for Q3 summarization."""

from __future__ import annotations

import re


_WHITESPACE_RE = re.compile(r"\s+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def clean_article(text: str) -> str:
    cleaned = text.replace("@highlight", " ")
    cleaned = cleaned.replace("\u2019", "'")
    cleaned = cleaned.replace("\u201c", '"').replace("\u201d", '"')
    return _WHITESPACE_RE.sub(" ", cleaned).strip()


def truncate_article(text: str, max_words: int = 900) -> str:
    words = text.split()
    if max_words <= 0 or len(words) <= max_words:
        return text
    return " ".join(words[:max_words])


def split_into_sentences(text: str, min_sentence_words: int = 4) -> list[str]:
    normalized = clean_article(text)
    if not normalized:
        return []

    candidates = [sentence.strip() for sentence in _SENTENCE_SPLIT_RE.split(normalized) if sentence.strip()]
    filtered = [sentence for sentence in candidates if len(sentence.split()) >= min_sentence_words]
    return filtered or candidates[:1]