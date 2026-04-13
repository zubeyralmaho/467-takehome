# Agent Status Board

Last updated: 2026-04-13 14:54

This file is generated from `status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Project Overview

| Area | Owner | Status | Notes |
|------|-------|--------|-------|
| Shared infrastructure | unassigned | in_progress | Initial config, seed, dataset split, metrics, export scaffold, shared evaluator, and confusion-matrix visualization helper are implemented; trainer and broader visualization slices remain |
| Q1 Text Classification | unassigned | in_progress | TF-IDF, BiLSTM, and DistilBERT paths are implemented; matched smoke-test comparison artifacts are ready while preprocessing sweeps and larger-budget neural runs remain open |
| Q2 Named Entity Recognition | unassigned | in_progress | The Q2 CRF baseline and a BERT smoke-test path are in place; BiLSTM-CRF remains unclaimed and larger-budget BERT training/comparison remain open |
| Q3 Summarization | unassigned | todo | TextRank + BART/T5 |
| Q4 Machine Translation | unassigned | todo | Seq2Seq + Transformer |
| Q5 Language Modeling | unassigned | todo | N-gram + LSTM + optional GPT-2 |
| Evaluation and analysis | copilot-q1-eval | review | Shared Q1 evaluation now exports confusion-matrix data, CSVs, and PNG figures; broader reporting and comparison analysis remain separate slices |
| Report preparation | unassigned | todo | LaTeX report structure and results write-up |
| Project state sync | copilot-tracker | done | docs/agents state synced with the implemented Q1 baseline and scaffold |
| Q2 CRF baseline | copilot-q2-crf | done | Self-contained CoNLL CRF baseline implemented and validated on a capped run; any larger-budget experiment can now be claimed as a separate slice |
| Q2 CRF experiment | copilot-q2-crf | done | Full-split CRF experiment completed with exported validation/test artifacts under outputs/q2/run_20260413_141702 |
| Q1 DistilBERT baseline | copilot-q1-distilbert | review | Self-contained DistilBERT baseline implemented and smoke-tested on IMDb; larger-budget training and comparison analysis remain |
| Q2 BiLSTM-CRF baseline | copilot-q2-bilstm-crf | review | BiLSTM-CRF path is implemented and smoke-tested on a capped Q2 run; a larger-budget neural experiment is still needed before comparison against the CRF baseline |
| Q2 BERT baseline | copilot-q2-bert | review | Self-contained BERT token-classification baseline implemented and smoke-tested on a capped CoNLL run; larger-budget training and anti-collapse tuning remain |
| Q1 visualization | copilot-q1-visualization | review | Shared confusion-matrix figure export is implemented and validated on Q1; training curves and model-comparison figures remain separate visualization slices |
| Q2 BERT experiment | copilot-q2-bert | in_progress | A full-split 2-epoch BERT experiment is actively running under outputs/q2/run_20260413_144742; metrics and comparison analysis are pending when the run finishes |
| Q2 BiLSTM-CRF experiment | copilot-q2-bilstm-crf-experiment | in_progress | Larger-budget BiLSTM-CRF experiment claimed on top of the implemented Q2 neural baseline |
| Q1 model comparison | copilot-q1-comparison | review | Matched Q1 smoke-test comparison artifacts were generated under outputs/q1/run_20260413_145244; larger-budget comparison remains a separate slice |

---

## Current Priorities

1. Run larger-budget Q1 neural experiments and compare TF-IDF, BiLSTM, and DistilBERT on a stable export format.
2. Claim the next Q2 neural slice against the stabilized CRF baseline.
3. Turn the exported Q1 and Q2 artifacts into report-ready analysis, tables, and visualizations.

---

## Open Blockers

- None recorded yet.

---

## Update Rules

- Use `status.json` as the single source of truth.
- Regenerate this board with `python scripts/agent_status.py sync` after manual JSON edits.
- Detailed agent notes are rendered into `active/*.md`.
