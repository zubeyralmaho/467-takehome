# 05 - Q2: Named Entity Recognition

> [Ana Sayfa](README.md) | Onceki: [Q1 - Text Classification](04-q1-text-classification.md) | Sonraki: [Q3 - Summarization](06-q3-summarization.md)

---

## Hedef

Sequence labeling ve contextual modeling'i NER gorevi uzerinde incelemek. Klasik (CRF), hibrit (BiLSTM-CRF) ve transformer (BERT) yaklasimlarini karsilastirmak.

---

## Dataset: CoNLL-2003

### Ozellikler
- **Dil**: Ingilizce
- **Kaynak**: Reuters haber metinleri
- **Annotation**: IOB2 (BIO) tagging scheme
- **Entity turleri**: PER (Person), ORG (Organization), LOC (Location), MISC (Miscellaneous)
- **Boyut**:
  - Train: ~14,041 cumle / ~203K token
  - Dev (Val): ~3,250 cumle / ~51K token
  - Test: ~3,453 cumle / ~46K token
- **Kaynak**: `datasets.load_dataset("conll2003")`

### BIO Tagging Yapisi

```
Token:  Alex   is    from   New    York   City   .
BIO:    B-PER  O     O      B-LOC  I-LOC  I-LOC  O
```

| Tag | Anlam |
|-----|-------|
| B-{TYPE} | Entity baslangici |
| I-{TYPE} | Entity devami |
| O | Entity disinda |

### Label Listesi (9 etiket)
```
O, B-PER, I-PER, B-ORG, I-ORG, B-LOC, I-LOC, B-MISC, I-MISC
```

---

## Preprocessing

### preprocess.py

```python
def load_conll_data(split: str = "train") -> list[dict]:
    """
    HuggingFace'ten yukler, her ornek:
    {
        "tokens": ["Alex", "is", "from", "New", "York", "City", "."],
        "ner_tags": [3, 0, 0, 5, 6, 6, 0]  # numerik BIO
    }
    """

def align_labels_with_tokens(labels, word_ids):
    """
    BERT tokenizer subword alignment:
    - Ilk subword: orijinal label
    - Sonraki subwordlar: I-{TYPE} (B ise) veya ayni label
    - Special tokens ([CLS], [SEP]): -100 (ignore)
    """

def extract_features_for_crf(tokens: list[str]) -> list[dict]:
    """
    CRF icin el ile ozellik cikarimi:
    - word.lower(), word.isupper(), word.istitle()
    - word[-3:], word[-2:] (suffix)
    - word[:3], word[:2] (prefix)
    - Onceki/sonraki kelimenin ozellikleri (bigram context)
    - BOS/EOS flag
    - is_digit, has_hyphen
    """
```

### Token-Label Alignment Problemi (BERT icin)

```
Orjinal:     ["New",    "York",   "City"]
BERT tokens: ["new",    "york",   "city"]       -> basit durum
             ["New",    "York",   "Ci", "##ty"] -> subword durumu

Alignment:
"New"   -> B-LOC
"York"  -> I-LOC
"Ci"    -> I-LOC   (ilk subword, orijinal label)
"##ty"  -> -100    (ignore in loss)
```

---

## Model Mimarileri

### Model 1: CRF (Feature-based)

**Dosya**: `models/crf.py`

```python
class FeatureBasedCRF:
    """sklearn-crfsuite tabanli CRF modeli."""

    def __init__(self, algorithm: str = "lbfgs",
                 c1: float = 0.1, c2: float = 0.1,
                 max_iterations: int = 100):
        """
        algorithm: "lbfgs" veya "l2sgd"
        c1: L1 regularization
        c2: L2 regularization
        """

    def extract_features(self, sentence: list[str]) -> list[dict]:
        """Her token icin feature dict olusturur."""

    def fit(self, sentences, label_sequences) -> None: ...
    def predict(self, sentences) -> list[list[str]]: ...
```

**Feature Vector Ornegi**:
```python
{
    "bias": 1.0,
    "word.lower": "york",
    "word.isupper": False,
    "word.istitle": True,
    "word[-3:]": "ork",
    "word[-2:]": "rk",
    "postag": "NNP",          # opsiyonel POS tag
    "-1:word.lower": "new",   # onceki kelime
    "-1:word.istitle": True,
    "+1:word.lower": "city",  # sonraki kelime
    "BOS": False,
    "EOS": False
}
```

