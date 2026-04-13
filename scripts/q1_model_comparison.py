"""Build report-ready Q1 comparison artifacts from existing run directories."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.config import Config
from src.common.export import create_run_dir, generate_latex_table, save_environment_info, save_metrics
from src.common.visualization import plot_metric_comparison


DISPLAY_NAMES = {
    "tfidf_lr": "TF-IDF + LR",
    "tfidf_svm": "TF-IDF + SVM",
    "bilstm": "BiLSTM",
    "distilbert": "DistilBERT",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Q1 comparison artifacts from existing run outputs.")
    parser.add_argument("--run", dest="run_dirs", action="append", required=True, help="Path to a Q1 run directory.")
    parser.add_argument("--split", default="test", help="Evaluation split to compare. Defaults to 'test'.")
    parser.add_argument("--metric", default="macro_f1", help="Primary metric for the comparison plot.")
    parser.add_argument("--output-dir", help="Optional output directory. Defaults to a new outputs/q1/run_* directory.")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _resolve_output_dir(output_dir: str | None) -> Path:
    if output_dir:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        return destination
    return Path(create_run_dir("outputs", "q1"))


def _load_rows(run_dir: Path, split: str) -> list[dict[str, Any]]:
    metrics = _load_json(run_dir / "metrics.json")
    config = Config.from_yaml(run_dir / "config.yaml").to_dict()
    dataset_config = config.get("dataset", {})

    rows: list[dict[str, Any]] = []
    for model_name, model_splits in metrics.items():
        if split not in model_splits:
            raise ValueError(f"Run {run_dir} does not contain split '{split}' for model '{model_name}'.")

        metric_values = model_splits[split]["metrics"]
        rows.append(
            {
                "model": model_name,
                "display_name": DISPLAY_NAMES.get(model_name, model_name),
                "accuracy": float(metric_values.get("accuracy", 0.0)),
                "macro_f1": float(metric_values.get("macro_f1", 0.0)),
                "source_run": run_dir.name,
                "train_limit": dataset_config.get("limit_train_samples"),
                "test_limit": dataset_config.get("limit_test_samples"),
            }
        )
    return rows


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _ensure_unique_models(rows: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        model_name = str(row["model"])
        if model_name in seen:
            duplicates.add(model_name)
        seen.add(model_name)
    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        raise ValueError(f"Comparison rows must have unique models. Duplicates found: {duplicate_list}")


def main() -> None:
    args = parse_args()
    run_dirs = [Path(run_dir).resolve() for run_dir in args.run_dirs]

    comparison_rows: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        comparison_rows.extend(_load_rows(run_dir, args.split))

    _ensure_unique_models(comparison_rows)
    comparison_rows.sort(key=lambda row: row[args.metric], reverse=True)

    output_dir = _resolve_output_dir(args.output_dir)
    save_environment_info(output_dir)

    summary = {
        "question": "q1",
        "split": args.split,
        "primary_metric": args.metric,
        "source_runs": [str(run_dir) for run_dir in run_dirs],
        "rows": comparison_rows,
        "best_model": comparison_rows[0]["model"],
        "best_run": comparison_rows[0]["source_run"],
    }
    save_metrics(summary, output_dir / "metrics.json")
    save_metrics(
        {
            "source_runs": [str(run_dir) for run_dir in run_dirs],
            "split": args.split,
            "primary_metric": args.metric,
        },
        output_dir / "comparison_manifest.json",
    )

    _write_csv(comparison_rows, output_dir / "model_comparison.csv")
    latex_table = generate_latex_table(
        comparison_rows,
        columns=["display_name", "accuracy", "macro_f1", "source_run"],
        caption=f"Q1 {args.split} smoke-test model comparison.",
        label="tab:q1_smoke_comparison",
    )
    (output_dir / "model_comparison.tex").write_text(latex_table, encoding="utf-8")
    plot_metric_comparison(
        comparison_rows,
        metric=args.metric,
        output_path=output_dir / "figures" / "model_comparison.png",
        title=f"Q1 {args.split} {args.metric.replace('_', ' ')} comparison",
    )

    print(f"Saved comparison outputs to {output_dir}")


if __name__ == "__main__":
    main()