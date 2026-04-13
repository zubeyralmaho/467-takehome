"""Models for Q2 named entity recognition."""

try:
    from src.q2_ner.models.crf import FeatureBasedCRF
except ImportError:  # pragma: no cover - optional dependency during bootstrap
    FeatureBasedCRF = None

try:
    from src.q2_ner.models.bilstm_crf import BiLSTMCRFTagger
except ImportError:  # pragma: no cover - optional dependency during bootstrap
    BiLSTMCRFTagger = None

try:
    from src.q2_ner.models.bert_ner import BERTNERModel
except ImportError:  # pragma: no cover - optional dependency during bootstrap
    BERTNERModel = None

__all__ = ["FeatureBasedCRF", "BiLSTMCRFTagger", "BERTNERModel"]