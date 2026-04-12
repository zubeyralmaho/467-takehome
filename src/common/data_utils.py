"""Dataset loading and split helpers."""

from __future__ import annotations

from typing import Any

from datasets import Dataset, DatasetDict, load_dataset


def load_hf_dataset(name: str, subset: str | None = None, cache_dir: str | None = None) -> DatasetDict:
    if subset:
        return load_dataset(name, subset, cache_dir=cache_dir)
    return load_dataset(name, cache_dir=cache_dir)


def subsample(dataset: Dataset, n: int | None, seed: int = 42) -> Dataset:
    if n is None or n >= len(dataset):
        return dataset
    return dataset.shuffle(seed=seed).select(range(n))


def create_splits(dataset: Dataset, val_ratio: float = 0.2, seed: int = 42, label_column: str | None = None) -> dict[str, Dataset]:
    if not 0 < val_ratio < 1:
        raise ValueError("val_ratio must be between 0 and 1.")

    split_kwargs: dict[str, Any] = {"test_size": val_ratio, "seed": seed}
    if label_column and label_column in dataset.column_names:
        split_kwargs["stratify_by_column"] = label_column

    try:
        split = dataset.train_test_split(**split_kwargs)
    except ValueError:
        split_kwargs.pop("stratify_by_column", None)
        split = dataset.train_test_split(**split_kwargs)

    return {"train": split["train"], "validation": split["test"]}