---

### Model 2: BiLSTM-CRF

**Dosya**: `models/bilstm_crf.py`

```python
class BiLSTMCRF(nn.Module):
    def __init__(self, vocab_size: int, tagset_size: int,
                 embed_dim: int = 100, hidden_dim: int = 256,
                 num_layers: int = 1, dropout: float = 0.5,
                 pretrained_embeddings=None):
        """
        Katmanlar:
        1. Word Embedding (GloVe opsiyonel)
        2. BiLSTM encoder
        3. Linear (hidden -> tagset)
        4. CRF layer (TorchCRF)
        """

    def forward(self, x, tags=None, mask=None):
        """
        Training: CRF negative log-likelihood loss
        Inference: CRF Viterbi decode
        """

    def _get_lstm_features(self, x):
        """embed -> BiLSTM -> linear -> emission scores"""

    def decode(self, x, mask=None):
        """Viterbi decoding ile en iyi tag sequence"""
```

**Mimari Diyagrami**:
```
Input:  [Alex]  [is]  [from]  [New]  [York]  [City]
          |      |      |       |      |       |
          v      v      v       v      v       v
    [Embedding Layer] (100d, GloVe init)
          |      |      |       |      |       |
          v      v      v       v      v       v
    [    BiLSTM (hidden=256, bidirectional)     ]
          |      |      |       |      |       |
          v      v      v       v      v       v
    [     Linear (512 -> 9 tags)               ]
          |      |      |       |      |       |
          v      v      v       v      v       v
    [     CRF Layer (transition matrix)        ]
          |      |      |       |      |       |
          v      v      v       v      v       v
Output: B-PER    O      O     B-LOC  I-LOC  I-LOC
```

**CRF Katmaninin Rolu**:
- Transition score matrisi: `T[i,j]` = tag_i'den tag_j'ye gecis skoru
- Gecersiz gecisleri penalize eder (orn: O -> I-PER)
- Viterbi algoritmasiyla global optimal tag sequence bulur
- BiLSTM'in emission scores'u + CRF transition scores = final scores

**Hyperparametreler**:
| Parametre | Deger |
|-----------|-------|
| embed_dim | 100 |
| hidden_dim | 256 |
| num_layers | 1 |
| dropout | 0.5 |
| batch_size | 32 |
| learning_rate | 0.01 (SGD) veya 1e-3 (Adam) |
| optimizer | SGD + momentum=0.9 (veya Adam) |
| max_epochs | 30 |
| early_stopping | patience=5 |
| gradient_clipping | max_norm=5.0 |

---

### Model 3: BERT-NER (Token Classification)

**Dosya**: `models/bert_ner.py`

```python
class BERTNERModel:
    def __init__(self, num_labels: int = 9,
                 model_name: str = "bert-base-cased"):
        """
        HuggingFace BertForTokenClassification wrapper.
        Onemli: NER icin cased model kullanilir (buyuk/kucuk harf bilgisi).
        """

    def tokenize_and_align(self, examples):
        """
        Batch tokenization + label alignment.
        Subword tokenlar icin -100 label atar.
        """

    def train(self, train_dataset, val_dataset, config): ...
    def predict(self, sentences) -> list[list[str]]: ...
```

**Fine-tuning Yapisi**:
```
[BERT-base-cased] (110M params)
        |
        v
[Token-level hidden states] (768d per token)
        |
        v
[Dropout (0.1)]
        |
        v
[Linear (768 -> 9)]  # her token icin tag tahmini
        |
        v
[CrossEntropyLoss]    # -100 label'li tokenlar ignore edilir
```

**Hyperparametreler**:
| Parametre | Deger |
|-----------|-------|
| model_name | bert-base-cased |
| max_seq_length | 128 |
| batch_size | 16 |
| learning_rate | 5e-5 |
| weight_decay | 0.01 |
| warmup_ratio | 0.1 |
| num_epochs | 5 |
| optimizer | AdamW |

---

## Evaluation

