"""Helpers for saving experiment outputs."""

from __future__ import annotations

import csv
import json
import platform
import sys
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import Any, Iterable, Mapping

from src.common.config import Config


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass
    return value


def create_run_dir(base_dir: str, question: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(base_dir) / question / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return str(run_dir)


def save_metrics(metrics: Mapping, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(_to_jsonable(metrics), handle, ensure_ascii=False, indent=2)


def save_predictions(rows: Iterable[Mapping[str, object]], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        return

    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_confusion_matrix_csv(confusion_matrix: Mapping[str, Any], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    label_names = [str(label) for label in confusion_matrix["label_names"]]
    matrix = confusion_matrix["matrix"]
    fieldnames = ["actual_label", *[f"predicted_{label}" for label in label_names], "total"]

    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for actual_label, row in zip(label_names, matrix, strict=False):
            writer.writerow(
                {
                    "actual_label": actual_label,
                    **{f"predicted_{label}": int(value) for label, value in zip(label_names, row, strict=False)},
                    "total": int(sum(row)),
                }
            )


def _latex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": "\\textbackslash{}",
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
        "~": "\\textasciitilde{}",
        "^": "\\textasciicircum{}",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def generate_latex_table(
    rows: Any,
    columns: Iterable[str] | None = None,
    caption: str | None = None,
    label: str | None = None,
) -> str:
    if hasattr(rows, "to_dict"):
        records = list(rows.to_dict("records"))
    else:
        records = list(rows)

    if not records:
        raise ValueError("At least one row is required to generate a LaTeX table.")

    selected_columns = list(columns) if columns is not None else list(records[0].keys())
    column_spec = "l" * len(selected_columns)

    def _format_cell(value: object) -> str:
        if isinstance(value, float):
            return f"{value:.4f}"
        return _latex_escape(value)

    lines = ["\\begin{table}[htbp]", "\\centering", f"\\begin{{tabular}}{{{column_spec}}}", "\\hline"]
    lines.append(" & ".join(_latex_escape(column) for column in selected_columns) + r" \\")
    lines.append("\\hline")
    for record in records:
        lines.append(" & ".join(_format_cell(record.get(column, "")) for column in selected_columns) + r" \\")
    lines.append("\\hline")
    lines.append("\\end{tabular}")
    if caption:
        lines.append(f"\\caption{{{_latex_escape(caption)}}}")
    if label:
        lines.append(f"\\label{{{_latex_escape(label)}}}")
    lines.append("\\end{table}")
    return "\n".join(lines) + "\n"


def save_config_copy(config: Config, run_dir: str | Path) -> None:
    config.save(Path(run_dir) / "config.yaml")


def save_environment_info(run_dir: str | Path) -> None:
    packages: dict[str, str] = {}
    for package_name in [
        "datasets",
        "matplotlib",
        "numpy",
        "PyYAML",
        "pytorch-crf",
        "scikit-learn",
        "torch",
        "tqdm",
        "transformers",
    ]:
        try:
            packages[package_name] = metadata.version(package_name)
        except metadata.PackageNotFoundError:
            packages[package_name] = "not-installed"

    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "packages": packages,
    }
    save_metrics(environment, Path(run_dir) / "environment.json")
