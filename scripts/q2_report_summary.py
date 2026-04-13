"""Build report-ready Q2 summary artifacts from existing outputs."""

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
    "crf": "Feature CRF",
    "bilstm_crf": "BiLSTM-CRF",
    "bert": "BERT",
}
ENTITY_ORDER = ["LOC", "MISC", "ORG", "PER"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build report-ready Q2 summary artifacts from completed outputs.")
    parser.add_argument("--crf-run", required=True, help="Path to the completed Q2 CRF run directory.")
    parser.add_argument("--bilstm-run", required=True, help="Path to the completed Q2 BiLSTM-CRF run directory.")
    parser.add_argument("--bert-run", required=True, help="Path to the completed Q2 BERT run directory.")
    parser.add_argument("--output-dir", help="Optional output directory. Defaults to a new outputs/q2/run_* directory.")
    return parser.parse_args()


def _resolve_output_dir(output_dir: str | None) -> Path:
    if output_dir:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        return destination
    return Path(create_run_dir("outputs", "q2"))


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_run(run_dir: Path) -> tuple[str, dict[str, Any], dict[str, Any]]:
    metrics_payload = _load_json(run_dir / "metrics.json")
    error_payload = _load_json(run_dir / "error_analysis.json")
    model_key = next(iter(metrics_payload["models"].keys()))
    return model_key, metrics_payload, error_payload


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
    validation = model_metrics["validation"]["metrics"]
    test = model_metrics["test"]["metrics"]
    return {
        "model": model_key,
        "display_name": DISPLAY_NAMES.get(model_key, model_key),
        "validation_precision": validation["precision"],
        "validation_recall": validation["recall"],
        "validation_f1": validation["f1"],
        "validation_accuracy": validation["accuracy"],
        "test_precision": test["precision"],
        "test_recall": test["recall"],
        "test_f1": test["f1"],
        "test_accuracy": test["accuracy"],
        "source_run": run_dir.name,
    }


def _build_entity_rows(model_key: str, metrics_payload: dict[str, Any]) -> list[dict[str, Any]]:
    classification_report = metrics_payload["models"][model_key]["test"]["classification_report"]
    rows: list[dict[str, Any]] = []
    for entity in ENTITY_ORDER:
        entity_metrics = classification_report[entity]
        rows.append(
            {
                "model": model_key,
                "display_name": DISPLAY_NAMES.get(model_key, model_key),
                "entity": entity,
                "precision": entity_metrics["precision"],
                "recall": entity_metrics["recall"],
                "f1": entity_metrics["f1-score"],
                "support": entity_metrics["support"],
            }
        )
    return rows


def _top_confusion(error_payload: dict[str, Any], model_key: str) -> str:
    confusions = error_payload["models"][model_key]["test"].get("label_confusions", [])
    if not confusions:
        return "No exported token-level confusions were available."
    top = confusions[0]
    return f"{top['true_label']} -> {top['predicted_label']} ({top['count']} tokens)"


def _build_findings(overall_rows: list[dict[str, Any]], entity_rows: list[dict[str, Any]]) -> tuple[list[str], list[str], str]:
    rows_by_model = {row["model"]: row for row in overall_rows}
    ranked_rows = sorted(overall_rows, key=lambda row: row["test_f1"], reverse=True)
    best_model = ranked_rows[0]
    runner_up = ranked_rows[1]

    best_model_entities = [row for row in entity_rows if row["model"] == best_model["model"]]
    weakest_best_entity = min(best_model_entities, key=lambda row: row["f1"])

    crf_row = rows_by_model.get("crf")
    bilstm_row = rows_by_model.get("bilstm_crf")

    findings = [
        (
            f"{best_model['display_name']} is the strongest finished Q2 model with validation F1 "
            f"{best_model['validation_f1']:.3f} and test F1 {best_model['test_f1']:.3f}, beating "
            f"{runner_up['display_name']} by {best_model['test_f1'] - runner_up['test_f1']:.3f} test F1 points."
        ),
        (
            f"Even after a full-data run, BiLSTM-CRF remains behind the feature-based CRF baseline by "
            f"{crf_row['test_f1'] - bilstm_row['test_f1']:.3f} test F1 points and "
            f"{crf_row['validation_f1'] - bilstm_row['validation_f1']:.3f} validation F1 points."
        ),
        (
            f"For the best model, {weakest_best_entity['entity']} is still the hardest entity type, with test F1 "
            f"{weakest_best_entity['f1']:.3f}; LOC and PER are the most stable entity categories."
        ),
    ]

    discussion = [
        "Use the BERT run as the main Q2 result in the report, with CRF as the strongest classical baseline and BiLSTM-CRF as the underperforming hybrid comparator.",
        "The CRF baseline staying ahead of BiLSTM-CRF suggests that Q2 gains are currently driven more by strong inductive bias or pretrained context than by the recurrent architecture alone.",
        "If additional Q2 time remains, focus follow-up effort on BiLSTM-CRF optimization or a targeted MISC-error analysis rather than opening a new baseline implementation path.",
    ]

    recommendation = (
        "Anchor the final Q2 write-up on the BERT run under outputs/q2/run_20260413_144742, include the CRF run as the strongest non-transformer baseline, "
        "and treat BiLSTM-CRF as a weaker neural comparison unless a separate tuning slice materially improves it."
    )
    return findings, discussion, recommendation


def _build_markdown(
    split_sizes: dict[str, Any],
    source_runs: dict[str, Path],
    overall_rows: list[dict[str, Any]],
    entity_rows: list[dict[str, Any]],
    confusion_rows: list[dict[str, str]],
    findings: list[str],
    discussion: list[str],
    recommendation: str,
) -> str:
    overall_table = _markdown_table(
        overall_rows,
        [
            ("display_name", "Model"),
            ("validation_precision", "Val P"),
            ("validation_recall", "Val R"),
            ("validation_f1", "Val F1"),
            ("test_precision", "Test P"),
            ("test_recall", "Test R"),
            ("test_f1", "Test F1"),
            ("test_accuracy", "Test Acc"),
            ("source_run", "Source Run"),
        ],
    )
    entity_table = _markdown_table(
        entity_rows,
        [
            ("display_name", "Model"),
            ("entity", "Entity"),
            ("precision", "Precision"),
            ("recall", "Recall"),
            ("f1", "F1"),
            ("support", "Support"),
        ],
    )

    lines = [
        "# Q2 Report Summary",
        "",
        "## Source Artifacts",
        "",
        f"- CRF run: {source_runs['crf']}",
        f"- BiLSTM-CRF run: {source_runs['bilstm_crf']}",
        f"- BERT run: {source_runs['bert']}",
        "",
        "## Dataset Snapshot",
        "",
        f"- Train sentences: {split_sizes['train']}",
        f"- Validation sentences: {split_sizes['validation']}",
        f"- Test sentences: {split_sizes['test']}",
        "",
        "## Overall Results",
        "",
        overall_table,
        "",
        "## Per-Entity Test Metrics",
        "",
        entity_table,
        "",
        "## Error Analysis Highlights",
        "",
        *[
            f"- {row['display_name']}: top exported test confusion was {row['top_confusion']}."
            for row in confusion_rows
        ],
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
    source_runs = {
        "crf": Path(args.crf_run).resolve(),
        "bilstm_crf": Path(args.bilstm_run).resolve(),
        "bert": Path(args.bert_run).resolve(),
    }
    output_dir = _resolve_output_dir(args.output_dir)

    overall_rows: list[dict[str, Any]] = []
    entity_rows: list[dict[str, Any]] = []
    confusion_rows: list[dict[str, str]] = []
    split_sizes: dict[str, Any] | None = None

    for expected_key, run_dir in source_runs.items():
        model_key, metrics_payload, error_payload = _load_run(run_dir)
        if model_key != expected_key:
            raise ValueError(f"Expected model '{expected_key}' in {run_dir}, found '{model_key}'.")
        if split_sizes is None:
            split_sizes = metrics_payload["split_sizes"]
        overall_rows.append(_build_overall_row(model_key, metrics_payload, run_dir))
        entity_rows.extend(_build_entity_rows(model_key, metrics_payload))
        confusion_rows.append(
            {
                "model": model_key,
                "display_name": DISPLAY_NAMES.get(model_key, model_key),
                "top_confusion": _top_confusion(error_payload, model_key),
            }
        )

    overall_rows.sort(key=lambda row: row["test_f1"], reverse=True)
    entity_rows.sort(key=lambda row: (ENTITY_ORDER.index(row["entity"]), -row["f1"], row["display_name"]))
    confusion_rows.sort(key=lambda row: DISPLAY_NAMES.get(row["model"], row["model"]))

    findings, discussion, recommendation = _build_findings(overall_rows, entity_rows)
    markdown_summary = _build_markdown(
        split_sizes=split_sizes or {},
        source_runs=source_runs,
        overall_rows=overall_rows,
        entity_rows=entity_rows,
        confusion_rows=confusion_rows,
        findings=findings,
        discussion=discussion,
        recommendation=recommendation,
    )

    overall_table_tex = generate_latex_table(
        overall_rows,
        columns=[
            "display_name",
            "validation_precision",
            "validation_recall",
            "validation_f1",
            "test_precision",
            "test_recall",
            "test_f1",
            "test_accuracy",
            "source_run",
        ],
        caption="Q2 full-data model comparison across CRF, BiLSTM-CRF, and BERT.",
        label="tab:q2_model_comparison",
    )
    entity_table_tex = generate_latex_table(
        entity_rows,
        columns=["display_name", "entity", "precision", "recall", "f1", "support"],
        caption="Q2 per-entity test metrics for the finished CRF, BiLSTM-CRF, and BERT runs.",
        label="tab:q2_entity_metrics",
    )
    latex_summary = "\n".join(
        [
            "% Q2 summary tables",
            overall_table_tex,
            entity_table_tex,
            "% Key findings",
            _latex_itemize(findings),
            "% Discussion prompts",
            _latex_itemize(discussion),
        ]
    )

    summary_payload = {
        "question": "q2",
        "summary_type": "report_ready_model_summary",
        "source_runs": {key: str(value) for key, value in source_runs.items()},
        "split_sizes": split_sizes,
        "overall_rows": overall_rows,
        "entity_rows": entity_rows,
        "confusion_rows": confusion_rows,
        "findings": findings,
        "discussion": discussion,
        "recommended_next_step": recommendation,
        "best_model": overall_rows[0]["display_name"],
        "best_test_f1": overall_rows[0]["test_f1"],
    }

    save_environment_info(output_dir)
    save_metrics(summary_payload, output_dir / "q2_report_summary.json")
    (output_dir / "q2_report_summary.md").write_text(markdown_summary, encoding="utf-8")
    (output_dir / "q2_report_summary.tex").write_text(latex_summary, encoding="utf-8")

    print(f"Saved Q2 report summary outputs to {output_dir}")


if __name__ == "__main__":
    main()