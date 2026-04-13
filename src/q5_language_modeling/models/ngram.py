"""N-gram language model for Q5."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence
import math
import random


class NGramLanguageModel:
    """Smoothed n-gram language model with simple sampling."""

    def __init__(self, n: int = 3, smoothing: str = "add_k", alpha: float = 0.1, min_token_frequency: int = 2):
        if n < 2:
            raise ValueError("n must be at least 2 for an n-gram language model.")
        if smoothing not in {"add_k", "laplace"}:
            raise ValueError("Supported smoothing methods are 'add_k' and 'laplace'.")
        if min_token_frequency < 1:
            raise ValueError("min_token_frequency must be at least 1.")

        self.n = int(n)
        self.smoothing = smoothing
        self.alpha = 1.0 if smoothing == "laplace" else float(alpha)
        self.min_token_frequency = int(min_token_frequency)

        self._bos_token = "<bos>"
        self._eos_token = "<eos>"
        self._unk_token = "<unk>"
        self._context_counts: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
        self._unigram_counts: Counter[str] = Counter()
        self._vocab: list[str] = []

    @property
    def vocab_size(self) -> int:
        return max(len(self._vocab), 1)

    def _normalize_token(self, token: str) -> str:
        if token in self._vocab:
            return token
        return self._unk_token

    def _prepare_sequence(self, token_sequence: Sequence[str]) -> list[str]:
        normalized_sequence = [self._normalize_token(token) for token in token_sequence]
        return [self._bos_token] * (self.n - 1) + normalized_sequence + [self._eos_token]

    def _normalize_context(self, context: Sequence[str]) -> tuple[str, ...]:
        context_tokens = list(context)[-(self.n - 1) :]
        if len(context_tokens) < self.n - 1:
            context_tokens = [self._bos_token] * (self.n - 1 - len(context_tokens)) + context_tokens
        return tuple(context_tokens)

    def fit(self, token_sequences: list[list[str]]) -> None:
        self._context_counts = defaultdict(Counter)
        self._unigram_counts = Counter()

        raw_counts = Counter(token for token_sequence in token_sequences for token in token_sequence)
        if not raw_counts:
            raise ValueError("At least one non-empty token sequence is required to fit the n-gram model.")

        kept_tokens = {
            token
            for token, count in raw_counts.items()
            if count >= self.min_token_frequency
        }
        kept_tokens.update({self._unk_token, self._eos_token})
        self._vocab = sorted(kept_tokens)

        for token_sequence in token_sequences:
            prepared = self._prepare_sequence(token_sequence)
            for index in range(self.n - 1, len(prepared)):
                context = tuple(prepared[index - self.n + 1 : index])
                token = prepared[index]
                self._context_counts[context][token] += 1
                self._unigram_counts[token] += 1

        if not self._unigram_counts:
            raise ValueError("At least one non-empty token sequence is required to fit the n-gram model.")

    def probability(self, token: str, context: Sequence[str]) -> float:
        if not self._vocab:
            raise ValueError("The n-gram model must be fit before probabilities can be queried.")

        normalized_context = self._normalize_context(context)
        normalized_token = self._normalize_token(token)
        context_counter = self._context_counts.get(normalized_context)
        if context_counter:
            count = context_counter.get(normalized_token, 0)
            total = sum(context_counter.values())
        else:
            count = self._unigram_counts.get(normalized_token, 0)
            total = sum(self._unigram_counts.values())

        return (count + self.alpha) / (total + self.alpha * self.vocab_size)

    def perplexity(self, token_sequence: Sequence[str]) -> float:
        return self.corpus_perplexity([list(token_sequence)])

    def corpus_perplexity(self, token_sequences: list[list[str]]) -> float:
        total_log_probability = 0.0
        total_predictions = 0

        for token_sequence in token_sequences:
            prepared = self._prepare_sequence(token_sequence)
            for index in range(self.n - 1, len(prepared)):
                context = prepared[index - self.n + 1 : index]
                token = prepared[index]
                probability = max(self.probability(token, context), 1e-12)
                total_log_probability += math.log(probability)
                total_predictions += 1

        if total_predictions == 0:
            raise ValueError("At least one prediction is required to compute perplexity.")

        return math.exp(-total_log_probability / total_predictions)

    def generate(self, seed_tokens: Sequence[str], max_length: int = 50, temperature: float = 1.0) -> list[str]:
        if not self._vocab:
            raise ValueError("The n-gram model must be fit before text can be generated.")

        adjusted_temperature = max(float(temperature), 1e-6)
        generated = [self._normalize_token(token) for token in seed_tokens]

        for _ in range(max_length):
            context = self._normalize_context(generated)
            candidate_counter = self._context_counts.get(context)
            candidates = list(candidate_counter.keys()) if candidate_counter else list(self._vocab)
            candidates = [token for token in candidates if token != self._unk_token]
            if not candidates:
                candidates = [token for token in self._vocab if token != self._unk_token]
            if self._eos_token not in candidates:
                candidates.append(self._eos_token)

            weights = [max(self.probability(token, context), 1e-12) ** (1.0 / adjusted_temperature) for token in candidates]
            next_token = random.choices(candidates, weights=weights, k=1)[0]
            if next_token == self._eos_token:
                break
            generated.append(next_token)

        return generated