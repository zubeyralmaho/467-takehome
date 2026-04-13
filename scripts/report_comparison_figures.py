"""Generate report-local comparison figures for the drafted Q3-Q5 sections."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.common.visualization import plot_grouped_metric_comparison


def _default_repo_root() -> Path:
    return REPO_ROOT


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _build_q3_rows(metrics: dict[str, Any]) -> list[dict[str, float | str]]:
    return [
        {
            "display_name": "TextRank",
            "rouge1": float(metrics["models"]["textrank"]["test"]["metrics"]["rouge1"]),
            "rouge2": float(metrics["models"]["textrank"]["test"]["metrics"]["rouge2"]),
            "rougeL": float(metrics["models"]["textrank"]["test"]["metrics"]["rougeL"]),
            "bleu": float(metrics["models"]["textrank"]["test"]["metrics"]["bleu"]),
            "meteor": float(metrics["models"]["textrank"]["test"]["metrics"]["meteor"]),
        },
        {
            "display_name": "DistilBART",
            "rouge1": float(metrics["models"]["bart"]["test"]["metrics"]["rouge1"]),
            "rouge2": float(metrics["models"]["bart"]["test"]["metrics"]["rouge2"]),
            "rougeL": float(metrics["models"]["bart"]["test"]["metrics"]["rougeL"]),
            "bleu": float(metrics["models"]["bart"]["test"]["metrics"]["bleu"]),
            "meteor": float(metrics["models"]["bart"]["test"]["metrics"]["meteor"]),
        },
    ]


def _build_q4_rows(summary: dict[str, Any]) -> list[dict[str, float | str]]:
    rows_by_model = {row["model"]: row for row in summary["overall_rows"]}
    return [
        {
            "display_name": "Seq2Seq + Attention",
            "test_bleu": float(rows_by_model["seq2seq"]["test_bleu"]),
            "test_chrf": float(rows_by_model["seq2seq"]["test_chrf"]),
        },
        {
            "display_name": "Transformer (Opus-MT)",
            "test_bleu": float(rows_by_model["transformer"]["test_bleu"]),
            "test_chrf": float(rows_by_model["transformer"]["test_chrf"]),
        },
    ]


def _build_q5_rows(summary: dict[str, Any]) -> list[dict[str, float | str]]:
    metrics = summary["metrics"]
    return [
        {
            "display_name": "Trigram add-k",
            "validation_perplexity": float(metrics["ngram"]["validation_perplexity"]),
            "test_perplexity": float(metrics["ngram"]["test_perplexity"]),
        },
        {
            "display_name": "LSTM",
            "validation_perplexity": float(metrics["lstm"]["validation_perplexity"]),
            "test_perplexity": float(metrics["lstm"]["test_perplexity"]),
        },
        {
            "display_name": "distilGPT-2",
            "validation_perplexity": float(metrics["gpt2"]["validation_perplexity"]),
            "test_perplexity": float(metrics["gpt2"]["test_perplexity"]),
        },
    ]


def parse_args() -> argparse.Namespace:
    repo_root = _default_repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--q3-metrics",
        type=Path,
        default=repo_root / "outputs" / "q3" / "run_20260413_192426" / "metrics.json",
        help="Path to the Q3 metrics.json file.",
    )
    parser.add_argument(
        "--q4-summary",
        type=Path,
        default=repo_root / "outputs" / "q4" / "run_20260413_231508" / "q4_report_summary.json",
        help="Path to the Q4 report summary JSON.",
    )
    parser.add_argument(
        "--q5-summary",
        type=Path,
        default=repo_root / "outputs" / "q5" / "run_20260413_214837" / "q5_report_summary.json",
        help="Path to the Q5 report summary JSON.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=repo_root / "report" / "figures",
        help="Directory under which report-local figure folders will be created.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    q3_rows = _build_q3_rows(_load_json(args.q3_metrics))
    q4_rows = _build_q4_rows(_load_json(args.q4_summary))
    q5_rows = _build_q5_rows(_load_json(args.q5_summary))

    plot_grouped_metric_comparison(
        q3_rows,
        metrics=["rouge1", "rouge2", "rougeL", "bleu", "meteor"],
        output_path=args.output_root / "q3" / "test_metric_comparison.png",
        title="Q3 test-set metric comparison",
        y_label="Score",
        metric_labels={
            "rouge1": "ROUGE-1",
            "rouge2": "ROUGE-2",
            "rougeL": "ROUGE-L",
            "bleu": "BLEU",
            "meteor": "METEOR",
        },
    )

    plot_grouped_metric_comparison(
        q4_rows,
        metrics=["test_bleu", "test_chrf"],
        output_path=args.output_root / "q4" / "test_metric_comparison.png",
        title="Q4 test-set translation metric comparison",
        y_label="Score",
        metric_labels={
            "test_bleu": "Test BLEU",
            "test_chrf": "Test ChrF",
        },
    )

    plot_grouped_metric_comparison(
        q5_rows,
        metrics=["validation_perplexity", "test_perplexity"],
        output_path=args.output_root / "q5" / "perplexity_comparison.png",
        title="Q5 validation/test perplexity comparison",
        y_label="Perplexity (log scale)",
        metric_labels={
            "validation_perplexity": "Validation",
            "test_perplexity": "Test",
        },
        label_formats={
            "validation_perplexity": "{:.1f}",
            "test_perplexity": "{:.1f}",
        },
        log_scale=True,
    )

    manifest = {
        "sources": {
            "q3": str(args.q3_metrics),
            "q4": str(args.q4_summary),
            "q5": str(args.q5_summary),
        },
        "outputs": {
            "q3": str(args.output_root / "q3" / "test_metric_comparison.png"),
            "q4": str(args.output_root / "q4" / "test_metric_comparison.png"),
            "q5": str(args.output_root / "q5" / "perplexity_comparison.png"),
        },
    }
    manifest_path = args.output_root / "report_comparison_figures_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Saved report comparison figures under {args.output_root}")


if __name__ == "__main__":
    main()