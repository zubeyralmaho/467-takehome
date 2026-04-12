# 03 - Ortak Altyapi (`src/common/`)

> [Ana Sayfa](README.md) | Onceki: [Dizin Yapisi](02-project-structure.md) | Sonraki: [Q1 - Text Classification](04-q1-text-classification.md)

---

## Genel Bakis

`src/common/` modulu, bes sorunun hepsinin paylastigi temel islev birimlerini icerir. Amac: kod tekrarini onlemek, tutarli evaluation saglamak ve reproducibility'yi garanti etmek.

```
src/common/
|-- __init__.py
|-- config.py           # Config yukleyici
|-- seed.py             # Global seed yonetimi
|-- data_utils.py       # Veri yukleme / bolme yardimcilari
|-- vocab.py            # Vocabulary builder
|-- metrics.py          # Metrik hesaplama fonksiyonlari
|-- evaluation.py       # Evaluation orchestrator
|-- trainer.py          # Generic PyTorch training loop
|-- visualization.py    # Plot fonksiyonlari
+-- export.py           # Sonuc kaydetme
```

---

## config.py - Konfigurasyon Yonetimi

### Sorumluluk
YAML dosyalarindan konfigurasyonu okur, `base.yaml` ile soru-ozel config'i birlestirir, CLI override destegi saglar.

### API

```python
class Config:
    """Nested dot-access config objesi."""

    @staticmethod
    def from_yaml(path: str) -> "Config":
        """YAML dosyasindan config yukler."""

    def merge(self, override: dict) -> "Config":
        """Ustune yazma ile birlestirme (deep merge)."""

    def to_dict(self) -> dict:
        """Serializasyon icin dict'e cevirir."""

    def save(self, path: str) -> None:
        """Config'i YAML olarak kaydeder (reproducibility icin)."""


def load_config(config_path: str, cli_overrides: dict = None) -> Config:
    """
    1. base.yaml yukle
    2. config_path yukle
    3. deep merge (config_path, base uzerine)
    4. cli_overrides uygula
    5. Config objesi dondur
    """
```

### Config Merge Sirasi
```
base.yaml (defaults) -> q{n}.yaml (soru ozel) -> CLI args (en yuksek oncelik)
```

### Ornek base.yaml
```yaml
seed: 42
device: "cuda"     # auto-detect ile degistirilebilir
output_dir: "outputs"
logging:
  level: "INFO"
  save_logs: true
data:
  cache_dir: "data/cache"
  num_workers: 4
training:
  early_stopping_patience: 3
  save_best_model: true
```

---

## seed.py - Reproducibility

### Sorumluluk
Tum random kaynaklarini tek bir seed ile kontrol altina alir.

### API

```python
def set_global_seed(seed: int = 42) -> None:
    """
    Asagidaki kaynaklari seed'ler:
    - random.seed(seed)
    - numpy.random.seed(seed)
    - torch.manual_seed(seed)
    - torch.cuda.manual_seed_all(seed)
    - torch.backends.cudnn.deterministic = True
    - torch.backends.cudnn.benchmark = False
    - os.environ['PYTHONHASHSEED'] = str(seed)
    """

def worker_init_fn(worker_id: int) -> None:
    """DataLoader worker'lari icin seed fonksiyonu.
    Her worker farkli ama deterministik seed alir."""
```

### Kullanim
```python
# Her main.py'nin ilk satiri
from src.common.seed import set_global_seed
set_global_seed(config.seed)
```

Detaylar icin: [Experiment Config](10-experiment-config.md)

---

## data_utils.py - Veri Yardimcilari

### Sorumluluk
HuggingFace Datasets uzerinden veri yukleme, train/val/test split yonetimi, caching.

### API

```python
def load_hf_dataset(name: str, subset: str = None,
                    cache_dir: str = None) -> DatasetDict:
    """HuggingFace dataset yukler, cache'e kaydeder."""

def create_splits(dataset, train_ratio=0.8, val_ratio=0.1,
                  test_ratio=0.1, seed=42) -> dict:
    """Eger dataset'te val/test yoksa olusturur.
    Stratified split uygulanir (classification icin)."""

def get_dataloaders(train_ds, val_ds, test_ds,
                    batch_size: int, collate_fn=None,
                    num_workers: int = 4) -> tuple:
    """PyTorch DataLoader'lari olusturur.
    worker_init_fn otomatik atanir."""

def subsample(dataset, n: int, seed: int = 42):
    """Buyuk datasetlerden subset alir (hizli deney icin)."""
```

