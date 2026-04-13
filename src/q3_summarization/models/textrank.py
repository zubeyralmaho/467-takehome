"""Graph-based extractive summarizer for Q3."""

from __future__ import annotations

import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.q3_summarization.preprocess import split_into_sentences


class TextRankSummarizer:
    def __init__(
        self,
        similarity_method: str = "tfidf",
        damping: float = 0.85,
        num_sentences: int = 3,
        max_sentences: int = 40,
        min_sentence_words: int = 4,
    ):
        if similarity_method != "tfidf":
            raise ValueError("Only tfidf similarity is implemented in the current Q3 slice.")
        self.similarity_method = similarity_method
        self.damping = damping
        self.num_sentences = num_sentences
        self.max_sentences = max_sentences
        self.min_sentence_words = min_sentence_words

    def fit(self, *_args, **_kwargs) -> None:
        return None

    def build_similarity_matrix(self, sentences: list[str]) -> np.ndarray:
        if len(sentences) <= 1:
            return np.zeros((len(sentences), len(sentences)), dtype=float)

        try:
            tfidf_matrix = TfidfVectorizer(stop_words="english").fit_transform(sentences)
        except ValueError:
            return np.zeros((len(sentences), len(sentences)), dtype=float)

        similarity_matrix = cosine_similarity(tfidf_matrix)
        np.fill_diagonal(similarity_matrix, 0.0)
        return similarity_matrix

    def rank_sentences(self, similarity_matrix: np.ndarray) -> list[float]:
        sentence_count = similarity_matrix.shape[0]
        if sentence_count == 0:
            return []
        if sentence_count == 1 or np.count_nonzero(similarity_matrix) == 0:
            return [1.0] * sentence_count

        graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(graph, alpha=self.damping, max_iter=100, tol=1.0e-6, weight="weight")
        return [float(scores[index]) for index in range(sentence_count)]

    def summarize(self, text: str) -> str:
        sentences = split_into_sentences(text, min_sentence_words=self.min_sentence_words)
        if not sentences:
            return ""

        candidate_sentences = sentences[: self.max_sentences]
        if len(candidate_sentences) <= self.num_sentences:
            return " ".join(candidate_sentences)

        similarity_matrix = self.build_similarity_matrix(candidate_sentences)
        scores = self.rank_sentences(similarity_matrix)
        ranked_indices = sorted(
            range(len(candidate_sentences)),
            key=lambda index: (-scores[index], index),
        )
        selected_indices = sorted(ranked_indices[: self.num_sentences])
        return " ".join(candidate_sentences[index] for index in selected_indices)

    def predict(self, texts: list[str]) -> list[str]:
        return [self.summarize(text) for text in texts]