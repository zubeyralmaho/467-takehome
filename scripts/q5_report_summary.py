"""Build report-ready Q5 summary artifacts from existing outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.export import create_run_dir, generate_latex_table, save_environment_info, save_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build report-ready Q5 summary artifacts from completed outputs.")
    parser.add_argument("--baseline-run", required=True, help="Path to the completed Q5 baseline run directory.")
    parser.add_argument("--output-dir", help="Optional output directory. Defaults to a new outputs/q5/run_* directory.")
    return parser.parse_args()


def _resolve_output_dir(output_dir: str | None) -> Path:
    if output_dir:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        return destination
    return Path(create_run_dir("outputs", "q5"))


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _markdown_table(rows: list[dict[str, Any]], columns: list[tuple[str, str]]) -> str:
    headers = [header for _, header in columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        values: list[str] = []
        for key, _ in columns:
            value = row.get(key, "")
            if isinstance(value, float):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _latex_itemize(items: list[str]) -> str:
    lines = ["\\begin{itemize}"]
    for item in items:
        lines.append(f"  \\item {item}")
    lines.append("\\end{itemize}")
    return "\n".join(lines) + "\n"


def _build_findings(metrics_payload: dict[str, Any], generations: list[dict[str, Any]]) -> tuple[list[str], list[str], list[str], str]:
    ngram = metrics_payload["models"]["ngram"]
    config = ngram["config"]
    split_sizes = metrics_payload["split_sizes"]
    token_counts = metrics_payload["token_counts"]
    validation_perplexity = ngram["validation"]["metrics"]["perplexity"]
    test_perplexity = ngram["test"]["metrics"]["perplexity"]

    findings = [
        (
            f"The trigram add-k baseline reached validation perplexity {validation_perplexity:.2f} and test perplexity {test_perplexity:.2f} "
            f"on a capped WikiText-2 split with {split_sizes['train']} train, {split_sizes['validation']} validation, and {split_sizes['test']} test lines."
        ),
        (
            f"The baseline used a fixed lowercase vocabulary with minimum token frequency {config['min_token_frequency']}, "
            f"resulting in {token_counts['train']} train tokens and consistent <unk>-aware evaluation across validation and test."
        ),
        "Generated samples preserve short-range lexical continuity for simple prompts, but longer continuations still drift semantically and syntactically, which is typical of sparse n-gram models on limited context.",
    ]

    discussion = [
        "This trigram model is a useful classical reference point for Q5 because it exposes the gap between count-based next-token prediction and neural sequence modeling.",
        "The very high perplexity indicates that the capped dataset and short context window are not enough for fluent long-range continuation, so an LSTM or GPT-style model remains the natural next comparison.",
        "Because the baseline already exports seeded generations, later Q5 work can compare not only perplexity but also local fluency and coherence under matched prompts.",
    ]

    sample_lines = [
        f"Seed '{sample['seed_text']}' -> {sample['generated_text']}"
        for sample in generations
    ]

    recommendation = (
        "Keep the trigram baseline as the classical Q5 reference and add an LSTM language-model slice next if Q5 modeling continues; otherwise, use this artifact to draft the baseline-only Q5 report section."
    )
    return findings, discussion, sample_lines, recommendation


def _build_markdown(
    baseline_run: Path,
    metrics_payload: dict[str, Any],
    generations: list[dict[str, Any]],
    findings: list[str],
    discussion: list[str],
    recommendation: str,
) -> str:
    ngram = metrics_payload["models"]["ngram"]
    config = ngram["config"]
    split_sizes = metrics_payload["split_sizes"]
    token_counts = metrics_payload["token_counts"]
    results_rows = [
        {
            "model": "Trigram add-k",
            "validation_perplexity": ngram["validation"]["metrics"]["perplexity"],
            "test_perplexity": ngram["test"]["metrics"]["perplexity"],
            "source_run": baseline_run.name,
        }
    ]
    results_table = _markdown_table(
        results_rows,
        [
            ("model", "Model"),
            ("validation_perplexity", "Validation Perplexity"),
            ("test_perplexity", "Test Perplexity"),
            ("source_run", "Source Run"),
        ],
    )
    generation_table = _markdown_table(
        [
            {
                "sample_id": sample["sample_id"],
                "seed_text": sample["seed_text"],
                "generated_text": sample["generated_text"],
            }
            for sample in generations
        ],
        [
            ("sample_id", "Sample"),
            ("seed_text", "Seed"),
            ("generated_text", "Generated Text"),
        ],
    )

    lines = [
        "# Q5 Report Summary",
        "",
        "## Source Artifact",
        "",
        f"- Baseline run: {baseline_run}",
        "",
        "## Dataset Snapshot",
        "",
        f"- Dataset source: {metrics_payload['dataset_source']}",
        f"- Train lines: {split_sizes['train']} ({token_counts['train']} tokens)",
        f"- Validation lines: {split_sizes['validation']} ({token_counts['validation']} tokens)",
        f"- Test lines: {split_sizes['test']} ({token_counts['test']} tokens)",
        "",
        "## Baseline Configuration",
        "",
        f"- Model: trigram n-gram",
        f"- Smoothing: {config['smoothing']}",
        f"- Alpha: {config['alpha']}",
        f"- Minimum token frequency: {config['min_token_frequency']}",
        "",
        "## Perplexity Results",
        "",
        results_table,
        "",
        "## Generated Text Samples",
        "",
        generation_table,
        "",
        "## Key Findings",
        "",
        *[f"- {item}" for item in findings],
        "",
        "## Discussion Prompts",
        "",
        *[f"- {item}" for item in discussion],
        "",
        "## Recommendation",
        "",
        f"- {recommendation}",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    baseline_run = Path(args.baseline_run).resolve()
    output_dir = _resolve_output_dir(args.output_dir)

    metrics_payload = _load_json(baseline_run / "metrics.json")
    qualitative_payload = _load_json(baseline_run / "qualitative_analysis.json")
    generations = qualitative_payload["models"]["ngram"]["generations"]

    findings, discussion, sample_lines, recommendation = _build_findings(metrics_payload, generations)
    markdown_summary = _build_markdown(
        baseline_run=baseline_run,
        metrics_payload=metrics_payload,
        generations=generations,
        findings=findings,
        discussion=discussion,
        recommendation=recommendation,
    )

    latex_table = generate_latex_table(
        [
            {
                "model": "Trigram add-k",
                "validation_perplexity": metrics_payload["models"]["ngram"]["validation"]["metrics"]["perplexity"],
                "test_perplexity": metrics_payload["models"]["ngram"]["test"]["metrics"]["perplexity"],
                "source_run": baseline_run.name,
            }
        ],
        columns=["model", "validation_perplexity", "test_perplexity", "source_run"],
        caption="Q5 trigram baseline perplexity on the capped WikiText-2 split.",
        label="tab:q5_ngram_results",
    )
    latex_summary = "\n".join(
        [
            "% Q5 summary table",
            latex_table,
            "% Key findings",
            _latex_itemize(findings),
            "% Discussion prompts",
            _latex_itemize(discussion),
            "% Generation samples",
            _latex_itemize(sample_lines),
        ]
    )

    summary_payload = {
        "question": "q5",
        "summary_type": "report_ready_baseline_summary",
        "baseline_run": str(baseline_run),
        "dataset_source": metrics_payload["dataset_source"],
        "split_sizes": metrics_payload["split_sizes"],
        "token_counts": metrics_payload["token_counts"],
        "model_config": metrics_payload["models"]["ngram"]["config"],
        "metrics": {
            "validation_perplexity": metrics_payload["models"]["ngram"]["validation"]["metrics"]["perplexity"],
            "test_perplexity": metrics_payload["models"]["ngram"]["test"]["metrics"]["perplexity"],
        },
        "generations": generations,
        "findings": findings,
        "discussion": discussion,
        "recommended_next_step": recommendation,
    }

    save_environment_info(output_dir)
    save_metrics(summary_payload, output_dir / "q5_report_summary.json")
    (output_dir / "q5_report_summary.md").write_text(markdown_summary, encoding="utf-8")
    (output_dir / "q5_report_summary.tex").write_text(latex_summary, encoding="utf-8")

    print(f"Saved Q5 report summary outputs to {output_dir}")


if __name__ == "__main__":
    main()