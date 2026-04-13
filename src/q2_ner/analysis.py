"""Error analysis helpers for Q2 named entity recognition."""

from __future__ import annotations

from collections import Counter
from typing import Sequence


def _parse_label(label: str) -> tuple[str, str | None]:
    if label == "O":
        return "O", None
    if "-" not in label:
        return label, None
    prefix, entity_type = label.split("-", 1)
    return prefix, entity_type


def extract_entities(tokens: Sequence[str], labels: Sequence[str]) -> list[dict[str, object]]:
    entities: list[dict[str, object]] = []
    start_index: int | None = None
    entity_type: str | None = None

    for index, label in enumerate([*labels, "O"]):
        prefix, current_type = _parse_label(label)

        if entity_type is not None and (prefix != "I" or current_type != entity_type):
            entities.append(
                {
                    "type": entity_type,
                    "start": start_index,
                    "end": index - 1,
                    "text": " ".join(tokens[start_index:index]),
                }
            )
            start_index = None
            entity_type = None

        if prefix == "B":
            start_index = index
            entity_type = current_type
        elif prefix == "I" and current_type is not None and entity_type is None:
            start_index = index
            entity_type = current_type

    return entities


def analyze_sequence_errors(
    token_sequences: Sequence[Sequence[str]],
    references: Sequence[Sequence[str]],
    predictions: Sequence[Sequence[str]],
    token_confidences: Sequence[Sequence[float | None]] | None = None,
    n_examples: int = 5,
) -> list[dict[str, object]]:
    examples: list[dict[str, object]] = []
    confidence_sequences = (
        list(token_confidences)
        if token_confidences is not None
        else [[None] * len(tokens) for tokens in token_sequences]
    )

    for sentence_index, (tokens, true_labels, predicted_labels, confidences) in enumerate(
        zip(token_sequences, references, predictions, confidence_sequences, strict=False)
    ):
        if list(true_labels) == list(predicted_labels):
            continue

        token_errors: list[dict[str, object]] = []
        mismatched_confidences: list[float] = []
        for token_index, (token, true_label, predicted_label, confidence) in enumerate(
            zip(tokens, true_labels, predicted_labels, confidences, strict=False)
        ):
            if true_label == predicted_label:
                continue
            if confidence is not None:
                mismatched_confidences.append(float(confidence))
            token_errors.append(
                {
                    "token_index": token_index,
                    "token": token,
                    "true_label": true_label,
                    "predicted_label": predicted_label,
                    "confidence": round(float(confidence), 4) if confidence is not None else None,
                }
            )
            if len(token_errors) >= 10:
                break

        examples.append(
            {
                "sentence_index": sentence_index,
                "sentence": " ".join(tokens),
                "token_error_count": sum(
                    1
                    for true_label, predicted_label in zip(true_labels, predicted_labels, strict=False)
                    if true_label != predicted_label
                ),
                "mean_mismatched_confidence": (
                    round(sum(mismatched_confidences) / len(mismatched_confidences), 4)
                    if mismatched_confidences
                    else None
                ),
                "true_entities": extract_entities(tokens, true_labels),
                "predicted_entities": extract_entities(tokens, predicted_labels),
                "token_errors": token_errors,
            }
        )

        if len(examples) >= n_examples:
            break

    return examples


def summarize_label_confusions(
    references: Sequence[Sequence[str]],
    predictions: Sequence[Sequence[str]],
    top_n: int = 10,
) -> list[dict[str, object]]:
    confusion_counts: Counter[tuple[str, str]] = Counter()
    for true_labels, predicted_labels in zip(references, predictions, strict=False):
        for true_label, predicted_label in zip(true_labels, predicted_labels, strict=False):
            if true_label == predicted_label:
                continue
            confusion_counts[(true_label, predicted_label)] += 1

    return [
        {
            "true_label": true_label,
            "predicted_label": predicted_label,
            "count": count,
        }
        for (true_label, predicted_label), count in confusion_counts.most_common(top_n)
    ]