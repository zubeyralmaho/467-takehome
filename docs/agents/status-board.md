# Agent Status Board

Last updated: 2026-04-13 01:35

This file is generated from `status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Project Overview

| Area | Owner | Status | Notes |
|------|-------|--------|-------|
| Shared infrastructure | unassigned | in_progress | Initial config, seed, dataset split, metrics, and export scaffold implemented; trainer, evaluator, vocab, and visualization remain |
| Q1 Text Classification | unassigned | in_progress | TF-IDF baselines and the BiLSTM path are implemented; DistilBERT remains the next unclaimed Q1 slice |
| Q2 Named Entity Recognition | copilot-q2-crf | in_progress | CRF baseline slice claimed; CoNLL-2003 data flow and initial training pipeline in progress |
| Q3 Summarization | unassigned | todo | TextRank + BART/T5 |
| Q4 Machine Translation | unassigned | todo | Seq2Seq + Transformer |
| Q5 Language Modeling | unassigned | todo | N-gram + LSTM + optional GPT-2 |
| Evaluation and analysis | copilot-q1-eval | in_progress | Q1 confusion-matrix and evaluation artifact export in progress; keep model-training ownership unchanged |
| Report preparation | unassigned | todo | LaTeX report structure and results write-up |
| Project state sync | copilot-tracker | done | docs/agents state synced with the implemented Q1 baseline and scaffold |

---

## Current Priorities

1. Extend the shared scaffold only where Q1 needs it next.
2. Implement BiLSTM and DistilBERT on top of the verified Q1 classical baselines.
3. Freeze broader evaluation and export conventions before scaling Q2-Q5.

---

## Open Blockers

- None recorded yet.

---

## Update Rules

- Use `status.json` as the single source of truth.
- Regenerate this board with `python scripts/agent_status.py sync` after manual JSON edits.
- Detailed agent notes are rendered into `active/*.md`.
