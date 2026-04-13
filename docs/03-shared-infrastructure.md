# 03 - Shared Infrastructure (`src/common/`)

> [Home](README.md) | Previous: [Directory Structure](02-project-structure.md) | Next: [Q1 - Text Classification](04-q1-text-classification.md)

---

## Overview

The `src/common/` module contains the core utility components shared by all five questions. Purpose: prevent code duplication, ensure consistent evaluation, and guarantee reproducibility.

```
src/common/
|-- __init__.py
|-- config.py           # Config loader
|-- seed.py             # Global seed management
|-- data_utils.py       # Data loading / splitting helpers
|-- vocab.py            # Vocabulary builder
|-- metrics.py          # Metric computation functions
|-- evaluation.py       # Evaluation orchestrator
|-- trainer.py          # Generic PyTorch training loop
|-- visualization.py    # Plot functions
+-- export.py           # Result saving
```

---

## config.py - Configuration Management

### Responsibility
Reads configuration from YAML files, merges `base.yaml` with question-specific config, provides CLI override support.

### API

```python
class Config:
    """Nested dot-access config object."""

    @staticmethod
    def from_yaml(path: str) -> "Config":
        """Loads config from a YAML file."""

    def merge(self, override: dict) -> "Config":
        """Merges with override (deep merge)."""

    def to_dict(self) -> dict:
        """Converts to dict for serialization."""

    def save(self, path: str) -> None:
        """Saves config as YAML (for reproducibility)."""


def load_config(config_path: str, cli_overrides: dict = None) -> Config:
    """
    1. Load base.yaml
    2. Load config_path
    3. Deep merge (config_path on top of base)
    4. Apply cli_overrides
    5. Return Config object
    """
```

### Config Merge Order
```
base.yaml (defaults) -> q{n}.yaml (question-specific) -> CLI args (highest priority)
```

### Example base.yaml
```yaml
seed: 42
device: "cuda"     # Can be overridden with auto-detect
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

### Responsibility
Controls all random sources with a single seed.

### API

```python
def set_global_seed(seed: int = 42) -> None:
    """
    Seeds the following sources:
    - random.seed(seed)
    - numpy.random.seed(seed)
    - torch.manual_seed(seed)
    - torch.cuda.manual_seed_all(seed)
    - torch.backends.cudnn.deterministic = True
    - torch.backends.cudnn.benchmark = False
    - os.environ['PYTHONHASHSEED'] = str(seed)
    """

def worker_init_fn(worker_id: int) -> None:
    """Seed function for DataLoader workers.
    Each worker gets a different but deterministic seed."""
```

### Usage
```python
# First line of every main.py
from src.common.seed import set_global_seed
set_global_seed(config.seed)
```

For details see: [Experiment Config](10-experiment-config.md)

---

## data_utils.py - Data Helpers

### Responsibility
Data loading via HuggingFace Datasets, train/val/test split management, caching.

### API

```python
def load_hf_dataset(name: str, subset: str = None,
                    cache_dir: str = None) -> DatasetDict:
    """Loads a HuggingFace dataset and saves to cache."""

def create_splits(dataset, train_ratio=0.8, val_ratio=0.1,
                  test_ratio=0.1, seed=42) -> dict:
    """Creates val/test splits if they don't exist in the dataset.
    Applies stratified split (for classification)."""

def get_dataloaders(train_ds, val_ds, test_ds,
                    batch_size: int, collate_fn=None,
                    num_workers: int = 4) -> tuple:
    """Creates PyTorch DataLoaders.
    worker_init_fn is automatically assigned."""

def subsample(dataset, n: int, seed: int = 42):
    """Takes a subset from large datasets (for quick experiments)."""
```

---

## vocab.py - Vocabulary Builder

### Responsibility
Creates token -> index mapping for neural models (BiLSTM, Seq2Seq, LSTM-LM).

### API

```python
class Vocabulary:
    PAD_TOKEN = "<PAD>"   # index 0
    UNK_TOKEN = "<UNK>"   # index 1
    BOS_TOKEN = "<BOS>"   # index 2 (for seq2seq)
    EOS_TOKEN = "<EOS>"   # index 3 (for seq2seq)

    def __init__(self, min_freq: int = 2, max_size: int = None):
        """min_freq: minimum frequency threshold
           max_size: maximum vocabulary size"""

    def build(self, token_lists: list[list[str]]) -> "Vocabulary":
        """Builds vocabulary from token lists."""

    def encode(self, tokens: list[str]) -> list[int]:
        """Converts a token list to an index list."""

    def decode(self, indices: list[int]) -> list[str]:
        """Converts an index list to a token list."""

    def __len__(self) -> int: ...

    def save(self, path: str) -> None: ...

    @classmethod
    def load(cls, path: str) -> "Vocabulary": ...
```

### Questions Where Used
- **Q1**: Word vocabulary for BiLSTM
- **Q4**: Source/target vocabulary for Seq2Seq
- **Q5**: Corpus vocabulary for LSTM LM

> Note: Transformer-based models (BERT, BART, T5) use their own tokenizers; they do not use this class.

---

## metrics.py - Metric Computation

### Responsibility
Centrally computes all metrics needed by all questions.

### API

```python
# --- Classification Metrics (Q1) ---
def compute_accuracy(y_true, y_pred) -> float: ...
def compute_macro_f1(y_true, y_pred) -> float: ...
def compute_classification_report(y_true, y_pred, labels=None) -> dict: ...
def compute_confusion_matrix(y_true, y_pred, labels=None) -> np.ndarray: ...

