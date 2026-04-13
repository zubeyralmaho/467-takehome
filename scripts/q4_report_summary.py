"""Build report-ready Q4 summary artifacts from existing outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.export import create_run_dir, generate_latex_table, save_environment_info, save_metrics


DISPLAY_NAMES = {
    "seq2seq": "Seq2Seq + Attention",
    "transformer": "Transformer (Opus-MT)",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build report-ready Q4 summary artifacts from completed outputs.")
    parser.add_argument(
        "--run",
        action="append",
        default=[],
        help="Path to a completed Q4 run directory. Repeat to compare multiple models.",
    )
    parser.add_argument("--output-dir", help="Optional output directory. Defaults to a new outputs/q4/run_* directory.")
    return parser.parse_args()


def _resolve_output_dir(output_dir: str | None) -> Path:
    if output_dir:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        return destination
    return Path(create_run_dir("outputs", "q4"))


def _resolve_runs(args: argparse.Namespace) -> list[Path]:
    if not args.run:
        raise ValueError("At least one Q4 run directory must be provided via --run.")
    return [Path(value).resolve() for value in args.run]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


def _load_run(run_dir: Path) -> tuple[str, dict[str, Any], dict[str, Any], dict[str, Any]]:
    metrics_payload = _load_json(run_dir / "metrics.json")
    qualitative_payload = _load_json(run_dir / "qualitative_analysis.json")
    config_payload = _load_yaml(run_dir / "config.yaml")
    model_key = next(iter(metrics_payload["models"].keys()))
    return model_key, metrics_payload, qualitative_payload, config_payload


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


def _build_setup_row(model_key: str, config_payload: dict[str, Any], train_size: int, run_dir: Path) -> dict[str, Any]:
    preprocess = config_payload.get("preprocess", {})
    lowercase_source = bool(preprocess.get("lowercase_source", False))
    lowercase_target = bool(preprocess.get("lowercase_target", False))
    casing = "Lowercased" if lowercase_source or lowercase_target else "Casing preserved"

    if model_key == "transformer":
        transformer_cfg = config_payload.get("models", {}).get("transformer", {})
        detail = (
            f"{transformer_cfg.get('model_name', 'unknown checkpoint')}, "
            f"{transformer_cfg.get('num_beams', '?')}-beam decoding"
        )
        training_regime = "Pretrained inference only"
    elif model_key == "seq2seq":
        seq2seq_cfg = config_payload.get("models", {}).get("seq2seq", {})
        detail = (
            f"GRU encoder-decoder, emb {seq2seq_cfg.get('embedding_dim', '?')}, "
            f"hidden {seq2seq_cfg.get('hidden_dim', '?')}, epochs {seq2seq_cfg.get('max_epochs', '?')}"
        )
        training_regime = "Trained from scratch"
    else:
        detail = "Custom model configuration"
        training_regime = "Unknown"

    return {
        "model": model_key,
        "display_name": DISPLAY_NAMES.get(model_key, model_key),
        "training_regime": training_regime,
        "train_size": train_size,
        "preprocessing": casing,
        "detail": detail,
        "source_run": run_dir.name,
    }


def _build_overall_row(model_key: str, metrics_payload: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    model_metrics = metrics_payload["models"][model_key]
    validation = model_metrics["validation"]["metrics"]
    test = model_metrics["test"]["metrics"]
    return {
        "model": model_key,
        "display_name": DISPLAY_NAMES.get(model_key, model_key),
        "train_size": metrics_payload["split_sizes"]["train"],
        "validation_bleu": validation["bleu"],
        "test_bleu": test["bleu"],
        "validation_chrf": validation["chrf"],
        "test_chrf": test["chrf"],
        "source_run": run_dir.name,
    }


def _build_example_rows(model_key: str, qualitative_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split_name in ("validation", "test"):
        for sample in qualitative_payload["models"][model_key][split_name]["examples"]:
            rows.append(
                {
                    "model": model_key,
                    "display_name": DISPLAY_NAMES.get(model_key, model_key),
                    "split": split_name,
                    "sample_id": sample["id"],
                    "source_text": sample["source_text"],
                    "reference_translation": sample["reference_translation"],
                    "predicted_translation": sample["predicted_translation"],
                    "bleu": sample["bleu"],
                    "chrf": sample["chrf"],
                }
            )
    return rows


def _select_qualitative_highlights(example_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    highlights: list[dict[str, Any]] = []
    for model_key in sorted({row["model"] for row in example_rows}):
        test_rows = [row for row in example_rows if row["model"] == model_key and row["split"] == "test"]
        if not test_rows:
            continue
        best_row = max(test_rows, key=lambda row: row["bleu"])
        weakest_row = min(test_rows, key=lambda row: row["bleu"])
        highlights.append(
            {
                "model": model_key,
                "display_name": DISPLAY_NAMES.get(model_key, model_key),
                "type": "best",
                "sample_id": best_row["sample_id"],
                "source_text": best_row["source_text"],
                "reference_translation": best_row["reference_translation"],
                "predicted_translation": best_row["predicted_translation"],
                "bleu": best_row["bleu"],
                "chrf": best_row["chrf"],
            }
        )
        if weakest_row["sample_id"] != best_row["sample_id"]:
            highlights.append(
                {
                    "model": model_key,
                    "display_name": DISPLAY_NAMES.get(model_key, model_key),
                    "type": "weakest",
                    "sample_id": weakest_row["sample_id"],
                    "source_text": weakest_row["source_text"],
                    "reference_translation": weakest_row["reference_translation"],
                    "predicted_translation": weakest_row["predicted_translation"],
                    "bleu": weakest_row["bleu"],
                    "chrf": weakest_row["chrf"],
                }
            )
    return highlights


def _build_findings(
    dataset_source: str,
    split_sizes_by_model: dict[str, dict[str, int]],
    overall_rows: list[dict[str, Any]],
    setup_rows: list[dict[str, Any]],
    highlight_rows: list[dict[str, Any]],
) -> tuple[list[str], list[str], list[str], str]:
    ranked_rows = sorted(overall_rows, key=lambda row: row["test_bleu"], reverse=True)
    best_row = ranked_rows[0]
    findings = [
        (
            f"{best_row['display_name']} is the strongest finished Q4 model, reaching validation/test BLEU "
            f"{best_row['validation_bleu']:.4f}/{best_row['test_bleu']:.4f} and validation/test ChrF "
            f"{best_row['validation_chrf']:.4f}/{best_row['test_chrf']:.4f} on Multi30k."
        )
    ]

    rows_by_model = {row["model"]: row for row in overall_rows}
    setup_by_model = {row["model"]: row for row in setup_rows}

    if "transformer" in rows_by_model and "seq2seq" in rows_by_model:
        transformer_row = rows_by_model["transformer"]
        seq2seq_row = rows_by_model["seq2seq"]
        findings.append(
            (
                f"On the shared 100-example validation/test evaluation, the pretrained transformer beats the classical seq2seq baseline by "
                f"{transformer_row['validation_bleu'] - seq2seq_row['validation_bleu']:.4f}/{transformer_row['test_bleu'] - seq2seq_row['test_bleu']:.4f} BLEU "
                f"and {transformer_row['validation_chrf'] - seq2seq_row['validation_chrf']:.4f}/{transformer_row['test_chrf'] - seq2seq_row['test_chrf']:.4f} ChrF on validation/test."
            )
        )
        findings.append(
            (
                f"The comparison uses the same dataset source ({dataset_source}) and identical validation/test sizes, but not a matched training budget: "
                f"the transformer run is {setup_by_model['transformer']['training_regime'].lower()} while the seq2seq run trains on "
                f"{split_sizes_by_model['seq2seq']['train']} capped examples."
            )
        )

    transformer_weak = next(
        (
            row
            for row in highlight_rows
            if row["model"] == "transformer" and row["type"] == "weakest"
        ),
        None,
    )
    seq2seq_weak = next(
        (
            row
            for row in highlight_rows
            if row["model"] == "seq2seq" and row["type"] == "weakest"
        ),
        None,
    )
    if transformer_weak is not None and seq2seq_weak is not None:
        findings.append(
            (
                f"Qualitatively, the transformer stays much more fluent, although its weakest exported test example still drifts into a longer, less reference-like paraphrase; "
                f"the seq2seq baseline instead still shows lexical drift and repetition, for example on {seq2seq_weak['sample_id']} where it predicts '{seq2seq_weak['predicted_translation']}'."
            )
        )

    discussion = [
        "Use the Opus-MT transformer as the main Q4 result and the seq2seq model as the classical reference point for the final report.",
        "Because the transformer was evaluated as a pretrained system rather than fine-tuned on Multi30k, the current comparison is best framed as classical baseline versus practical pretrained reference, not a matched-from-scratch study.",
        "If more Q4 time remains, prioritize either seq2seq tuning on a larger capped train split or transformer fine-tuning so the comparison becomes more budget-aligned.",
    ]

    sample_lines = [
        (
            f"{row['display_name']} {row['type']} example {row['sample_id']}: "
            f"'{row['source_text']}' -> '{row['predicted_translation']}' "
            f"(ref: '{row['reference_translation']}', BLEU {row['bleu']:.4f}, ChrF {row['chrf']:.4f})"
        )
        for row in highlight_rows
    ]

    recommendation = (
        "Anchor Q4 reporting on the transformer-versus-seq2seq comparison now exported, and only reopen modeling after deciding whether the next step should be seq2seq tuning or transformer fine-tuning on a matched train budget."
    )
    return findings, discussion, sample_lines, recommendation


def _build_markdown(
    dataset_source: str,
    source_runs: dict[str, Path],
    split_sizes_by_model: dict[str, dict[str, int]],
    setup_rows: list[dict[str, Any]],
    overall_rows: list[dict[str, Any]],
    highlight_rows: list[dict[str, Any]],
    findings: list[str],
    discussion: list[str],
    recommendation: str,
) -> str:
    setup_table = _markdown_table(
        setup_rows,
        [
            ("display_name", "Model"),
            ("training_regime", "Training Regime"),
            ("train_size", "Train Split"),
            ("preprocessing", "Preprocessing"),
            ("detail", "Model Detail"),
            ("source_run", "Source Run"),
        ],
    )
    results_table = _markdown_table(
        overall_rows,
        [
            ("display_name", "Model"),
            ("train_size", "Train Split"),
            ("validation_bleu", "Validation BLEU"),
            ("test_bleu", "Test BLEU"),
            ("validation_chrf", "Validation ChrF"),
            ("test_chrf", "Test ChrF"),
            ("source_run", "Source Run"),
        ],
    )
    highlight_lines = [
        (
            f"- {row['display_name']} {row['type']} example {row['sample_id']}: {row['source_text']} -> {row['predicted_translation']} "
            f"(ref: {row['reference_translation']}, BLEU {row['bleu']:.4f}, ChrF {row['chrf']:.4f})"
        )
        for row in highlight_rows
    ]

    lines = [
        "# Q4 Report Summary",
        "",
        "## Source Artifacts",
        "",
        *[f"- {DISPLAY_NAMES.get(model_key, model_key)} run: {run_dir}" for model_key, run_dir in source_runs.items()],
        "",
        "## Evaluation Snapshot",
        "",
        f"- Dataset source: {dataset_source}",
        f"- Shared validation size: {next(iter(split_sizes_by_model.values()))['validation']}",
        f"- Shared test size: {next(iter(split_sizes_by_model.values()))['test']}",
        f"- Transformer train split retained in artifact contract: {split_sizes_by_model.get('transformer', {}).get('train', 'n/a')}",
        f"- Seq2Seq train split used for training: {split_sizes_by_model.get('seq2seq', {}).get('train', 'n/a')}",
        "",
        "## Model Setup",
        "",
        setup_table,
        "",
        "## Translation Results",
        "",
        results_table,
        "",
        "## Qualitative Highlights",
        "",
        *highlight_lines,
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
    split_sizes_by_model: dict[str, dict[str, int]] = {}
    setup_rows: list[dict[str, Any]] = []
    overall_rows: list[dict[str, Any]] = []
    example_rows: list[dict[str, Any]] = []
    model_configs: dict[str, dict[str, Any]] = {}
    dataset_source: str | None = None
    shared_validation_size: int | None = None
    shared_test_size: int | None = None

    for run_dir in run_dirs:
        model_key, metrics_payload, qualitative_payload, config_payload = _load_run(run_dir)
        current_split_sizes = metrics_payload["split_sizes"]
        if dataset_source is None:
            dataset_source = metrics_payload["dataset_source"]
            shared_validation_size = current_split_sizes["validation"]
            shared_test_size = current_split_sizes["test"]
        else:
            if metrics_payload["dataset_source"] != dataset_source:
                raise ValueError("All Q4 runs used for a direct comparison summary must share the same dataset source.")
            if current_split_sizes["validation"] != shared_validation_size or current_split_sizes["test"] != shared_test_size:
                raise ValueError(
                    "All Q4 runs used for a direct comparison summary must share the same validation and test split sizes."
                )

        source_runs[model_key] = run_dir
        split_sizes_by_model[model_key] = current_split_sizes
        setup_rows.append(_build_setup_row(model_key, config_payload, current_split_sizes["train"], run_dir))
        overall_rows.append(_build_overall_row(model_key, metrics_payload, run_dir))
        example_rows.extend(_build_example_rows(model_key, qualitative_payload))
        model_configs[model_key] = config_payload.get("models", {}).get(model_key, {})

    setup_rows.sort(key=lambda row: row["display_name"])
    overall_rows.sort(key=lambda row: row["test_bleu"], reverse=True)
    example_rows.sort(key=lambda row: (row["display_name"], row["split"], -row["bleu"], row["sample_id"]))
    highlight_rows = _select_qualitative_highlights(example_rows)
    findings, discussion, sample_lines, recommendation = _build_findings(
        dataset_source=dataset_source or "",
        split_sizes_by_model=split_sizes_by_model,
        overall_rows=overall_rows,
        setup_rows=setup_rows,
        highlight_rows=highlight_rows,
    )
    markdown_summary = _build_markdown(
        dataset_source=dataset_source or "",
        source_runs=source_runs,
        split_sizes_by_model=split_sizes_by_model,
        setup_rows=setup_rows,
        overall_rows=overall_rows,
        highlight_rows=highlight_rows,
        findings=findings,
        discussion=discussion,
        recommendation=recommendation,
    )

    latex_rows = [
        {
            "Model": row["display_name"],
            "Train Split": row["train_size"],
            "Val BLEU": row["validation_bleu"],
            "Test BLEU": row["test_bleu"],
            "Val ChrF": row["validation_chrf"],
            "Test ChrF": row["test_chrf"],
            "Source Run": row["source_run"],
        }
        for row in overall_rows
    ]
    latex_table = generate_latex_table(
        latex_rows,
        columns=["Model", "Train Split", "Val BLEU", "Test BLEU", "Val ChrF", "Test ChrF", "Source Run"],
        caption=(
            "Q4 capped Multi30k comparison between the finished pretrained transformer reference and the classical seq2seq baseline."
        ),
        label="tab:q4_model_comparison",
    )
    latex_summary = "\n".join(
        [
            "% Q4 summary table",
            latex_table,
            "% Key findings",
            _latex_itemize(findings),
            "% Discussion prompts",
            _latex_itemize(discussion),
            "% Qualitative highlights",
            _latex_itemize(sample_lines),
        ]
    )

    summary_payload = {
        "question": "q4",
        "summary_type": "report_ready_comparison_summary",
        "source_runs": {model_key: str(run_dir) for model_key, run_dir in source_runs.items()},
        "dataset_source": dataset_source,
        "shared_evaluation_split_sizes": {
            "validation": shared_validation_size,
            "test": shared_test_size,
        },
        "split_sizes_by_model": split_sizes_by_model,
        "train_splits_match": len({sizes["train"] for sizes in split_sizes_by_model.values()}) == 1,
        "model_configs": model_configs,
        "setup_rows": setup_rows,
        "overall_rows": overall_rows,
        "qualitative_highlights": highlight_rows,
        "findings": findings,
        "discussion": discussion,
        "recommended_next_step": recommendation,
        "best_model": overall_rows[0]["display_name"],
        "best_test_bleu": overall_rows[0]["test_bleu"],
    }

    save_environment_info(output_dir)
    save_metrics(summary_payload, output_dir / "q4_report_summary.json")
    (output_dir / "q4_report_summary.md").write_text(markdown_summary, encoding="utf-8")
    (output_dir / "q4_report_summary.tex").write_text(latex_summary, encoding="utf-8")

    print(f"Saved Q4 report summary outputs to {output_dir}")


if __name__ == "__main__":
    main()