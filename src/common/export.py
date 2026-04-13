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


def save_config_copy(config: Config, run_dir: str | Path) -> None:
    config.save(Path(run_dir) / "config.yaml")


def save_environment_info(run_dir: str | Path) -> None:
    packages: dict[str, str] = {}
    for package_name in ["datasets", "numpy", "PyYAML", "scikit-learn", "torch", "tqdm", "transformers"]:
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