# --- Sequence Labeling Metrics (Q2) ---
def compute_entity_metrics(y_true_bio, y_pred_bio) -> dict:
    """Uses the seqeval library. Returns entity-level P/R/F1."""

# --- Summarization Metrics (Q3) ---
def compute_rouge(predictions, references) -> dict:
    """Computes ROUGE-1, ROUGE-2, ROUGE-L."""

def compute_bleu(predictions, references) -> float:
    """Computes corpus-level BLEU."""

def compute_meteor(predictions, references) -> float:
    """Computes METEOR score."""

def compute_bertscore(predictions, references,
                      lang: str = "en") -> dict:
    """Computes BERTScore (P, R, F1)."""

# --- Translation Metrics (Q4) ---
def compute_chrf(predictions, references) -> float:
    """Computes ChrF score."""
# (BLEU, METEOR, BERTScore are shared with above)

# --- Language Modeling Metrics (Q5) ---
def compute_perplexity(loss: float) -> float:
    """Perplexity from cross-entropy loss: exp(loss)"""

# --- General ---
def compute_metrics(task: str, predictions, references,
                    **kwargs) -> dict:
    """
    Unified entry point.
    task: "classification" | "ner" | "summarization" |
          "translation" | "language_model"
    Computes the relevant metrics and returns them as a dict.
    """
```

### Metric-Question Matrix

| Metric | Q1 | Q2 | Q3 | Q4 | Q5 |
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

For details see: [Evaluation Framework](09-evaluation-framework.md)

---

## evaluation.py - Evaluation Orchestrator

### Responsibility
Runs the evaluation pipeline on model outputs, collects and formats results.

### API

```python
class Evaluator:
    def __init__(self, task: str, config: Config):
        """task: the question's task, config: metric settings"""

    def evaluate(self, model, dataloader, **kwargs) -> dict:
        """
        1. Model inference (over batches)
        2. Collect predictions
        3. Call compute_metrics
        4. Return results as dict
        """

    def compare_models(self, results: dict[str, dict]) -> pd.DataFrame:
        """Converts multiple model results into a comparison table."""

    def save_results(self, results: dict, output_dir: str) -> None:
        """Saves as JSON + CSV."""
```

---

## trainer.py - Generic Training Loop

### Responsibility
Standard training loop for PyTorch models. Includes early stopping, checkpointing, and logging.

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
        1. For each epoch:
           a. train_one_epoch()
           b. validate()
           c. Early stopping check
           d. Best model checkpoint
        2. Return training history
        """

    def train_one_epoch(self, loader) -> float:
        """Single epoch train, returns average loss."""

    def validate(self, loader) -> dict:
        """Computes validation metrics."""

    def save_checkpoint(self, path: str) -> None: ...
    def load_checkpoint(self, path: str) -> None: ...
```

### Questions Where Used
- **Q1**: BiLSTM, DistilBERT training
- **Q2**: BiLSTM-CRF, BERT-NER training
- **Q3**: BART fine-tuning
- **Q4**: Seq2Seq, Transformer training
- **Q5**: LSTM training

> Note: scikit-learn models (TF-IDF+LR/SVM, CRF) use their own `.fit()` methods; they do not need the Trainer.

---

## visualization.py - Visualization

### API

```python
def plot_training_curves(history: dict, output_path: str) -> None:
    """Loss and metric curves (train vs val)."""

def plot_confusion_matrix(cm, labels, output_path: str) -> None:
    """Confusion matrix heatmap (for Q1)."""

def plot_metric_comparison(results_df: pd.DataFrame,
                           metric: str, output_path: str) -> None:
    """Bar chart comparison across models."""

def plot_attention_weights(attention, src_tokens, tgt_tokens,
                           output_path: str) -> None:
    """Attention heatmap (for Q4)."""

def plot_entity_distribution(entities: dict,
                             output_path: str) -> None:
    """Entity type distribution (for Q2)."""
```

---

## export.py - Result Saving

### API

```python
def create_run_dir(base_dir: str, question: str) -> str:
    """Creates a timestamped run directory:
    outputs/q1/run_20260415_143022/"""

def save_metrics(metrics: dict, path: str) -> None:
    """Saves metrics as JSON."""

def save_predictions(predictions, references, path: str) -> None:
    """Saves predictions as CSV."""

def save_confusion_matrix_csv(confusion_matrix: dict, path: str) -> None:
    """Saves a tabular confusion matrix export as CSV."""

def save_config_copy(config: Config, run_dir: str) -> None:
    """Saves a copy of the used config to the run directory."""

def generate_latex_table(results_df: pd.DataFrame) -> str:
    """Converts a DataFrame to LaTeX table format."""
```

---

## Data Flow Diagram (General for All Questions)

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

## Related Documents

- [Directory Structure](02-project-structure.md) - File organization
- [Evaluation Framework](09-evaluation-framework.md) - Metric details
- [Experiment Config](10-experiment-config.md) - Config schema and examples
