"""Evaluation helpers for Q4 machine translation."""

from __future__ import annotations

import re

from sacrebleu.metrics import BLEU, CHRF

_TOKEN_RE = re.compile(r"\w+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


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
        position = next((v for v in candidate_positions if v not in used_positions), None)
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


def _bertscore(predictions: list[str], references: list[str]) -> float:
    try:
        from bert_score import score as bert_score_fn
    except ImportError:
        raise ImportError("BERTScore requires the 'bert-score' package. Install via: pip install bert-score")

    _, _, f1 = bert_score_fn(predictions, references, lang="de", verbose=False)
    return float(f1.mean().item())


def evaluate_predictions(predictions: list[str], references: list[str], metrics: list[str]) -> dict[str, object]:
    bleu_metric = BLEU(tokenize="intl", effective_order=True)
    chrf_metric = CHRF()

    overall: dict[str, float] = {}
    if "bleu" in metrics:
        overall["bleu"] = bleu_metric.corpus_score(predictions, [references]).score / 100.0
    if "chrf" in metrics:
        overall["chrf"] = chrf_metric.corpus_score(predictions, [references]).score / 100.0
    if "meteor" in metrics:
        scores = [_meteor_score(p, r) for p, r in zip(predictions, references, strict=False)]
        overall["meteor"] = sum(scores) / max(len(scores), 1)
    if "bertscore" in metrics:
        overall["bertscore"] = _bertscore(predictions, references)

    per_example: list[dict[str, float]] = []
    for prediction, reference in zip(predictions, references, strict=False):
        row: dict[str, float] = {}
        if "bleu" in metrics:
            row["bleu"] = bleu_metric.sentence_score(prediction, [reference]).score / 100.0
        if "chrf" in metrics:
            row["chrf"] = chrf_metric.sentence_score(prediction, [reference]).score / 100.0
        if "meteor" in metrics:
            row["meteor"] = _meteor_score(prediction, reference)
        per_example.append(row)

    return {
        "metrics": overall,
        "per_example": per_example,
    }