---

## vocab.py - Vocabulary Builder

### Sorumluluk
Neural modeller (BiLSTM, Seq2Seq, LSTM-LM) icin token -> index mapping olusturur.

### API

```python
class Vocabulary:
    PAD_TOKEN = "<PAD>"   # index 0
    UNK_TOKEN = "<UNK>"   # index 1
    BOS_TOKEN = "<BOS>"   # index 2 (seq2seq icin)
    EOS_TOKEN = "<EOS>"   # index 3 (seq2seq icin)

    def __init__(self, min_freq: int = 2, max_size: int = None):
        """min_freq: minimum frekans esigi
           max_size: maksimum vocab boyutu"""

    def build(self, token_lists: list[list[str]]) -> "Vocabulary":
        """Token listelerinden vocab olusturur."""

    def encode(self, tokens: list[str]) -> list[int]:
        """Token listesini index listesine cevirir."""

    def decode(self, indices: list[int]) -> list[str]:
        """Index listesini token listesine cevirir."""

    def __len__(self) -> int: ...

    def save(self, path: str) -> None: ...

    @classmethod
    def load(cls, path: str) -> "Vocabulary": ...
```

### Kullanildigi Sorular
- **Q1**: BiLSTM icin word vocabulary
- **Q4**: Seq2Seq icin source/target vocabulary
- **Q5**: LSTM LM icin corpus vocabulary

> Not: Transformer-based modeller (BERT, BART, T5) kendi tokenizer'larini kullanir; bu sinifi kullanmazlar.

---

## metrics.py - Metrik Hesaplama

### Sorumluluk
Tum sorularin ihtiyac duydugu metrikleri merkezi olarak hesaplar.

### API

```python
# --- Classification Metrikleri (Q1) ---
def compute_accuracy(y_true, y_pred) -> float: ...
def compute_macro_f1(y_true, y_pred) -> float: ...
def compute_classification_report(y_true, y_pred, labels=None) -> dict: ...
def compute_confusion_matrix(y_true, y_pred, labels=None) -> np.ndarray: ...

# --- Sequence Labeling Metrikleri (Q2) ---
def compute_entity_metrics(y_true_bio, y_pred_bio) -> dict:
    """seqeval kutuphanesi kullanir. Entity-level P/R/F1 dondurur."""

# --- Summarization Metrikleri (Q3) ---
def compute_rouge(predictions, references) -> dict:
    """ROUGE-1, ROUGE-2, ROUGE-L hesaplar."""

def compute_bleu(predictions, references) -> float:
    """Corpus-level BLEU hesaplar."""

def compute_meteor(predictions, references) -> float:
    """METEOR score hesaplar."""

def compute_bertscore(predictions, references,
                      lang: str = "en") -> dict:
    """BERTScore (P, R, F1) hesaplar."""

# --- Translation Metrikleri (Q4) ---
def compute_chrf(predictions, references) -> float:
    """ChrF score hesaplar."""
# (BLEU, METEOR, BERTScore yukariyla paylasir)

# --- Language Modeling Metrikleri (Q5) ---
def compute_perplexity(loss: float) -> float:
    """Cross-entropy loss'tan perplexity: exp(loss)"""

# --- Genel ---
def compute_metrics(task: str, predictions, references,
                    **kwargs) -> dict:
    """
    Unified entry point.
    task: "classification" | "ner" | "summarization" |
          "translation" | "language_model"
    Ilgili metrikleri hesaplayip dict olarak dondurur.
    """
```

### Metrik-Soru Matrisi

| Metrik | Q1 | Q2 | Q3 | Q4 | Q5 |
|--------|----|----|----|----|-----|
| Accuracy | x | | | | |
| Macro-F1 | x | | | | |
| Precision | | x | | | |
| Recall | | x | | | |
| Entity F1 | | x | | | |
| ROUGE-1/2/L | | | x | | |
| BLEU | | | x | x | |
| METEOR | | | x | x | |
| BERTScore | | | x | x | |
| ChrF | | | | x | |
| Perplexity | | | | | x |

Detaylar icin: [Evaluation Framework](09-evaluation-framework.md)

---

## evaluation.py - Evaluation Orchestrator

### Sorumluluk
Model ciktilari uzerinde evaluation pipeline'ini calistirir, sonuclari toplar ve formatlar.

### API

