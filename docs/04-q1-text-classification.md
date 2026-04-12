# 04 - Q1: Text Classification (Representation Learning)

> [Ana Sayfa](README.md) | Onceki: [Ortak Altyapi](03-shared-infrastructure.md) | Sonraki: [Q2 - NER](05-q2-ner.md)

---

## Hedef

Farkli representation learning stratejilerinin (sparse/TF-IDF, dense/embedding, contextual/transformer) siniflandirma performansina ve genellestirilirlige etkisini analiz etmek.

---

## Dataset

### IMDb Movie Reviews
- **Boyut**: 50,000 review (25K train, 25K test)
- **Siniflar**: 2 (positive, negative) - dengeli dagilim
- **Ortalama uzunluk**: ~230 kelime
- **Kaynak**: `datasets.load_dataset("imdb")`

### Split Stratejisi
```
Orijinal Train (25K) -> Train (20K) + Validation (5K)   [stratified]
Orijinal Test  (25K) -> Test (25K)                       [degistirilmez]
```

> Test seti yalnizca **bir kez**, final evaluation icin kullanilir.

---

## Preprocessing Pipeline

### preprocess.py Modulu

```python
class TextPreprocessor:
    def __init__(self, config):
        self.lowercase = config.preprocess.lowercase        # True
        self.remove_html = config.preprocess.remove_html    # True
        self.remove_special = config.preprocess.remove_special  # True
        self.remove_stopwords = config.preprocess.remove_stopwords  # deney
        self.max_length = config.preprocess.max_length      # 256/512

    def __call__(self, text: str) -> str:
        """Pipeline: HTML strip -> lowercase -> special char -> stopword"""
```

### Tokenization Stratejileri (Karsilastirma Gerekli)

| Strateji | Aciklama | Kullanildigi Model |
|----------|----------|--------------------|
| **Word-level** | Whitespace + punctuation split | TF-IDF, BiLSTM |
| **Subword (WordPiece)** | DistilBERT tokenizer | DistilBERT |
| (Opsiyonel) **Character n-gram** | TF-IDF icin char_wb | TF-IDF varyant |

### Preprocessing Karsilastirma Deneyi

Asagidaki ayarlarin etkisi olculur (TF-IDF+LR uzerinde hizli sweep):

| Deney | Stopword | Lowercase | Max Features |
|-------|----------|-----------|--------------|
| A     | Kaldir   | Evet      | 50,000       |
| B     | Birak    | Evet      | 50,000       |
| C     | Kaldir   | Evet      | 100,000      |
| D     | Birak    | Hayir     | 50,000       |

---

## Model Mimarileri

### Model 1: TF-IDF + Logistic Regression / SVM

**Dosya**: `models/tfidf_classifier.py`

```python
class TFIDFClassifier:
    def __init__(self, classifier_type: str = "lr",
                 max_features: int = 50000,
                 ngram_range: tuple = (1, 2)):
        """
        classifier_type: "lr" (LogisticRegression) veya "svm" (LinearSVC)
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

**Hyperparametreler**:
| Parametre | Deger |
|-----------|-------|
| max_features | 50,000 |
| ngram_range | (1, 2) |
| LR: C | 1.0 |
| LR: max_iter | 1000 |
| SVM: C | 1.0 |

---

### Model 2: BiLSTM

**Dosya**: `models/bilstm.py`

```python
class BiLSTMClassifier(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 300,
                 hidden_dim: int = 256, num_layers: int = 2,
                 dropout: float = 0.3, num_classes: int = 2,
                 pretrained_embeddings: torch.Tensor = None):
        """
        Katmanlar:
        1. Embedding (opsiyonel GloVe pretrained)
        2. Bidirectional LSTM (2 katman)
        3. Dropout
        4. Linear classification head
        """

    def forward(self, x, lengths):
        """
        x: (batch, seq_len) token indices
        lengths: (batch,) gercek uzunluklar (padding haric)

        Akis:
        embed -> pack_padded -> BiLSTM -> unpack -> son hidden concat -> dropout -> fc
        """
