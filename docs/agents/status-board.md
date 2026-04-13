# Agent Status Board

Last updated: 2026-04-13 14:18

This file is generated from `status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Project Overview

| Area | Owner | Status | Notes |
|------|-------|--------|-------|
| Shared infrastructure | unassigned | in_progress | Initial config, seed, dataset split, metrics, and export scaffold implemented; trainer, evaluator, vocab, and visualization remain |
| Q1 Text Classification | unassigned | in_progress | TF-IDF baselines and the BiLSTM path are implemented; the DistilBERT slice is now claimed separately while preprocessing sweeps and any larger-budget neural runs remain unclaimed |
| Q2 Named Entity Recognition | unassigned | in_progress | The Q2 CRF baseline and larger-budget run are complete; BiLSTM-CRF and BERT slices remain unclaimed |
| Q3 Summarization | unassigned | todo | TextRank + BART/T5 |
| Q4 Machine Translation | unassigned | todo | Seq2Seq + Transformer |
| Q5 Language Modeling | unassigned | todo | N-gram + LSTM + optional GPT-2 |
| Evaluation and analysis | copilot-q1-eval | review | Shared Q1 evaluation now exports confusion-matrix data in metrics.json and per-split confusion_matrices CSVs; visualization figures remain a separate slice |
| Report preparation | unassigned | todo | LaTeX report structure and results write-up |
| Project state sync | copilot-tracker | done | docs/agents state synced with the implemented Q1 baseline and scaffold |
| Q2 CRF baseline | copilot-q2-crf | done | Self-contained CoNLL CRF baseline implemented and validated on a capped run; any larger-budget experiment can now be claimed as a separate slice |
| Q2 CRF experiment | copilot-q2-crf | done | Full-split CRF experiment completed with exported validation/test artifacts under outputs/q2/run_20260413_141702 |
| Q1 DistilBERT baseline | copilot-q1-distilbert | in_progress | DistilBERT sequence-classification slice claimed; integrate a Hugging Face baseline into the existing Q1 training/export path |

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
