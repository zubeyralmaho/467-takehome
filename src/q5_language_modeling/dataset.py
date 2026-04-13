"""Dataset helpers for Q5 language modeling."""

from __future__ import annotations

import random
from typing import Any

from src.common.data_utils import load_hf_dataset


def tokenize_text(text: str, lowercase: bool = True) -> list[str]:
    normalized = " ".join(str(text).strip().split())
    if lowercase:
        normalized = normalized.lower()
    return normalized.split() if normalized else []


def _collect_sequences(
    split: Any,
    text_column: str,
    limit: int | None,
    seed: int,
    lowercase: bool,
    min_tokens: int,
) -> list[list[str]]:
    indices = list(range(len(split)))
    random.Random(seed).shuffle(indices)

    sequences: list[list[str]] = []
    for index in indices:
        tokens = tokenize_text(split[index][text_column], lowercase=lowercase)
        if len(tokens) < min_tokens:
            continue
        sequences.append(tokens)
        if limit is not None and len(sequences) >= limit:
            break
    return sequences


def prepare_datasets(config) -> dict[str, object]:
    dataset = load_hf_dataset(
        config.dataset.name,
        subset=getattr(config.dataset, "version", None),
        cache_dir=config.data.cache_dir,
    )

    dataset_source = config.dataset.name
    if getattr(config.dataset, "version", None):
        dataset_source = f"{config.dataset.name}:{config.dataset.version}"

    split_limits = {
        "train": getattr(config.dataset, "limit_train_samples", None),
        "validation": getattr(config.dataset, "limit_validation_samples", None),
        "test": getattr(config.dataset, "limit_test_samples", None),
    }

    prepared: dict[str, object] = {
        "dataset_source": dataset_source,
        "split_sizes": {},
        "token_counts": {},
    }

    for offset, split_name in enumerate(["train", "validation", "test"]):
        if split_name not in dataset:
            continue
        sequences = _collect_sequences(
            dataset[split_name],
            text_column=config.dataset.text_column,
            limit=split_limits[split_name],
            seed=config.seed + offset,
            lowercase=getattr(config.preprocess, "lowercase", True),
            min_tokens=getattr(config.preprocess, "min_tokens_per_line", 2),
        )
        prepared[split_name] = sequences
        prepared["split_sizes"][split_name] = len(sequences)
        prepared["token_counts"][split_name] = sum(len(sequence) for sequence in sequences)

    return prepared