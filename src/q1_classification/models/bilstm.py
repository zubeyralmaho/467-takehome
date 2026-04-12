"""BiLSTM classifier for Q1 text classification."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_sequence
from torch.utils.data import DataLoader, Dataset

from src.common.seed import worker_init_fn

PAD_TOKEN = "<pad>"
UNK_TOKEN = "<unk>"


@dataclass(frozen=True)
class Vocabulary:
    """Vocabulary for mapping preprocessed word tokens to integer ids."""

    token_to_id: dict[str, int]
    id_to_token: list[str]
    pad_id: int
    unk_id: int

    @classmethod
    def build(
        cls,
        texts: Sequence[str],
        max_vocab_size: int | None = None,
        min_frequency: int = 1,
    ) -> "Vocabulary":
        counter: Counter[str] = Counter()
        for text in texts:
            counter.update(text.split())

        tokens = [PAD_TOKEN, UNK_TOKEN]
        limit = None if max_vocab_size is None else max(max_vocab_size - len(tokens), 0)

        for token, frequency in counter.most_common(limit):
            if frequency < min_frequency:
                continue
            if token in {PAD_TOKEN, UNK_TOKEN}:
                continue
            tokens.append(token)

        token_to_id = {token: index for index, token in enumerate(tokens)}
        return cls(
            token_to_id=token_to_id,
            id_to_token=tokens,
            pad_id=token_to_id[PAD_TOKEN],
            unk_id=token_to_id[UNK_TOKEN],
        )

    def encode(self, text: str, max_length: int | None = None) -> list[int]:
        tokens = text.split()
        if max_length:
            tokens = tokens[:max_length]
        if not tokens:
            return [self.unk_id]
        return [self.token_to_id.get(token, self.unk_id) for token in tokens]


class EncodedTextDataset(Dataset):
    """Dataset of variable-length token id sequences."""

    def __init__(
        self,
        texts: Sequence[str],
        vocabulary: Vocabulary,
        max_length: int | None,
        labels: Sequence[int] | None = None,
    ):
        self.encoded_texts = [
            torch.tensor(vocabulary.encode(text, max_length=max_length), dtype=torch.long)
            for text in texts
        ]
        self.labels = None if labels is None else [int(label) for label in labels]

    def __len__(self) -> int:
        return len(self.encoded_texts)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int | None]:
        label = None if self.labels is None else self.labels[index]
        return self.encoded_texts[index], label


class BatchCollator:
    """Pads variable-length sequences to the longest example in a batch."""

    def __init__(self, pad_id: int):
        self.pad_id = pad_id

    def __call__(self, batch: list[tuple[torch.Tensor, int | None]]) -> dict[str, torch.Tensor | None]:
        sequences = [sequence for sequence, _ in batch]
        padded = pad_sequence(sequences, batch_first=True, padding_value=self.pad_id)
        lengths = torch.tensor([sequence.size(0) for sequence in sequences], dtype=torch.long)

        labels = None
        if batch and batch[0][1] is not None:
            labels = torch.tensor([label for _, label in batch], dtype=torch.long)

        return {
            "input_ids": padded,
            "lengths": lengths,
            "labels": labels,
        }


class _BiLSTMNetwork(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int,
        hidden_dim: int,
        num_layers: int,
        dropout: float,
        num_classes: int,
        pad_id: int,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=pad_id)
        self.encoder = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,
            bidirectional=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, input_ids: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(input_ids)
        packed = pack_padded_sequence(embedded, lengths.cpu(), batch_first=True, enforce_sorted=False)
        _, (hidden_state, _) = self.encoder(packed)
        features = torch.cat((hidden_state[-2], hidden_state[-1]), dim=1)
        return self.classifier(self.dropout(features))


class BiLSTMClassifier:
    """PyTorch BiLSTM wrapper with a scikit-like fit/predict interface."""

    def __init__(
        self,
        embedding_dim: int = 128,
        hidden_dim: int = 128,
        num_layers: int = 1,
        dropout: float = 0.3,
        batch_size: int = 64,
        learning_rate: float = 1e-3,
        max_epochs: int = 6,
        early_stopping_patience: int = 2,
        max_vocab_size: int | None = 30000,
        min_frequency: int = 2,
        max_seq_length: int = 256,
        weight_decay: float = 0.0,
        monitor_metric: str = "macro_f1",
        num_workers: int = 0,
        device: str = "auto",
        seed: int = 42,
    ):
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.max_epochs = max_epochs
        self.early_stopping_patience = early_stopping_patience
        self.max_vocab_size = max_vocab_size
        self.min_frequency = min_frequency
        self.max_seq_length = max_seq_length
        self.weight_decay = weight_decay
        self.monitor_metric = monitor_metric
        self.num_workers = num_workers
        self.seed = seed
        self.device = self._resolve_device(device)

        self.vocabulary: Vocabulary | None = None
        self.model: _BiLSTMNetwork | None = None

    @staticmethod
    def _resolve_device(device: str) -> torch.device:
        if device != "auto":
            return torch.device(device)
        if torch.cuda.is_available():
            return torch.device("cuda")
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    def _require_fitted(self) -> tuple[_BiLSTMNetwork, Vocabulary]:
        if self.model is None or self.vocabulary is None:
            raise RuntimeError("BiLSTMClassifier must be fit before inference.")
        return self.model, self.vocabulary

    def _create_dataloader(
        self,
        texts: Sequence[str],
        labels: Sequence[int] | None,
        vocabulary: Vocabulary,
        shuffle: bool,
    ) -> DataLoader:
        dataset = EncodedTextDataset(
            texts=texts,
            labels=labels,
            vocabulary=vocabulary,
            max_length=self.max_seq_length,
        )
        generator = torch.Generator()
        generator.manual_seed(self.seed)

        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=shuffle,
            num_workers=self.num_workers,
            collate_fn=BatchCollator(vocabulary.pad_id),
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
        self.vocabulary = Vocabulary.build(
            texts=texts,
            max_vocab_size=self.max_vocab_size,
            min_frequency=self.min_frequency,
        )
        self.model = _BiLSTMNetwork(
            vocab_size=len(self.vocabulary.id_to_token),
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
            dropout=self.dropout,
            num_classes=num_classes,
            pad_id=self.vocabulary.pad_id,
        ).to(self.device)

        optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay,
        )
        criterion = nn.CrossEntropyLoss()

        train_loader = self._create_dataloader(texts, labels, self.vocabulary, shuffle=True)
        validation_loader = None
        if validation_data is not None:
            validation_loader = self._create_dataloader(
                validation_data["texts"],
                validation_data["labels"],
                self.vocabulary,
                shuffle=False,
            )

        best_state = deepcopy(self.model.state_dict())
        best_score = float("-inf")
        epochs_without_improvement = 0

        for _ in range(self.max_epochs):
            self.model.train()
            for batch in train_loader:
                input_ids = batch["input_ids"].to(self.device)
                lengths = batch["lengths"]
                batch_labels = batch["labels"]
                if batch_labels is None:
                    continue
                batch_labels = batch_labels.to(self.device)

                optimizer.zero_grad(set_to_none=True)
                logits = self.model(input_ids, lengths)
                loss = criterion(logits, batch_labels)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()

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
                lengths = batch["lengths"]
                logits = model(input_ids, lengths)
                probabilities = torch.softmax(logits, dim=1).cpu().numpy()
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
        model, vocabulary = self._require_fitted()
        if not texts:
            return np.empty((0, model.classifier.out_features), dtype=float)

        data_loader = self._create_dataloader(texts, labels=None, vocabulary=vocabulary, shuffle=False)
        model.eval()

        probability_batches: list[np.ndarray] = []
        with torch.no_grad():
            for batch in data_loader:
                input_ids = batch["input_ids"].to(self.device)
                lengths = batch["lengths"]
                logits = model(input_ids, lengths)
                probability_batches.append(torch.softmax(logits, dim=1).cpu().numpy())

        return np.concatenate(probability_batches, axis=0)

    def predict_confidence(self, texts: Sequence[str]) -> list[float | None]:
        probabilities = self.predict_proba(texts)
        return probabilities.max(axis=1).astype(float).tolist()