# 05 - Q2: Named Entity Recognition

> [Home](README.md) | Previous: [Q1 - Text Classification](04-q1-text-classification.md) | Next: [Q3 - Summarization](06-q3-summarization.md)

---

## Objective

Investigate sequence labeling and contextual modeling on the NER task. Compare classical (CRF), hybrid (BiLSTM-CRF), and transformer (BERT) approaches.

---

## Dataset: CoNLL-2003

### Properties
- **Language**: English
- **Source**: Reuters news articles
- **Annotation**: IOB2 (BIO) tagging scheme
- **Entity types**: PER (Person), ORG (Organization), LOC (Location), MISC (Miscellaneous)
- **Size**:
  - Train: ~14,041 sentences / ~203K tokens
  - Dev (Val): ~3,250 sentences / ~51K tokens
  - Test: ~3,453 sentences / ~46K tokens
- **Source**: `datasets.load_dataset("conll2003")`

### BIO Tagging Structure

```
Token:  Alex   is    from   New    York   City   .
BIO:    B-PER  O     O      B-LOC  I-LOC  I-LOC  O
```

| Tag | Meaning |
|-----|---------|
| B-{TYPE} | Entity beginning |
| I-{TYPE} | Entity continuation |
| O | Outside entity |

### Label List (9 labels)
```
O, B-PER, I-PER, B-ORG, I-ORG, B-LOC, I-LOC, B-MISC, I-MISC
```

---

## Preprocessing

### preprocess.py

```python
def load_conll_data(split: str = "train") -> list[dict]:
    """
    Loads from HuggingFace, each example:
    {
        "tokens": ["Alex", "is", "from", "New", "York", "City", "."],
        "ner_tags": [3, 0, 0, 5, 6, 6, 0]  # numeric BIO
    }
    """

def align_labels_with_tokens(labels, word_ids):
    """
    BERT tokenizer subword alignment:
    - First subword: original label
    - Subsequent subwords: I-{TYPE} (if B) or same label
    - Special tokens ([CLS], [SEP]): -100 (ignore)
    """

def extract_features_for_crf(tokens: list[str]) -> list[dict]:
    """
    Manual feature extraction for CRF:
    - word.lower(), word.isupper(), word.istitle()
    - word[-3:], word[-2:] (suffix)
    - word[:3], word[:2] (prefix)
    - Previous/next word features (bigram context)
    - BOS/EOS flag
    - is_digit, has_hyphen
    """
```

### Token-Label Alignment Problem (for BERT)

```
Original:    ["New",    "York",   "City"]
BERT tokens: ["new",    "york",   "city"]       -> simple case
             ["New",    "York",   "Ci", "##ty"] -> subword case

Alignment:
"New"   -> B-LOC
"York"  -> I-LOC
"Ci"    -> I-LOC   (first subword, original label)
"##ty"  -> -100    (ignore in loss)
```

---

## Model Architectures

### Model 1: CRF (Feature-based)

**File**: `models/crf.py`

```python
class FeatureBasedCRF:
    """CRF model based on sklearn-crfsuite."""

    def __init__(self, algorithm: str = "lbfgs",
                 c1: float = 0.1, c2: float = 0.1,
                 max_iterations: int = 100):
        """
        algorithm: "lbfgs" or "l2sgd"
        c1: L1 regularization
        c2: L2 regularization
        """

    def extract_features(self, sentence: list[str]) -> list[dict]:
        """Creates a feature dict for each token."""

    def fit(self, sentences, label_sequences) -> None: ...
    def predict(self, sentences) -> list[list[str]]: ...
```

**Feature Vector Example**:
```python
{
    "bias": 1.0,
    "word.lower": "york",
    "word.isupper": False,
    "word.istitle": True,
    "word[-3:]": "ork",
    "word[-2:]": "rk",
    "postag": "NNP",          # optional POS tag
    "-1:word.lower": "new",   # previous word
    "-1:word.istitle": True,
    "+1:word.lower": "city",  # next word
    "BOS": False,
    "EOS": False
}
```

---

### Model 2: BiLSTM-CRF

**File**: `models/bilstm_crf.py`

```python
class BiLSTMCRF(nn.Module):
    def __init__(self, vocab_size: int, tagset_size: int,
                 embed_dim: int = 100, hidden_dim: int = 256,
                 num_layers: int = 1, dropout: float = 0.5,
                 pretrained_embeddings=None):
        """
        Layers:
        1. Word Embedding (GloVe optional)
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
        """Best tag sequence via Viterbi decoding"""
```

