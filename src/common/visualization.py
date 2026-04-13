"""Shared plotting helpers for experiment outputs."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Mapping

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover - optional dependency during bootstrap
    plt = None


def _require_matplotlib() -> None:
    if plt is None:
        raise ImportError("Visualization support requires the 'matplotlib' package. Install dependencies from requirements.txt.")


def plot_confusion_matrix(
    confusion_matrix: Mapping[str, Any],
    output_path: str | Path,
    title: str | None = None,
) -> None:
    _require_matplotlib()

    label_names = [str(label) for label in confusion_matrix["label_names"]]
    matrix = confusion_matrix["matrix"]
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(6, 5))
    image = axis.imshow(matrix, cmap="Blues")
    figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)

    axis.set_xticks(range(len(label_names)), labels=label_names)
    axis.set_yticks(range(len(label_names)), labels=label_names)
    axis.set_xlabel("Predicted label")
    axis.set_ylabel("Actual label")
    axis.set_title(title or "Confusion matrix")

    max_value = max((max(row) for row in matrix), default=0)
    threshold = max_value / 2 if max_value else 0
    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            axis.text(
                column_index,
                row_index,
                str(int(value)),
                ha="center",
                va="center",
                color="white" if value > threshold else "black",
            )

    figure.tight_layout()
    figure.savefig(destination, dpi=180, bbox_inches="tight")
    plt.close(figure)


def plot_metric_comparison(
    rows: Sequence[Mapping[str, Any]],
    metric: str,
    output_path: str | Path,
    title: str | None = None,
) -> None:
    _require_matplotlib()

    if not rows:
        raise ValueError("At least one comparison row is required.")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    labels = [str(row.get("display_name", row.get("model", "model"))) for row in rows]
    values = [float(row[metric]) for row in rows]

    figure, axis = plt.subplots(figsize=(8, 5))
    bars = axis.bar(labels, values, color=["#1f77b4", "#4c78a8", "#72b7b2", "#f28e2b", "#e15759"][: len(rows)])

    axis.set_ylim(0.0, max(max(values) * 1.15, 1.0))
    axis.set_ylabel(metric.replace("_", " ").title())
    axis.set_title(title or f"{metric.replace('_', ' ').title()} comparison")
    axis.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.4)
    axis.set_axisbelow(True)

    for bar, value in zip(bars, values, strict=False):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.01,
            f"{value:.3f}",
            ha="center",
            va="bottom",
        )

    figure.tight_layout()
    figure.savefig(destination, dpi=180, bbox_inches="tight")
    plt.close(figure)