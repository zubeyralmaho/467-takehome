"""Build report-ready Q2 comparison artifacts from existing run directories."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.config import Config
from src.common.export import create_run_dir, generate_latex_table, save_environment_info, save_metrics
from src.common.visualization import plot_metric_comparison


DISPLAY_NAMES = {
    "crf": "CRF",
    "bilstm_crf": "BiLSTM-CRF",
    "bert": "BERT",
}

AVERAGE_REPORT_KEYS = {"micro avg", "macro avg", "weighted avg"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Q2 comparison artifacts from existing run outputs.")
    parser.add_argument("--run", dest="run_dirs", action="append", required=True, help="Path to a Q2 run directory.")
    parser.add_argument("--split", default="test", help="Evaluation split to compare. Defaults to 'test'.")
    parser.add_argument("--metric", default="f1", help="Primary metric for the overall comparison plot.")
    parser.add_argument("--output-dir", help="Optional output directory. Defaults to a new outputs/q2/run_* directory.")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _resolve_output_dir(output_dir: str | None) -> Path:
    if output_dir:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        return destination
    return Path(create_run_dir("outputs", "q2"))


def _load_rows(run_dir: Path, split: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    metrics = _load_json(run_dir / "metrics.json")
    config = Config.from_yaml(run_dir / "config.yaml").to_dict()
    dataset_config = config.get("dataset", {})

    overall_rows: list[dict[str, Any]] = []
    per_entity_rows: list[dict[str, Any]] = []
    for model_name, model_splits in metrics["models"].items():
        if split not in model_splits:
            raise ValueError(f"Run {run_dir} does not contain split '{split}' for model '{model_name}'.")

        split_payload = model_splits[split]
        metric_values = split_payload["metrics"]
        overall_rows.append(
            {
                "model": model_name,
                "display_name": DISPLAY_NAMES.get(model_name, model_name),
                "precision": float(metric_values.get("precision", 0.0)),
                "recall": float(metric_values.get("recall", 0.0)),
                "f1": float(metric_values.get("f1", 0.0)),
                "accuracy": float(metric_values.get("accuracy", 0.0)),
                "source_run": run_dir.name,
                "train_limit": dataset_config.get("limit_train_samples"),
                "validation_limit": dataset_config.get("limit_validation_samples"),
                "test_limit": dataset_config.get("limit_test_samples"),
            }
        )

        for entity_type, entity_metrics in split_payload["classification_report"].items():
            if entity_type in AVERAGE_REPORT_KEYS:
                continue
            per_entity_rows.append(
                {
                    "entity_type": entity_type,
                    "model": model_name,
                    "display_name": DISPLAY_NAMES.get(model_name, model_name),
                    "precision": float(entity_metrics.get("precision", 0.0)),
                    "recall": float(entity_metrics.get("recall", 0.0)),
                    "f1": float(entity_metrics.get("f1-score", entity_metrics.get("f1", 0.0))),
                    "support": int(entity_metrics.get("support", 0)),
                    "source_run": run_dir.name,
                }
            )
    return overall_rows, per_entity_rows


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


def _build_per_entity_tables(rows: list[dict[str, Any]]) -> str:
    grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped_rows[str(row["entity_type"])].append(row)

    sections: list[str] = ["% Q2 per-entity comparison tables"]
    for entity_type in sorted(grouped_rows):
        entity_rows = sorted(grouped_rows[entity_type], key=lambda row: row["f1"], reverse=True)
        sections.append(
            generate_latex_table(
                entity_rows,
                columns=["display_name", "precision", "recall", "f1", "support", "source_run"],
                caption=f"Q2 {entity_type} comparison on the test split.",
                label=f"tab:q2_{entity_type.lower()}_comparison",
            )
        )
    return "\n".join(sections)


def _best_per_entity(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped_rows[str(row["entity_type"])].append(row)

    best_rows: list[dict[str, Any]] = []
    for entity_type in sorted(grouped_rows):
        best_row = max(grouped_rows[entity_type], key=lambda row: row["f1"])
        best_rows.append(
            {
                "entity_type": entity_type,
                "best_model": best_row["model"],
                "best_display_name": best_row["display_name"],
                "f1": best_row["f1"],
                "source_run": best_row["source_run"],
            }
        )
    return best_rows


def main() -> None:
    args = parse_args()
    run_dirs = [Path(run_dir).resolve() for run_dir in args.run_dirs]

    overall_rows: list[dict[str, Any]] = []
    per_entity_rows: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        run_overall_rows, run_per_entity_rows = _load_rows(run_dir, args.split)
        overall_rows.extend(run_overall_rows)
        per_entity_rows.extend(run_per_entity_rows)

    _ensure_unique_models(overall_rows)
    overall_rows.sort(key=lambda row: row[args.metric], reverse=True)
    per_entity_rows.sort(key=lambda row: (row["entity_type"], -row["f1"], row["display_name"]))

    output_dir = _resolve_output_dir(args.output_dir)
    save_environment_info(output_dir)

    best_per_entity = _best_per_entity(per_entity_rows)
    summary = {
        "question": "q2",
        "split": args.split,
        "primary_metric": args.metric,
        "source_runs": [str(run_dir) for run_dir in run_dirs],
        "overall_rows": overall_rows,
        "per_entity_rows": per_entity_rows,
        "best_model": overall_rows[0]["model"],
        "best_run": overall_rows[0]["source_run"],
        "best_per_entity": best_per_entity,
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

    _write_csv(overall_rows, output_dir / "overall_model_comparison.csv")
    _write_csv(per_entity_rows, output_dir / "per_entity_model_comparison.csv")

    overall_table = generate_latex_table(
        overall_rows,
        columns=["display_name", "precision", "recall", "f1", "accuracy", "source_run"],
        caption=f"Q2 {args.split} model comparison.",
        label="tab:q2_model_comparison",
    )
    (output_dir / "overall_model_comparison.tex").write_text(overall_table, encoding="utf-8")
    (output_dir / "per_entity_model_comparison.tex").write_text(_build_per_entity_tables(per_entity_rows), encoding="utf-8")

    plot_metric_comparison(
        overall_rows,
        metric=args.metric,
        output_path=output_dir / "figures" / "entity_f1_comparison.png",
        title=f"Q2 {args.split} {args.metric.upper()} comparison",
    )

    print(f"Saved Q2 comparison outputs to {output_dir}")


if __name__ == "__main__":
    main()