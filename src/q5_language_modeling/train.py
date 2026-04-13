"""Training orchestration for Q5 language modeling."""

from __future__ import annotations

from pathlib import Path

from src.common.export import save_metrics, save_predictions
from src.q5_language_modeling.analysis import generate_samples
from src.q5_language_modeling.dataset import prepare_datasets
from src.q5_language_modeling.evaluation import evaluate_language_model
from src.q5_language_modeling.models import LSTMLanguageModel, NGramLanguageModel


def _build_model(config) -> tuple[str, object, dict[str, object]]:
    model_type = getattr(config.model, "type", "ngram")
    if model_type == "ngram":
        model = NGramLanguageModel(
            n=getattr(config.model, "n", 3),
            smoothing=getattr(config.model, "smoothing", "add_k"),
            alpha=getattr(config.model, "alpha", 0.1),
            min_token_frequency=getattr(config.model, "min_token_frequency", 2),
        )
        model_config = {
            "n": model.n,
            "smoothing": model.smoothing,
            "alpha": model.alpha,
            "min_token_frequency": model.min_token_frequency,
        }
        return "ngram", model, model_config

    if model_type == "lstm":
        if LSTMLanguageModel is None:
            raise ImportError("Q5 LSTM support requires the 'torch' package. Install dependencies from requirements.txt.")

        model = LSTMLanguageModel(
            embedding_dim=getattr(config.model, "embedding_dim", 128),
            hidden_dim=getattr(config.model, "hidden_dim", 128),
            num_layers=getattr(config.model, "num_layers", 2),
            dropout=getattr(config.model, "dropout", 0.2),
            batch_size=getattr(config.model, "batch_size", 32),
            learning_rate=getattr(config.model, "learning_rate", 1e-3),
            weight_decay=getattr(config.model, "weight_decay", 0.0),
            max_epochs=getattr(config.model, "max_epochs", 8),
            early_stopping_patience=getattr(config.model, "early_stopping_patience", 2),
            max_seq_length=getattr(config.model, "max_seq_length", 35),
            max_vocab_size=getattr(config.model, "max_vocab_size", 15000),
            min_token_frequency=getattr(config.model, "min_token_frequency", 2),
            tie_weights=getattr(config.model, "tie_weights", True),
            gradient_clip=getattr(config.model, "gradient_clip", 1.0),
            num_workers=getattr(config.model, "num_workers", 0),
            device=config.device,
            seed=config.seed,
        )
        model_config = {
            "embedding_dim": model.embedding_dim,
            "hidden_dim": model.hidden_dim,
            "num_layers": model.num_layers,
            "dropout": model.dropout,
            "batch_size": model.batch_size,
            "learning_rate": model.learning_rate,
            "weight_decay": model.weight_decay,
            "max_epochs": model.max_epochs,
            "early_stopping_patience": model.early_stopping_patience,
            "max_seq_length": model.max_seq_length,
            "max_vocab_size": model.max_vocab_size,
            "min_token_frequency": model.min_token_frequency,
            "tie_weights": model.tie_weights,
            "gradient_clip": model.gradient_clip,
        }
        return "lstm", model, model_config

    raise ValueError(f"Unsupported Q5 model type: {model_type}")


def run_training(config, run_dir: str, final_eval: bool = False) -> dict[str, object]:
    datasets = prepare_datasets(config)
    model_name, model, model_config = _build_model(config)
    model.fit(datasets["train"], validation_data=datasets["validation"])
    run_path = Path(run_dir)

    split_names = ["validation"]
    if final_eval:
        split_names.append("test")

    metrics_output: dict[str, object] = {
        "dataset_source": datasets["dataset_source"],
        "split_sizes": datasets["split_sizes"],
        "token_counts": datasets["token_counts"],
        "models": {
            model_name: {
                "config": model_config,
            }
        },
    }

    for split_name in split_names:
        metrics_output["models"][model_name][split_name] = evaluate_language_model(model, datasets[split_name])

    generation_rows = generate_samples(
        model,
        seed_texts=getattr(config.generation, "seed_texts", ["the"]),
        lowercase=getattr(config.preprocess, "lowercase", True),
        max_length=getattr(config.generation, "max_length", 25),
        temperature=getattr(config.generation, "temperature", 1.0),
        num_samples=getattr(config.generation, "num_samples", 3),
    )
    save_predictions(generation_rows, run_path / "predictions" / f"{model_name}_generations.csv")

    qualitative_output: dict[str, object] = {
        "dataset_source": datasets["dataset_source"],
        "models": {
            model_name: {
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