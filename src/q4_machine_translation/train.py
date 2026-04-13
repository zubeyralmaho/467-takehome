"""Training orchestration for Q4 machine translation."""

from __future__ import annotations

from pathlib import Path

from src.common.export import save_metrics, save_predictions
from src.q4_machine_translation.analysis import qualitative_translation_examples
from src.q4_machine_translation.dataset import prepare_datasets
from src.q4_machine_translation.evaluation import evaluate_predictions
from src.q4_machine_translation.models import PretrainedTransformerMT, Seq2SeqAttentionMT


def _build_models(config) -> dict[str, object]:
    models: dict[str, object] = {}
    if "seq2seq" in config.models and config.models.seq2seq.enabled:
        if Seq2SeqAttentionMT is None:
            raise ImportError("Q4 seq2seq support requires the 'torch' package. Install dependencies from requirements.txt.")

        model_config = config.models.seq2seq
        models["seq2seq"] = Seq2SeqAttentionMT(
            embedding_dim=getattr(model_config, "embedding_dim", 128),
            hidden_dim=getattr(model_config, "hidden_dim", 128),
            num_layers=getattr(model_config, "num_layers", 1),
            dropout=getattr(model_config, "dropout", 0.2),
            batch_size=getattr(model_config, "batch_size", 32),
            learning_rate=getattr(model_config, "learning_rate", 1e-3),
            weight_decay=getattr(model_config, "weight_decay", 0.0),
            max_epochs=getattr(model_config, "max_epochs", 8),
            early_stopping_patience=getattr(model_config, "early_stopping_patience", 2),
            teacher_forcing_ratio=getattr(model_config, "teacher_forcing_ratio", 0.5),
            max_vocab_size=getattr(model_config, "max_vocab_size", 8000),
            min_token_frequency=getattr(model_config, "min_token_frequency", 2),
            max_output_length=getattr(model_config, "max_output_length", 32),
            gradient_clip=getattr(model_config, "gradient_clip", 1.0),
            num_workers=getattr(model_config, "num_workers", 0),
            device=config.device,
            seed=config.seed,
        )

    if "transformer" in config.models and config.models.transformer.enabled:
        model_config = config.models.transformer
        models["transformer"] = PretrainedTransformerMT(
            model_name=model_config.model_name,
            batch_size=getattr(model_config, "batch_size", 8),
            max_input_length=getattr(model_config, "max_input_length", 96),
            max_output_length=getattr(model_config, "max_output_length", 96),
            num_beams=getattr(model_config, "num_beams", 4),
            length_penalty=getattr(model_config, "length_penalty", 1.0),
            early_stopping=getattr(model_config, "early_stopping", True),
            device=config.device,
        )
    if not models:
        raise ValueError("No Q4 models are enabled in the current config.")
    return models


def _prediction_rows(split_data: dict[str, list[str]], predictions: list[str], per_example_metrics: list[dict[str, float]]):
    rows = []
    for index, prediction in enumerate(predictions):
        source = split_data["sources"][index]
        reference = split_data["references"][index]
        metrics = per_example_metrics[index]
        rows.append(
            {
                "id": split_data["ids"][index],
                "source_text": source,
                "reference_translation": reference,
                "predicted_translation": prediction,
                "source_word_count": len(source.split()),
                "reference_word_count": len(reference.split()),
                "prediction_word_count": len(prediction.split()),
                "bleu": round(metrics.get("bleu", 0.0), 6),
                "chrf": round(metrics.get("chrf", 0.0), 6),
            }
        )
    return rows


def _evaluate_model(config, model, split_data: dict[str, list[str]]) -> dict[str, object]:
    predictions = model.predict(split_data["sources"])
    evaluation = evaluate_predictions(
        predictions,
        split_data["references"],
        metrics=list(config.evaluation.metrics),
    )
    qualitative_examples = qualitative_translation_examples(
        split_data["ids"],
        split_data["sources"],
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
        model.fit(
            datasets["train"]["sources"],
            datasets["train"]["references"],
            validation_data=datasets.get("validation"),
        )
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
                run_path / "predictions" / f"{model_name}_{split_name}_translations.csv",
            )

    save_metrics(metrics_output, run_path / "metrics.json")
    save_metrics(qualitative_output, run_path / "qualitative_analysis.json")
    return {
        "metrics": metrics_output,
        "qualitative_analysis": qualitative_output,
    }