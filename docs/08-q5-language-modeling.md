# 08 - Q5: Language Modeling

> [Home](README.md) | Previous: [Q4 - Machine Translation](07-q4-machine-translation.md) | Next: [Evaluation Framework](09-evaluation-framework.md)

---

## Objective

Explore probabilistic sequence modeling and text generation. Compare N-gram, LSTM, and optionally transformer-based models. Evaluate with perplexity, analyze fluency and coherence of generated text.

---

## Dataset: WikiText-2

### Properties
- **Size**: ~2M tokens (train), ~217K tokens (val), ~245K tokens (test)
- **Content**: Wikipedia articles (Good/Featured Articles)
- **Vocabulary**: ~33K unique tokens
- **Source**: `datasets.load_dataset("wikitext", "wikitext-2-raw-v1")`

### Alternative: Penn Treebank (PTB)
- **Size**: ~929K train / ~73K val / ~82K test tokens
- **Smaller vocabulary**: ~10K
- **Advantage**: Smaller, faster experiments; standard benchmark in NLP

### Recommendation
WikiText-2 is preferred (larger, more modern, cleaner).

---

## Preprocessing

### preprocess.py

```python
def load_and_tokenize(dataset_name: str = "wikitext-2",
                      tokenizer_type: str = "word") -> dict:
    """
    1. Load raw text
    2. Filter empty lines
    3. Tokenize (word-level)
    4. Build vocabulary
    """

def create_sequences(token_ids: list[int],
                     seq_length: int = 35) -> tuple:
    """
    Create input/target pairs using sliding window:
    Input:  [w1, w2, w3, ..., w35]
    Target: [w2, w3, w4, ..., w36]
    (shifted by 1)
    """

class LMDataset(Dataset):
    """
    Language Modeling dataset.
    Batchified data (contiguous sequences).
    """

    def __init__(self, data: torch.Tensor, seq_length: int = 35):
        """
        data: (total_tokens,) tensor
        Each __getitem__: (seq_length,) input, (seq_length,) target
        """

def batchify(data: torch.Tensor, batch_size: int) -> torch.Tensor:
    """
    Splits data into batch_size equal chunks.
    Standard LM batchification:
    data shape: (total_tokens,) -> (total_tokens // batch_size, batch_size)
    """
```

---

## Model Architectures

### Model 1: N-gram Language Model

**File**: `models/ngram.py`

```python
class NGramLanguageModel:
    """
    N-gram LM with smoothing.
    Supports bigram and trigram.
    """

    def __init__(self, n: int = 3,
                 smoothing: str = "laplace",
                 alpha: float = 1.0):
        """
        n: n-gram size (2=bigram, 3=trigram)
        smoothing: "laplace" (add-k), "kneser_ney", or "interpolation"
        """

    def fit(self, token_sequences: list[list[str]]) -> None:
        """
        Builds n-gram counts:
        - Unigram counts
        - Bigram counts
        - Trigram counts (if n=3)
        """

    def probability(self, token: str, context: tuple) -> float:
        """Computes P(token | context) with smoothing."""

    def perplexity(self, token_sequence: list[str]) -> float:
        """
        PP = exp(-1/N * sum(log P(w_i | context)))
        """

    def generate(self, seed_tokens: list[str],
                 max_length: int = 50,
                 temperature: float = 1.0) -> list[str]:
        """
        Text generation via sampling from the probability distribution.
        temperature: <1 conservative, >1 creative
        """
```

**N-gram Smoothing Methods**:

| Method | Formula (simplified) | Advantage |
|--------|----------------------|-----------|
| Laplace (Add-1) | (count + 1) / (total + V) | Simple |
| Add-k | (count + k) / (total + kV) | k is adjustable |
| Kneser-Ney | Discount + backoff | Best performance |
| Linear Interpolation | lambda1*P_tri + lambda2*P_bi + lambda3*P_uni | Balanced |

**Parameters**:
| Parameter | Value |
|-----------|-------|
| n | 3 (trigram) |
| smoothing | Laplace or Kneser-Ney |
| alpha (Laplace) | 1.0 |

---

### Model 2: LSTM Language Model

**File**: `models/lstm_lm.py`

