# 04 - Q1: Text Classification (Representation Learning)

> [Home](README.md) | Previous: [Shared Infrastructure](03-shared-infrastructure.md) | Next: [Q2 - NER](05-q2-ner.md)

---

## Objective

To analyze the effect of different representation learning strategies (sparse/TF-IDF, dense/embedding, contextual/transformer) on classification performance and generalizability.

---

## Dataset

### IMDb Movie Reviews
- **Size**: 50,000 reviews (25K train, 25K test)
- **Classes**: 2 (positive, negative) - balanced distribution
- **Average length**: ~230 words
- **Source**: `datasets.load_dataset("imdb")`

### Split Strategy
```
Original Train (25K) -> Train (20K) + Validation (5K)   [stratified]
Original Test  (25K) -> Test (25K)                       [unchanged]
```

> The test set is used only **once**, for final evaluation.

---

## Preprocessing Pipeline

### preprocess.py Module

```python
class TextPreprocessor:
    def __init__(self, config):
        self.lowercase = config.preprocess.lowercase        # True
        self.remove_html = config.preprocess.remove_html    # True
        self.remove_special = config.preprocess.remove_special  # True
        self.remove_stopwords = config.preprocess.remove_stopwords  # experiment
        self.max_length = config.preprocess.max_length      # 256/512

    def __call__(self, text: str) -> str:
        """Pipeline: HTML strip -> lowercase -> special char -> stopword"""
```

### Tokenization Strategies (Comparison Required)

| Strategy | Description | Used In Model |
|----------|-------------|---------------|
| **Word-level** | Whitespace + punctuation split | TF-IDF, BiLSTM |
| **Subword (WordPiece)** | DistilBERT tokenizer | DistilBERT |
| (Optional) **Character n-gram** | char_wb for TF-IDF | TF-IDF variant |

### Preprocessing Comparison Experiment

The effect of the following settings is measured (quick sweep on TF-IDF+LR):

| Experiment | Stopword | Lowercase | Max Features |
|------------|----------|-----------|--------------|
| A          | Remove   | Yes       | 50,000       |
| B          | Keep     | Yes       | 50,000       |
| C          | Remove   | Yes       | 100,000      |
| D          | Keep     | No        | 50,000       |

---

## Model Architectures

### Model 1: TF-IDF + Logistic Regression / SVM

**File**: `models/tfidf_classifier.py`

```python
class TFIDFClassifier:
    def __init__(self, classifier_type: str = "lr",
                 max_features: int = 50000,
                 ngram_range: tuple = (1, 2)):
        """
        classifier_type: "lr" (LogisticRegression) or "svm" (LinearSVC)
        TfidfVectorizer + classifier pipeline
        """

    def fit(self, texts: list[str], labels: list[int]) -> None: ...
    def predict(self, texts: list[str]) -> np.ndarray: ...
    def predict_proba(self, texts: list[str]) -> np.ndarray: ...
```

**Pipeline**:
```
Raw Text -> TextPreprocessor -> TfidfVectorizer -> LR/SVM -> Label
```

**Hyperparameters**:
| Parameter | Value |
|-----------|-------|
| max_features | 50,000 |
| ngram_range | (1, 2) |
| LR: C | 1.0 |
| LR: max_iter | 1000 |
| SVM: C | 1.0 |

---

### Model 2: BiLSTM

**File**: `models/bilstm.py`

```python
class BiLSTMClassifier(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 300,
                 hidden_dim: int = 256, num_layers: int = 2,
                 dropout: float = 0.3, num_classes: int = 2,
                 pretrained_embeddings: torch.Tensor = None):
        """
        Layers:
        1. Embedding (optional GloVe pretrained)
        2. Bidirectional LSTM (2 layers)
        3. Dropout
        4. Linear classification head
        """

    def forward(self, x, lengths):
        """
        x: (batch, seq_len) token indices
        lengths: (batch,) actual lengths (excluding padding)

        Flow:
        embed -> pack_padded -> BiLSTM -> unpack -> last hidden concat -> dropout -> fc
        """
```

**Architecture Diagram**:
```
Input Tokens: [CLS] the movie was great [PAD] [PAD]
      |
      v
[Embedding Layer] (300d, GloVe init)
      |
      v
[BiLSTM Layer 1] (hidden=256, bidirectional)
      |
      v
[BiLSTM Layer 2] (hidden=256, bidirectional)
      |
      v
[Concat: forward_last + backward_last] -> (512d)
      |
      v
[Dropout (0.3)]
      |
      v
[Linear (512 -> 2)]
      |
      v
Prediction: positive
```

**Hyperparameters**:
| Parameter | Value |
|-----------|-------|
| embed_dim | 300 |
| hidden_dim | 256 |
| num_layers | 2 |
| dropout | 0.3 |
| batch_size | 64 |
| learning_rate | 1e-3 |
| optimizer | Adam |
| max_epochs | 10 |
| early_stopping | patience=3 |
| max_seq_length | 256 |
| pretrained | GloVe 6B 300d |

---

### Model 3: DistilBERT

**File**: `models/distilbert.py`

