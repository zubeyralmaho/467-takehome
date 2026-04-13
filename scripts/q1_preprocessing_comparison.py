"""Run the documented Q1 preprocessing sweep for TF-IDF + Logistic Regression."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.config import load_config
from src.common.evaluation import evaluate_predictions
from src.common.export import create_run_dir, save_config_copy, save_environment_info, save_metrics
from src.q1_classification.dataset import load_q1_splits, materialize_split
from src.q1_classification.models import TFIDFClassifier
from src.q1_classification.preprocess import TextPreprocessor


EXPERIMENTS = [
    {
        "experiment": "A",
        "description": "Remove stopwords, lowercase, 50k max features",
        "remove_stopwords": True,
        "lowercase": True,
        "max_features": 50000,
    },
    {
        "experiment": "B",
        "description": "Keep stopwords, lowercase, 50k max features",
        "remove_stopwords": False,
        "lowercase": True,
        "max_features": 50000,
    },
    {
        "experiment": "C",
        "description": "Remove stopwords, lowercase, 100k max features",
        "remove_stopwords": True,
        "lowercase": True,
        "max_features": 100000,
    },
    {
        "experiment": "D",
        "description": "Keep stopwords, preserve case, 50k max features",
        "remove_stopwords": False,
        "lowercase": False,
        "max_features": 50000,
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Q1 preprocessing comparison sweep.")
    parser.add_argument("--config", required=True, help="Path to configs/q1.yaml.")
    parser.add_argument("--train-limit", type=int, default=1000, help="Optional cap applied before the train/validation split.")
    parser.add_argument("--output-dir", help="Optional output directory. Defaults to a new outputs/q1/run_* directory.")
    return parser.parse_args()


def _resolve_output_dir(base_config, output_dir: str | None) -> Path:
    if output_dir:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        return destination
    return Path(create_run_dir(base_config.output_dir, base_config.question))


def _variant_config(base_config, experiment: dict[str, Any]):
    return base_config.merge(
        {
            "preprocess": {
                "remove_stopwords": experiment["remove_stopwords"],
                "lowercase": experiment["lowercase"],
            },
            "models": {
                "tfidf_lr": {
                    "enabled": True,
                    "classifier": "lr",
                    "max_features": experiment["max_features"],
                },
                "tfidf_svm": {"enabled": False},
                "bilstm": {"enabled": False},
                "distilbert": {"enabled": False},
            },
        }
    )


def _materialize_with_preprocessor(base_config, raw_splits, experiment: dict[str, Any]) -> dict[str, dict[str, list]]:
    variant_config = _variant_config(base_config, experiment)
    preprocessor = TextPreprocessor(variant_config, max_length=None)

    return {
        split_name: materialize_split(
            raw_splits[split_name],
            text_column=variant_config.dataset.text_column,
            label_column=variant_config.dataset.label_column,
            preprocessor=preprocessor,
        )
        for split_name in ["train", "validation"]
    }


def _build_model(base_config, experiment: dict[str, Any]) -> TFIDFClassifier:
    variant_config = _variant_config(base_config, experiment)
    model_config = variant_config.models.tfidf_lr
    return TFIDFClassifier(
        classifier_type=model_config.classifier,
        max_features=model_config.max_features,
        ngram_range=tuple(model_config.ngram_range),
        C=model_config.C,
    )


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    base_config = load_config(args.config)
    if args.train_limit is not None:
        base_config = base_config.merge({"dataset": {"limit_train_samples": args.train_limit}})

    output_dir = _resolve_output_dir(base_config, args.output_dir)
    save_config_copy(base_config, output_dir)
    save_environment_info(output_dir)

    raw_splits = load_q1_splits(base_config)
    rows: list[dict[str, Any]] = []

    for experiment in EXPERIMENTS:
        datasets = _materialize_with_preprocessor(base_config, raw_splits, experiment)
        model = _build_model(base_config, experiment)
        model.fit(datasets["train"]["texts"], datasets["train"]["labels"])

        predictions = model.predict(datasets["validation"]["texts"])
        evaluation = evaluate_predictions(
            base_config.task,
            predictions=predictions,
            references=datasets["validation"]["labels"],
            metrics=base_config.evaluation.metrics,
        )

        rows.append(
            {
                "experiment": experiment["experiment"],
                "description": experiment["description"],
                "remove_stopwords": experiment["remove_stopwords"],
                "lowercase": experiment["lowercase"],
                "max_features": experiment["max_features"],
                "accuracy": float(evaluation["metrics"].get("accuracy", 0.0)),
                "macro_f1": float(evaluation["metrics"].get("macro_f1", 0.0)),
                "train_examples": len(datasets["train"]["texts"]),
                "validation_examples": len(datasets["validation"]["texts"]),
            }
        )

    rows.sort(key=lambda row: row["macro_f1"], reverse=True)
    best_experiment = rows[0]

    _write_csv(rows, output_dir / "preprocessing_comparison.csv")
    save_metrics(
        {
            "question": "q1",
            "comparison_type": "preprocessing",
            "evaluation_split": "validation",
            "train_limit": args.train_limit,
            "rows": rows,
            "best_experiment": best_experiment,
        },
        output_dir / "preprocessing_comparison.json",
    )

    print(f"Saved preprocessing comparison outputs to {output_dir}")


if __name__ == "__main__":
    main()