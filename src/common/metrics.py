"""Metric computation helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score


def compute_accuracy(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    return float(accuracy_score(y_true, y_pred))


def compute_macro_f1(y_true: Sequence[int], y_pred: Sequence[int]) -> float:
    return float(f1_score(y_true, y_pred, average="macro"))


def compute_classification_report(y_true: Sequence[int], y_pred: Sequence[int], labels: list[int] | None = None) -> dict:
    return classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)


def compute_confusion_matrix(y_true: Sequence[int], y_pred: Sequence[int], labels: list[int] | None = None) -> np.ndarray:
    return confusion_matrix(y_true, y_pred, labels=labels)


def compute_metrics(task: str, predictions, references, metrics: Sequence[str] | None = None, **kwargs) -> dict[str, float]:
    del kwargs
    requested = list(metrics) if metrics else []

    if task != "classification":
        raise NotImplementedError(f"Task '{task}' is not implemented in the current slice.")

    available = {
        "accuracy": compute_accuracy(references, predictions),
        "macro_f1": compute_macro_f1(references, predictions),
    }
    if not requested:
        return available
    return {name: available[name] for name in requested if name in available}
