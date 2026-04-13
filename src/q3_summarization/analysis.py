"""Qualitative analysis helpers for Q3 summarization."""

from __future__ import annotations


def _truncate(text: str, max_chars: int = 400) -> str:
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 3]}..."


def qualitative_comparison(
    ids: list[str],
    articles: list[str],
    references: list[str],
    predictions: list[str],
    per_example_metrics: list[dict[str, float]],
    n_examples: int = 3,
) -> list[dict[str, object]]:
    if not predictions:
        return []

    ranked_indices = sorted(
        range(len(predictions)),
        key=lambda index: per_example_metrics[index].get("rougeL", 0.0),
    )

    if len(ranked_indices) <= n_examples:
        selected_indices = ranked_indices
    else:
        selected_indices = [ranked_indices[0], ranked_indices[len(ranked_indices) // 2], ranked_indices[-1]]
        selected_indices = selected_indices[:n_examples]

    examples: list[dict[str, object]] = []
    for index in selected_indices:
        article = articles[index]
        reference = references[index]
        prediction = predictions[index]
        metric_values = per_example_metrics[index]
        examples.append(
            {
                "id": ids[index],
                "article_excerpt": _truncate(article),
                "reference_summary": reference,
                "predicted_summary": prediction,
                "article_word_count": len(article.split()),
                "reference_word_count": len(reference.split()),
                "prediction_word_count": len(prediction.split()),
                "coverage_vs_reference": metric_values.get("rouge1", 0.0),
                "bigram_overlap": metric_values.get("rouge2", 0.0),
                "structure_overlap": metric_values.get("rougeL", 0.0),
                "meteor": metric_values.get("meteor", 0.0),
            }
        )
    return examples