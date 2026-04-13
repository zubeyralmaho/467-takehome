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
from src.q2_ner.models import BERTNERModel, BiLSTMCRFTagger, FeatureBasedCRF


def _ensure_seqeval_available() -> None:
    if seqeval_accuracy_score is None or seqeval_classification_report is None or IOB2 is None:
        raise ImportError("NER evaluation requires the 'seqeval' package. Install dependencies from requirements.txt.")


def _build_models(config, label_names: list[str]) -> dict[str, object]:
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

    if "bilstm_crf" in config.models and config.models.bilstm_crf.enabled:
        if BiLSTMCRFTagger is None:
            raise ImportError(
                "BiLSTM-CRF support requires the 'pytorch-crf' package. Install dependencies from requirements.txt."
            )

        model_config = config.models.bilstm_crf
        models["bilstm_crf"] = BiLSTMCRFTagger(
            label_names=label_names,
            embedding_dim=model_config.embedding_dim,
            hidden_dim=model_config.hidden_dim,
            num_layers=model_config.num_layers,
            dropout=model_config.dropout,
            batch_size=model_config.batch_size,
            learning_rate=model_config.learning_rate,
            weight_decay=getattr(model_config, "weight_decay", 0.0),
            max_epochs=model_config.max_epochs,
            early_stopping_patience=getattr(
                model_config,
                "early_stopping_patience",
                getattr(config.training, "early_stopping_patience", 3),
            ),
            max_vocab_size=model_config.max_vocab_size,
            min_frequency=model_config.min_frequency,
            num_workers=getattr(model_config, "num_workers", 0),
            monitor_metric=getattr(model_config, "monitor_metric", "f1"),
            device=config.device,
            seed=config.seed,
        )

    if "bert" in config.models and config.models.bert.enabled:
        if BERTNERModel is None:
            raise ImportError(
                "BERT NER support requires the 'transformers' package. Install dependencies from requirements.txt."
            )

        model_config = config.models.bert
        models["bert"] = BERTNERModel(
            label_names=label_names,
            model_name=model_config.model_name,
            batch_size=model_config.batch_size,
            learning_rate=model_config.learning_rate,
            weight_decay=model_config.weight_decay,
            max_epochs=model_config.max_epochs,
            early_stopping_patience=getattr(model_config, "early_stopping_patience", 2),
            max_seq_length=model_config.max_seq_length,
            warmup_ratio=getattr(model_config, "warmup_ratio", 0.1),
            monitor_metric=getattr(model_config, "monitor_metric", "f1"),
            num_workers=getattr(model_config, "num_workers", 0),
            device=config.device,
            seed=config.seed,
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
    models = _build_models(config, label_names=datasets["label_names"])
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
        model.fit(
            datasets["train"]["tokens"],
            datasets["train"]["labels"],
            validation_data=datasets["validation"],
        )

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