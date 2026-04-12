"""TF-IDF based baselines for text classification."""

from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC


class TFIDFClassifier:
    """TF-IDF vectorizer paired with a classical linear classifier."""

    def __init__(
        self,
        classifier_type: str = "lr",
        max_features: int = 50000,
        ngram_range: tuple[int, int] = (1, 2),
        C: float = 1.0,
    ):
        self.classifier_type = classifier_type
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            strip_accents="unicode",
            sublinear_tf=True,
        )
        if classifier_type == "lr":
            self.classifier = LogisticRegression(C=C, max_iter=1000, solver="liblinear", random_state=42)
        elif classifier_type == "svm":
            self.classifier = LinearSVC(C=C)
        else:
            raise ValueError(f"Unsupported classifier_type: {classifier_type}")

    def fit(self, texts: list[str], labels: list[int]) -> None:
        features = self.vectorizer.fit_transform(texts)
        self.classifier.fit(features, labels)

    def predict(self, texts: list[str]) -> np.ndarray:
        features = self.vectorizer.transform(texts)
        return self.classifier.predict(features)

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        if not hasattr(self.classifier, "predict_proba"):
            raise AttributeError(f"{self.classifier.__class__.__name__} does not support predict_proba.")
        features = self.vectorizer.transform(texts)
        return self.classifier.predict_proba(features)

    def predict_confidence(self, texts: list[str]) -> list[float | None]:
        features = self.vectorizer.transform(texts)

        if hasattr(self.classifier, "predict_proba"):
            probabilities = self.classifier.predict_proba(features)
            return probabilities.max(axis=1).astype(float).tolist()

        if hasattr(self.classifier, "decision_function"):
            margins = np.asarray(self.classifier.decision_function(features))
            if margins.ndim > 1:
                margins = np.max(margins, axis=1)
            confidences = 1.0 / (1.0 + np.exp(-np.abs(margins)))
            return confidences.astype(float).tolist()

        return [None] * features.shape[0]
