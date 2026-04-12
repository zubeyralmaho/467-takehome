"""Training orchestration for Q1 text classification."""

from __future__ import annotations

from pathlib import Path

from src.common.export import save_metrics, save_predictions
from src.common.metrics import compute_classification_report, compute_metrics
from src.q1_classification.analysis import analyze_misclassifications, identify_error_patterns
from src.q1_classification.dataset import prepare_datasets
from src.q1_classification.models import BiLSTMClassifier, TFIDFClassifier


def _build_models(config) -> dict[str, object]:
    models: dict[str, object] = {}
    for model_name in ["tfidf_lr", "tfidf_svm"]:
        model_config = getattr(config.models, model_name)
        if not model_config.enabled:
            continue
        models[model_name] = TFIDFClassifier(
            classifier_type=model_config.classifier,
            max_features=model_config.max_features,
            ngram_range=tuple(model_config.ngram_range),
            C=model_config.C,
        )

    if "bilstm" in config.models and config.models.bilstm.enabled:
        model_config = config.models.bilstm
        if BiLSTMClassifier is None:
            raise ImportError("BiLSTM support requires the 'torch' package. Install dependencies from requirements.txt.")
        models["bilstm"] = BiLSTMClassifier(
            embedding_dim=model_config.embedding_dim,
            hidden_dim=model_config.hidden_dim,
            num_layers=model_config.num_layers,
            dropout=model_config.dropout,
            batch_size=model_config.batch_size,
            learning_rate=model_config.learning_rate,
            max_epochs=model_config.max_epochs,
            early_stopping_patience=getattr(
                model_config,
                "early_stopping_patience",
                getattr(config.training, "early_stopping_patience", 3),
            ),
            max_vocab_size=model_config.max_vocab_size,
            min_frequency=model_config.min_frequency,
            max_seq_length=model_config.max_seq_length,
            weight_decay=getattr(model_config, "weight_decay", 0.0),
            monitor_metric=getattr(model_config, "monitor_metric", "macro_f1"),
            num_workers=getattr(model_config, "num_workers", 0),
            device=config.device,
            seed=config.seed,
        )
    return models


def _prediction_rows(texts, labels, predictions, confidences):
    rows = []
    for index, (text, label, prediction, confidence) in enumerate(zip(texts, labels, predictions, confidences, strict=False)):
        rows.append(
            {
                "index": index,
                "text": text,
                "true_label": int(label),
                "predicted_label": int(prediction),
                "confidence": round(float(confidence), 6) if confidence is not None else "",
            }
        )
    return rows


def _evaluate_model(config, model, split_data: dict[str, list]) -> dict:
    predictions = model.predict(split_data["texts"])
    confidences = model.predict_confidence(split_data["texts"])
    metrics = compute_metrics(
        config.task,
        predictions=predictions,
        references=split_data["labels"],
        metrics=config.evaluation.metrics,
    )
    report = compute_classification_report(split_data["labels"], predictions)
    misclassified = analyze_misclassifications(
        split_data["texts"],
        split_data["labels"],
        predictions,
        confidences=confidences,
        n_examples=config.evaluation.num_misclassified_examples,
    )
    return {
        "metrics": metrics,
        "classification_report": report,
        "predictions": predictions.tolist(),
        "confidences": confidences,
        "misclassified_examples": misclassified,
        "error_patterns": identify_error_patterns(misclassified),
    }


def run_training(config, run_dir: str, final_eval: bool = False) -> dict:
    datasets = prepare_datasets(config)
    models = _build_models(config)
    run_path = Path(run_dir)

    split_names = ["validation"]
    if final_eval:
        split_names.append("test")

    metrics_output: dict[str, dict] = {}
    analysis_output: dict[str, dict] = {}

    for model_name, model in models.items():
        is_bilstm = BiLSTMClassifier is not None and isinstance(model, BiLSTMClassifier)
        if is_bilstm:
            model.fit(
                datasets["train"]["texts"],
                datasets["train"]["labels"],
                validation_data=datasets["validation"],
            )
        else:
            model.fit(datasets["train"]["texts"], datasets["train"]["labels"])

        metrics_output[model_name] = {}
        analysis_output[model_name] = {}

        for split_name in split_names:
            evaluation = _evaluate_model(config, model, datasets[split_name])
            metrics_output[model_name][split_name] = {
                "metrics": evaluation["metrics"],
                "classification_report": evaluation["classification_report"],
            }
            analysis_output[model_name][split_name] = {
                "misclassified_examples": evaluation["misclassified_examples"],
                "error_patterns": evaluation["error_patterns"],
            }

            save_predictions(
                _prediction_rows(
                    datasets[split_name]["texts"],
                    datasets[split_name]["labels"],
                    evaluation["predictions"],
                    evaluation["confidences"],
                ),
                run_path / "predictions" / f"{model_name}_{split_name}_predictions.csv",
            )

    save_metrics(metrics_output, run_path / "metrics.json")
    save_metrics(analysis_output, run_path / "misclassification_analysis.json")

    return {"metrics": metrics_output, "analysis": analysis_output}