```python
class LSTMLanguageModel(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 200,
                 hidden_dim: int = 200, num_layers: int = 2,
                 dropout: float = 0.2, tie_weights: bool = True):
        """
        Layers:
        1. Embedding
        2. LSTM (multi-layer)
        3. Dropout
        4. Linear (hidden -> vocab)

        tie_weights: Share embedding and output projection weights
        (parameter savings + performance improvement)
        """

    def forward(self, x, hidden):
        """
        x: (batch, seq_len) token indices
        hidden: (h_0, c_0) tuple

        Output: (batch, seq_len, vocab_size) logits, new_hidden
        """

    def init_hidden(self, batch_size: int):
        """Zero-initialize hidden state."""

    def generate(self, seed_indices: list[int], max_length: int = 100,
                 temperature: float = 1.0,
                 top_k: int = None) -> list[int]:
        """
        Autoregressive text generation:
        1. Start with seed
        2. At each step:
           a. Forward pass
           b. Get logits of the last step
           c. temperature / top-k sampling
           d. Select next token
        3. Continue until max_length
        """
```

**Architecture Diagram**:
```
Input:   [The]  [cat]  [sat]  [on]  [the]
           |      |      |      |      |
           v      v      v      v      v
    [Embedding Layer] (200d)
           |      |      |      |      |
           v      v      v      v      v
    [   LSTM Layer 1 (hidden=200)      ]
           |      |      |      |      |
           v      v      v      v      v
    [   Dropout (0.2)                  ]
           |      |      |      |      |
           v      v      v      v      v
    [   LSTM Layer 2 (hidden=200)      ]
           |      |      |      |      |
           v      v      v      v      v
    [   Dropout (0.2)                  ]
           |      |      |      |      |
           v      v      v      v      v
    [   Linear (200 -> vocab_size)     ]
           |      |      |      |      |
           v      v      v      v      v
Target:  [cat]  [sat]  [on]  [the]  [mat]
```

**Weight Tying**:
```
Embedding.weight == Linear.weight (transposed)
```
- Significantly reduces the number of parameters
- Makes the embedding and output space consistent

**Hyperparameters**:
| Parameter | Value |
|-----------|-------|
| embed_dim | 200 |
| hidden_dim | 200 |
| num_layers | 2 |
| dropout | 0.2 |
| tie_weights | True |
| batch_size | 20 |
| seq_length (bptt) | 35 |
| learning_rate | 20.0 (SGD) |
| optimizer | SGD |
| lr_scheduler | ReduceLROnPlateau (factor=0.25) |
| gradient_clip | 0.25 |
| num_epochs | 40 |

> Note: SGD + high LR + aggressive clipping is an approach close to the AWD-LSTM style. Adam (lr=1e-3) is also an alternative.

---

### Model 3 (Optional): GPT-2 Fine-tuning

**File**: `models/gpt2_lm.py`

```python
class GPT2LanguageModel:
    """
    GPT-2 small (117M params) fine-tuning.
    Optional but important comparison.
    """

    def __init__(self, model_name: str = "gpt2"):
        """Loads HuggingFace GPT2LMHeadModel."""

    def fine_tune(self, train_text, val_text, config):
        """
        Causal LM fine-tuning.
        Uses HuggingFace Trainer.
        """

    def compute_perplexity(self, text: str) -> float:
        """Computes model perplexity."""

    def generate(self, prompt: str, max_length: int = 100,
                 temperature: float = 0.7,
                 top_k: int = 50, top_p: float = 0.9) -> str:
        """Generation with nucleus sampling."""
```

---

## Text Generation

### generate.py

```python
def generate_samples(model, vocab, config,
                     num_samples: int = 5) -> list[str]:
    """
    Generates short text samples for each model.
    Tries different sampling strategies.
    """

# Sampling Strategies:
def greedy_decode(logits):
    """argmax - most probable token"""

def temperature_sampling(logits, temperature=1.0):
    """logits / temperature -> softmax -> sample"""

def top_k_sampling(logits, k=50):
    """Sample from the top k tokens"""

def nucleus_sampling(logits, p=0.9):
    """Sample from tokens up to cumulative probability p"""
```

### Sampling Strategies Comparison

