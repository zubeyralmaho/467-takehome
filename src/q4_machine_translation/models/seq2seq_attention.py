"""Seq2Seq with additive attention for Q4 machine translation."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass
import random

import torch
from torch import nn
from torch.nn.utils.rnn import pad_packed_sequence, pad_sequence, pack_padded_sequence
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

    def encode(self, tokens: Sequence[str]) -> list[int]:
        return [
            self.bos_id,
            *[self.token_to_id.get(token, self.unk_id) for token in tokens],
            self.eos_id,
        ]

    def decode(self, token_ids: Sequence[int]) -> list[str]:
        tokens: list[str] = []
        for token_id in token_ids:
            if token_id == self.eos_id:
                break
            if token_id in {self.pad_id, self.bos_id}:
                continue
            tokens.append(self.id_to_token[token_id])
        return tokens


class TranslationDataset(Dataset):
    def __init__(
        self,
        source_sequences: Sequence[Sequence[str]],
        target_sequences: Sequence[Sequence[str]],
        source_vocabulary: Vocabulary,
        target_vocabulary: Vocabulary,
    ):
        self.source_tensors = [
            torch.tensor(source_vocabulary.encode(tokens), dtype=torch.long)
            for tokens in source_sequences
        ]
        self.target_tensors = [
            torch.tensor(target_vocabulary.encode(tokens), dtype=torch.long)
            for tokens in target_sequences
        ]

    def __len__(self) -> int:
        return len(self.source_tensors)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.source_tensors[index], self.target_tensors[index]


class BatchCollator:
    def __init__(self, src_pad_id: int, tgt_pad_id: int):
        self.src_pad_id = src_pad_id
        self.tgt_pad_id = tgt_pad_id

    def __call__(self, batch: list[tuple[torch.Tensor, torch.Tensor]]) -> dict[str, torch.Tensor]:
        sources = [source for source, _ in batch]
        targets = [target for _, target in batch]
        source_lengths = torch.tensor([source.size(0) for source in sources], dtype=torch.long)
        target_lengths = torch.tensor([target.size(0) for target in targets], dtype=torch.long)
        return {
            "src_ids": pad_sequence(sources, batch_first=True, padding_value=self.src_pad_id),
            "src_lengths": source_lengths,
            "tgt_ids": pad_sequence(targets, batch_first=True, padding_value=self.tgt_pad_id),
            "tgt_lengths": target_lengths,
        }


class Encoder(nn.Module):
    def __init__(
        self,
        input_dim: int,
        embedding_dim: int,
        hidden_dim: int,
        num_layers: int,
        dropout: float,
        pad_id: int,
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.embedding = nn.Embedding(input_dim, embedding_dim, padding_idx=pad_id)
        self.dropout = nn.Dropout(dropout)
        self.rnn = nn.GRU(
            input_size=embedding_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,
            bidirectional=True,
        )
        self.bridge = nn.Linear(hidden_dim * 2, hidden_dim)

    def forward(self, src_ids: torch.Tensor, src_lengths: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        embedded = self.dropout(self.embedding(src_ids))
        packed = pack_padded_sequence(embedded, src_lengths.cpu(), batch_first=True, enforce_sorted=False)
        outputs, hidden = self.rnn(packed)
        outputs, _ = pad_packed_sequence(outputs, batch_first=True)

        hidden = hidden.view(self.num_layers, 2, src_ids.size(0), self.hidden_dim)
        hidden = torch.cat([hidden[:, 0], hidden[:, 1]], dim=2)
        hidden = torch.tanh(self.bridge(hidden))
        return outputs, hidden


class AdditiveAttention(nn.Module):
    def __init__(self, encoder_dim: int, decoder_dim: int):
        super().__init__()
        self.encoder_projection = nn.Linear(encoder_dim, decoder_dim, bias=False)
        self.decoder_projection = nn.Linear(decoder_dim, decoder_dim, bias=False)
        self.energy_projection = nn.Linear(decoder_dim, 1, bias=False)

    def forward(
        self,
        decoder_hidden: torch.Tensor,
        encoder_outputs: torch.Tensor,
        mask: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        energy = self.energy_projection(
            torch.tanh(
                self.encoder_projection(encoder_outputs)
                + self.decoder_projection(decoder_hidden).unsqueeze(1)
            )
        ).squeeze(-1)
        energy = energy.masked_fill(~mask, -1e9)
        attention_weights = torch.softmax(energy, dim=1)
        context = torch.bmm(attention_weights.unsqueeze(1), encoder_outputs).squeeze(1)
        return attention_weights, context


class Decoder(nn.Module):
    def __init__(
        self,
        output_dim: int,
        embedding_dim: int,
        hidden_dim: int,
        num_layers: int,
        dropout: float,
        attention: AdditiveAttention,
        pad_id: int,
    ):
        super().__init__()
        self.embedding = nn.Embedding(output_dim, embedding_dim, padding_idx=pad_id)
        self.dropout = nn.Dropout(dropout)
        self.attention = attention
        self.rnn = nn.GRU(
            input_size=embedding_dim + hidden_dim * 2,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,
        )
        self.output_projection = nn.Linear(hidden_dim + hidden_dim * 2 + embedding_dim, output_dim)

    def forward(
        self,
        input_token: torch.Tensor,
        hidden: torch.Tensor,
        encoder_outputs: torch.Tensor,
        mask: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        embedded = self.dropout(self.embedding(input_token.unsqueeze(1)))
        _, context = self.attention(hidden[-1], encoder_outputs, mask)
        rnn_input = torch.cat([embedded, context.unsqueeze(1)], dim=2)
        output, hidden = self.rnn(rnn_input, hidden)
        logits = self.output_projection(
            torch.cat([output.squeeze(1), context, embedded.squeeze(1)], dim=1)
        )
        return logits, hidden


class _Seq2SeqAttentionNetwork(nn.Module):
    def __init__(self, encoder: Encoder, decoder: Decoder, src_pad_id: int):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.src_pad_id = src_pad_id

    def _mask(self, src_ids: torch.Tensor) -> torch.Tensor:
        return src_ids != self.src_pad_id

    def forward(
        self,
        src_ids: torch.Tensor,
        src_lengths: torch.Tensor,
        tgt_ids: torch.Tensor,
        teacher_forcing_ratio: float,
    ) -> torch.Tensor:
        encoder_outputs, hidden = self.encoder(src_ids, src_lengths)
        mask = self._mask(src_ids)
        batch_size = tgt_ids.size(0)
        steps = max(tgt_ids.size(1) - 1, 1)
        vocab_size = self.decoder.output_projection.out_features
        logits = torch.zeros(batch_size, steps, vocab_size, device=src_ids.device)

        input_token = tgt_ids[:, 0]
        for step in range(steps):
            step_logits, hidden = self.decoder(input_token, hidden, encoder_outputs, mask)
            logits[:, step] = step_logits
            if step + 1 >= tgt_ids.size(1):
                continue
            teacher_force = random.random() < teacher_forcing_ratio
            predicted_token = step_logits.argmax(dim=1)
            input_token = tgt_ids[:, step + 1] if teacher_force else predicted_token

        return logits

    def greedy_decode(
        self,
        src_ids: torch.Tensor,
        src_lengths: torch.Tensor,
        bos_id: int,
        eos_id: int,
        max_length: int,
    ) -> torch.Tensor:
        encoder_outputs, hidden = self.encoder(src_ids, src_lengths)
        mask = self._mask(src_ids)

        input_token = torch.full((src_ids.size(0),), bos_id, dtype=torch.long, device=src_ids.device)
        predictions: list[torch.Tensor] = []
        finished = torch.zeros(src_ids.size(0), dtype=torch.bool, device=src_ids.device)

        for _ in range(max_length):
            step_logits, hidden = self.decoder(input_token, hidden, encoder_outputs, mask)
            input_token = step_logits.argmax(dim=1)
            predictions.append(input_token)
            finished = finished | input_token.eq(eos_id)
            if bool(finished.all()):
                break

        if not predictions:
            return torch.empty((src_ids.size(0), 0), dtype=torch.long, device=src_ids.device)
        return torch.stack(predictions, dim=1)


class Seq2SeqAttentionMT:
    def __init__(
        self,
        embedding_dim: int = 128,
        hidden_dim: int = 128,
        num_layers: int = 1,
        dropout: float = 0.2,
        batch_size: int = 32,
        learning_rate: float = 1e-3,
        weight_decay: float = 0.0,
        max_epochs: int = 8,
        early_stopping_patience: int = 2,
        teacher_forcing_ratio: float = 0.5,
        max_vocab_size: int | None = 8000,
        min_token_frequency: int = 2,
        max_output_length: int = 32,
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
        self.teacher_forcing_ratio = float(teacher_forcing_ratio)
        self.max_vocab_size = None if max_vocab_size is None else int(max_vocab_size)
        self.min_token_frequency = int(min_token_frequency)
        self.max_output_length = int(max_output_length)
        self.gradient_clip = float(gradient_clip)
        self.num_workers = int(num_workers)
        self.seed = int(seed)
        self.device = self._resolve_device(device)

        self.source_vocabulary: Vocabulary | None = None
        self.target_vocabulary: Vocabulary | None = None
        self.model: _Seq2SeqAttentionNetwork | None = None

    @staticmethod
    def _resolve_device(device: str) -> torch.device:
        if device != "auto":
            return torch.device(device)
        if torch.cuda.is_available():
            return torch.device("cuda")
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return str(text).split()

    def _require_fitted(self) -> tuple[_Seq2SeqAttentionNetwork, Vocabulary, Vocabulary]:
        if self.model is None or self.source_vocabulary is None or self.target_vocabulary is None:
            raise RuntimeError("Seq2SeqAttentionMT must be fit before inference.")
        return self.model, self.source_vocabulary, self.target_vocabulary

    def _create_dataloader(
        self,
        sources: Sequence[str],
        targets: Sequence[str],
        source_vocabulary: Vocabulary,
        target_vocabulary: Vocabulary,
        shuffle: bool,
    ) -> DataLoader:
        dataset = TranslationDataset(
            source_sequences=[self._tokenize(text) for text in sources],
            target_sequences=[self._tokenize(text) for text in targets],
            source_vocabulary=source_vocabulary,
            target_vocabulary=target_vocabulary,
        )
        generator = torch.Generator()
        generator.manual_seed(self.seed)

        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=shuffle,
            num_workers=self.num_workers,
            collate_fn=BatchCollator(source_vocabulary.pad_id, target_vocabulary.pad_id),
            worker_init_fn=worker_init_fn if self.num_workers > 0 else None,
            generator=generator,
        )

    def fit(self, sources: Sequence[str], targets: Sequence[str], validation_data: dict[str, list[str]] | None = None) -> None:
        source_tokens = [self._tokenize(text) for text in sources]
        target_tokens = [self._tokenize(text) for text in targets]
        self.source_vocabulary = Vocabulary.build(
            source_tokens,
            max_vocab_size=self.max_vocab_size,
            min_frequency=self.min_token_frequency,
        )
        self.target_vocabulary = Vocabulary.build(
            target_tokens,
            max_vocab_size=self.max_vocab_size,
            min_frequency=self.min_token_frequency,
        )

        encoder = Encoder(
            input_dim=len(self.source_vocabulary.id_to_token),
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
            dropout=self.dropout,
            pad_id=self.source_vocabulary.pad_id,
        )
        attention = AdditiveAttention(encoder_dim=self.hidden_dim * 2, decoder_dim=self.hidden_dim)
        decoder = Decoder(
            output_dim=len(self.target_vocabulary.id_to_token),
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
            dropout=self.dropout,
            attention=attention,
            pad_id=self.target_vocabulary.pad_id,
        )
        self.model = _Seq2SeqAttentionNetwork(encoder=encoder, decoder=decoder, src_pad_id=self.source_vocabulary.pad_id).to(self.device)

        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay)
        train_loader = self._create_dataloader(
            sources,
            targets,
            self.source_vocabulary,
            self.target_vocabulary,
            shuffle=True,
        )

        validation_loader = None
        if validation_data is not None:
            validation_loader = self._create_dataloader(
                validation_data["sources"],
                validation_data["references"],
                self.source_vocabulary,
                self.target_vocabulary,
                shuffle=False,
            )

        criterion = nn.CrossEntropyLoss(ignore_index=self.target_vocabulary.pad_id, reduction="sum")
        best_state = deepcopy(self.model.state_dict())
        best_loss = float("inf")
        epochs_without_improvement = 0

        for _ in range(self.max_epochs):
            self.model.train()
            for batch in train_loader:
                src_ids = batch["src_ids"].to(self.device)
                src_lengths = batch["src_lengths"]
                tgt_ids = batch["tgt_ids"].to(self.device)

                optimizer.zero_grad(set_to_none=True)
                logits = self.model(src_ids, src_lengths, tgt_ids, teacher_forcing_ratio=self.teacher_forcing_ratio)
                gold_targets = tgt_ids[:, 1: 1 + logits.size(1)]
                loss = criterion(logits.reshape(-1, logits.size(-1)), gold_targets.reshape(-1))
                token_count = max(int((gold_targets != self.target_vocabulary.pad_id).sum().item()), 1)
                normalized_loss = loss / token_count
                normalized_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.gradient_clip)
                optimizer.step()

            if validation_loader is None:
                best_state = deepcopy(self.model.state_dict())
                continue

            validation_loss = self._validation_loss(validation_loader, criterion)
            if validation_loss + 1e-6 < best_loss:
                best_loss = validation_loss
                best_state = deepcopy(self.model.state_dict())
                epochs_without_improvement = 0
                continue

            epochs_without_improvement += 1
            if epochs_without_improvement >= self.early_stopping_patience:
                break

        self.model.load_state_dict(best_state)

    def _validation_loss(self, data_loader: DataLoader, criterion: nn.CrossEntropyLoss) -> float:
        model, _, target_vocabulary = self._require_fitted()
        model.eval()
        total_loss = 0.0
        total_tokens = 0

        with torch.no_grad():
            for batch in data_loader:
                src_ids = batch["src_ids"].to(self.device)
                src_lengths = batch["src_lengths"]
                tgt_ids = batch["tgt_ids"].to(self.device)
                logits = model(src_ids, src_lengths, tgt_ids, teacher_forcing_ratio=1.0)
                gold_targets = tgt_ids[:, 1: 1 + logits.size(1)]
                total_loss += float(criterion(logits.reshape(-1, logits.size(-1)), gold_targets.reshape(-1)).item())
                total_tokens += int((gold_targets != target_vocabulary.pad_id).sum().item())

        return total_loss / max(total_tokens, 1)

    def predict(self, texts: list[str]) -> list[str]:
        if not texts:
            return []

        model, source_vocabulary, target_vocabulary = self._require_fitted()
        model.eval()
        predictions: list[str] = []

        with torch.no_grad():
            for start in range(0, len(texts), self.batch_size):
                batch_tokens = [self._tokenize(text) for text in texts[start : start + self.batch_size]]
                batch_tensors = [torch.tensor(source_vocabulary.encode(tokens), dtype=torch.long) for tokens in batch_tokens]
                src_lengths = torch.tensor([tensor.size(0) for tensor in batch_tensors], dtype=torch.long)
                src_ids = pad_sequence(batch_tensors, batch_first=True, padding_value=source_vocabulary.pad_id).to(self.device)
                decoded_ids = model.greedy_decode(
                    src_ids,
                    src_lengths,
                    bos_id=target_vocabulary.bos_id,
                    eos_id=target_vocabulary.eos_id,
                    max_length=self.max_output_length,
                )
                for row in decoded_ids.cpu().tolist():
                    predictions.append(" ".join(target_vocabulary.decode(row)).strip())

        return predictions