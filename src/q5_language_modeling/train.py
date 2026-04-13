"""Training orchestration for Q5 language modeling."""

from __future__ import annotations

from pathlib import Path

from src.common.export import save_metrics, save_predictions
from src.q5_language_modeling.analysis import generate_samples
from src.q5_language_modeling.dataset import prepare_datasets
from src.q5_language_modeling.evaluation import evaluate_language_model
from src.q5_language_modeling.models import NGramLanguageModel


def _build_model(config) -> NGramLanguageModel:
    if getattr(config.model, "type", "ngram") != "ngram":
        raise ValueError("Q5 currently supports only the ngram baseline.")
    return NGramLanguageModel(
        n=getattr(config.model, "n", 3),
        smoothing=getattr(config.model, "smoothing", "add_k"),
        alpha=getattr(config.model, "alpha", 0.1),
        min_token_frequency=getattr(config.model, "min_token_frequency", 2),
    )


def run_training(config, run_dir: str, final_eval: bool = False) -> dict[str, object]:
    datasets = prepare_datasets(config)
    model = _build_model(config)
    model.fit(datasets["train"])
    run_path = Path(run_dir)

    split_names = ["validation"]
    if final_eval:
        split_names.append("test")

    metrics_output: dict[str, object] = {
        "dataset_source": datasets["dataset_source"],
        "split_sizes": datasets["split_sizes"],
        "token_counts": datasets["token_counts"],
        "models": {
            "ngram": {
                "config": {
                    "n": model.n,
                    "smoothing": model.smoothing,
                    "alpha": model.alpha,
                    "min_token_frequency": model.min_token_frequency,
                }
            }
        },
    }

    for split_name in split_names:
        metrics_output["models"]["ngram"][split_name] = evaluate_language_model(model, datasets[split_name])

    generation_rows = generate_samples(
        model,
        seed_texts=getattr(config.generation, "seed_texts", ["the"]),
        lowercase=getattr(config.preprocess, "lowercase", True),
        max_length=getattr(config.generation, "max_length", 25),
        temperature=getattr(config.generation, "temperature", 1.0),
        num_samples=getattr(config.generation, "num_samples", 3),
    )
    save_predictions(generation_rows, run_path / "predictions" / "ngram_generations.csv")

    qualitative_output: dict[str, object] = {
        "dataset_source": datasets["dataset_source"],
        "models": {
            "ngram": {
                "generations": generation_rows,
            }
        },
    }

    save_metrics(metrics_output, run_path / "metrics.json")
    save_metrics(qualitative_output, run_path / "qualitative_analysis.json")
    return {
        "metrics": metrics_output,
        "qualitative_analysis": qualitative_output,
    }