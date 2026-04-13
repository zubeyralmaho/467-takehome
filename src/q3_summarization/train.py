"""Training orchestration for Q3 summarization."""

from __future__ import annotations

from pathlib import Path

from src.common.export import save_metrics, save_predictions
from src.q3_summarization.analysis import qualitative_comparison
from src.q3_summarization.dataset import prepare_datasets
from src.q3_summarization.evaluation import evaluate_predictions
from src.q3_summarization.models import TextRankSummarizer


def _build_models(config) -> dict[str, object]:
    models: dict[str, object] = {}
    if "textrank" in config.models and config.models.textrank.enabled:
        model_config = config.models.textrank
        models["textrank"] = TextRankSummarizer(
            similarity_method=model_config.similarity_method,
            damping=model_config.damping,
            num_sentences=model_config.num_sentences,
            max_sentences=getattr(model_config, "max_sentences", 40),
            min_sentence_words=getattr(config.preprocess, "min_sentence_words", 4),
        )

    if not models:
        raise ValueError("No Q3 models are enabled in the current config.")
    return models


def _prediction_rows(split_data: dict[str, list[str]], predictions: list[str], per_example_metrics: list[dict[str, float]]):
    rows = []
    for index, prediction in enumerate(predictions):
        article = split_data["articles"][index]
        reference = split_data["references"][index]
        metrics = per_example_metrics[index]
        rows.append(
            {
                "id": split_data["ids"][index],
                "article_excerpt": article[:280],
                "reference_summary": reference,
                "predicted_summary": prediction,
                "article_word_count": len(article.split()),
                "reference_word_count": len(reference.split()),
                "prediction_word_count": len(prediction.split()),
                "rouge1": round(metrics.get("rouge1", 0.0), 6),
                "rouge2": round(metrics.get("rouge2", 0.0), 6),
                "rougeL": round(metrics.get("rougeL", 0.0), 6),
                "meteor": round(metrics.get("meteor", 0.0), 6),
            }
        )
    return rows


def _evaluate_model(config, model, split_data: dict[str, list[str]]) -> dict[str, object]:
    predictions = model.predict(split_data["articles"])
    evaluation = evaluate_predictions(
        predictions,
        split_data["references"],
        metrics=list(config.evaluation.metrics),
    )
    qualitative_examples = qualitative_comparison(
        split_data["ids"],
        split_data["articles"],
        split_data["references"],
        predictions,
        evaluation["per_example"],
        n_examples=getattr(config.evaluation, "num_qualitative_examples", 3),
    )
    return {
        "metrics": evaluation["metrics"],
        "per_example": evaluation["per_example"],
        "predictions": predictions,
        "qualitative_examples": qualitative_examples,
    }


def run_training(config, run_dir: str, final_eval: bool = False) -> dict[str, object]:
    datasets = prepare_datasets(config)
    models = _build_models(config)
    run_path = Path(run_dir)

    split_names = ["validation"]
    if final_eval:
        split_names.append("test")

    metrics_output: dict[str, object] = {
        "dataset_source": datasets["dataset_source"],
        "split_sizes": datasets["split_sizes"],
        "models": {},
    }
    qualitative_output: dict[str, object] = {
        "dataset_source": datasets["dataset_source"],
        "models": {},
    }

    for model_name, model in models.items():
        model.fit(None)
        metrics_output["models"][model_name] = {}
        qualitative_output["models"][model_name] = {}

        for split_name in split_names:
            evaluation = _evaluate_model(config, model, datasets[split_name])
            metrics_output["models"][model_name][split_name] = {
                "metrics": evaluation["metrics"],
            }
            qualitative_output["models"][model_name][split_name] = {
                "examples": evaluation["qualitative_examples"],
            }
            save_predictions(
                _prediction_rows(datasets[split_name], evaluation["predictions"], evaluation["per_example"]),
                run_path / "predictions" / f"{model_name}_{split_name}_summaries.csv",
            )

    save_metrics(metrics_output, run_path / "metrics.json")
    save_metrics(qualitative_output, run_path / "qualitative_analysis.json")
    return {
        "metrics": metrics_output,
        "qualitative_analysis": qualitative_output,
    }