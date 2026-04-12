"""Training orchestration for the initial Q1 baseline slice."""

from __future__ import annotations

from pathlib import Path

from src.common.export import save_metrics, save_predictions
from src.common.metrics import compute_classification_report, compute_metrics
from src.q1_classification.analysis import analyze_misclassifications, identify_error_patterns
from src.q1_classification.dataset import prepare_datasets
from src.q1_classification.models import TFIDFClassifier


def _build_models(config) -> dict[str, TFIDFClassifier]:
    models: dict[str, TFIDFClassifier] = {}
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
