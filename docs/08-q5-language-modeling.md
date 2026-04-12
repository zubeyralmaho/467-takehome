# 08 - Q5: Language Modeling

> [Ana Sayfa](README.md) | Onceki: [Q4 - Machine Translation](07-q4-machine-translation.md) | Sonraki: [Evaluation Framework](09-evaluation-framework.md)

---

## Hedef

Olasiliksal sequence modelling ve text generation'i incelemek. N-gram, LSTM ve opsiyonel olarak transformer-based modelleri karsilastirmak. Perplexity ile degerlendirmek, olusturulan metinlerin akicilik ve tutarliligini analiz etmek.

---

## Dataset: WikiText-2

### Ozellikler
- **Boyut**: ~2M token (train), ~217K token (val), ~245K token (test)
- **Icerik**: Wikipedia makaleleri (Good/Featured Articles)
- **Vocabulary**: ~33K unique token
- **Kaynak**: `datasets.load_dataset("wikitext", "wikitext-2-raw-v1")`

### Alternatif: Penn Treebank (PTB)
- **Boyut**: ~929K train / ~73K val / ~82K test token
- **Daha kucuk vocabulary**: ~10K
- **Avantaj**: Daha kucuk, hizli deney; NLP'de standard benchmark

### Secim Onerisi
WikiText-2 tercih edilir (daha buyuk, daha modern, daha temiz).

---

## Preprocessing

### preprocess.py

```python
def load_and_tokenize(dataset_name: str = "wikitext-2",
                      tokenizer_type: str = "word") -> dict:
    """
    1. Raw metni yukle
    2. Bos satirlari filtrele
    3. Tokenize et (word-level)
    4. Vocabulary olustur
    """

def create_sequences(token_ids: list[int],
                     seq_length: int = 35) -> tuple:
    """
    Sliding window ile input/target cifti olustur:
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
        Her __getitem__: (seq_length,) input, (seq_length,) target
        """

def batchify(data: torch.Tensor, batch_size: int) -> torch.Tensor:
    """
    Veriyi batch_size sayida esit parcaya boler.
    Standard LM batchification:
    data shape: (total_tokens,) -> (total_tokens // batch_size, batch_size)
    """
```

---

## Model Mimarileri

### Model 1: N-gram Language Model

**Dosya**: `models/ngram.py`

```python
class NGramLanguageModel:
    """
    N-gram LM with smoothing.
    Bigram ve Trigram destegi.
    """

    def __init__(self, n: int = 3,
                 smoothing: str = "laplace",
                 alpha: float = 1.0):
        """
        n: n-gram boyutu (2=bigram, 3=trigram)
        smoothing: "laplace" (add-k), "kneser_ney", veya "interpolation"
        """

    def fit(self, token_sequences: list[list[str]]) -> None:
        """
        N-gram sayimlarini olusturur:
        - Unigram counts
        - Bigram counts
        - Trigram counts (n=3 ise)
        """

    def probability(self, token: str, context: tuple) -> float:
        """P(token | context) hesaplar, smoothing ile."""

    def perplexity(self, token_sequence: list[str]) -> float:
        """
        PP = exp(-1/N * sum(log P(w_i | context)))
        """

    def generate(self, seed_tokens: list[str],
                 max_length: int = 50,
                 temperature: float = 1.0) -> list[str]:
        """
        Olasilik dagilimina gore sampling ile text uretimi.
        temperature: <1 conservative, >1 creative
        """
```

**N-gram Smoothing Yontemleri**:

| Yontem | Formul (basitlestirilmis) | Avantaj |
|--------|--------------------------|---------|
| Laplace (Add-1) | (count + 1) / (total + V) | Basit |
| Add-k | (count + k) / (total + kV) | k ayarlanabilir |
| Kneser-Ney | Discount + backoff | En iyi performans |
| Linear Interpolation | lambda1*P_tri + lambda2*P_bi + lambda3*P_uni | Dengeli |

**Parametreler**:
| Parametre | Deger |
|-----------|-------|
| n | 3 (trigram) |
| smoothing | Laplace veya Kneser-Ney |
| alpha (Laplace) | 1.0 |

---

### Model 2: LSTM Language Model

**Dosya**: `models/lstm_lm.py`

```python
class LSTMLanguageModel(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 200,
                 hidden_dim: int = 200, num_layers: int = 2,
                 dropout: float = 0.2, tie_weights: bool = True):
        """
        Katmanlar:
        1. Embedding
        2. LSTM (multi-layer)
        3. Dropout
        4. Linear (hidden -> vocab)

        tie_weights: Embedding ve output projection agirliklarini paylas
        (parametre tasarrufu + performance artisi)
        """

    def forward(self, x, hidden):
        """
        x: (batch, seq_len) token indices
        hidden: (h_0, c_0) tuple

        Output: (batch, seq_len, vocab_size) logits, new_hidden
        """

    def init_hidden(self, batch_size: int):
        """Sifir-initialize hidden state."""

    def generate(self, seed_indices: list[int], max_length: int = 100,
                 temperature: float = 1.0,
                 top_k: int = None) -> list[int]:
        """
        Autoregressive text generation:
        1. Seed ile baslat
        2. Her adimda:
           a. Forward pass
           b. Son adimin logits'ini al
           c. temperature / top-k sampling
           d. Sonraki token'i sec
        3. max_length'e kadar devam et
        """
```

**Mimari Diyagrami**:
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
- Parametre sayisini onemli olcude azaltir
- Embedding ve output space'i tutarli yapar