```

**Mimari Diyagrami**:
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

**Hyperparametreler**:
| Parametre | Deger |
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

**Dosya**: `models/distilbert.py`

```python
class DistilBERTClassifier:
    def __init__(self, num_classes: int = 2,
                 model_name: str = "distilbert-base-uncased",
                 learning_rate: float = 2e-5):
        """
        HuggingFace DistilBertForSequenceClassification wrapper.
        """

    def get_tokenizer(self):
        """DistilBertTokenizer dondurur."""

    def create_dataset(self, texts, labels, max_length=512):
        """HuggingFace Dataset + tokenization."""

    def train(self, train_dataset, val_dataset, config):
        """HuggingFace Trainer veya custom loop ile fine-tuning."""

    def predict(self, texts):
        """Inference."""
```

**Fine-tuning Stratejisi**:
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

**Hyperparametreler**:
| Parametre | Deger |
|-----------|-------|
| model_name | distilbert-base-uncased |
| max_seq_length | 512 |
| batch_size | 16 |
| learning_rate | 2e-5 |
| weight_decay | 0.01 |
| warmup_steps | %10 of total |
| num_epochs | 3 |
| optimizer | AdamW |
| scheduler | linear warmup |

---

## Training Akisi

**Dosya**: `train.py`

```python
def run_training(config: Config):
    """
    1. Data yukle + preprocess
    2. Tum modelleri sirasiyla train et:
       a. TF-IDF + LR  (sklearn .fit)
       b. TF-IDF + SVM (sklearn .fit)
       c. BiLSTM        (Trainer loop)
       d. DistilBERT    (HF Trainer / custom loop)
    3. Her model icin validation metrikleri kaydet
    4. En iyi modellerin test evaluation'ini calistir
    """
```

---

## Analysis & Error Patterns

**Dosya**: `analysis.py`

```python
def analyze_misclassifications(texts, y_true, y_pred,
                                n_examples: int = 5) -> list[dict]:
    """
    En az 5 yanlis siniflandirilmis ornegi secer.
    Her ornek icin:
    - Orjinal metin (truncated)
    - True label
    - Predicted label
    - Model confidence (varsa)
    - Olasi hata nedeni (pattern)
    """

def identify_error_patterns(misclassified: list[dict]) -> dict:
    """
    Ortak hata pattern'leri:
    - Ironi/sarkasm
    - Karisik duygu (mixed sentiment)
    - Negation handling hatalari
    - Domain-specific jargon
    - Cok kisa/uzun metinler
    """
```

---

## Beklenen Ciktilar

```
outputs/q1/run_{timestamp}/
|-- config.yaml               # Kullanilan config
|-- preprocessing_comparison.csv  # Tokenization/preprocessing etki tablosu
|-- metrics.json               # Tum model metrikleri
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

## Config Ornegi (q1.yaml)

```yaml
question: "q1"
task: "classification"

dataset:
  name: "imdb"
  val_split_ratio: 0.2    # train'den ayrilacak val orani

preprocess:
  lowercase: true
  remove_html: true
  remove_special: true
  remove_stopwords: false
  max_length: 256          # BiLSTM icin

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

## Representation Karsilastirma Cercevesi

Raporda sunulacak karsilastirma:

| Boyut | TF-IDF (Sparse) | BiLSTM (Dense) | DistilBERT (Contextual) |
|-------|-----------------|----------------|------------------------|
| Representation | Bag-of-words, n-gram | Static embeddings | Contextual embeddings |
| Boyut | ~50K sparse | 300d dense | 768d contextual |
| Baglamsal mi? | Hayir | Hayir (static) | Evet |
| Egitim suresi | Saniyeler | Dakikalar | Dakikalar-saat |
| Interpretability | Yuksek (feature weights) | Dusuk | Cok dusuk |
| Performans | Iyi baseline | Orta-iyi | En yuksek |

---

## Iliskili Dokumanlar

- [Ortak Altyapi](03-shared-infrastructure.md) - Trainer, Evaluator, metrics
- [Evaluation Framework](09-evaluation-framework.md) - Accuracy, Macro-F1 detaylari
- [Experiment Config](10-experiment-config.md) - Config yapisi
- [LaTeX Rapor](11-report-structure.md) - Q1 section yapisi
