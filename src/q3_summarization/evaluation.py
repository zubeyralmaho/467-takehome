"""Evaluation helpers for Q3 summarization."""

from __future__ import annotations

from collections import Counter
import math
import re
from typing import Iterable


_TOKEN_RE = re.compile(r"\w+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _ngrams(tokens: list[str], n: int) -> Counter[tuple[str, ...]]:
    if len(tokens) < n:
        return Counter()
    return Counter(tuple(tokens[index : index + n]) for index in range(len(tokens) - n + 1))


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _f1(overlap: int, predicted_total: int, reference_total: int) -> float:
    precision = _safe_divide(overlap, predicted_total)
    recall = _safe_divide(overlap, reference_total)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _rouge_n(prediction: str, reference: str, n: int) -> float:
    prediction_tokens = _tokenize(prediction)
    reference_tokens = _tokenize(reference)
    prediction_ngrams = _ngrams(prediction_tokens, n)
    reference_ngrams = _ngrams(reference_tokens, n)
    overlap = sum((prediction_ngrams & reference_ngrams).values())
    return _f1(overlap, sum(prediction_ngrams.values()), sum(reference_ngrams.values()))


def _lcs_length(first: list[str], second: list[str]) -> int:
    if not first or not second:
        return 0

    previous = [0] * (len(second) + 1)
    for first_token in first:
        current = [0]
        for index, second_token in enumerate(second, start=1):
            if first_token == second_token:
                current.append(previous[index - 1] + 1)
            else:
                current.append(max(current[-1], previous[index]))
        previous = current
    return previous[-1]


def _rouge_l(prediction: str, reference: str) -> float:
    prediction_tokens = _tokenize(prediction)
    reference_tokens = _tokenize(reference)
    overlap = _lcs_length(prediction_tokens, reference_tokens)
    return _f1(overlap, len(prediction_tokens), len(reference_tokens))


def _modified_precision(candidate_tokens: list[str], reference_tokens: list[str], n: int) -> tuple[int, int]:
    candidate_counts = _ngrams(candidate_tokens, n)
    reference_counts = _ngrams(reference_tokens, n)
    overlap = sum((candidate_counts & reference_counts).values())
    return overlap, max(sum(candidate_counts.values()), 1)


def _corpus_bleu(predictions: Iterable[str], references: Iterable[str], max_n: int = 4) -> float:
    clipped_counts = [0] * max_n
    total_counts = [0] * max_n
    prediction_length = 0
    reference_length = 0

    for prediction, reference in zip(predictions, references, strict=False):
        prediction_tokens = _tokenize(prediction)
        reference_tokens = _tokenize(reference)
        prediction_length += len(prediction_tokens)
        reference_length += len(reference_tokens)
        for n in range(1, max_n + 1):
            overlap, total = _modified_precision(prediction_tokens, reference_tokens, n)
            clipped_counts[n - 1] += overlap
            total_counts[n - 1] += total

    if prediction_length == 0:
        return 0.0

    precisions = []
    for overlap, total in zip(clipped_counts, total_counts, strict=False):
        precisions.append((overlap + 1.0) / (total + 1.0))

    brevity_penalty = 1.0
    if prediction_length < reference_length:
        brevity_penalty = math.exp(1 - (reference_length / prediction_length))
    return brevity_penalty * math.exp(sum(math.log(value) for value in precisions) / max_n)


def _meteor_score(prediction: str, reference: str) -> float:
    prediction_tokens = _tokenize(prediction)
    reference_tokens = _tokenize(reference)
    if not prediction_tokens or not reference_tokens:
        return 0.0

    reference_positions: dict[str, list[int]] = {}
    for index, token in enumerate(reference_tokens):
        reference_positions.setdefault(token, []).append(index)

    matches = 0
    chunks = 0
    last_position = -2
    used_positions: set[int] = set()

    for token in prediction_tokens:
        candidate_positions = reference_positions.get(token, [])
        position = next((value for value in candidate_positions if value not in used_positions), None)
        if position is None:
            continue
        used_positions.add(position)
        matches += 1
        if position != last_position + 1:
            chunks += 1
        last_position = position

    if matches == 0:
        return 0.0

    precision = matches / len(prediction_tokens)
    recall = matches / len(reference_tokens)
    harmonic_mean = (10 * precision * recall) / ((9 * precision) + recall)
    penalty = 0.5 * ((chunks / matches) ** 3)
    return harmonic_mean * (1 - penalty)


def _example_metrics(prediction: str, reference: str) -> dict[str, float]:
    return {
        "rouge1": _rouge_n(prediction, reference, 1),
        "rouge2": _rouge_n(prediction, reference, 2),
        "rougeL": _rouge_l(prediction, reference),
        "meteor": _meteor_score(prediction, reference),
    }


def _bertscore(predictions: list[str], references: list[str]) -> float:
    try:
        from bert_score import score as bert_score_fn
    except ImportError:
        raise ImportError("BERTScore requires the 'bert-score' package. Install via: pip install bert-score")

    _, _, f1 = bert_score_fn(predictions, references, lang="en", verbose=False)
    return float(f1.mean().item())


def evaluate_predictions(predictions: list[str], references: list[str], metrics: list[str] | None = None) -> dict[str, object]:
    requested = list(metrics) if metrics else ["rouge1", "rouge2", "rougeL", "bleu", "meteor"]
    per_example = [_example_metrics(prediction, reference) for prediction, reference in zip(predictions, references, strict=False)]

    available: dict[str, float] = {}
    if per_example:
        available.update(
            {
                "rouge1": sum(item["rouge1"] for item in per_example) / len(per_example),
                "rouge2": sum(item["rouge2"] for item in per_example) / len(per_example),
                "rougeL": sum(item["rougeL"] for item in per_example) / len(per_example),
                "meteor": sum(item["meteor"] for item in per_example) / len(per_example),
            }
        )
    else:
        available.update({"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0, "meteor": 0.0})
    available["bleu"] = _corpus_bleu(predictions, references)
    available["rougeLsum"] = available["rougeL"]

    if "bertscore" in requested:
        available["bertscore"] = _bertscore(predictions, references)

    unsupported = [name for name in requested if name not in available]
    if unsupported:
        raise ValueError(f"Unsupported Q3 metrics requested: {unsupported}")

    return {
        "metrics": {name: float(available[name]) for name in requested},
        "per_example": per_example,
    }