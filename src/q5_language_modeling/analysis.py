"""Generation analysis helpers for Q5 language modeling."""

from __future__ import annotations

from collections.abc import Sequence

from src.q5_language_modeling.dataset import tokenize_text


def generate_samples(
    model,
    seed_texts: Sequence[str],
    lowercase: bool,
    max_length: int,
    temperature: float,
    num_samples: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, seed_text in enumerate(list(seed_texts)[:num_samples], start=1):
        seed_tokens = tokenize_text(seed_text, lowercase=lowercase)
        generated_tokens = model.generate(
            seed_tokens,
            max_length=max_length,
            temperature=temperature,
        )
        rows.append(
            {
                "sample_id": index,
                "seed_text": seed_text,
                "generated_text": " ".join(generated_tokens),
                "generated_token_count": len(generated_tokens),
                "seed_token_count": len(seed_tokens),
            }
        )
    return rows