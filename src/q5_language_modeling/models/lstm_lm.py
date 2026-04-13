"""LSTM language model for Q5."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass
import math

import torch
from torch import nn
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, Dataset

from src.common.seed import worker_init_fn

PAD_TOKEN = "<pad>"
UNK_TOKEN = "<unk>"
BOS_TOKEN = "<bos>"
EOS_TOKEN = "<eos>"


@dataclass(frozen=True)
class Vocabulary:
    token_to_id: dict[str, int]
    id_to_token: list[str]
    pad_id: int
    unk_id: int
    bos_id: int
    eos_id: int

    @classmethod
    def build(
        cls,
        token_sequences: Sequence[Sequence[str]],
        max_vocab_size: int | None = None,
        min_frequency: int = 1,
    ) -> "Vocabulary":
        counter: Counter[str] = Counter()
        for token_sequence in token_sequences:
            counter.update(token_sequence)

        tokens = [PAD_TOKEN, UNK_TOKEN, BOS_TOKEN, EOS_TOKEN]
        limit = None if max_vocab_size is None else max(max_vocab_size - len(tokens), 0)

        for token, frequency in counter.most_common(limit):
            if frequency < min_frequency:
                continue
            if token in {PAD_TOKEN, UNK_TOKEN, BOS_TOKEN, EOS_TOKEN}:
                continue
            tokens.append(token)

        token_to_id = {token: index for index, token in enumerate(tokens)}
        return cls(
            token_to_id=token_to_id,
            id_to_token=tokens,
            pad_id=token_to_id[PAD_TOKEN],
            unk_id=token_to_id[UNK_TOKEN],
            bos_id=token_to_id[BOS_TOKEN],
            eos_id=token_to_id[EOS_TOKEN],
        )

    def encode(self, token_sequence: Sequence[str]) -> list[int]:
        if not token_sequence:
            return [self.unk_id]
        return [self.token_to_id.get(token, self.unk_id) for token in token_sequence]


class LanguageModelingDataset(Dataset):
    def __init__(self, token_sequences: Sequence[Sequence[str]], vocabulary: Vocabulary, max_seq_length: int):
        self.inputs: list[torch.Tensor] = []
        self.targets: list[torch.Tensor] = []

        for token_sequence in token_sequences:
            encoded = [vocabulary.bos_id, *vocabulary.encode(token_sequence), vocabulary.eos_id]
            if len(encoded) < 2:
                continue
            for start in range(0, len(encoded) - 1, max_seq_length):
                input_ids = encoded[start : start + max_seq_length]
                target_ids = encoded[start + 1 : start + max_seq_length + 1]
                if not input_ids or not target_ids:
                    continue
                self.inputs.append(torch.tensor(input_ids, dtype=torch.long))
                self.targets.append(torch.tensor(target_ids, dtype=torch.long))

    def __len__(self) -> int:
        return len(self.inputs)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.inputs[index], self.targets[index]


class BatchCollator:
    def __init__(self, pad_id: int):
        self.pad_id = pad_id

    def __call__(self, batch: list[tuple[torch.Tensor, torch.Tensor]]) -> dict[str, torch.Tensor]:
        inputs = [item[0] for item in batch]
        targets = [item[1] for item in batch]
        padded_inputs = pad_sequence(inputs, batch_first=True, padding_value=self.pad_id)
        padded_targets = pad_sequence(targets, batch_first=True, padding_value=self.pad_id)
        return {"input_ids": padded_inputs, "targets": padded_targets}


class _LSTMNetwork(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int,
        hidden_dim: int,
        num_layers: int,
        dropout: float,
        pad_id: int,
        tie_weights: bool,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=pad_id)
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.decoder = nn.Linear(hidden_dim, vocab_size)

        if tie_weights:
            if embedding_dim != hidden_dim:
                raise ValueError("tie_weights requires embedding_dim to match hidden_dim.")
            self.decoder.weight = self.embedding.weight

    def forward(
        self,
        input_ids: torch.Tensor,
        hidden_state: tuple[torch.Tensor, torch.Tensor] | None = None,
    ) -> tuple[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
        embedded = self.embedding(input_ids)
        outputs, hidden_state = self.lstm(embedded, hidden_state)
        logits = self.decoder(self.dropout(outputs))
        return logits, hidden_state


class LSTMLanguageModel:
    def __init__(
        self,
        embedding_dim: int = 128,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2,
        batch_size: int = 32,
        learning_rate: float = 1e-3,
        weight_decay: float = 0.0,
        max_epochs: int = 8,
        early_stopping_patience: int = 2,
        max_seq_length: int = 35,
        max_vocab_size: int | None = 15000,
        min_token_frequency: int = 2,
        tie_weights: bool = True,
        gradient_clip: float = 1.0,
        num_workers: int = 0,
        device: str = "auto",
        seed: int = 42,
    ):
        self.embedding_dim = int(embedding_dim)
        self.hidden_dim = int(hidden_dim)
        self.num_layers = int(num_layers)
        self.dropout = float(dropout)
        self.batch_size = int(batch_size)
        self.learning_rate = float(learning_rate)
        self.weight_decay = float(weight_decay)
        self.max_epochs = int(max_epochs)
        self.early_stopping_patience = int(early_stopping_patience)
        self.max_seq_length = int(max_seq_length)
        self.max_vocab_size = None if max_vocab_size is None else int(max_vocab_size)
        self.min_token_frequency = int(min_token_frequency)
        self.tie_weights = bool(tie_weights)
        self.gradient_clip = float(gradient_clip)
        self.num_workers = int(num_workers)
        self.seed = int(seed)
        self.device = self._resolve_device(device)

        self.vocabulary: Vocabulary | None = None
        self.model: _LSTMNetwork | None = None

    @staticmethod
    def _resolve_device(device: str) -> torch.device:
        if device != "auto":
            return torch.device(device)
        if torch.cuda.is_available():
            return torch.device("cuda")
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    def _require_fitted(self) -> tuple[_LSTMNetwork, Vocabulary]:
        if self.model is None or self.vocabulary is None:
            raise RuntimeError("LSTMLanguageModel must be fit before inference.")
        return self.model, self.vocabulary

    def _create_dataloader(
        self,
        token_sequences: Sequence[Sequence[str]],
        vocabulary: Vocabulary,
        shuffle: bool,
    ) -> DataLoader:
        dataset = LanguageModelingDataset(token_sequences, vocabulary=vocabulary, max_seq_length=self.max_seq_length)
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

    def fit(self, token_sequences: Sequence[Sequence[str]], validation_data: Sequence[Sequence[str]] | None = None) -> None:
        if not token_sequences:
            raise ValueError("At least one training sequence is required for the LSTM language model.")

        self.vocabulary = Vocabulary.build(
            token_sequences=token_sequences,
            max_vocab_size=self.max_vocab_size,
            min_frequency=self.min_token_frequency,
        )
        self.model = _LSTMNetwork(
            vocab_size=len(self.vocabulary.id_to_token),
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
            dropout=self.dropout,
            pad_id=self.vocabulary.pad_id,
            tie_weights=self.tie_weights,
        ).to(self.device)

        train_loader = self._create_dataloader(token_sequences, self.vocabulary, shuffle=True)
        validation_loader = None
        if validation_data:
            validation_loader = self._create_dataloader(validation_data, self.vocabulary, shuffle=False)

        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay)
        train_criterion = nn.CrossEntropyLoss(ignore_index=self.vocabulary.pad_id)

        best_state = deepcopy(self.model.state_dict())
        best_perplexity = float("inf")
        epochs_without_improvement = 0

        for _ in range(self.max_epochs):
            self.model.train()
            for batch in train_loader:
                input_ids = batch["input_ids"].to(self.device)
                targets = batch["targets"].to(self.device)

                optimizer.zero_grad(set_to_none=True)
                logits, _ = self.model(input_ids)
                loss = train_criterion(logits.view(-1, logits.size(-1)), targets.view(-1))
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.gradient_clip)
                optimizer.step()

            if validation_loader is None:
                best_state = deepcopy(self.model.state_dict())
                continue

            validation_perplexity = self._perplexity_from_loader(validation_loader)
            if validation_perplexity + 1e-6 < best_perplexity:
                best_perplexity = validation_perplexity
                best_state = deepcopy(self.model.state_dict())
                epochs_without_improvement = 0
                continue

            epochs_without_improvement += 1
            if epochs_without_improvement >= self.early_stopping_patience:
                break

        self.model.load_state_dict(best_state)

    def _perplexity_from_loader(self, data_loader: DataLoader) -> float:
        model, vocabulary = self._require_fitted()
        model.eval()
        total_loss = 0.0
        total_tokens = 0
        criterion = nn.CrossEntropyLoss(ignore_index=vocabulary.pad_id, reduction="sum")

        with torch.no_grad():
            for batch in data_loader:
                input_ids = batch["input_ids"].to(self.device)
                targets = batch["targets"].to(self.device)
                logits, _ = model(input_ids)
                total_loss += float(criterion(logits.view(-1, logits.size(-1)), targets.view(-1)).item())
                total_tokens += int((targets != vocabulary.pad_id).sum().item())

        if total_tokens == 0:
            raise ValueError("At least one token is required to compute perplexity.")
        return math.exp(total_loss / total_tokens)

    def corpus_perplexity(self, token_sequences: list[list[str]]) -> float:
        model, vocabulary = self._require_fitted()
        del model
        data_loader = self._create_dataloader(token_sequences, vocabulary=vocabulary, shuffle=False)
        return self._perplexity_from_loader(data_loader)

    def _sample_next_token(self, logits: torch.Tensor, vocabulary: Vocabulary, temperature: float) -> int:
        adjusted_temperature = max(float(temperature), 1e-6)
        candidate_logits = logits.detach().clone() / adjusted_temperature
        for token_id in [vocabulary.pad_id, vocabulary.bos_id, vocabulary.unk_id]:
            candidate_logits[..., token_id] = float("-inf")
        probabilities = torch.softmax(candidate_logits, dim=-1)
        if torch.isnan(probabilities).any() or float(probabilities.sum()) <= 0.0:
            probabilities = torch.zeros_like(probabilities)
            probabilities[..., vocabulary.eos_id] = 1.0
        return int(torch.multinomial(probabilities, num_samples=1).item())

    def generate(self, seed_tokens: Sequence[str], max_length: int = 50, temperature: float = 1.0) -> list[str]:
        model, vocabulary = self._require_fitted()
        model.eval()

        normalized_seed = [token if token in vocabulary.token_to_id else UNK_TOKEN for token in seed_tokens]
        generated = list(normalized_seed)
        context_ids = [vocabulary.bos_id, *vocabulary.encode(normalized_seed)]
        input_ids = torch.tensor([context_ids], dtype=torch.long, device=self.device)

        with torch.no_grad():
            logits, hidden_state = model(input_ids)
            next_logits = logits[:, -1, :]

            for _ in range(max_length):
                next_token_id = self._sample_next_token(next_logits.squeeze(0), vocabulary, temperature)
                if next_token_id == vocabulary.eos_id:
                    break

                generated.append(vocabulary.id_to_token[next_token_id])
                next_input = torch.tensor([[next_token_id]], dtype=torch.long, device=self.device)
                logits, hidden_state = model(next_input, hidden_state)
                next_logits = logits[:, -1, :]

        return generated