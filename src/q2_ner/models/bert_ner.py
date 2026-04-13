"""BERT token-classification model for Q2 named entity recognition."""

from __future__ import annotations

from copy import deepcopy
from typing import Sequence

import torch
from seqeval.metrics import accuracy_score as seqeval_accuracy_score
from seqeval.metrics import f1_score as seqeval_f1_score
from seqeval.scheme import IOB2
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset

from src.common.seed import worker_init_fn
from src.q2_ner.preprocess import align_labels_with_tokens

try:
    from transformers import AutoModelForTokenClassification, AutoTokenizer, get_linear_schedule_with_warmup
except ImportError:  # pragma: no cover - optional dependency during bootstrap
    AutoModelForTokenClassification = None
    AutoTokenizer = None
    get_linear_schedule_with_warmup = None


class TokenSequenceDataset(Dataset):
    """Dataset backed by tokenized sentence lists."""

    def __init__(self, sentences: Sequence[Sequence[str]], labels: Sequence[Sequence[str]] | None = None):
        self.sentences = [list(sentence) for sentence in sentences]
        self.labels = None if labels is None else [list(label_sequence) for label_sequence in labels]

    def __len__(self) -> int:
        return len(self.sentences)

    def __getitem__(self, index: int) -> dict[str, object]:
        item: dict[str, object] = {"tokens": self.sentences[index]}
        if self.labels is not None:
            item["labels"] = self.labels[index]
        return item


