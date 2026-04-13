"""Lead-3 extractive baseline for Q3 summarization."""

from __future__ import annotations

from src.q3_summarization.preprocess import split_into_sentences


class Lead3Summarizer:
    """Baseline that returns the first *n* sentences of each article."""

    def __init__(self, num_sentences: int = 3, min_sentence_words: int = 4):
        self.num_sentences = num_sentences
        self.min_sentence_words = min_sentence_words

    def fit(self, *_args, **_kwargs) -> None:
        return None

    def summarize(self, text: str) -> str:
        sentences = split_into_sentences(text, min_sentence_words=self.min_sentence_words)
        selected = sentences[: self.num_sentences]
        return " ".join(selected) if selected else text[:200]

    def predict(self, texts: list[str]) -> list[str]:
        return [self.summarize(t) for t in texts]
