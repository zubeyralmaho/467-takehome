"""Build report-ready Q1 summary artifacts from existing outputs."""

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

from src.common.export import create_run_dir, generate_latex_table, save_environment_info, save_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build report-ready Q1 summary artifacts from completed outputs.")
    parser.add_argument("--comparison-run", required=True, help="Path to a Q1 model comparison run directory.")
    parser.add_argument("--preprocessing-run", required=True, help="Path to a Q1 preprocessing comparison run directory.")
    parser.add_argument("--output-dir", help="Optional output directory. Defaults to a new outputs/q1/run_* directory.")
    return parser.parse_args()


def _resolve_output_dir(output_dir: str | None) -> Path:
    if output_dir:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        return destination
    return Path(create_run_dir("outputs", "q1"))


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_model_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "model": row["model"],
                    "display_name": row["display_name"],
                    "accuracy": float(row["accuracy"]),
                    "macro_f1": float(row["macro_f1"]),
                    "source_run": row["source_run"],
                    "train_limit": int(row["train_limit"]) if row.get("train_limit") else None,
                    "test_limit": int(row["test_limit"]) if row.get("test_limit") else None,
                }
            )
    return rows


def _markdown_table(rows: list[dict[str, Any]], columns: list[tuple[str, str]]) -> str:
    headers = [header for _, header in columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        values = []
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


def _build_findings(model_rows: list[dict[str, Any]], preprocessing_summary: dict[str, Any]) -> tuple[list[str], list[str]]:
    best_model = model_rows[0]
    runner_up = model_rows[1] if len(model_rows) > 1 else best_model
    best_preprocessing = preprocessing_summary["best_experiment"]

    findings = [
        (
            f"On the matched smoke-test runs, {best_model['display_name']} achieved the best test macro-F1 "
            f"({best_model['macro_f1']:.3f}) and accuracy ({best_model['accuracy']:.3f})."
        ),
        (
            f"The documented preprocessing sweep favored experiment {best_preprocessing['experiment']} "
            f"({best_preprocessing['description']}) with validation macro-F1 {best_preprocessing['macro_f1']:.3f}."
        ),
    ]

    neural_rows = [row for row in model_rows if row["model"] in {"bilstm", "distilbert"}]
    if neural_rows:
        weakest_neural = max(neural_rows, key=lambda row: best_model["macro_f1"] - row["macro_f1"])
        findings.append(
            (
                f"The neural smoke-test runs remain behind the sparse baselines; for example, "
                f"{weakest_neural['display_name']} trails the best model by "
                f"{best_model['macro_f1'] - weakest_neural['macro_f1']:.3f} macro-F1 points."
            )
        )

    discussion = [
        (
            f"Sparse representations are currently strongest under the capped 200/100 smoke-test budget, with "
            f"{best_model['display_name']} outperforming {runner_up['display_name']} by "
            f"{best_model['macro_f1'] - runner_up['macro_f1']:.3f} macro-F1 points."
        ),
        "The current lowercase + keep-stopwords preprocessing default is already a best validation setting, so further Q1 gains should come from model budget rather than immediate text-normalization changes.",
        "These artifacts are report-ready for a smoke-test subsection, but the final Q1 narrative should be refreshed after larger-budget BiLSTM and DistilBERT runs complete.",
    ]
    return findings, discussion


def _build_markdown(
    comparison_run: Path,
    preprocessing_run: Path,
    model_rows: list[dict[str, Any]],
    preprocessing_summary: dict[str, Any],
    findings: list[str],
    discussion: list[str],
) -> str:
    best_model = model_rows[0]
    best_model_figure = comparison_run.parent / best_model["source_run"] / "figures" / f"confusion_matrix_{best_model['model']}_test.png"

    model_table = _markdown_table(
        model_rows,
        [
            ("display_name", "Model"),
            ("accuracy", "Accuracy"),
            ("macro_f1", "Macro-F1"),
            ("source_run", "Source Run"),
        ],
    )
    preprocessing_table = _markdown_table(
        preprocessing_summary["rows"],
        [
            ("experiment", "Experiment"),
            ("description", "Setting"),
            ("accuracy", "Accuracy"),
            ("macro_f1", "Macro-F1"),
        ],
    )

    lines = [
        "# Q1 Smoke-Test Report Summary",
        "",
        "## Source Artifacts",
        "",
        f"- Model comparison run: {comparison_run}",
        f"- Preprocessing comparison run: {preprocessing_run}",
        f"- Comparison figure: {comparison_run / 'figures' / 'model_comparison.png'}",
        f"- Best-model confusion matrix reference: {best_model_figure}",
        "",
        "## Results Table",
        "",
        model_table,
        "",
        "## Preprocessing Sweep",
        "",
        preprocessing_table,
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
        "- Keep the current Q1 preprocessing default and spend the next budget on larger matched BiLSTM and DistilBERT runs before rewriting the representation comparison claims.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    comparison_run = Path(args.comparison_run).resolve()
    preprocessing_run = Path(args.preprocessing_run).resolve()
    output_dir = _resolve_output_dir(args.output_dir)

    model_rows = _load_model_rows(comparison_run / "model_comparison.csv")
    preprocessing_summary = _load_json(preprocessing_run / "preprocessing_comparison.json")
    findings, discussion = _build_findings(model_rows, preprocessing_summary)

    markdown_summary = _build_markdown(
        comparison_run=comparison_run,
        preprocessing_run=preprocessing_run,
        model_rows=model_rows,
        preprocessing_summary=preprocessing_summary,
        findings=findings,
        discussion=discussion,
    )

    model_table_tex = generate_latex_table(
        model_rows,
        columns=["display_name", "accuracy", "macro_f1", "source_run"],
        caption="Q1 matched smoke-test model comparison on the test split.",
        label="tab:q1_smoke_results",
    )
    preprocessing_table_tex = generate_latex_table(
        preprocessing_summary["rows"],
        columns=["experiment", "description", "accuracy", "macro_f1"],
        caption="Q1 preprocessing sweep on the validation split.",
        label="tab:q1_preprocessing_sweep",
    )
    latex_summary = "\n".join(
        [
            "% Q1 smoke-test summary tables",
            model_table_tex,
            preprocessing_table_tex,
            "% Key findings",
            _latex_itemize(findings),
            "% Discussion prompts",
            _latex_itemize(discussion),
        ]
    )

    summary_payload = {
        "question": "q1",
        "summary_type": "report_ready_smoke_summary",
        "comparison_run": str(comparison_run),
        "preprocessing_run": str(preprocessing_run),
        "model_rows": model_rows,
        "best_preprocessing": preprocessing_summary["best_experiment"],
        "findings": findings,
        "discussion": discussion,
        "recommended_next_step": "Run larger-budget matched BiLSTM and DistilBERT experiments, then rebuild the comparison artifacts.",
    }

    save_environment_info(output_dir)
    save_metrics(summary_payload, output_dir / "q1_report_summary.json")
    (output_dir / "q1_report_summary.md").write_text(markdown_summary, encoding="utf-8")
    (output_dir / "q1_report_summary.tex").write_text(latex_summary, encoding="utf-8")

    print(f"Saved Q1 report summary outputs to {output_dir}")


if __name__ == "__main__":
    main()