### Entity-Level Evaluation (seqeval)

```python
from seqeval.metrics import classification_report, f1_score

# Ornek:
y_true = [["B-PER", "O", "B-LOC", "I-LOC"]]
y_pred = [["B-PER", "O", "B-LOC", "O"]]     # boundary error!

# Entity-level hesaplama:
# PER: 1 correct / 1 true / 1 pred -> P=1.0, R=1.0, F1=1.0
# LOC: 0 correct / 1 true / 0 pred -> P=0.0, R=0.0, F1=0.0
# (Cunku "New York City" tahmininde "York City" eksik -> entity eslesmedi)
```

### Metrikler

| Metrik | Aciklama | Hesaplama Seviyesi |
|--------|----------|-------------------|
| Precision | Dogru tahmin / Toplam tahmin | Entity-level |
| Recall | Dogru tahmin / Toplam gercek | Entity-level |
| F1-score | 2*P*R / (P+R) | Entity-level, per-type + micro avg |

---

## Error Analysis

### analysis.py

```python
def analyze_ner_errors(y_true, y_pred, tokens) -> dict:
    """
    Hata kategorileri:
    1. Boundary errors: Entity sinirlari yanlis (B-LOC I-LOC vs B-LOC O)
    2. Type confusion: Dogru sinir, yanlis tip (B-PER vs B-ORG)
    3. Missing entities: Gercek entity tamamen kacirilmis
    4. Spurious entities: Olmayan entity tahmin edilmis
    """

def analyze_by_entity_type(y_true, y_pred) -> pd.DataFrame:
    """PER, ORG, LOC, MISC icin ayri metrikler."""

def contextual_embedding_analysis(model, examples) -> None:
    """Contextual embedding'lerin NER'e katkisini tartis."""
```

### Tipik Hata Ornekleri

| Hata Turu | Ornek | Aciklama |
|-----------|-------|----------|
| Boundary | "New York" -> B-LOC O | Entity sinirlari eksik |
| Type confusion | "Apple" -> B-ORG vs B-MISC | Sirket mi, meyve mi? |
| Missing | "EU" -> O | Kisaltma taninmamis |
| Spurious | "Monday" -> B-MISC | Zaman ifadesi entity degil |

---

## Beklenen Ciktilar

```
outputs/q2/run_{timestamp}/
|-- config.yaml
|-- metrics.json                    # Entity-level P/R/F1
|-- per_entity_metrics.csv          # PER, ORG, LOC, MISC ayri
|-- predictions/
|   |-- crf_preds.txt               # CoNLL format
|   |-- bilstm_crf_preds.txt
|   +-- bert_ner_preds.txt
|-- error_analysis.json
|-- figures/
|   |-- entity_f1_comparison.png
|   |-- error_type_distribution.png
|   |-- training_curves_bilstm_crf.png
|   +-- training_curves_bert.png
+-- model_best_*.pt
```

---

## Config Ornegi (q2.yaml)

```yaml
question: "q2"
task: "ner"

dataset:
  name: "conll2003"

preprocess:
  max_seq_length: 128

models:
  crf:
    algorithm: "lbfgs"
    c1: 0.1
    c2: 0.1
    max_iterations: 100

  bilstm_crf:
    embed_dim: 100
    hidden_dim: 256
    num_layers: 1
    dropout: 0.5
    pretrained_embeddings: "glove-6B-100d"
    batch_size: 32
    learning_rate: 0.01
    optimizer: "sgd"
    momentum: 0.9
    num_epochs: 30
    gradient_clip: 5.0

  bert_ner:
    model_name: "bert-base-cased"
    max_seq_length: 128
    batch_size: 16
    learning_rate: 5e-5
    weight_decay: 0.01
    warmup_ratio: 0.1
    num_epochs: 5

evaluation:
  metrics: ["precision", "recall", "f1"]
  per_entity_type: true
```

---

## Iliskili Dokumanlar

- [Ortak Altyapi](03-shared-infrastructure.md) - Trainer, vocab, metrics
- [Evaluation Framework](09-evaluation-framework.md) - Entity-level evaluation detaylari
- [Q1 - Text Classification](04-q1-text-classification.md) - Ayni embedding/BERT yaklasimi
