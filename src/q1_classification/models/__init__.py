"""Models for Q1 text classification."""

from src.q1_classification.models.tfidf_classifier import TFIDFClassifier

try:
	from src.q1_classification.models.bilstm import BiLSTMClassifier
except ImportError:  # pragma: no cover - optional dependency during bootstrap
	BiLSTMClassifier = None

__all__ = ["TFIDFClassifier", "BiLSTMClassifier"]
