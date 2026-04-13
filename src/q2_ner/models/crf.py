"""Feature-based CRF model for Q2 named entity recognition."""

from __future__ import annotations

from typing import Sequence

from src.q2_ner.preprocess import extract_features_for_crf

try:
    import sklearn_crfsuite
except ImportError:
    sklearn_crfsuite = None


class FeatureBasedCRF:
    """Thin wrapper around sklearn-crfsuite for BIO tagging."""

    def __init__(
        self,
        algorithm: str = "lbfgs",
        c1: float = 0.1,
        c2: float = 0.1,
        max_iterations: int = 100,
        all_possible_transitions: bool = True,
    ):
        if sklearn_crfsuite is None:
            raise ImportError(
                "CRF support requires the 'sklearn-crfsuite' package. Install dependencies from requirements.txt."
            )

        self.model = sklearn_crfsuite.CRF(
            algorithm=algorithm,
            c1=c1,
            c2=c2,
            max_iterations=max_iterations,
            all_possible_transitions=all_possible_transitions,
        )

    def extract_features(self, sentence: Sequence[str]) -> list[dict[str, object]]:
        return extract_features_for_crf(sentence)

    def fit(
        self,
        sentences: Sequence[Sequence[str]],
        label_sequences: Sequence[Sequence[str]],
        validation_data: dict[str, list] | None = None,
    ) -> None:
        del validation_data
        features = [self.extract_features(sentence) for sentence in sentences]
        self.model.fit(features, label_sequences)

    def predict(self, sentences: Sequence[Sequence[str]]) -> list[list[str]]:
        features = [self.extract_features(sentence) for sentence in sentences]
        return [list(labels) for labels in self.model.predict(features)]

    def predict_token_confidences(
        self,
        sentences: Sequence[Sequence[str]],
        predictions: Sequence[Sequence[str]] | None = None,
    ) -> list[list[float | None]]:
        features = [self.extract_features(sentence) for sentence in sentences]
        predicted_labels = list(predictions) if predictions is not None else self.predict(sentences)
        marginals = self.model.predict_marginals(features)

        confidences: list[list[float | None]] = []
        for sentence_marginals, sentence_predictions in zip(marginals, predicted_labels, strict=False):
            sentence_confidences: list[float | None] = []
            for label_distribution, predicted_label in zip(sentence_marginals, sentence_predictions, strict=False):
                sentence_confidences.append(float(label_distribution.get(predicted_label, 0.0)))
            confidences.append(sentence_confidences)

        return confidences