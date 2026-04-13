"""Pretrained transformer machine-translation model for Q4."""

from __future__ import annotations

import torch

try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
except ImportError:  # pragma: no cover - optional dependency during bootstrap
    AutoModelForSeq2SeqLM = None
    AutoTokenizer = None


class PretrainedTransformerMT:
    """Hugging Face seq2seq translation wrapper with a Q4-compatible interface."""

    def __init__(
        self,
        model_name: str = "Helsinki-NLP/opus-mt-en-de",
        batch_size: int = 8,
        max_input_length: int = 96,
        max_output_length: int = 96,
        num_beams: int = 4,
        length_penalty: float = 1.0,
        early_stopping: bool = True,
        device: str = "auto",
    ):
        self._ensure_transformers_available()

        self.model_name = model_name
        self.batch_size = int(batch_size)
        self.max_input_length = int(max_input_length)
        self.max_output_length = int(max_output_length)
        self.num_beams = int(num_beams)
        self.length_penalty = float(length_penalty)
        self.early_stopping = bool(early_stopping)
        self.device = self._resolve_device(device)

        self.tokenizer = None
        self.model = None

    @staticmethod
    def _ensure_transformers_available() -> None:
        if AutoModelForSeq2SeqLM is None or AutoTokenizer is None:
            raise ImportError("Q4 transformer support requires the 'transformers' package. Install dependencies from requirements.txt.")

    @staticmethod
    def _resolve_device(device: str) -> torch.device:
        if device != "auto":
            return torch.device(device)
        if torch.cuda.is_available():
            return torch.device("cuda")
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    def _ensure_loaded(self):
        if self.model is None or self.tokenizer is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name).to(self.device)
        return self.model, self.tokenizer

    def fit(self, *_args, **_kwargs) -> None:
        self._ensure_loaded()

    def predict(self, texts: list[str]) -> list[str]:
        if not texts:
            return []

        model, tokenizer = self._ensure_loaded()
        model.eval()

        predictions: list[str] = []
        with torch.inference_mode():
            for start in range(0, len(texts), self.batch_size):
                batch_texts = [str(text) for text in texts[start : start + self.batch_size]]
                encoded = tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=self.max_input_length,
                    return_tensors="pt",
                )
                encoded = {key: value.to(self.device) for key, value in encoded.items()}
                generated = model.generate(
                    **encoded,
                    max_length=self.max_output_length,
                    num_beams=self.num_beams,
                    length_penalty=self.length_penalty,
                    early_stopping=self.early_stopping,
                )
                predictions.extend(
                    tokenizer.batch_decode(
                        generated,
                        skip_special_tokens=True,
                        clean_up_tokenization_spaces=True,
                    )
                )

        return [prediction.strip() for prediction in predictions]