```python
class Evaluator:
    def __init__(self, task: str, config: Config):
        """task: Q'nun gorevi, config: metrik ayarlari"""

    def evaluate(self, model, dataloader, **kwargs) -> dict:
        """
        1. Model inference (batch'ler uzerinde)
        2. Predictions toplama
        3. compute_metrics cagirma
        4. Sonuclari dict olarak dondurme
        """

    def compare_models(self, results: dict[str, dict]) -> pd.DataFrame:
        """Birden fazla modelin sonuclarini karsilastirma tablosuna cevirir."""

    def save_results(self, results: dict, output_dir: str) -> None:
        """JSON + CSV olarak kaydeder."""
```

---

## trainer.py - Generic Training Loop

### Sorumluluk
PyTorch modelleri icin standart training loop. Early stopping, checkpoint, logging dahil.

### API

```python
class Trainer:
    def __init__(self, model, optimizer, criterion,
                 config: Config, device: str = "cuda"):
        """
        model: nn.Module
        optimizer: torch.optim.Optimizer
        criterion: loss function
        config: training hyperparameters
        """

    def train(self, train_loader, val_loader,
              num_epochs: int) -> dict:
        """
        Training loop:
        1. Her epoch icin:
           a. train_one_epoch()
           b. validate()
           c. Early stopping kontrolu
           d. Best model checkpoint
        2. Training history dondurme
        """

    def train_one_epoch(self, loader) -> float:
        """Tek epoch train, ortalama loss dondurur."""

    def validate(self, loader) -> dict:
        """Validation metrics hesaplar."""

    def save_checkpoint(self, path: str) -> None: ...
    def load_checkpoint(self, path: str) -> None: ...
```

### Kullanildigi Sorular
- **Q1**: BiLSTM, DistilBERT training
- **Q2**: BiLSTM-CRF, BERT-NER training
- **Q3**: BART fine-tuning
- **Q4**: Seq2Seq, Transformer training
- **Q5**: LSTM training

> Not: scikit-learn modelleri (TF-IDF+LR/SVM, CRF) kendi `.fit()` metodlarini kullanir; Trainer'a ihtiyac duymaz.

---

## visualization.py - Gorsellestirme

### API

```python
def plot_training_curves(history: dict, output_path: str) -> None:
    """Loss ve metrik egrileri (train vs val)."""

def plot_confusion_matrix(cm, labels, output_path: str) -> None:
    """Confusion matrix heatmap (Q1 icin)."""

def plot_metric_comparison(results_df: pd.DataFrame,
                           metric: str, output_path: str) -> None:
    """Modeller arasi bar chart karsilastirma."""

def plot_attention_weights(attention, src_tokens, tgt_tokens,
                           output_path: str) -> None:
    """Attention heatmap (Q4 icin)."""

def plot_entity_distribution(entities: dict,
                             output_path: str) -> None:
    """Entity type dagalimi (Q2 icin)."""
```

---

## export.py - Sonuc Kaydetme

### API

```python
def create_run_dir(base_dir: str, question: str) -> str:
    """Timestamped run dizini olusturur:
    outputs/q1/run_20260415_143022/"""

def save_metrics(metrics: dict, path: str) -> None:
    """Metrikleri JSON olarak kaydeder."""

def save_predictions(predictions, references, path: str) -> None:
    """Tahminleri CSV olarak kaydeder."""

def save_config_copy(config: Config, run_dir: str) -> None:
    """Kullanilan config'in kopyasini run dizinine kaydeder."""

def generate_latex_table(results_df: pd.DataFrame) -> str:
    """DataFrame'i LaTeX tablo formatina cevirir."""
```

---

## Veri Akis Diyagrami (Tum Sorular icin Genel)

```
[configs/q{n}.yaml] + [configs/base.yaml]
           |
           v
    config.py::load_config()
           |
           v
    seed.py::set_global_seed()
           |
           v
    q{n}/preprocess.py  ->  q{n}/dataset.py  ->  data_utils.py::get_dataloaders()
           |                                              |
           v                                              v
    q{n}/models/*.py  <-  q{n}/train.py  <-  trainer.py::Trainer
           |                     |
           v                     v
    evaluation.py::Evaluator  ->  metrics.py::compute_metrics()
           |
           v
    export.py (JSON/CSV)  +  visualization.py (figures)
           |
           v
    outputs/q{n}/run_{timestamp}/
```

---

## Iliskili Dokumanlar

- [Dizin Yapisi](02-project-structure.md) - Dosya organizasyonu
- [Evaluation Framework](09-evaluation-framework.md) - Metrik detaylari
- [Experiment Config](10-experiment-config.md) - Config sema ve ornekleri
