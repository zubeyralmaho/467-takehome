"""GPT-style language model wrapper for Q5."""

from __future__ import annotations

import math
from typing import Sequence

import torch

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
except ImportError:  # pragma: no cover - optional dependency during bootstrap
    AutoModelForCausalLM = None
    AutoTokenizer = None


class GPT2LanguageModel:
    """Practical pretrained GPT-style language model baseline."""

    def __init__(
        self,
        model_name: str = "distilgpt2",
        max_input_length: int = 256,
        eval_batch_size: int = 8,
        top_k: int = 50,
        device: str = "auto",
    ):
        self._ensure_transformers_available()

        self.model_name = model_name
        self.max_input_length = int(max_input_length)
        self.eval_batch_size = int(eval_batch_size)
        self.top_k = int(top_k)
        self.device = self._resolve_device(device)

        self.tokenizer = None
        self.model = None

    @staticmethod
    def _ensure_transformers_available() -> None:
        if AutoModelForCausalLM is None or AutoTokenizer is None:
            raise ImportError("Q5 GPT-2 support requires the 'transformers' package. Install dependencies from requirements.txt.")

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
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.tokenizer.pad_token_id
        return self.model, self.tokenizer

    @staticmethod
    def _to_text(token_sequences: Sequence[Sequence[str]]) -> list[str]:
        return [" ".join(token_sequence) for token_sequence in token_sequences if token_sequence]

    def fit(self, *_args, **_kwargs) -> None:
        self._ensure_loaded()

    def corpus_perplexity(self, token_sequences: list[list[str]]) -> float:
        texts = self._to_text(token_sequences)
        if not texts:
            raise ValueError("At least one token sequence is required to compute perplexity.")

        model, tokenizer = self._ensure_loaded()
        model.eval()

        total_negative_log_likelihood = 0.0
        total_target_tokens = 0

        with torch.no_grad():
            for start in range(0, len(texts), self.eval_batch_size):
                batch_texts = texts[start : start + self.eval_batch_size]
                encoded = tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=self.max_input_length,
                    return_tensors="pt",
                )
                input_ids = encoded["input_ids"].to(self.device)
                attention_mask = encoded["attention_mask"].to(self.device)
                labels = input_ids.masked_fill(attention_mask == 0, -100)

                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                target_tokens = int(attention_mask.sum().item()) - len(batch_texts)
                if target_tokens <= 0:
                    continue

                total_negative_log_likelihood += float(outputs.loss.item()) * target_tokens
                total_target_tokens += target_tokens

        if total_target_tokens <= 0:
            raise ValueError("At least one target token is required to compute perplexity.")

        return math.exp(total_negative_log_likelihood / total_target_tokens)

    def generate(self, seed_tokens: Sequence[str], max_length: int = 50, temperature: float = 1.0) -> list[str]:
        model, tokenizer = self._ensure_loaded()
        prompt_text = " ".join(seed_tokens).strip()
        if not prompt_text:
            prompt_text = "the"

        encoded = tokenizer(prompt_text, return_tensors="pt", truncation=True, max_length=self.max_input_length)
        input_ids = encoded["input_ids"].to(self.device)
        attention_mask = encoded["attention_mask"].to(self.device)

        model.eval()
        with torch.no_grad():
            generated = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=max_length,
                do_sample=True,
                temperature=max(float(temperature), 1e-6),
                top_k=self.top_k,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        decoded = tokenizer.decode(generated[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        return decoded.split()