class BERTNERModel:
    """Transformers-based BERT token classifier with a Q2-compatible interface."""

    def __init__(
        self,
        label_names: Sequence[str],
        model_name: str = "bert-base-cased",
        batch_size: int = 8,
        learning_rate: float = 5e-5,
        weight_decay: float = 0.01,
        max_epochs: int = 3,
        early_stopping_patience: int = 2,
        max_seq_length: int = 128,
        warmup_ratio: float = 0.1,
        monitor_metric: str = "f1",
        num_workers: int = 0,
        device: str = "auto",
        seed: int = 42,
    ):
        self._ensure_transformers_available()

        self.label_names = [str(label) for label in label_names]
        self.label_to_id = {label: index for index, label in enumerate(self.label_names)}
        self.id_to_label = {index: label for label, index in self.label_to_id.items()}

        self.model_name = model_name
        self.batch_size = int(batch_size)
        self.learning_rate = float(learning_rate)
        self.weight_decay = float(weight_decay)
        self.max_epochs = int(max_epochs)
        self.early_stopping_patience = int(early_stopping_patience)
        self.max_seq_length = int(max_seq_length)
        self.warmup_ratio = float(warmup_ratio)
        self.monitor_metric = monitor_metric
        self.num_workers = int(num_workers)
        self.seed = int(seed)
        self.device = self._resolve_device(device)

        self.tokenizer = None
        self.model = None

    @staticmethod
    def _ensure_transformers_available() -> None:
        if AutoModelForTokenClassification is None or AutoTokenizer is None or get_linear_schedule_with_warmup is None:
            raise ImportError(
                "BERT NER support requires the 'transformers' package. Install dependencies from requirements.txt."
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
            raise RuntimeError("BERTNERModel must be fit before inference.")
        return self.model, self.tokenizer

    def _collate_batch(self, batch: list[dict[str, object]]) -> dict[str, torch.Tensor]:
        _, tokenizer = self._require_fitted()
        token_sequences = [item["tokens"] for item in batch]
        encodings = tokenizer(
            token_sequences,
            is_split_into_words=True,
            padding=True,
            truncation=True,
            max_length=self.max_seq_length,
            return_tensors="pt",
        )

        payload = {
            "input_ids": encodings["input_ids"],
            "attention_mask": encodings["attention_mask"],
        }

        if "labels" in batch[0]:
            aligned_labels = []
            for batch_index, item in enumerate(batch):
                label_ids = [self.label_to_id[str(label)] for label in item["labels"]]
                aligned_labels.append(align_labels_with_tokens(label_ids, encodings.word_ids(batch_index=batch_index)))
            payload["labels"] = torch.tensor(aligned_labels, dtype=torch.long)

        return payload

    def _create_dataloader(
        self,
        sentences: Sequence[Sequence[str]],
        labels: Sequence[Sequence[str]] | None,
        shuffle: bool,
    ) -> DataLoader:
        dataset = TokenSequenceDataset(sentences, labels=labels)
        generator = torch.Generator()
        generator.manual_seed(self.seed)

        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=shuffle,
            num_workers=self.num_workers,
            collate_fn=self._collate_batch,
            worker_init_fn=worker_init_fn if self.num_workers > 0 else None,
            generator=generator,
        )

    def _validation_score(
        self,
        references: Sequence[Sequence[str]],
        predictions: Sequence[Sequence[str]],
    ) -> float:
        if self.monitor_metric == "accuracy":
            return float(seqeval_accuracy_score(references, predictions))
        if self.monitor_metric == "f1":
            return float(seqeval_f1_score(references, predictions, mode="strict", scheme=IOB2, zero_division=0))
        raise ValueError(f"Unsupported monitor_metric: {self.monitor_metric}")

    def fit(
        self,
        sentences: Sequence[Sequence[str]],
        label_sequences: Sequence[Sequence[str]],
        validation_data: dict[str, list] | None = None,
    ) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
        self.model = AutoModelForTokenClassification.from_pretrained(
            self.model_name,
            num_labels=len(self.label_names),
            id2label=self.id_to_label,
            label2id=self.label_to_id,
        ).to(self.device)

        train_loader = self._create_dataloader(sentences, label_sequences, shuffle=True)
        optimizer = AdamW(self.model.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay)
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
                labels = batch["labels"].to(self.device)

                optimizer.zero_grad(set_to_none=True)
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels,
                )
                outputs.loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()
                scheduler.step()

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

    def _predict_batches(self, sentences: Sequence[Sequence[str]]) -> tuple[list[list[str]], list[list[float | None]]]:
        model, tokenizer = self._require_fitted()
        model.eval()

        predictions: list[list[str]] = []
        confidences: list[list[float | None]] = []

        with torch.no_grad():
            for start in range(0, len(sentences), self.batch_size):
                batch_sentences = [list(sentence) for sentence in sentences[start : start + self.batch_size]]
                encodings = tokenizer(
                    batch_sentences,
                    is_split_into_words=True,
                    padding=True,
                    truncation=True,
                    max_length=self.max_seq_length,
                    return_tensors="pt",
                )
                model_inputs = {
                    "input_ids": encodings["input_ids"].to(self.device),
                    "attention_mask": encodings["attention_mask"].to(self.device),
                }

                outputs = model(**model_inputs)
                batch_probabilities = torch.softmax(outputs.logits, dim=-1).cpu()
                batch_predictions = batch_probabilities.argmax(dim=-1).tolist()

                for batch_index in range(len(batch_sentences)):
                    original_length = len(batch_sentences[batch_index])
                    word_ids = encodings.word_ids(batch_index=batch_index)
                    seen_word_ids: set[int] = set()
                    sentence_labels: list[str] = []
                    sentence_confidences: list[float | None] = []

                    for token_index, word_id in enumerate(word_ids):
                        if word_id is None or word_id in seen_word_ids:
                            continue
                        seen_word_ids.add(word_id)

                        label_id = int(batch_predictions[batch_index][token_index])
                        sentence_labels.append(self.id_to_label[label_id])
                        sentence_confidences.append(float(batch_probabilities[batch_index, token_index, label_id].item()))

                    if len(sentence_labels) < original_length:
                        missing_labels = original_length - len(sentence_labels)
                        sentence_labels.extend(["O"] * missing_labels)
                        sentence_confidences.extend([None] * missing_labels)
                    elif len(sentence_labels) > original_length:
                        sentence_labels = sentence_labels[:original_length]
                        sentence_confidences = sentence_confidences[:original_length]

                    predictions.append(sentence_labels)
                    confidences.append(sentence_confidences)

        return predictions, confidences

    def predict(self, sentences: Sequence[Sequence[str]]) -> list[list[str]]:
        predictions, _ = self._predict_batches(sentences)
        return predictions

    def predict_token_confidences(
        self,
        sentences: Sequence[Sequence[str]],
        predictions: Sequence[Sequence[str]] | None = None,
    ) -> list[list[float | None]]:
        del predictions
        _, confidences = self._predict_batches(sentences)
        return confidences