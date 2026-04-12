"""Helpers for saving experiment outputs."""

from __future__ import annotations

import csv
import json
import platform
import sys
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import Iterable, Mapping

from src.common.config import Config


def create_run_dir(base_dir: str, question: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(base_dir) / question / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return str(run_dir)


def save_metrics(metrics: Mapping, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, ensure_ascii=False, indent=2)


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


def save_config_copy(config: Config, run_dir: str | Path) -> None:
    config.save(Path(run_dir) / "config.yaml")


def save_environment_info(run_dir: str | Path) -> None:
    packages: dict[str, str] = {}
    for package_name in ["datasets", "numpy", "PyYAML", "scikit-learn", "tqdm"]:
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
