"""Evaluation helpers for Q4 machine translation."""

from __future__ import annotations

from sacrebleu.metrics import BLEU, CHRF


def evaluate_predictions(predictions: list[str], references: list[str], metrics: list[str]) -> dict[str, object]:
    bleu_metric = BLEU(tokenize="intl", effective_order=True)
    chrf_metric = CHRF()

    overall: dict[str, float] = {}
    if "bleu" in metrics:
        overall["bleu"] = bleu_metric.corpus_score(predictions, [references]).score / 100.0
    if "chrf" in metrics:
        overall["chrf"] = chrf_metric.corpus_score(predictions, [references]).score / 100.0

    per_example: list[dict[str, float]] = []
    for prediction, reference in zip(predictions, references, strict=False):
        row: dict[str, float] = {}
        if "bleu" in metrics:
            row["bleu"] = bleu_metric.sentence_score(prediction, [reference]).score / 100.0
        if "chrf" in metrics:
            row["chrf"] = chrf_metric.sentence_score(prediction, [reference]).score / 100.0
        per_example.append(row)

    return {
        "metrics": overall,
        "per_example": per_example,
    }