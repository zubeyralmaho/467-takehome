"""Abstractive BART summarizer for Q3."""

from __future__ import annotations

from typing import Sequence

import torch

try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
except ImportError:  # pragma: no cover - optional dependency during bootstrap
    AutoModelForSeq2SeqLM = None
    AutoTokenizer = None


class BARTSummarizer:
    """Transformers-based abstractive summarizer with a Q3-compatible interface."""

    def __init__(
        self,
        model_name: str = "sshleifer/distilbart-cnn-12-6",
        batch_size: int = 2,
        max_input_length: int = 1024,
        max_output_length: int = 142,
        min_output_length: int = 56,
        num_beams: int = 4,
        length_penalty: float = 2.0,
        no_repeat_ngram_size: int = 3,
        early_stopping: bool = True,
        device: str = "auto",
    ):
        self._ensure_transformers_available()

        self.model_name = model_name
        self.batch_size = int(batch_size)
        self.max_input_length = int(max_input_length)
        self.max_output_length = int(max_output_length)
        self.min_output_length = int(min_output_length)
        self.num_beams = int(num_beams)
        self.length_penalty = float(length_penalty)
        self.no_repeat_ngram_size = int(no_repeat_ngram_size)
        self.early_stopping = bool(early_stopping)
        self.device = self._resolve_device(device)

        self.tokenizer = None
        self.model = None

    def _prepare_input_text(self, text: str) -> str:
        if "t5" in self.model_name.lower() and not text.lower().startswith("summarize:"):
            return f"summarize: {text}"
        return text

    @staticmethod
    def _ensure_transformers_available() -> None:
        if AutoModelForSeq2SeqLM is None or AutoTokenizer is None:
            raise ImportError("BART support requires the 'transformers' package. Install dependencies from requirements.txt.")

    @staticmethod
    def _resolve_device(device: str) -> torch.device:
        if device != "auto":
            return torch.device(device)
        if torch.cuda.is_available():
            return torch.device("cuda")
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    def _ensure_loaded(self) -> tuple[object, object]:
        if self.model is None or self.tokenizer is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name).to(self.device)
            if getattr(self.tokenizer, "pad_token_id", None) is None and getattr(self.tokenizer, "eos_token_id", None) is not None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        return self.model, self.tokenizer

    def fit(self, *_args, **_kwargs) -> None:
        self._ensure_loaded()

    def predict(self, texts: Sequence[str]) -> list[str]:
        if not texts:
            return []

        model, tokenizer = self._ensure_loaded()
        model.eval()

        summaries: list[str] = []
        with torch.inference_mode():
            for start in range(0, len(texts), self.batch_size):
                batch_texts = [self._prepare_input_text(str(text)) for text in texts[start : start + self.batch_size]]
                encoded = tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=self.max_input_length,
                    return_tensors="pt",
                )
                encoded = {key: value.to(self.device) for key, value in encoded.items()}

                generation_kwargs = {
                    "max_length": self.max_output_length,
                    "min_length": min(self.min_output_length, self.max_output_length - 1),
                    "num_beams": self.num_beams,
                    "length_penalty": self.length_penalty,
                    "no_repeat_ngram_size": self.no_repeat_ngram_size,
                    "early_stopping": self.early_stopping,
                }
                forced_bos_token_id = getattr(model.generation_config, "forced_bos_token_id", None)
                if forced_bos_token_id is not None:
                    generation_kwargs["forced_bos_token_id"] = forced_bos_token_id

                generated = model.generate(**encoded, **generation_kwargs)
                summaries.extend(
                    tokenizer.batch_decode(
                        generated,
                        skip_special_tokens=True,
                        clean_up_tokenization_spaces=True,
                    )
                )

        return [summary.strip() for summary in summaries]