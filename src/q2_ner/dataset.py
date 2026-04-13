"""Dataset helpers for Q2 named entity recognition."""

from __future__ import annotations

from src.common.data_utils import load_hf_dataset, subsample
from src.q2_ner.preprocess import labels_from_ids


SCRIPT_DATASET_ERROR_FRAGMENT = "Dataset scripts are no longer supported"


def _candidate_dataset_names(config) -> list[str]:
    candidates = [config.dataset.name]
    fallback_name = getattr(config.dataset, "fallback_name", None)
    if fallback_name and fallback_name not in candidates:
        candidates.append(fallback_name)
    return candidates


def _load_dataset_with_fallback(config):
    last_error: Exception | None = None
    for dataset_name in _candidate_dataset_names(config):
        try:
            dataset = load_hf_dataset(dataset_name, cache_dir=config.data.cache_dir)
            return dataset, dataset_name
        except RuntimeError as error:
            last_error = error
            if SCRIPT_DATASET_ERROR_FRAGMENT not in str(error):
                raise

    tried_names = ", ".join(_candidate_dataset_names(config))
    raise RuntimeError(f"Unable to load a CoNLL-2003 dataset from: {tried_names}") from last_error


def _resolve_label_names(split, label_column: str) -> list[str]:
    label_feature = split.features[label_column]
    base_feature = getattr(label_feature, "feature", label_feature)
    names = getattr(base_feature, "names", None)
    if not names:
        raise ValueError(f"Label column '{label_column}' does not expose class label names.")
    return list(names)


def load_q2_splits(config) -> dict[str, object]:
    dataset, dataset_source = _load_dataset_with_fallback(config)
    label_names = _resolve_label_names(dataset["train"], config.dataset.label_column)

    split_limits = {
        "train": getattr(config.dataset, "limit_train_samples", None),
        "validation": getattr(config.dataset, "limit_validation_samples", None),
        "test": getattr(config.dataset, "limit_test_samples", None),
    }

    splits: dict[str, object] = {
        "dataset_source": dataset_source,
        "label_names": label_names,
    }
    for split_name, split in dataset.items():
        splits[split_name] = subsample(split, split_limits.get(split_name), seed=config.seed)

    return splits


def materialize_split(split, token_column: str, label_column: str, label_names: list[str]) -> dict[str, list[list[str]]]:
    tokens = [list(sentence_tokens) for sentence_tokens in split[token_column]]
    labels = [labels_from_ids(sentence_labels, label_names) for sentence_labels in split[label_column]]
    return {"tokens": tokens, "labels": labels}


def prepare_datasets(config) -> dict[str, object]:
    raw_splits = load_q2_splits(config)
    label_names = raw_splits["label_names"]
    prepared: dict[str, object] = {
        "dataset_source": raw_splits["dataset_source"],
        "label_names": label_names,
        "split_sizes": {},
    }

    for split_name in ["train", "validation", "test"]:
        if split_name not in raw_splits:
            continue
        materialized = materialize_split(
            raw_splits[split_name],
            token_column=config.dataset.token_column,
            label_column=config.dataset.label_column,
            label_names=label_names,
        )
        prepared[split_name] = materialized
        prepared["split_sizes"][split_name] = len(materialized["tokens"])

    return prepared