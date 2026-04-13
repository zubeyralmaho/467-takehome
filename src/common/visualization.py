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


def plot_grouped_metric_comparison(
    rows: Sequence[Mapping[str, Any]],
    metrics: Sequence[str],
    output_path: str | Path,
    title: str | None = None,
    y_label: str | None = None,
    metric_labels: Mapping[str, str] | None = None,
    label_formats: Mapping[str, str] | None = None,
    log_scale: bool = False,
) -> None:
    _require_matplotlib()

    if not rows:
        raise ValueError("At least one comparison row is required.")
    if not metrics:
        raise ValueError("At least one metric key is required.")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    labels = [str(row.get("display_name", row.get("model", "model"))) for row in rows]
    x_positions = list(range(len(labels)))
    bar_width = 0.8 / len(metrics)
    colors = ["#1f77b4", "#4c78a8", "#72b7b2", "#f28e2b", "#e15759"]

    figure_width = max(8, len(labels) * 2.4)
    figure, axis = plt.subplots(figsize=(figure_width, 5))

    all_values = [float(row[metric]) for metric in metrics for row in rows]
    positive_values = [value for value in all_values if value > 0]

    for metric_index, metric in enumerate(metrics):
        offsets = [
            position - 0.4 + (bar_width / 2) + (metric_index * bar_width)
            for position in x_positions
        ]
        values = [float(row[metric]) for row in rows]
        bars = axis.bar(
            offsets,
            values,
            width=bar_width,
            label=(metric_labels or {}).get(metric, metric.replace("_", " ").title()),
            color=colors[metric_index % len(colors)],
        )

        for bar, value in zip(bars, values, strict=False):
            label_format = (label_formats or {}).get(metric, "{:.3f}")
            if log_scale:
                text_y = value * 1.08
            else:
                text_y = value + max(max(all_values) * 0.02, 0.01)
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                text_y,
                label_format.format(value),
                ha="center",
                va="bottom",
                fontsize=9,
            )

    axis.set_xticks(x_positions, labels=labels)
    if any(len(label) > 14 for label in labels):
        axis.tick_params(axis="x", labelrotation=10)

    if log_scale:
        axis.set_yscale("log")
        if positive_values:
            axis.set_ylim(min(positive_values) * 0.8, max(all_values) * 1.35)
    else:
        axis.set_ylim(0.0, max(max(all_values) * 1.18, 1.0))

    axis.set_ylabel(y_label or "Score")
    axis.set_title(title or "Metric comparison")
    axis.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.4)
    axis.set_axisbelow(True)
    axis.legend()

    figure.tight_layout()
    figure.savefig(destination, dpi=180, bbox_inches="tight")
    plt.close(figure)