**Hyperparametreler**:
| Parametre | Deger |
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

> Not: SGD + yuksek LR + agresif clipping, AWD-LSTM stiline yakin bir yaklasimdir. Adam (lr=1e-3) de alternatiftir.

---

### Model 3 (Opsiyonel): GPT-2 Fine-tuning

**Dosya**: `models/gpt2_lm.py`

```python
class GPT2LanguageModel:
    """
    GPT-2 small (117M params) fine-tuning.
    Opsiyonel ama onemli karsilastirma.
    """

    def __init__(self, model_name: str = "gpt2"):
        """HuggingFace GPT2LMHeadModel yukler."""

    def fine_tune(self, train_text, val_text, config):
        """
        Causal LM fine-tuning.
        HuggingFace Trainer kullanir.
        """

    def compute_perplexity(self, text: str) -> float:
        """Model perplexity hesaplar."""

    def generate(self, prompt: str, max_length: int = 100,
                 temperature: float = 0.7,
                 top_k: int = 50, top_p: float = 0.9) -> str:
        """Nucleus sampling ile generation."""
```

---

## Text Generation

### generate.py

```python
def generate_samples(model, vocab, config,
                     num_samples: int = 5) -> list[str]:
    """
    Her model icin kisa metin ornekleri uretir.
    Farkli sampling stratejileri dener.
    """

# Sampling Stratejileri:
def greedy_decode(logits):
    """argmax - en olasilikli token"""

def temperature_sampling(logits, temperature=1.0):
    """logits / temperature -> softmax -> sample"""

def top_k_sampling(logits, k=50):
    """En yuksek k token arasindan sample"""

def nucleus_sampling(logits, p=0.9):
    """Kumulatif olasilik p'ye kadar olan tokenlar arasindan sample"""
```

### Sampling Stratejileri Karsilastirmasi

| Strateji | temperature | Ozellik |
|----------|-------------|---------|
| Greedy | - | Deterministic, tekrarli |
| Low temp | 0.5 | Conservative, tutarli |
| Normal | 1.0 | Dengeli |
| High temp | 1.5 | Yaratici, kaorik |
| Top-k (k=50) | 1.0 | Dusuk olasilikli tokenlari filtreler |
| Nucleus (p=0.9) | 1.0 | Dinamik filtreleme |

---

## Evaluation

### Perplexity

```python
def compute_perplexity(model, test_loader, criterion) -> float:
    """
    PP = exp(average cross-entropy loss)

    1. Model'i eval moduna al
    2. Tum test batch'leri uzerinde loss hesapla
    3. Ortalama loss al
    4. exp(avg_loss) = perplexity
    """
```

**Perplexity Yorumu**:
| Deger | Anlam |
|-------|-------|
| ~1 | Mukemmel tahmin (mumkun degil) |
| ~60-100 | Iyi LSTM performansi (WikiText-2) |
| ~100-200 | Makul performans |
| ~300+ | Zayif model |
| Vocab size | Random tahmin (en kotu) |

### N-gram icin Perplexity

```python
def ngram_perplexity(model, test_tokens: list[str]) -> float:
    """
    PP = exp(-1/N * sum(log P(w_i | w_{i-n+1}...w_{i-1})))
    N-gram smoothing ile hesaplanir.
    """
```

---

## Analysis

### Fluency ve Coherence Analizi

```python
def analyze_generated_text(samples: dict[str, list[str]]) -> dict:
    """
    Her model icin:
    - Fluency: Gramatikal dogruluk
    - Coherence: Konu tutarliligi
    - Repetition: Tekrar orani
    - Vocabulary diversity: Unique token orani
    """

def compute_repetition_rate(text: str, n: int = 3) -> float:
    """Tekrarlanan n-gram orani."""

def compute_distinct_n(texts: list[str], n: int = 2) -> float:
    """Unique n-gram orani (diversity olcusu)."""
```

### Beklenen Karsilastirma

| Boyut | N-gram | LSTM | GPT-2 (opsiyonel) |
|-------|--------|------|-------------------|
| Perplexity | Yuksek (~200+) | Orta (~80-120) | Dusuk (~30-50) |
| Fluency | Dusuk | Orta | Yuksek |
| Coherence | Cok dusuk | Kisa vadede iyi | Uzun vadede iyi |
| Long-range | Yok (n window) | Sinirli | Guclu |
| Training | Hizli (sayim) | Orta | Uzun |
| Memory | O(V^n) | O(params) | O(params) buyuk |

---

## Beklenen Ciktilar

```
outputs/q5/run_{timestamp}/
|-- config.yaml
|-- metrics.json                   # Perplexity degerleri
|-- generated_samples/
|   |-- ngram_samples.txt
|   |-- lstm_samples.txt
|   +-- gpt2_samples.txt           # opsiyonel
|-- analysis.json                  # Fluency, coherence analizi
|-- figures/
|   |-- perplexity_comparison.png
|   |-- training_curves_lstm.png
|   +-- loss_curves.png
+-- model_best_*.pt
```

---

## Config Ornegi (q5.yaml)

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

  gpt2:                          # opsiyonel
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

## Iliskili Dokumanlar

- [Ortak Altyapi](03-shared-infrastructure.md) - Vocabulary, Trainer
- [Q4 - Machine Translation](07-q4-machine-translation.md) - Benzer RNN/Transformer mimarileri
- [Evaluation Framework](09-evaluation-framework.md) - Perplexity detaylari
- [Experiment Config](10-experiment-config.md) - Config yapisi
