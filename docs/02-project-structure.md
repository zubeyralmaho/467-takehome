# 02 - Directory Structure

> [Home](README.md) | Previous: [Project Overview](01-project-overview.md) | Next: [Shared Infrastructure](03-shared-infrastructure.md)

---

## Project Root Directory

```
CENG467_Midterm/
|
|-- configs/                        # YAML configurations
|   |-- q1.yaml                     # Q1 Text Classification config
|   |-- q2.yaml                     # Q2 NER config
|   |-- q3.yaml                     # Q3 Summarization config
|   |-- q4.yaml                     # Q4 Translation config
|   |-- q5.yaml                     # Q5 Language Modeling config
|   +-- base.yaml                   # Shared default values (seed, device, paths)
|
|-- src/                            # Main source code
|   |-- common/                     # Shared infrastructure (details: 03-shared-infrastructure.md)
|   |   |-- __init__.py
|   |   |-- config.py               # YAML config loader + merge logic
|   |   |-- seed.py                 # Reproducibility: seed setup
|   |   |-- data_utils.py           # General data loader, split, cache
|   |   |-- vocab.py                # Vocabulary builder (for neural models)
|   |   |-- metrics.py              # Central metric computation engine
|   |   |-- evaluation.py           # Evaluation orchestrator
|   |   |-- visualization.py        # Shared plot functions
|   |   |-- trainer.py              # Generic training loop (PyTorch)
|   |   +-- export.py               # Result saving (JSON, CSV, tables)
|   |
|   |-- q1_classification/          # Question 1 (details: 04-q1-text-classification.md)
|   |   |-- __init__.py
|   |   |-- main.py                 # Entry point
|   |   |-- preprocess.py           # Tokenization strategies, normalization
|   |   |-- dataset.py              # IMDb/SST-2 Dataset wrapper
|   |   |-- models/
|   |   |   |-- __init__.py
|   |   |   |-- tfidf_classifier.py # TF-IDF + LogisticRegression / SVM
|   |   |   |-- bilstm.py           # BiLSTM classifier
|   |   |   +-- distilbert.py       # DistilBERT fine-tuning wrapper
|   |   |-- train.py                # Training orchestration
|   |   +-- analysis.py             # Misclassification analysis, error patterns
|   |
|   |-- q2_ner/                     # Question 2 (details: 05-q2-ner.md)
|   |   |-- __init__.py
|   |   |-- main.py
|   |   |-- preprocess.py           # CoNLL parser, BIO alignment
|   |   |-- dataset.py              # CoNLL-2003 Dataset wrapper
|   |   |-- models/
|   |   |   |-- __init__.py
|   |   |   |-- crf.py              # Standalone CRF (feature-based)
|   |   |   |-- bilstm_crf.py       # BiLSTM-CRF
|   |   |   +-- bert_ner.py         # BERT token classification
|   |   |-- train.py
|   |   +-- analysis.py             # Entity-level error analysis
|   |
|   |-- q3_summarization/           # Question 3 (details: 06-q3-summarization.md)
|   |   |-- __init__.py
|   |   |-- main.py
|   |   |-- preprocess.py           # Text cleaning, truncation
|   |   |-- dataset.py              # CNN/DailyMail subset loader
|   |   |-- models/
|   |   |   |-- __init__.py
|   |   |   |-- textrank.py         # Extractive: TextRank
|   |   |   +-- bart_summarizer.py  # Abstractive: BART (or T5)
|   |   |-- train.py                # BART fine-tuning
|   |   +-- analysis.py             # Qualitative analysis, fluency
|   |
|   |-- q4_translation/             # Question 4 (details: 07-q4-machine-translation.md)
|   |   |-- __init__.py
|   |   |-- main.py
|   |   |-- preprocess.py           # Tokenization, BPE, vocab build
|   |   |-- dataset.py              # Multi30k Dataset wrapper
|   |   |-- models/
|   |   |   |-- __init__.py
|   |   |   |-- seq2seq_attention.py # Seq2Seq + Bahdanau/Luong Attention
|   |   |   +-- transformer_mt.py   # Transformer-based translation
|   |   |-- train.py
|   |   +-- analysis.py             # Translation quality analysis
|   |
|   |-- q5_language_model/          # Question 5 (details: 08-q5-language-modeling.md)
|   |   |-- __init__.py
|   |   |-- main.py
|   |   |-- preprocess.py           # Corpus tokenization, vocabulary
|   |   |-- dataset.py              # WikiText-2 / PTB loader
|   |   |-- models/
|   |   |   |-- __init__.py
|   |   |   |-- ngram.py            # N-gram LM (bigram, trigram + smoothing)
|   |   |   |-- lstm_lm.py          # LSTM Language Model
|   |   |   +-- gpt2_lm.py          # (Optional) GPT-2 fine-tuning
|   |   |-- train.py
|   |   +-- generate.py             # Text generation + sampling strategies
|   |
|   +-- __init__.py
|
|-- notebooks/                      # Jupyter notebooks (quick experiments, visualization)
|   |-- q1_exploration.ipynb
|   |-- q2_exploration.ipynb
|   |-- q3_exploration.ipynb
|   |-- q4_exploration.ipynb
|   +-- q5_exploration.ipynb
|
|-- outputs/                        # Experiment outputs (in gitignore)
|   |-- q1/
|   |   |-- run_20260415_143022/    # Timestamped run
|   |   |   |-- config.yaml         # Copy of used config
|   |   |   |-- metrics.json        # Final metrics
|   |   |   |-- predictions.csv     # Model predictions
|   |   |   |-- model_best.pt       # Best model checkpoint
|   |   |   +-- figures/            # Plots
|   |   +-- ...
|   |-- q2/ ...
|   |-- q3/ ...
|   |-- q4/ ...
|   +-- q5/ ...
|
|-- report/                         # LaTeX report (details: 11-report-structure.md)
|   |-- main.tex
|   |-- sections/
|   |   |-- introduction.tex
|   |   |-- q1.tex
|   |   |-- q2.tex
|   |   |-- q3.tex
|   |   |-- q4.tex
|   |   +-- q5.tex
|   |-- figures/
|   |-- tables/
|   +-- references.bib
|
|-- docs/                           # This documentation directory
|   |-- 01-project-overview.md
|   |-- ...
|   |-- 11-report-structure.md
|   +-- agents/                    # Live AI agent tracking workspace
|       |-- README.md              # Rules and workflow for agent updates
|       |-- status-board.md        # Project-level status snapshot
|       |-- handoff.md             # Cross-agent blockers and next actions
|       |-- agent-template.md      # Template for per-agent logs
|       +-- active/                # One file per active agent
|
|-- requirements.txt                # pip dependencies
|-- environment.yml                 # conda environment (alternative)
|-- .gitignore
+-- README.md                       # Project root README
```

