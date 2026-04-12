"""Dataset helpers for Q1."""

from __future__ import annotations

from src.common.data_utils import create_splits, load_hf_dataset, subsample
from src.q1_classification.preprocess import TextPreprocessor


def load_q1_splits(config) -> dict[str, object]:
    dataset = load_hf_dataset(config.dataset.name, cache_dir=config.data.cache_dir)

    train_split = subsample(dataset["train"], config.dataset.limit_train_samples, seed=config.seed)
    test_split = subsample(dataset["test"], config.dataset.limit_test_samples, seed=config.seed)

    split = create_splits(
        train_split,
        val_ratio=config.dataset.val_split_ratio,
        seed=config.seed,
        label_column=config.dataset.label_column,
    )
    split["test"] = test_split
    return split


def materialize_split(split, text_column: str, label_column: str, preprocessor: TextPreprocessor) -> dict[str, list]:
    texts = [preprocessor(text) for text in split[text_column]]
    labels = [int(label) for label in split[label_column]]
    return {"texts": texts, "labels": labels}


def prepare_datasets(config) -> dict[str, dict[str, list]]:
    preprocessor = TextPreprocessor(config, max_length=None)
    raw_splits = load_q1_splits(config)
    return {
        split_name: materialize_split(
            split,
            text_column=config.dataset.text_column,
            label_column=config.dataset.label_column,
            preprocessor=preprocessor,
        )
        for split_name, split in raw_splits.items()
    }
