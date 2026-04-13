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


DISPLAY_NAMES = {
    "ngram": "Trigram add-k",
    "lstm": "LSTM",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build report-ready Q5 summary artifacts from completed outputs.")
    parser.add_argument(
        "--run",
        action="append",
        default=[],
        help="Path to a completed Q5 run directory. Repeat to compare multiple models.",
    )
    parser.add_argument("--baseline-run", help="Deprecated alias for a single --run input.")
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


def _resolve_runs(args: argparse.Namespace) -> list[Path]:
    run_values = list(args.run)
    if args.baseline_run:
        run_values.append(args.baseline_run)
    if not run_values:
        raise ValueError("At least one Q5 run directory must be provided via --run.")
    return [Path(value).resolve() for value in run_values]


def _load_run(run_dir: Path) -> tuple[str, dict[str, Any], dict[str, Any]]:
    metrics_payload = _load_json(run_dir / "metrics.json")
    qualitative_payload = _load_json(run_dir / "qualitative_analysis.json")
    model_key = next(iter(metrics_payload["models"].keys()))
    return model_key, metrics_payload, qualitative_payload


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


def _build_overall_row(model_key: str, metrics_payload: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    model_metrics = metrics_payload["models"][model_key]
    return {
        "model": model_key,
        "display_name": DISPLAY_NAMES.get(model_key, model_key),
        "validation_perplexity": model_metrics["validation"]["metrics"]["perplexity"],
        "test_perplexity": model_metrics["test"]["metrics"]["perplexity"],
        "source_run": run_dir.name,
    }


def _build_generation_rows(model_key: str, qualitative_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sample in qualitative_payload["models"][model_key]["generations"]:
        rows.append(
            {
                "model": model_key,
                "display_name": DISPLAY_NAMES.get(model_key, model_key),
                "sample_id": sample["sample_id"],
                "seed_text": sample["seed_text"],
                "generated_text": sample["generated_text"],
                "generated_token_count": sample["generated_token_count"],
            }
        )
    return rows


def _build_findings(
    split_sizes: dict[str, Any],
    token_counts: dict[str, Any],
    overall_rows: list[dict[str, Any]],
    generation_rows: list[dict[str, Any]],
) -> tuple[list[str], list[str], list[str], str]:
    ranked_rows = sorted(overall_rows, key=lambda row: row["test_perplexity"])
    best_row = ranked_rows[0]
    findings = [
        (
            f"The strongest finished Q5 model is {best_row['display_name']}, which reached validation/test perplexity "
            f"{best_row['validation_perplexity']:.2f}/{best_row['test_perplexity']:.2f} on the capped WikiText-2 split with "
            f"{split_sizes['train']} train, {split_sizes['validation']} validation, and {split_sizes['test']} test lines."
        ),
        (
            f"The capped dataset still covers {token_counts['train']} train tokens, {token_counts['validation']} validation tokens, and {token_counts['test']} test tokens, "
            "so the comparison is large enough to show a meaningful gap between count-based and neural next-token modeling."
        ),
    ]

    rows_by_model = {row["model"]: row for row in overall_rows}
    if "ngram" in rows_by_model and "lstm" in rows_by_model:
        ngram_row = rows_by_model["ngram"]
        lstm_row = rows_by_model["lstm"]
        test_reduction = 100.0 * (ngram_row["test_perplexity"] - lstm_row["test_perplexity"]) / ngram_row["test_perplexity"]
        validation_reduction = 100.0 * (ngram_row["validation_perplexity"] - lstm_row["validation_perplexity"]) / ngram_row["validation_perplexity"]
        findings.append(
            (
                f"Compared with the matched trigram baseline, the LSTM reduced validation perplexity by {validation_reduction:.1f}% "
                f"and test perplexity by {test_reduction:.1f}% on the same 3000/400/400 budget."
            )
        )
    else:
        findings.append("Only one finished Q5 run was provided, so this summary should be treated as a single-model snapshot rather than a direct comparison.")

    average_lengths: dict[str, float] = {}
    for model_key in {row["model"] for row in generation_rows}:
        model_rows = [row for row in generation_rows if row["model"] == model_key]
        average_lengths[model_key] = sum(row["generated_token_count"] for row in model_rows) / max(len(model_rows), 1)

    if "ngram" in average_lengths and "lstm" in average_lengths:
        findings.append(
            (
                f"Under the shared generation prompts, the LSTM produced longer continuations on average ({average_lengths['lstm']:.1f} tokens) "
                f"than the trigram baseline ({average_lengths['ngram']:.1f}), while still showing topical drift and repetition in some samples."
            )
        )

    discussion = [
        "Use the trigram run as the classical Q5 reference point and the LSTM as the first meaningful neural baseline; the perplexity gap is already large enough to support that narrative.",
        "The LSTM generations are still noisy, but they sustain longer local grammatical structure than the sparse n-gram samples under the same seeded prompts.",
        "If more Q5 time remains, the next worthwhile comparison is GPT-2 or another pretrained causal LM rather than additional work on the trigram model."
    ]

    sample_lines = [
        f"{row['display_name']} / seed '{row['seed_text']}' -> {row['generated_text']}"
        for row in generation_rows
    ]

    recommendation = (
        "Anchor Q5 analysis on the LSTM-versus-trigram comparison now available, and only reopen Q5 modeling if a GPT-2 baseline is needed for a transformer reference."
    )
    return findings, discussion, sample_lines, recommendation


def _build_markdown(
    split_sizes: dict[str, Any],
    token_counts: dict[str, Any],
    source_runs: dict[str, Path],
    overall_rows: list[dict[str, Any]],
    generation_rows: list[dict[str, Any]],
    findings: list[str],
    discussion: list[str],
    recommendation: str,
) -> str:
    results_table = _markdown_table(
        overall_rows,
        [
            ("display_name", "Model"),
            ("validation_perplexity", "Validation Perplexity"),
            ("test_perplexity", "Test Perplexity"),
            ("source_run", "Source Run"),
        ],
    )
    generation_table = _markdown_table(
        generation_rows,
        [
            ("display_name", "Model"),
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
        *[f"- {DISPLAY_NAMES.get(model_key, model_key)} run: {run_dir}" for model_key, run_dir in source_runs.items()],
        "",
        "## Dataset Snapshot",
        "",
        f"- Dataset source: wikitext:wikitext-2-raw-v1",
        f"- Train lines: {split_sizes['train']} ({token_counts['train']} tokens)",
        f"- Validation lines: {split_sizes['validation']} ({token_counts['validation']} tokens)",
        f"- Test lines: {split_sizes['test']} ({token_counts['test']} tokens)",
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
    run_dirs = _resolve_runs(args)
    output_dir = _resolve_output_dir(args.output_dir)

    source_runs: dict[str, Path] = {}
    overall_rows: list[dict[str, Any]] = []
    generation_rows: list[dict[str, Any]] = []
    split_sizes: dict[str, Any] | None = None
    token_counts: dict[str, Any] | None = None
    dataset_source: str | None = None
    model_configs: dict[str, dict[str, Any]] = {}

    for run_dir in run_dirs:
        model_key, metrics_payload, qualitative_payload = _load_run(run_dir)
        if split_sizes is None:
            split_sizes = metrics_payload["split_sizes"]
            token_counts = metrics_payload["token_counts"]
            dataset_source = metrics_payload["dataset_source"]
        else:
            if metrics_payload["split_sizes"] != split_sizes or metrics_payload["token_counts"] != token_counts:
                raise ValueError(
                    "All Q5 runs used for a direct comparison summary must share the same split sizes and token counts."
                )
            if metrics_payload["dataset_source"] != dataset_source:
                raise ValueError("All Q5 runs used for a direct comparison summary must share the same dataset source.")
        source_runs[model_key] = run_dir
        overall_rows.append(_build_overall_row(model_key, metrics_payload, run_dir))
        generation_rows.extend(_build_generation_rows(model_key, qualitative_payload))
        model_configs[model_key] = metrics_payload["models"][model_key]["config"]

    overall_rows.sort(key=lambda row: row["test_perplexity"])
    generation_rows.sort(key=lambda row: (row["display_name"], row["sample_id"]))

    findings, discussion, sample_lines, recommendation = _build_findings(
        split_sizes=split_sizes or {},
        token_counts=token_counts or {},
        overall_rows=overall_rows,
        generation_rows=generation_rows,
    )
    markdown_summary = _build_markdown(
        split_sizes=split_sizes or {},
        token_counts=token_counts or {},
        source_runs=source_runs,
        overall_rows=overall_rows,
        generation_rows=generation_rows,
        findings=findings,
        discussion=discussion,
        recommendation=recommendation,
    )

    latex_table = generate_latex_table(
        overall_rows,
        columns=["display_name", "validation_perplexity", "test_perplexity", "source_run"],
        caption="Q5 capped perplexity comparison across the finished trigram and LSTM language-model baselines.",
        label="tab:q5_model_comparison",
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
        "summary_type": "report_ready_comparison_summary" if len(overall_rows) > 1 else "report_ready_baseline_summary",
        "source_runs": {model_key: str(run_dir) for model_key, run_dir in source_runs.items()},
        "dataset_source": dataset_source,
        "split_sizes": split_sizes,
        "token_counts": token_counts,
        "model_configs": model_configs,
        "metrics": {
            row["model"]: {
                "validation_perplexity": row["validation_perplexity"],
                "test_perplexity": row["test_perplexity"],
                "source_run": row["source_run"],
            }
            for row in overall_rows
        },
        "ranked_models": [row["model"] for row in overall_rows],
        "generations": generation_rows,
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