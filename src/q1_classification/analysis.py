"""Error analysis helpers for Q1."""

from __future__ import annotations

from collections import Counter
from typing import Sequence


POSITIVE_HINTS = {"great", "good", "amazing", "excellent", "love", "best", "fun"}
NEGATIVE_HINTS = {"bad", "awful", "boring", "terrible", "hate", "worst", "waste"}
NEGATION_HINTS = {"not", "never", "no", "n't"}


def _truncate(text: str, max_chars: int = 280) -> str:
    return text if len(text) <= max_chars else f"{text[: max_chars - 3]}..."


def _guess_error_pattern(text: str) -> str:
    lowered = text.lower()
    tokens = set(lowered.split())

    if tokens & NEGATION_HINTS:
        return "negation_handling"
    if tokens & POSITIVE_HINTS and tokens & NEGATIVE_HINTS:
        return "mixed_sentiment"
    if any(marker in lowered for marker in ["yeah right", "as if", "sure", "totally"]) and "!" in lowered:
        return "irony_or_emphasis"
    if len(lowered.split()) < 20:
        return "very_short_text"
    if len(lowered.split()) > 220:
        return "very_long_text"
    return "domain_specific_or_ambiguous"


def analyze_misclassifications(
    texts: Sequence[str],
    y_true: Sequence[int],
    y_pred: Sequence[int],
    confidences: Sequence[float | None] | None = None,
    n_examples: int = 5,
) -> list[dict]:
    examples: list[dict] = []
    confidence_values = list(confidences) if confidences is not None else [None] * len(texts)

    for index, (text, true_label, predicted_label, confidence) in enumerate(
        zip(texts, y_true, y_pred, confidence_values, strict=False)
    ):
        if true_label == predicted_label:
            continue
        examples.append(
            {
                "index": index,
                "text": _truncate(text),
                "true_label": int(true_label),
                "predicted_label": int(predicted_label),
                "confidence": round(float(confidence), 4) if confidence is not None else None,
                "error_pattern": _guess_error_pattern(text),
            }
        )
        if len(examples) >= n_examples:
            break

    return examples


def identify_error_patterns(misclassified: list[dict]) -> dict[str, int]:
    counts = Counter(item["error_pattern"] for item in misclassified)
    return dict(counts)