---

## Module Dependency Map

```
configs/*.yaml
    |
    v
src/common/config.py  <---- All main.py files import this
    |
    +---> src/common/seed.py
    +---> src/common/data_utils.py
    +---> src/common/metrics.py
    +---> src/common/evaluation.py
    +---> src/common/trainer.py
    +---> src/common/visualization.py
    +---> src/common/export.py
    |
    v
src/q{n}_*/main.py
    |-- preprocess.py  (question-specific)
    |-- dataset.py     (question-specific, uses data_utils)
    |-- models/*.py    (question-specific)
    |-- train.py       (uses common/trainer)
    +-- analysis.py    (uses common/metrics + visualization)
```

---

## Import Conventions

```python
# Import from shared infrastructure
from src.common.config import load_config
from src.common.seed import set_global_seed
from src.common.metrics import compute_metrics
from src.common.trainer import Trainer
from src.common.evaluation import Evaluator

# Import from question-specific model
from src.q1_classification.models.bilstm import BiLSTMClassifier
from src.q1_classification.preprocess import preprocess_pipeline
```

---

## .gitignore Contents

```
outputs/
*.pt
*.bin
__pycache__/
.ipynb_checkpoints/
data/         # HuggingFace cache, large files
*.egg-info/
wandb/
```

---

## Related Documents

- [Shared Infrastructure](03-shared-infrastructure.md) - `src/common/` details
- [Experiment Config](10-experiment-config.md) - Config file format
- Each question document explains the details of its own subdirectory
