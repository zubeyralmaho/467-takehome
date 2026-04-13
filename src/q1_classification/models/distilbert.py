"""DistilBERT classifier for Q1 text classification."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset

from src.common.seed import worker_init_fn

try:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup
except ImportError:  # pragma: no cover - optional dependency during bootstrap
    AutoModelForSequenceClassification = None
    AutoTokenizer = None
    get_linear_schedule_with_warmup = None


@dataclass(frozen=True)
class EncodedBatch:
    input_ids: torch.Tensor
    attention_mask: torch.Tensor
    labels: torch.Tensor | None


class EncodedTextDataset(Dataset):
    """Dataset backed by a tokenizer output dictionary."""

    def __init__(
        self,
        tokenizer,
        texts: Sequence[str],
        max_length: int,
        labels: Sequence[int] | None = None,
    ):
        encodings = tokenizer(
            list(texts),
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        self.input_ids = encodings["input_ids"]
        self.attention_mask = encodings["attention_mask"]
        self.labels = None if labels is None else torch.tensor([int(label) for label in labels], dtype=torch.long)

    def __len__(self) -> int:
        return int(self.input_ids.size(0))

    def __getitem__(self, index: int) -> EncodedBatch:
        labels = None if self.labels is None else self.labels[index]
        return EncodedBatch(
            input_ids=self.input_ids[index],
            attention_mask=self.attention_mask[index],
            labels=labels,
        )


def _collate_batch(batch: list[EncodedBatch]) -> dict[str, torch.Tensor | None]:
    input_ids = torch.stack([item.input_ids for item in batch])
    attention_mask = torch.stack([item.attention_mask for item in batch])

    labels = None
    if batch and batch[0].labels is not None:
        labels = torch.stack([item.labels for item in batch if item.labels is not None])

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
    }


class DistilBERTClassifier:
    """Transformers-based DistilBERT wrapper with a scikit-like interface."""

    def __init__(
        self,
        model_name: str = "distilbert-base-uncased",
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        weight_decay: float = 0.01,
        max_epochs: int = 3,
        early_stopping_patience: int = 2,
        max_seq_length: int = 256,
        warmup_ratio: float = 0.1,
        monitor_metric: str = "macro_f1",
        num_workers: int = 0,
        device: str = "auto",
        seed: int = 42,
    ):
        self._ensure_transformers_available()

        self.model_name = model_name
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.max_epochs = max_epochs
        self.early_stopping_patience = early_stopping_patience
        self.max_seq_length = max_seq_length
        self.warmup_ratio = warmup_ratio
        self.monitor_metric = monitor_metric
        self.num_workers = num_workers
        self.seed = seed
        self.device = self._resolve_device(device)

        self.tokenizer = None
        self.model = None

    @staticmethod
    def _ensure_transformers_available() -> None:
        if AutoModelForSequenceClassification is None or AutoTokenizer is None or get_linear_schedule_with_warmup is None:
            raise ImportError(
                "DistilBERT support requires the 'transformers' package. Install dependencies from requirements.txt."
            )

    @staticmethod
    def _resolve_device(device: str) -> torch.device:
        if device != "auto":
            return torch.device(device)
        if torch.cuda.is_available():
            return torch.device("cuda")
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    def _require_fitted(self):
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("DistilBERTClassifier must be fit before inference.")
        return self.model, self.tokenizer

    def _create_dataloader(
        self,
        texts: Sequence[str],
        labels: Sequence[int] | None,
        shuffle: bool,
    ) -> DataLoader:
        _, tokenizer = self._require_fitted()
        dataset = EncodedTextDataset(
            tokenizer=tokenizer,
            texts=texts,
            labels=labels,
            max_length=self.max_seq_length,
        )
        generator = torch.Generator()
        generator.manual_seed(self.seed)

        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=shuffle,
            num_workers=self.num_workers,
            collate_fn=_collate_batch,
            worker_init_fn=worker_init_fn if self.num_workers > 0 else None,
            generator=generator,
        )

    def _validation_score(self, references: Sequence[int], predictions: Sequence[int]) -> float:
        if self.monitor_metric == "accuracy":
            return float(accuracy_score(references, predictions))
        if self.monitor_metric == "macro_f1":
            return float(f1_score(references, predictions, average="macro"))
        raise ValueError(f"Unsupported monitor_metric: {self.monitor_metric}")

    def fit(self, texts: Sequence[str], labels: Sequence[int], validation_data: dict[str, list] | None = None) -> None:
        labels = [int(label) for label in labels]
        num_classes = max(labels) + 1

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=num_classes,
        ).to(self.device)

        optimizer = AdamW(self.model.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay)
        train_loader = self._create_dataloader(texts, labels, shuffle=True)
        validation_loader = None
        if validation_data is not None:
            validation_loader = self._create_dataloader(
                validation_data["texts"],
                validation_data["labels"],
                shuffle=False,
            )

        total_steps = max(len(train_loader) * self.max_epochs, 1)
        warmup_steps = int(total_steps * self.warmup_ratio)
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps,
        )

        best_state = deepcopy(self.model.state_dict())
        best_score = float("-inf")
        epochs_without_improvement = 0

        for _ in range(self.max_epochs):
            self.model.train()
            for batch in train_loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                batch_labels = batch["labels"]
                if batch_labels is None:
                    continue
                batch_labels = batch_labels.to(self.device)

                optimizer.zero_grad(set_to_none=True)
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=batch_labels,
                )
                outputs.loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()
                scheduler.step()

            if validation_loader is None:
                best_state = deepcopy(self.model.state_dict())
                continue

            predictions, _, references = self._predict_with_references(validation_loader)
            validation_score = self._validation_score(references, predictions)

            if validation_score > best_score + 1e-6:
                best_score = validation_score
                best_state = deepcopy(self.model.state_dict())
                epochs_without_improvement = 0
                continue

            epochs_without_improvement += 1
            if epochs_without_improvement >= self.early_stopping_patience:
                break

        self.model.load_state_dict(best_state)

    def _predict_with_references(self, data_loader: DataLoader) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        model, _ = self._require_fitted()
        model.eval()

        probability_batches: list[np.ndarray] = []
        references: list[np.ndarray] = []
        with torch.no_grad():
            for batch in data_loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                probabilities = torch.softmax(outputs.logits, dim=1).cpu().numpy()
                probability_batches.append(probabilities)

                batch_labels = batch["labels"]
                if batch_labels is not None:
                    references.append(batch_labels.cpu().numpy())

        stacked_probabilities = np.concatenate(probability_batches, axis=0)
        predictions = stacked_probabilities.argmax(axis=1)
        stacked_references = np.concatenate(references, axis=0) if references else np.empty((0,), dtype=int)
        return predictions, stacked_probabilities, stacked_references

    def predict(self, texts: Sequence[str]) -> np.ndarray:
        probabilities = self.predict_proba(texts)
        return probabilities.argmax(axis=1)

    def predict_proba(self, texts: Sequence[str]) -> np.ndarray:
        model, tokenizer = self._require_fitted()
        dataset = EncodedTextDataset(
            tokenizer=tokenizer,
            texts=texts,
            labels=None,
            max_length=self.max_seq_length,
        )
        data_loader = DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            collate_fn=_collate_batch,
            worker_init_fn=worker_init_fn if self.num_workers > 0 else None,
        )

        model.eval()
        probability_batches: list[np.ndarray] = []
        with torch.no_grad():
            for batch in data_loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                probability_batches.append(torch.softmax(outputs.logits, dim=1).cpu().numpy())
        return np.concatenate(probability_batches, axis=0)

    def predict_confidence(self, texts: Sequence[str]) -> list[float | None]:
        probabilities = self.predict_proba(texts)
        return probabilities.max(axis=1).astype(float).tolist()