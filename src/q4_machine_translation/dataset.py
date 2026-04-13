"""Dataset helpers for Q4 machine translation."""

from __future__ import annotations

from src.common.data_utils import load_hf_dataset, subsample


def _normalize_text(text: str, lowercase: bool) -> str:
    normalized = " ".join(str(text).strip().split())
    return normalized.lower() if lowercase else normalized


def prepare_datasets(config) -> dict[str, object]:
    dataset = load_hf_dataset(
        config.dataset.name,
        cache_dir=config.data.cache_dir,
    )

    split_limits = {
        "train": getattr(config.dataset, "limit_train_samples", None),
        "validation": getattr(config.dataset, "limit_validation_samples", None),
        "test": getattr(config.dataset, "limit_test_samples", None),
    }

    prepared: dict[str, object] = {
        "dataset_source": config.dataset.name,
        "split_sizes": {},
    }

    for offset, split_name in enumerate(["train", "validation", "test"]):
        if split_name not in dataset:
            continue
        sampled_split = subsample(dataset[split_name], split_limits[split_name], seed=config.seed + offset)

        sources: list[str] = []
        references: list[str] = []
        example_ids: list[str] = []
        for index, example in enumerate(sampled_split):
            sources.append(_normalize_text(example[config.dataset.src_lang], getattr(config.preprocess, "lowercase_source", False)))
            references.append(_normalize_text(example[config.dataset.tgt_lang], getattr(config.preprocess, "lowercase_target", False)))
            example_ids.append(f"{split_name}_{index}")

        prepared[split_name] = {
            "ids": example_ids,
            "sources": sources,
            "references": references,
        }
        prepared["split_sizes"][split_name] = len(example_ids)

    return prepared