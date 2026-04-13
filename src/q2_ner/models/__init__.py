"""Models for Q2 named entity recognition."""

try:
    from src.q2_ner.models.crf import FeatureBasedCRF
except ImportError:  # pragma: no cover - optional dependency during bootstrap
    FeatureBasedCRF = None

__all__ = ["FeatureBasedCRF"]