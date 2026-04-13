"""Evaluation helpers for Q5 language modeling."""

from __future__ import annotations


def evaluate_language_model(model, token_sequences: list[list[str]]) -> dict[str, object]:
    return {
        "metrics": {
            "perplexity": model.corpus_perplexity(token_sequences),
        },
        "sequence_count": len(token_sequences),
        "token_count": sum(len(sequence) for sequence in token_sequences),
    }