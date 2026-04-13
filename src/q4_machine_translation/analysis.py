"""Qualitative analysis helpers for Q4 machine translation."""

from __future__ import annotations


def qualitative_translation_examples(
    ids: list[str],
    sources: list[str],
    references: list[str],
    predictions: list[str],
    per_example_metrics: list[dict[str, float]],
    n_examples: int = 3,
) -> list[dict[str, object]]:
    if not ids:
        return []

    sorted_indices = sorted(
        range(len(ids)),
        key=lambda index: per_example_metrics[index].get("chrf", per_example_metrics[index].get("bleu", 0.0)),
    )

    selected_indices: list[int] = []
    if sorted_indices:
        selected_indices.append(sorted_indices[-1])
    if len(sorted_indices) > 2 and n_examples > 2:
        selected_indices.append(sorted_indices[len(sorted_indices) // 2])
    if len(sorted_indices) > 1 and n_examples > 1:
        selected_indices.append(sorted_indices[0])

    deduplicated = []
    for index in selected_indices:
        if index not in deduplicated:
            deduplicated.append(index)

    rows: list[dict[str, object]] = []
    for index in deduplicated[:n_examples]:
        metrics = per_example_metrics[index]
        rows.append(
            {
                "id": ids[index],
                "source_text": sources[index],
                "reference_translation": references[index],
                "predicted_translation": predictions[index],
                "source_word_count": len(sources[index].split()),
                "reference_word_count": len(references[index].split()),
                "prediction_word_count": len(predictions[index].split()),
                "bleu": round(metrics.get("bleu", 0.0), 6),
                "chrf": round(metrics.get("chrf", 0.0), 6),
            }
        )
    return rows