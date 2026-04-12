# 01 - Project Overview

> [Home](README.md) | Next: [Directory Structure](02-project-structure.md)

---

## Objective

This project aims to implement and comparatively evaluate five fundamental NLP tasks (text classification, NER, summarization, machine translation, language modeling) using different architectural approaches (classical, neural, transformer).

---

## Question Map and Task Summary

| Question | Task | Dataset | Models | Main Metrics |
|----------|------|---------|--------|--------------|
| Q1 | Text Classification | IMDb (or SST-2) | TF-IDF+LR, TF-IDF+SVM, BiLSTM, DistilBERT | Accuracy, Macro-F1 |
| Q2 | Named Entity Recognition | CoNLL-2003 | CRF, BiLSTM-CRF, BERT-NER | Precision, Recall, F1 (entity-level) |
| Q3 | Text Summarization | CNN/DailyMail (subset) | TextRank, BART (or T5) | ROUGE-1/2/L, BLEU, METEOR, BERTScore |
| Q4 | Machine Translation | Multi30k (EN-DE) | Seq2Seq+Attention, Transformer | BLEU, METEOR, ChrF, BERTScore |
| Q5 | Language Modeling | WikiText-2 (or PTB) | N-gram, LSTM, (optional: GPT-2) | Perplexity |

---

## Technology Stack

### Core Framework

| Layer | Technology | Version | Usage |
|-------|------------|---------|-------|
| Deep Learning | PyTorch | >=2.0 | All neural models |
| Transformers | HuggingFace Transformers | >=4.35 | BERT, DistilBERT, BART, T5 |
| Tokenization | HuggingFace Tokenizers | >=0.15 | Subword tokenization |
| Classical ML | scikit-learn | >=1.3 | TF-IDF, LR, SVM, CRF |
| NER CRF | sklearn-crfsuite / TorchCRF | - | CRF and BiLSTM-CRF |
| Data | HuggingFace Datasets | >=2.14 | Dataset loading/splitting |
| Metrics | evaluate + custom | - | ROUGE, BLEU, METEOR, BERTScore |

### Auxiliary Tools

| Tool | Usage |
|------|-------|
| PyYAML | Config management |
| matplotlib / seaborn | Visualization |
| pandas | Result tables |
| tqdm | Progress bar |
| LaTeX (texlive) | Report writing |

### Environment

- **Python**: 3.10+
- **GPU**: CUDA supported (Colab T4/V100 or local)
- **Reproducibility**: seed=42 in every experiment (configurable)

---

## Design Principles

### 1. Modularity
Each question is designed as an independent module living within its own sub-package (`src/q{n}_*/`). Shared functionalities are centralized under `src/common/`.

### 2. Configuration-Driven Execution
All hyperparameters, dataset settings, and model options are managed through YAML config files. No hardcoded values.

### 3. Reproducibility
- Fixed random seed (global + per-worker)
- Deterministic PyTorch settings
- Config files are stored alongside result directories
- Each experiment output is kept in a timestamped directory

### 4. Consistent Evaluation
All questions use the same evaluation engine. Metrics are computed centrally, and results are saved in a standard format (JSON + CSV).

### 5. Incremental Development
Each question can be developed and tested independently. A failure in one does not affect the others.

---

## Development Order (Recommended)

```
Week 1:  [03-shared-infrastructure.md] -> Shared infrastructure (config, data, eval)
         [04-q1-text-classification.md] -> Q1 (simplest, validates the infrastructure)

Week 2:  [05-q2-ner.md] -> Q2 NER
         [06-q3-summarization.md] -> Q3 Summarization

Week 3:  [07-q4-machine-translation.md] -> Q4 Translation
         [08-q5-language-modeling.md] -> Q5 Language Modeling

Week 4:  [09-evaluation-framework.md] -> Final evaluation, error analysis
         [11-report-structure.md] -> LaTeX report writing
```

---

## Related Documents

- [Directory Structure](02-project-structure.md) - File and directory organization
- [Shared Infrastructure](03-shared-infrastructure.md) - Shared code details
- [Experiment Config](10-experiment-config.md) - Reproducibility details
