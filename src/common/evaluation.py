"""Evaluation orchestration helpers shared across tasks."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from src.common.metrics import compute_classification_report, compute_confusion_matrix, compute_metrics


def _ordered_labels(predictions: Sequence[int], references: Sequence[int]) -> list[int]:
    labels = {int(label) for label in references}
    labels.update(int(label) for label in predictions)
    return sorted(labels)


def _resolve_label_names(labels: Sequence[int], label_names: Mapping[int, str] | Sequence[str] | None) -> list[str]:
    if isinstance(label_names, Mapping):
        return [str(label_names.get(label, label)) for label in labels]

    if label_names is not None:
        names = list(label_names)
        if len(names) != len(labels):
            raise ValueError("label_names must match the number of evaluated labels.")
        return [str(name) for name in names]

    if list(labels) == [0, 1]:
        return ["negative", "positive"]
    return [str(label) for label in labels]


def _normalize_confusion_matrix(matrix: np.ndarray) -> list[list[float]]:
    row_totals = matrix.sum(axis=1, keepdims=True)
    normalized = np.divide(
        matrix,
        row_totals,
        out=np.zeros_like(matrix, dtype=float),
        where=row_totals != 0,
    )
    return normalized.round(6).tolist()


def evaluate_predictions(
    task: str,
    predictions: Sequence[int],
    references: Sequence[int],
    metrics: Sequence[str] | None = None,
    label_names: Mapping[int, str] | Sequence[str] | None = None,
) -> dict[str, Any]:
    if task != "classification":
        raise NotImplementedError(f"Task '{task}' is not implemented in the current slice.")

    ordered_labels = _ordered_labels(predictions, references)
    resolved_label_names = _resolve_label_names(ordered_labels, label_names)
    confusion_matrix = compute_confusion_matrix(references, predictions, labels=ordered_labels)

    return {
        "metrics": compute_metrics(
            task,
            predictions=predictions,
            references=references,
            metrics=metrics,
        ),
        "classification_report": compute_classification_report(
            references,
            predictions,
            labels=ordered_labels,
        ),
        "confusion_matrix": {
            "label_ids": ordered_labels,
            "label_names": resolved_label_names,
            "matrix": confusion_matrix.tolist(),
            "row_normalized": _normalize_confusion_matrix(confusion_matrix),
            "row_totals": confusion_matrix.sum(axis=1).astype(int).tolist(),
            "column_totals": confusion_matrix.sum(axis=0).astype(int).tolist(),
        },
    }
