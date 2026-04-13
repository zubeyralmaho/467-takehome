"""Evaluation helpers for Q2 named entity recognition."""

from __future__ import annotations

from typing import Any, Sequence

from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
from seqeval.scheme import IOB2


def _compute_token_accuracy(references: Sequence[Sequence[str]], predictions: Sequence[Sequence[str]]) -> float:
    total = 0
    correct = 0
    for gold_sequence, predicted_sequence in zip(references, predictions, strict=False):
        for gold_label, predicted_label in zip(gold_sequence, predicted_sequence, strict=False):
            total += 1
            if gold_label == predicted_label:
                correct += 1
    return float(correct / total) if total else 0.0


def evaluate_predictions(
    predictions: Sequence[Sequence[str]],
    references: Sequence[Sequence[str]],
    metrics: Sequence[str] | None = None,
) -> dict[str, Any]:
    available = {
        "entity_precision": float(precision_score(references, predictions, mode="strict", scheme=IOB2, zero_division=0)),
        "entity_recall": float(recall_score(references, predictions, mode="strict", scheme=IOB2, zero_division=0)),
        "entity_f1": float(f1_score(references, predictions, mode="strict", scheme=IOB2, zero_division=0)),
        "token_accuracy": _compute_token_accuracy(references, predictions),
    }
    selected_metrics = available if not metrics else {name: available[name] for name in metrics if name in available}
    report = classification_report(
        references,
        predictions,
        mode="strict",
        scheme=IOB2,
        output_dict=True,
        zero_division=0,
    )
    return {
        "metrics": selected_metrics,
        "classification_report": report,
    }