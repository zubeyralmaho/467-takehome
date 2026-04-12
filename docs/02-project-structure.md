# 02 - Dizin Yapisi

> [Ana Sayfa](README.md) | Onceki: [Proje Genel Bakis](01-project-overview.md) | Sonraki: [Ortak Altyapi](03-shared-infrastructure.md)

---

## Proje Kok Dizini

```
CENG467_Midterm/
|
|-- configs/                        # YAML konfigurasyonlari
|   |-- q1.yaml                     # Q1 Text Classification config
|   |-- q2.yaml                     # Q2 NER config
|   |-- q3.yaml                     # Q3 Summarization config
|   |-- q4.yaml                     # Q4 Translation config
|   |-- q5.yaml                     # Q5 Language Modeling config
|   +-- base.yaml                   # Ortak default degerler (seed, device, paths)
|
|-- src/                            # Ana kaynak kodu
|   |-- common/                     # Paylasilan altyapi (detay: 03-shared-infrastructure.md)
|   |   |-- __init__.py
|   |   |-- config.py               # YAML config loader + merge logic
|   |   |-- seed.py                 # Reproducibility: seed ayarlama
|   |   |-- data_utils.py           # Genel data yukleyici, split, cache
|   |   |-- vocab.py                # Vocabulary builder (neural modeller icin)
|   |   |-- metrics.py              # Merkezi metrik hesaplama engine
|   |   |-- evaluation.py           # Evaluation orchestrator
|   |   |-- visualization.py        # Ortak plot fonksiyonlari
|   |   |-- trainer.py              # Generic training loop (PyTorch)
|   |   +-- export.py               # Sonuc kaydetme (JSON, CSV, tablolar)
|   |
|   |-- q1_classification/          # Soru 1 (detay: 04-q1-text-classification.md)
|   |   |-- __init__.py
|   |   |-- main.py                 # Entry point
|   |   |-- preprocess.py           # Tokenization stratejileri, normalization
|   |   |-- dataset.py              # IMDb/SST-2 Dataset wrapper
|   |   |-- models/
|   |   |   |-- __init__.py
|   |   |   |-- tfidf_classifier.py # TF-IDF + LogisticRegression / SVM
|   |   |   |-- bilstm.py           # BiLSTM classifier
|   |   |   +-- distilbert.py       # DistilBERT fine-tuning wrapper
|   |   |-- train.py                # Training orchestration
|   |   +-- analysis.py             # Misclassification analysis, error patterns
|   |
|   |-- q2_ner/                     # Soru 2 (detay: 05-q2-ner.md)
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
|   |-- q3_summarization/           # Soru 3 (detay: 06-q3-summarization.md)
|   |   |-- __init__.py
|   |   |-- main.py
|   |   |-- preprocess.py           # Text cleaning, truncation
|   |   |-- dataset.py              # CNN/DailyMail subset loader
|   |   |-- models/
|   |   |   |-- __init__.py
|   |   |   |-- textrank.py         # Extractive: TextRank
|   |   |   +-- bart_summarizer.py  # Abstractive: BART (veya T5)
|   |   |-- train.py                # BART fine-tuning
|   |   +-- analysis.py             # Qualitative analysis, fluency
|   |
|   |-- q4_translation/             # Soru 4 (detay: 07-q4-machine-translation.md)
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
|   |-- q5_language_model/          # Soru 5 (detay: 08-q5-language-modeling.md)
|   |   |-- __init__.py
|   |   |-- main.py
|   |   |-- preprocess.py           # Corpus tokenization, vocabulary
|   |   |-- dataset.py              # WikiText-2 / PTB loader
|   |   |-- models/
|   |   |   |-- __init__.py
|   |   |   |-- ngram.py            # N-gram LM (bigram, trigram + smoothing)
|   |   |   |-- lstm_lm.py          # LSTM Language Model
|   |   |   +-- gpt2_lm.py          # (Opsiyonel) GPT-2 fine-tuning
|   |   |-- train.py
|   |   +-- generate.py             # Text generation + sampling strategies
|   |
|   +-- __init__.py
|
|-- notebooks/                      # Jupyter notebooks (hizli deney, gorsellestirme)
|   |-- q1_exploration.ipynb
|   |-- q2_exploration.ipynb
|   |-- q3_exploration.ipynb
|   |-- q4_exploration.ipynb
|   +-- q5_exploration.ipynb
|
|-- outputs/                        # Deney ciktilari (gitignore'da)
|   |-- q1/
|   |   |-- run_20260415_143022/    # Timestamped run
|   |   |   |-- config.yaml         # Kullanilan config kopyasi
|   |   |   |-- metrics.json        # Nihai metrikler
|   |   |   |-- predictions.csv     # Model tahminleri
|   |   |   |-- model_best.pt       # En iyi model checkpoint
|   |   |   +-- figures/            # Plotlar
|   |   +-- ...
|   |-- q2/ ...
|   |-- q3/ ...
|   |-- q4/ ...
|   +-- q5/ ...
|
|-- report/                         # LaTeX rapor (detay: 11-report-structure.md)
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
|-- docs/                           # Bu dokumantasyon dizini
|
|-- requirements.txt                # pip dependencies
|-- environment.yml                 # conda environment (alternatif)
|-- .gitignore
+-- README.md                       # Proje root README
```

---

## Modul Bagimlilk Haritasi

```
configs/*.yaml
    |
    v
src/common/config.py  <---- Tum main.py dosyalari bunu import eder
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
    |-- preprocess.py  (q'ye ozel)
    |-- dataset.py     (q'ye ozel, data_utils kullanir)
    |-- models/*.py    (q'ye ozel)
    |-- train.py       (common/trainer kullanir)
    +-- analysis.py    (common/metrics + visualization kullanir)
```

---

## Import Konvansiyonlari

```python
# Ortak altyapidan import
from src.common.config import load_config
from src.common.seed import set_global_seed
from src.common.metrics import compute_metrics
from src.common.trainer import Trainer
from src.common.evaluation import Evaluator

# Soru-ozel modelden import
from src.q1_classification.models.bilstm import BiLSTMClassifier
from src.q1_classification.preprocess import preprocess_pipeline
```

---

## .gitignore Icerigi

```
outputs/
*.pt
*.bin
__pycache__/
.ipynb_checkpoints/
data/         # HuggingFace cache, buyuk dosyalar
*.egg-info/
wandb/
```

---

## Iliskili Dokumanlar

- [Ortak Altyapi](03-shared-infrastructure.md) - `src/common/` detaylari
- [Experiment Config](10-experiment-config.md) - Config dosyasi formati
- Her soru dokumani kendi alt dizininin detayini aciklar
