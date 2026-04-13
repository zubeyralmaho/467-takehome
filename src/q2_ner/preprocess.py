"""Preprocessing and feature extraction utilities for Q2 NER."""

from __future__ import annotations

from typing import Sequence


def labels_from_ids(label_ids: Sequence[int], label_names: Sequence[str]) -> list[str]:
    return [str(label_names[int(label_id)]) for label_id in label_ids]


def _token_features(tokens: Sequence[str], index: int) -> dict[str, object]:
    token = tokens[index]
    features: dict[str, object] = {
        "bias": 1.0,
        "word.lower": token.lower(),
        "word[-3:]": token[-3:],
        "word[-2:]": token[-2:],
        "word[:3]": token[:3],
        "word[:2]": token[:2],
        "word.isupper": token.isupper(),
        "word.istitle": token.istitle(),
        "word.isdigit": token.isdigit(),
        "word.has_hyphen": "-" in token,
        "word.length": len(token),
    }

    if index > 0:
        previous = tokens[index - 1]
        features.update(
            {
                "-1:word.lower": previous.lower(),
                "-1:word.istitle": previous.istitle(),
                "-1:word.isupper": previous.isupper(),
            }
        )
    else:
        features["BOS"] = True

    if index < len(tokens) - 1:
        following = tokens[index + 1]
        features.update(
            {
                "+1:word.lower": following.lower(),
                "+1:word.istitle": following.istitle(),
                "+1:word.isupper": following.isupper(),
            }
        )
    else:
        features["EOS"] = True

    return features


def extract_features_for_crf(tokens: Sequence[str]) -> list[dict[str, object]]:
    return [_token_features(tokens, index) for index in range(len(tokens))]