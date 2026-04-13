"""Dataset helpers for Q3 summarization."""

from __future__ import annotations

from src.common.data_utils import load_hf_dataset, subsample
from src.q3_summarization.preprocess import clean_article, truncate_article


def load_q3_splits(config) -> dict[str, object]:
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

    splits: dict[str, object] = {
        "dataset_source": dataset_source,
        "split_sizes": {},
    }
    for split_name in ["train", "validation", "test"]:
        if split_name not in dataset:
            continue
        sampled_split = subsample(dataset[split_name], split_limits[split_name], seed=config.seed)
        splits[split_name] = sampled_split
        splits["split_sizes"][split_name] = len(sampled_split)
    return splits


def materialize_split(split, config) -> dict[str, list[str]]:
    article_column = config.dataset.article_column
    summary_column = config.dataset.summary_column
    id_column = getattr(config.dataset, "id_column", None)

    articles: list[str] = []
    references: list[str] = []
    example_ids: list[str] = []

    for index, example in enumerate(split):
        article = truncate_article(
            clean_article(example[article_column]),
            max_words=config.preprocess.max_article_words,
        )
        reference = clean_article(example[summary_column])
        example_id = str(example[id_column]) if id_column and id_column in example else str(index)

        articles.append(article)
        references.append(reference)
        example_ids.append(example_id)

    return {
        "ids": example_ids,
        "articles": articles,
        "references": references,
    }


def prepare_datasets(config) -> dict[str, object]:
    raw_splits = load_q3_splits(config)
    prepared: dict[str, object] = {
        "dataset_source": raw_splits["dataset_source"],
        "split_sizes": raw_splits["split_sizes"],
    }
    for split_name in ["train", "validation", "test"]:
        if split_name not in raw_splits:
            continue
        prepared[split_name] = materialize_split(raw_splits[split_name], config)
    return prepared