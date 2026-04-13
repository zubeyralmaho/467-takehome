"""BiLSTM-CRF baseline for Q2 named entity recognition."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from typing import Sequence

import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence, pad_sequence
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset

from src.common.seed import worker_init_fn
from src.q2_ner.evaluation import evaluate_predictions

try:
    from torchcrf import CRF
except ImportError:  # pragma: no cover - optional dependency during bootstrap
    CRF = None

PAD_TOKEN = "<pad>"
UNK_TOKEN = "<unk>"


@dataclass(frozen=True)
class Vocabulary:
    """Vocabulary for mapping token sequences to integer ids."""

    token_to_id: dict[str, int]
    id_to_token: list[str]
    pad_id: int
    unk_id: int

    @classmethod
    def build(
        cls,
        token_sequences: Sequence[Sequence[str]],
        max_vocab_size: int | None = None,
        min_frequency: int = 1,
    ) -> "Vocabulary":
        counter: Counter[str] = Counter()
        for sequence in token_sequences:
            counter.update(sequence)

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

    def encode(self, tokens: Sequence[str]) -> list[int]:
        if not tokens:
            return [self.unk_id]
        return [self.token_to_id.get(token, self.unk_id) for token in tokens]


class EncodedSequenceDataset(Dataset):
    """Dataset of variable-length token and label id sequences."""

    def __init__(
        self,
        token_sequences: Sequence[Sequence[str]],
        vocabulary: Vocabulary,
        label_to_id: dict[str, int],
        labels: Sequence[Sequence[str]] | None = None,
    ):
        self.input_ids = [torch.tensor(vocabulary.encode(sequence), dtype=torch.long) for sequence in token_sequences]
        self.label_ids = None
        if labels is not None:
            self.label_ids = [
                torch.tensor([label_to_id[label] for label in sequence], dtype=torch.long)
                for sequence in labels
            ]

    def __len__(self) -> int:
        return len(self.input_ids)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor | None]:
        label_ids = None if self.label_ids is None else self.label_ids[index]
        return self.input_ids[index], label_ids


class BatchCollator:
    """Pads variable-length token and tag sequences to the batch maximum."""

    def __init__(self, pad_id: int, pad_label_id: int):
        self.pad_id = pad_id
        self.pad_label_id = pad_label_id

    def __call__(self, batch: list[tuple[torch.Tensor, torch.Tensor | None]]) -> dict[str, torch.Tensor | None]:
        sequences = [sequence for sequence, _ in batch]
        input_ids = pad_sequence(sequences, batch_first=True, padding_value=self.pad_id)
        lengths = torch.tensor([sequence.size(0) for sequence in sequences], dtype=torch.long)
        mask = torch.arange(input_ids.size(1)).unsqueeze(0) < lengths.unsqueeze(1)

        labels = None
        if batch and batch[0][1] is not None:
            labels = pad_sequence(
                [label for _, label in batch if label is not None],
                batch_first=True,
                padding_value=self.pad_label_id,
            )

        return {
            "input_ids": input_ids,
            "lengths": lengths,
            "mask": mask,
            "labels": labels,
        }


class _BiLSTMCRFNetwork(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int,
        hidden_dim: int,
        num_layers: int,
        dropout: float,
        num_tags: int,
        pad_id: int,
    ):
        super().__init__()
        if CRF is None:
            raise ImportError(
                "BiLSTM-CRF support requires the 'pytorch-crf' package. Install dependencies from requirements.txt."
            )

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
        self.classifier = nn.Linear(hidden_dim * 2, num_tags)
        self.crf = CRF(num_tags, batch_first=True)

    def emissions(self, input_ids: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(input_ids)
        packed = pack_padded_sequence(embedded, lengths.cpu(), batch_first=True, enforce_sorted=False)
        packed_output, _ = self.encoder(packed)
        encoded, _ = pad_packed_sequence(packed_output, batch_first=True, total_length=input_ids.size(1))
        return self.classifier(self.dropout(encoded))

    def loss(self, input_ids: torch.Tensor, lengths: torch.Tensor, tags: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        emissions = self.emissions(input_ids, lengths)
        return -self.crf(emissions, tags, mask=mask, reduction="mean")

    def decode(self, input_ids: torch.Tensor, lengths: torch.Tensor, mask: torch.Tensor) -> tuple[torch.Tensor, list[list[int]]]:
        emissions = self.emissions(input_ids, lengths)
        return emissions, self.crf.decode(emissions, mask=mask)


class BiLSTMCRFTagger:
    """PyTorch BiLSTM-CRF wrapper with a scikit-like fit/predict interface."""

    def __init__(
        self,
        label_names: Sequence[str],
        embedding_dim: int = 100,
        hidden_dim: int = 128,
        num_layers: int = 1,
        dropout: float = 0.3,
        batch_size: int = 32,
        learning_rate: float = 1e-3,
        weight_decay: float = 0.0,
        max_epochs: int = 8,
        early_stopping_patience: int = 2,
        max_vocab_size: int | None = 30000,
        min_frequency: int = 1,
        num_workers: int = 0,
        monitor_metric: str = "f1",
        device: str = "auto",
        seed: int = 42,
    ):
        self.label_names = [str(label) for label in label_names]
        self.label_to_id = {label: index for index, label in enumerate(self.label_names)}
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.max_epochs = max_epochs
        self.early_stopping_patience = early_stopping_patience
        self.max_vocab_size = max_vocab_size
        self.min_frequency = min_frequency
        self.num_workers = num_workers
        self.monitor_metric = monitor_metric
        self.seed = seed
        self.device = self._resolve_device(device)

        self.pad_label_id = self.label_to_id.get("O", 0)
        self.vocabulary: Vocabulary | None = None
        self.model: _BiLSTMCRFNetwork | None = None

    @staticmethod
    def _resolve_device(device: str) -> torch.device:
        if device != "auto":
            return torch.device(device)
        if torch.cuda.is_available():
            return torch.device("cuda")
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    def _require_fitted(self) -> tuple[_BiLSTMCRFNetwork, Vocabulary]:
        if self.model is None or self.vocabulary is None:
            raise RuntimeError("BiLSTMCRFTagger must be fit before inference.")
        return self.model, self.vocabulary

    def _create_dataloader(
        self,
        token_sequences: Sequence[Sequence[str]],
        labels: Sequence[Sequence[str]] | None,
        vocabulary: Vocabulary,
        shuffle: bool,
    ) -> DataLoader:
        dataset = EncodedSequenceDataset(
            token_sequences=token_sequences,
            vocabulary=vocabulary,
            label_to_id=self.label_to_id,
            labels=labels,
        )
        generator = torch.Generator()
        generator.manual_seed(self.seed)

        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=shuffle,
            num_workers=self.num_workers,
            collate_fn=BatchCollator(vocabulary.pad_id, self.pad_label_id),
            worker_init_fn=worker_init_fn if self.num_workers > 0 else None,
            generator=generator,
        )

    def _validation_score(self, references: Sequence[Sequence[str]], predictions: Sequence[Sequence[str]]) -> float:
        metrics = evaluate_predictions(predictions, references, metrics=[self.monitor_metric])["metrics"]
        if self.monitor_metric not in metrics:
            raise ValueError(f"Unsupported monitor_metric: {self.monitor_metric}")
        return float(metrics[self.monitor_metric])

    def fit(
        self,
        token_sequences: Sequence[Sequence[str]],
        label_sequences: Sequence[Sequence[str]],
        validation_data: dict[str, list] | None = None,
    ) -> None:
        self.vocabulary = Vocabulary.build(
            token_sequences=token_sequences,
            max_vocab_size=self.max_vocab_size,
            min_frequency=self.min_frequency,
        )
        self.model = _BiLSTMCRFNetwork(
            vocab_size=len(self.vocabulary.id_to_token),
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
            dropout=self.dropout,
            num_tags=len(self.label_names),
            pad_id=self.vocabulary.pad_id,
        ).to(self.device)

        optimizer = AdamW(self.model.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay)
        train_loader = self._create_dataloader(token_sequences, label_sequences, self.vocabulary, shuffle=True)

        best_state = deepcopy(self.model.state_dict())
        best_score = float("-inf")
        epochs_without_improvement = 0

        for _ in range(self.max_epochs):
            self.model.train()
            for batch in train_loader:
                input_ids = batch["input_ids"].to(self.device)
                lengths = batch["lengths"]
                mask = batch["mask"].to(self.device)
                labels = batch["labels"]
                if labels is None:
                    continue
                labels = labels.to(self.device)

                optimizer.zero_grad(set_to_none=True)
                loss = self.model.loss(input_ids, lengths, labels, mask)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=5.0)
                optimizer.step()

            if validation_data is None:
                best_state = deepcopy(self.model.state_dict())
                continue

            predictions = self.predict(validation_data["tokens"])
            validation_score = self._validation_score(validation_data["labels"], predictions)

            if validation_score > best_score + 1e-6:
                best_score = validation_score
                best_state = deepcopy(self.model.state_dict())
                epochs_without_improvement = 0
                continue

            epochs_without_improvement += 1
            if epochs_without_improvement >= self.early_stopping_patience:
                break

        self.model.load_state_dict(best_state)

    def _predict_sequences(
        self,
        token_sequences: Sequence[Sequence[str]],
        return_confidences: bool,
    ) -> tuple[list[list[str]], list[list[float | None]] | None]:
        model, vocabulary = self._require_fitted()
        if not token_sequences:
            return [], [] if return_confidences else None

        data_loader = self._create_dataloader(token_sequences, labels=None, vocabulary=vocabulary, shuffle=False)
        model.eval()

        predictions: list[list[str]] = []
        confidences: list[list[float | None]] = []
        with torch.no_grad():
            for batch in data_loader:
                input_ids = batch["input_ids"].to(self.device)
                lengths = batch["lengths"]
                mask = batch["mask"].to(self.device)

                emissions, decoded_sequences = model.decode(input_ids, lengths, mask)
                probability_tensor = torch.softmax(emissions, dim=-1).cpu()
                batch_mask = batch["mask"]

                for decoded_ids, token_probabilities, token_mask in zip(
                    decoded_sequences,
                    probability_tensor,
                    batch_mask,
                    strict=False,
                ):
                    valid_length = int(token_mask.sum().item())
                    decoded_ids = list(decoded_ids)[:valid_length]
                    predictions.append([self.label_names[tag_id] for tag_id in decoded_ids])

                    if return_confidences:
                        confidences.append(
                            [
                                float(token_probabilities[position, tag_id])
                                for position, tag_id in enumerate(decoded_ids)
                            ]
                        )

        return predictions, confidences if return_confidences else None

    def predict(self, token_sequences: Sequence[Sequence[str]]) -> list[list[str]]:
        predictions, _ = self._predict_sequences(token_sequences, return_confidences=False)
        return predictions

    def predict_token_confidences(
        self,
        token_sequences: Sequence[Sequence[str]],
        predictions: Sequence[Sequence[str]] | None = None,
    ) -> list[list[float | None]]:
        del predictions
        _, confidences = self._predict_sequences(token_sequences, return_confidences=True)
        return confidences or []