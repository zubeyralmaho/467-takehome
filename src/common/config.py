"""Configuration loading and merge utilities."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml


def _deep_merge(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _set_nested_value(target: dict[str, Any], path: str, value: Any) -> None:
    cursor = target
    keys = path.split(".")
    for key in keys[:-1]:
        child = cursor.get(key)
        if not isinstance(child, dict):
            child = {}
            cursor[key] = child
        cursor = child
    cursor[keys[-1]] = value


def parse_cli_overrides(overrides: Iterable[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for item in overrides:
        if "=" not in item:
            raise ValueError(f"Invalid override '{item}'. Expected key=value.")
        key, raw_value = item.split("=", 1)
        value = yaml.safe_load(raw_value)
        _set_nested_value(parsed, key, value)
    return parsed


class Config:
    """Nested dot-access configuration object."""

    def __init__(self, data: Mapping[str, Any]):
        object.__setattr__(self, "_data", {})
        for key, value in data.items():
            self._data[key] = self._wrap(value)

    @staticmethod
    def _wrap(value: Any) -> Any:
        if isinstance(value, Mapping):
            return Config(value)
        if isinstance(value, list):
            return [Config._wrap(item) for item in value]
        return value

    @staticmethod
    def from_yaml(path: str | Path) -> "Config":
        with Path(path).open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return Config(data)

    def merge(self, override: Mapping[str, Any]) -> "Config":
        return Config(_deep_merge(self.to_dict(), override))

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in self._data.items():
            if isinstance(value, Config):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [item.to_dict() if isinstance(item, Config) else item for item in value]
            else:
                result[key] = value
        return result

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(self.to_dict(), handle, sort_keys=False)

    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError as error:
            raise AttributeError(name) from error

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __repr__(self) -> str:
        return f"Config({self.to_dict()!r})"


def load_config(config_path: str | Path, cli_overrides: Iterable[str] | Mapping[str, Any] | None = None) -> Config:
    config_path = Path(config_path)
    base_path = config_path.parent / "base.yaml"

    merged: dict[str, Any] = {}
    if base_path.exists():
        merged = Config.from_yaml(base_path).to_dict()

    question_config = Config.from_yaml(config_path).to_dict()
    merged = _deep_merge(merged, question_config)

    if cli_overrides:
        overrides = parse_cli_overrides(cli_overrides) if not isinstance(cli_overrides, Mapping) else dict(cli_overrides)
        merged = _deep_merge(merged, overrides)

    return Config(merged)
