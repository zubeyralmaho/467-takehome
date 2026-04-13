"""Shared plotting helpers for experiment outputs."""

from __future__ import annotations

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