```python
class DistilBERTClassifier:
    def __init__(self, num_classes: int = 2,
                 model_name: str = "distilbert-base-uncased",
                 learning_rate: float = 2e-5):
        """
        HuggingFace DistilBertForSequenceClassification wrapper.
        """

    def get_tokenizer(self):
        """Returns DistilBertTokenizer."""

    def create_dataset(self, texts, labels, max_length=512):
        """HuggingFace Dataset + tokenization."""

    def train(self, train_dataset, val_dataset, config):
        """Fine-tuning with HuggingFace Trainer or custom loop."""

    def predict(self, texts):
        """Inference."""
```

**Fine-tuning Strategy**:
```
[DistilBERT Pretrained Weights] (66M params)
        |
        v
[All layers unfrozen] (full fine-tuning)
        |
        v
[Classification Head: Linear(768 -> 2)]
        |
        v
[AdamW + Linear Warmup + Weight Decay]
```

**Hyperparameters**:
| Parameter | Value |
|-----------|-------|
| model_name | distilbert-base-uncased |
| max_seq_length | 512 |
| batch_size | 16 |
| learning_rate | 2e-5 |
| weight_decay | 0.01 |
| warmup_steps | 10% of total |
| num_epochs | 3 |
| optimizer | AdamW |
| scheduler | linear warmup |

---

## Training Flow

**File**: `train.py`

```python
def run_training(config: Config):
    """
    1. Load data + preprocess
    2. Train all models sequentially:
       a. TF-IDF + LR  (sklearn .fit)
       b. TF-IDF + SVM (sklearn .fit)
       c. BiLSTM        (Trainer loop)
       d. DistilBERT    (HF Trainer / custom loop)
    3. Save validation metrics for each model
    4. Run test evaluation for the best models
    """
```

---

## Analysis & Error Patterns

**File**: `analysis.py`

```python
def analyze_misclassifications(texts, y_true, y_pred,
                                n_examples: int = 5) -> list[dict]:
    """
    Selects at least 5 misclassified examples.
    For each example:
    - Original text (truncated)
    - True label
    - Predicted label
    - Model confidence (if available)
    - Possible error reason (pattern)
    """

def identify_error_patterns(misclassified: list[dict]) -> dict:
    """
    Common error patterns:
    - Irony/sarcasm
    - Mixed sentiment
    - Negation handling errors
    - Domain-specific jargon
    - Very short/long texts
    """
```

---

## Expected Outputs

```
outputs/q1/run_{timestamp}/
|-- config.yaml               # Config used
|-- preprocessing_comparison.csv  # Tokenization/preprocessing impact table
|-- metrics.json               # All model metrics
|-- predictions/
|   |-- tfidf_lr_preds.csv
|   |-- tfidf_svm_preds.csv
|   |-- bilstm_preds.csv
|   +-- distilbert_preds.csv
|-- misclassification_analysis.json
|-- figures/
|   |-- confusion_matrix_*.png
|   |-- training_curves_bilstm.png
|   |-- training_curves_distilbert.png
|   +-- model_comparison.png
+-- model_best_*.pt
```

---

## Config Example (q1.yaml)

```yaml
question: "q1"
task: "classification"

dataset:
  name: "imdb"
  val_split_ratio: 0.2    # validation ratio to split from train

preprocess:
  lowercase: true
  remove_html: true
  remove_special: true
  remove_stopwords: false
  max_length: 256          # for BiLSTM

models:
  tfidf_lr:
    max_features: 50000
    ngram_range: [1, 2]
    classifier: "lr"
    C: 1.0

  tfidf_svm:
    max_features: 50000
    ngram_range: [1, 2]
    classifier: "svm"
    C: 1.0

  bilstm:
    embed_dim: 300
    hidden_dim: 256
    num_layers: 2
    dropout: 0.3
    pretrained_embeddings: "glove-6B-300d"
    batch_size: 64
    learning_rate: 0.001
    num_epochs: 10

  distilbert:
    model_name: "distilbert-base-uncased"
    max_seq_length: 512
    batch_size: 16
    learning_rate: 2e-5
    weight_decay: 0.01
    num_epochs: 3

evaluation:
  metrics: ["accuracy", "macro_f1"]
  num_misclassified_examples: 5
```

---

## Representation Comparison Framework

Comparison to be presented in the report:

| Dimension | TF-IDF (Sparse) | BiLSTM (Dense) | DistilBERT (Contextual) |
|-----------|-----------------|----------------|------------------------|
| Representation | Bag-of-words, n-gram | Static embeddings | Contextual embeddings |
| Dimensionality | ~50K sparse | 300d dense | 768d contextual |
| Context-aware? | No | No (static) | Yes |
| Training time | Seconds | Minutes | Minutes-hours |
| Interpretability | High (feature weights) | Low | Very low |
| Performance | Good baseline | Medium-good | Highest |

---

## Related Documents

- [Shared Infrastructure](03-shared-infrastructure.md) - Trainer, Evaluator, metrics
- [Evaluation Framework](09-evaluation-framework.md) - Accuracy, Macro-F1 details
- [Experiment Config](10-experiment-config.md) - Config structure
- [LaTeX Report](11-report-structure.md) - Q1 section structure