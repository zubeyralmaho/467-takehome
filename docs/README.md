# CENG 467 - Take-Home Midterm: Architecture Documentation

> Natural Language Understanding and Generation - Prof. Dr. Aytug Onan

This documentation comprehensively defines the technical architecture, data flows, inter-module relationships, and implementation plan for the CENG 467 take-home midterm project.

---

## Documentation Map

| # | Document | Description |
|---|----------|-------------|
| 1 | [Project Overview](01-project-overview.md) | Scope, objectives, technology choices |
| 2 | [Directory Structure](02-project-structure.md) | Folder/file organization, module map |
| 3 | [Shared Infrastructure](03-shared-infrastructure.md) | Config, data loaders, evaluation engine, logging |
| 4 | [Q1 - Text Classification](04-q1-text-classification.md) | TF-IDF + LR/SVM, BiLSTM, DistilBERT |
| 5 | [Q2 - Named Entity Recognition](05-q2-ner.md) | CRF, BiLSTM-CRF, BERT-NER |
| 6 | [Q3 - Text Summarization](06-q3-summarization.md) | TextRank, BART/T5 |
| 7 | [Q4 - Machine Translation](07-q4-machine-translation.md) | Seq2Seq + Attention, Transformer |
| 8 | [Q5 - Language Modeling](08-q5-language-modeling.md) | N-gram, LSTM, GPT-2 |
| 9 | [Evaluation Framework](09-evaluation-framework.md) | Metrics, reporting, comparison |
| 10 | [Experiment & Reproducibility](10-experiment-config.md) | Seed, hyperparameter management, execution |
| 11 | [LaTeX Report Structure](11-report-structure.md) | Report template, section plan |

---

## Operational Tracking

For live AI agent coordination, use the `agents/` subfolder:

- [Agent Workspace](agents/README.md) - Collaboration rules and workflow
- [Status Board](agents/status-board.md) - High-level project snapshot
- [Handoff](agents/handoff.md) - Shared blockers and next actions

---

## Dependency Graph (Documentation)

```
README.md (this file)
    |
    +-- 01-project-overview.md
    |       |
    |       +-- 02-project-structure.md
    |       |       |
    |       |       +-- 03-shared-infrastructure.md
    |       |               |
    |       |               +-- 09-evaluation-framework.md
    |       |               +-- 10-experiment-config.md
    |       |
    |       +-- 04-q1-text-classification.md ---+
    |       +-- 05-q2-ner.md -------------------+-- All depend on 03 and 09
    |       +-- 06-q3-summarization.md ---------+
    |       +-- 07-q4-machine-translation.md ---+
    |       +-- 08-q5-language-modeling.md -----+
    |
    +-- 11-report-structure.md (covers all questions)
    |
    +-- agents/ (live agent coordination and status tracking)
```

---

## Quick Start

Each question has its own entry point. See the relevant document for details:

```bash
# Q1 - Text Classification
python -m src.q1_classification.main --config configs/q1.yaml

# Q2 - NER
python -m src.q2_ner.main --config configs/q2.yaml

# Q3 - Summarization
python -m src.q3_summarization.main --config configs/q3.yaml

# Q4 - Machine Translation
python -m src.q4_translation.main --config configs/q4.yaml

# Q5 - Language Modeling
python -m src.q5_language_model.main --config configs/q5.yaml
```