| Strategy | temperature | Property |
|----------|-------------|----------|
| Greedy | - | Deterministic, repetitive |
| Low temp | 0.5 | Conservative, consistent |
| Normal | 1.0 | Balanced |
| High temp | 1.5 | Creative, chaotic |
| Top-k (k=50) | 1.0 | Filters low-probability tokens |
| Nucleus (p=0.9) | 1.0 | Dynamic filtering |

---

## Evaluation

### Perplexity

```python
def compute_perplexity(model, test_loader, criterion) -> float:
    """
    PP = exp(average cross-entropy loss)

    1. Set model to eval mode
    2. Compute loss over all test batches
    3. Take average loss
    4. exp(avg_loss) = perplexity
    """
```

**Perplexity Interpretation**:
| Value | Meaning |
|-------|---------|
| ~1 | Perfect prediction (not possible) |
| ~60-100 | Good LSTM performance (WikiText-2) |
| ~100-200 | Reasonable performance |
| ~300+ | Weak model |
| Vocab size | Random prediction (worst case) |

### Perplexity for N-gram

```python
def ngram_perplexity(model, test_tokens: list[str]) -> float:
    """
    PP = exp(-1/N * sum(log P(w_i | w_{i-n+1}...w_{i-1})))
    Computed with n-gram smoothing.
    """
```

---

## Analysis

### Fluency and Coherence Analysis

```python
def analyze_generated_text(samples: dict[str, list[str]]) -> dict:
    """
    For each model:
    - Fluency: Grammatical correctness
    - Coherence: Topic consistency
    - Repetition: Repetition rate
    - Vocabulary diversity: Unique token ratio
    """

def compute_repetition_rate(text: str, n: int = 3) -> float:
    """Repeated n-gram ratio."""

def compute_distinct_n(texts: list[str], n: int = 2) -> float:
    """Unique n-gram ratio (diversity measure)."""
```

### Expected Comparison

| Dimension | N-gram | LSTM | GPT-2 (optional) |
|-----------|--------|------|-------------------|
| Perplexity | High (~200+) | Medium (~80-120) | Low (~30-50) |
| Fluency | Low | Medium | High |
| Coherence | Very low | Good in short-range | Good in long-range |
| Long-range | None (n window) | Limited | Strong |
| Training | Fast (counting) | Medium | Long |
| Memory | O(V^n) | O(params) | O(params) large |

---

## Expected Outputs

```
outputs/q5/run_{timestamp}/
|-- config.yaml
|-- metrics.json                   # Perplexity values
|-- generated_samples/
|   |-- ngram_samples.txt
|   |-- lstm_samples.txt
|   +-- gpt2_samples.txt           # optional
|-- analysis.json                  # Fluency, coherence analysis
|-- figures/
|   |-- perplexity_comparison.png
|   |-- training_curves_lstm.png
|   +-- loss_curves.png
+-- model_best_*.pt
```

---

## Config Example (q5.yaml)

```yaml
question: "q5"
task: "language_model"

dataset:
  name: "wikitext"
  config: "wikitext-2-raw-v1"

preprocess:
  tokenization: "word"
  min_freq: 3
  seq_length: 35

models:
  ngram:
    n: 3
    smoothing: "laplace"
    alpha: 1.0

  lstm:
    embed_dim: 200
    hidden_dim: 200
    num_layers: 2
    dropout: 0.2
    tie_weights: true
    batch_size: 20
    learning_rate: 20.0
    optimizer: "sgd"
    lr_scheduler: "plateau"
    lr_factor: 0.25
    gradient_clip: 0.25
    num_epochs: 40

  gpt2:                          # optional
    model_name: "gpt2"
    batch_size: 4
    learning_rate: 5e-5
    num_epochs: 3

generation:
  num_samples: 5
  max_length: 100
  temperatures: [0.5, 0.7, 1.0]
  top_k: 50

evaluation:
  metrics: ["perplexity"]
```

---

## Related Documents

- [Shared Infrastructure](03-shared-infrastructure.md) - Vocabulary, Trainer
- [Q4 - Machine Translation](07-q4-machine-translation.md) - Similar RNN/Transformer architectures
- [Evaluation Framework](09-evaluation-framework.md) - Perplexity details
- [Experiment Config](10-experiment-config.md) - Config structure