**Architecture Diagram**:
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

**Role of the CRF Layer**:
- Transition score matrix: `T[i,j]` = transition score from tag_i to tag_j
- Penalizes invalid transitions (e.g., O -> I-PER)
- Finds the globally optimal tag sequence via the Viterbi algorithm
- BiLSTM emission scores + CRF transition scores = final scores

**Hyperparameters**:
| Parameter | Value |
|-----------|-------|
| embed_dim | 100 |
| hidden_dim | 256 |
| num_layers | 1 |
| dropout | 0.5 |
| batch_size | 32 |
| learning_rate | 0.01 (SGD) or 1e-3 (Adam) |
| optimizer | SGD + momentum=0.9 (or Adam) |
| max_epochs | 30 |
| early_stopping | patience=5 |
| gradient_clipping | max_norm=5.0 |

---

### Model 3: BERT-NER (Token Classification)

**File**: `models/bert_ner.py`

```python
class BERTNERModel:
    def __init__(self, num_labels: int = 9,
                 model_name: str = "bert-base-cased"):
        """
        HuggingFace BertForTokenClassification wrapper.
        Important: A cased model is used for NER (case information matters).
        """

    def tokenize_and_align(self, examples):
        """
        Batch tokenization + label alignment.
        Assigns -100 label for subword tokens.
        """

    def train(self, train_dataset, val_dataset, config): ...
    def predict(self, sentences) -> list[list[str]]: ...
```

**Fine-tuning Structure**:
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
[Linear (768 -> 9)]  # tag prediction for each token
        |
        v
[CrossEntropyLoss]    # tokens with -100 label are ignored
```

**Hyperparameters**:
| Parameter | Value |
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

# Example:
y_true = [["B-PER", "O", "B-LOC", "I-LOC"]]
y_pred = [["B-PER", "O", "B-LOC", "O"]]     # boundary error!

# Entity-level computation:
# PER: 1 correct / 1 true / 1 pred -> P=1.0, R=1.0, F1=1.0
# LOC: 0 correct / 1 true / 0 pred -> P=0.0, R=0.0, F1=0.0
# (Because "New York City" prediction is missing "York City" -> entity did not match)
```

### Metrics

| Metric | Description | Computation Level |
|--------|-------------|-------------------|
| Precision | Correct predictions / Total predictions | Entity-level |
| Recall | Correct predictions / Total actual | Entity-level |
| F1-score | 2*P*R / (P+R) | Entity-level, per-type + micro avg |

---

## Error Analysis

### analysis.py

```python
def analyze_ner_errors(y_true, y_pred, tokens) -> dict:
    """
    Error categories:
    1. Boundary errors: Entity boundaries are wrong (B-LOC I-LOC vs B-LOC O)
    2. Type confusion: Correct boundary, wrong type (B-PER vs B-ORG)
    3. Missing entities: True entity completely missed
    4. Spurious entities: Non-existent entity predicted
    """

def analyze_by_entity_type(y_true, y_pred) -> pd.DataFrame:
    """Separate metrics for PER, ORG, LOC, MISC."""

def contextual_embedding_analysis(model, examples) -> None:
    """Discuss the contribution of contextual embeddings to NER."""
```

### Typical Error Examples

| Error Type | Example | Description |
|------------|---------|-------------|
| Boundary | "New York" -> B-LOC O | Entity boundaries incomplete |
| Type confusion | "Apple" -> B-ORG vs B-MISC | Company or fruit? |
| Missing | "EU" -> O | Abbreviation not recognized |
| Spurious | "Monday" -> B-MISC | Time expression is not an entity |

---

## Expected Outputs

```
outputs/q2/run_{timestamp}/
|-- config.yaml
|-- metrics.json                    # Entity-level P/R/F1
|-- per_entity_metrics.csv          # PER, ORG, LOC, MISC separate
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

Dedicated comparison/reporting runs may additionally write:

```
outputs/q2/run_{timestamp}/
|-- comparison_manifest.json
|-- overall_model_comparison.csv
|-- overall_model_comparison.tex
|-- per_entity_model_comparison.csv
|-- per_entity_model_comparison.tex
+-- figures/
    +-- entity_f1_comparison.png
```

---

## Config Example (q2.yaml)

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

## Related Documents

- [Shared Infrastructure](03-shared-infrastructure.md) - Trainer, vocab, metrics
- [Evaluation Framework](09-evaluation-framework.md) - Entity-level evaluation details
- [Q1 - Text Classification](04-q1-text-classification.md) - Same embedding/BERT approach
