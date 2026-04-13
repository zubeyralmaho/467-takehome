"""Training orchestration for Q2 named entity recognition."""

from __future__ import annotations

from pathlib import Path

try:
    from seqeval.metrics import accuracy_score as seqeval_accuracy_score
    from seqeval.metrics import classification_report as seqeval_classification_report
    from seqeval.metrics import f1_score as seqeval_f1_score
    from seqeval.metrics import precision_score as seqeval_precision_score
    from seqeval.metrics import recall_score as seqeval_recall_score
    from seqeval.scheme import IOB2
except ImportError:
    seqeval_accuracy_score = None
    seqeval_classification_report = None
    seqeval_f1_score = None
    seqeval_precision_score = None
    seqeval_recall_score = None
    IOB2 = None

from src.common.export import save_metrics, save_predictions
from src.q2_ner.analysis import analyze_sequence_errors, summarize_label_confusions
from src.q2_ner.dataset import prepare_datasets
from src.q2_ner.models import FeatureBasedCRF


def _ensure_seqeval_available() -> None:
    if seqeval_accuracy_score is None or seqeval_classification_report is None or IOB2 is None:
        raise ImportError("NER evaluation requires the 'seqeval' package. Install dependencies from requirements.txt.")


def _build_models(config) -> dict[str, object]:
    models: dict[str, object] = {}
    if "crf" in config.models and config.models.crf.enabled:
        if FeatureBasedCRF is None:
            raise ImportError(
                "CRF support requires the 'sklearn-crfsuite' package. Install dependencies from requirements.txt."
            )

        model_config = config.models.crf
        models["crf"] = FeatureBasedCRF(
            algorithm=model_config.algorithm,
            c1=model_config.c1,
            c2=model_config.c2,
            max_iterations=model_config.max_iterations,
            all_possible_transitions=getattr(model_config, "all_possible_transitions", True),
        )

    if not models:
        raise ValueError("No Q2 models are enabled in the current config.")
    return models


def _prediction_rows(token_sequences, references, predictions, confidences):
    rows = []
    for sentence_index, (tokens, true_labels, predicted_labels) in enumerate(
        zip(token_sequences, references, predictions, strict=False)
    ):
        sentence_confidences = confidences[sentence_index] if confidences is not None else [None] * len(tokens)
        for token_index, (token, true_label, predicted_label, confidence) in enumerate(
            zip(tokens, true_labels, predicted_labels, sentence_confidences, strict=False)
        ):
            rows.append(
                {
                    "sentence_index": sentence_index,
                    "token_index": token_index,
                    "token": token,
                    "true_label": true_label,
                    "predicted_label": predicted_label,
                    "confidence": round(float(confidence), 6) if confidence is not None else "",
                }
            )
    return rows


def _compute_ner_metrics(references, predictions, metrics=None) -> dict[str, float]:
    _ensure_seqeval_available()
    requested = list(metrics) if metrics else []

    available = {
        "precision": float(seqeval_precision_score(references, predictions, mode="strict", scheme=IOB2, zero_division=0)),
        "recall": float(seqeval_recall_score(references, predictions, mode="strict", scheme=IOB2, zero_division=0)),
        "f1": float(seqeval_f1_score(references, predictions, mode="strict", scheme=IOB2, zero_division=0)),
        "accuracy": float(seqeval_accuracy_score(references, predictions)),
    }
    if not requested:
        return available
    return {name: available[name] for name in requested if name in available}


def _compute_sequence_report(references, predictions) -> dict:
    _ensure_seqeval_available()
    return seqeval_classification_report(
        references,
        predictions,
        mode="strict",
        scheme=IOB2,
        zero_division=0,
        output_dict=True,
    )


def _evaluate_model(config, model, split_data: dict[str, list]) -> dict:
    predictions = model.predict(split_data["tokens"])
    token_confidences = model.predict_token_confidences(split_data["tokens"], predictions=predictions)
    metrics = _compute_ner_metrics(
        split_data["labels"],
        predictions,
        metrics=config.evaluation.metrics,
    )
    report = _compute_sequence_report(split_data["labels"], predictions)
    error_examples = analyze_sequence_errors(
        split_data["tokens"],
        split_data["labels"],
        predictions,
        token_confidences=token_confidences,
        n_examples=config.evaluation.num_error_examples,
    )
    return {
        "metrics": metrics,
        "classification_report": report,
        "predictions": predictions,
        "token_confidences": token_confidences,
        "error_examples": error_examples,
        "label_confusions": summarize_label_confusions(
            split_data["labels"],
            predictions,
            top_n=getattr(config.evaluation, "top_confusions", 10),
        ),
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
        "label_names": datasets["label_names"],
        "split_sizes": datasets["split_sizes"],
        "models": {},
    }
    analysis_output: dict[str, object] = {
        "dataset_source": datasets["dataset_source"],
        "models": {},
    }

    for model_name, model in models.items():
        model.fit(datasets["train"]["tokens"], datasets["train"]["labels"])

        metrics_output["models"][model_name] = {}
        analysis_output["models"][model_name] = {}

        for split_name in split_names:
            evaluation = _evaluate_model(config, model, datasets[split_name])
            metrics_output["models"][model_name][split_name] = {
                "metrics": evaluation["metrics"],
                "classification_report": evaluation["classification_report"],
            }
            analysis_output["models"][model_name][split_name] = {
                "error_examples": evaluation["error_examples"],
                "label_confusions": evaluation["label_confusions"],
            }

            save_predictions(
                _prediction_rows(
                    datasets[split_name]["tokens"],
                    datasets[split_name]["labels"],
                    evaluation["predictions"],
                    evaluation["token_confidences"],
                ),
                run_path / "predictions" / f"{model_name}_{split_name}_predictions.csv",
            )

    save_metrics(metrics_output, run_path / "metrics.json")
    save_metrics(analysis_output, run_path / "error_analysis.json")

    return {"metrics": metrics_output, "analysis": analysis_output}