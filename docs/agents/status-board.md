# Agent Status Board

Last updated: 2026-04-13 18:44

This file is generated from `status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Project Overview

| Area | Owner | Status | Notes |
|------|-------|--------|-------|
| Shared infrastructure | unassigned | in_progress | Initial config, seed, dataset split, metrics, export scaffold, shared evaluator, and confusion-matrix visualization helper are implemented; trainer and broader visualization slices remain |
| Q1 Text Classification | unassigned | in_progress | TF-IDF, BiLSTM, and DistilBERT paths are implemented; matched 4k-train/2k-test BiLSTM and DistilBERT runs plus refreshed larger-budget comparison artifacts now exist, while a report-summary refresh remains open |
| Q2 Named Entity Recognition | unassigned | in_progress | All three full-data Q2 runs are complete, BERT is the strongest finished model, and a report-ready comparison summary now exists under outputs/q2/run_20260413_151034 |
| Q3 Summarization | unassigned | todo | TextRank + BART/T5 |
| Q4 Machine Translation | unassigned | todo | Seq2Seq + Transformer |
| Q5 Language Modeling | unassigned | todo | N-gram + LSTM + optional GPT-2 |
| Evaluation and analysis | copilot-q1-eval | review | Shared Q1 evaluation now exports confusion-matrix data, CSVs, and PNG figures; broader reporting and comparison analysis remain separate slices |
| Report preparation | unassigned | in_progress | A minimal LaTeX scaffold now exists under report/, Q2 already has a drafted section, and report/README.md documents how to extend and compile the report once a LaTeX toolchain is available |
| Project state sync | copilot-tracker | done | docs/agents state synced with the implemented Q1 baseline and scaffold |
| Q2 CRF baseline | copilot-q2-crf | done | Self-contained CoNLL CRF baseline implemented and validated on a capped run; any larger-budget experiment can now be claimed as a separate slice |
| Q2 CRF experiment | copilot-q2-crf | done | Full-split CRF experiment completed with exported validation/test artifacts under outputs/q2/run_20260413_141702 |
| Q1 DistilBERT baseline | copilot-q1-distilbert | done | DistilBERT baseline path is implemented and validated by the larger-budget run under outputs/q1/run_20260413_151402; comparison work remains separate |
| Q2 BiLSTM-CRF baseline | copilot-q2-bilstm-crf | done | BiLSTM-CRF path is implemented and validated by the full-data run under outputs/q2/run_20260413_144913; any further optimization is a separate slice |
| Q2 BERT baseline | copilot-q2-bert | done | Self-contained BERT token-classification baseline is implemented and now validated by the larger-budget run under outputs/q2/run_20260413_144742 |
| Q1 visualization | copilot-q1-visualization | review | Shared confusion-matrix figure export is implemented and validated on Q1; training curves and model-comparison figures remain separate visualization slices |
| Q2 BERT experiment | copilot-q2-bert-experiment | done | Full-split 2-epoch BERT experiment completed under outputs/q2/run_20260413_144742 and outperformed the CRF baseline on validation/test F1 (0.9517/0.9062 vs 0.8765/0.7948) |
| Q2 BiLSTM-CRF experiment | copilot-q2-bilstm-crf-experiment | done | Full-split BiLSTM-CRF experiment completed with exported validation/test artifacts under outputs/q2/run_20260413_144913; current test F1 0.714 trails the CRF baseline |
| Q1 model comparison | copilot-q1-comparison | review | Matched Q1 smoke-test comparison artifacts were generated under outputs/q1/run_20260413_145244; larger-budget comparison remains a separate slice |
| Q1 preprocessing comparison | copilot-q1-preprocessing | review | The documented TF-IDF+LR preprocessing sweep is implemented and exported under outputs/q1/run_20260413_145735; the current lowercase+keep-stopwords default already matches the best validation setting |
| Q1 report summary | copilot-q1-report | review | Report-ready Q1 smoke-test summary artifacts were generated under outputs/q1/run_20260413_150237 from the completed comparison and preprocessing runs |
| Q2 report summary | copilot-q2-report | review | Report-ready Q2 summary artifacts were generated under outputs/q2/run_20260413_151034 from the completed CRF, BiLSTM-CRF, and BERT full-data runs |
| Q2 model comparison | copilot-q2-comparison | review | Report-ready Q2 comparison artifacts were generated under outputs/q2/run_20260413_151143, ranking BERT ahead of the CRF baseline and BiLSTM-CRF on overall and per-entity test F1 |
| Q1 DistilBERT experiment | copilot-q1-distilbert-experiment | done | Larger-budget DistilBERT experiment completed under outputs/q1/run_20260413_151402; validation/test macro-F1 0.875/0.879 on the 4k-train/2k-test run and no one-class collapse |
| Q2 report draft | copilot-q2-writeup | review | A minimal report scaffold now exists and q2.tex is drafted from the completed Q2 summary artifacts, including report-local tables and the entity-F1 comparison figure |
| Q1 BiLSTM experiment | copilot-q1-bilstm-experiment | review | Matched 4000-train/2000-test BiLSTM final-eval run completed under outputs/q1/run_20260413_151549 with validation/test macro-F1 0.7386/0.7011 for later Q1 comparison |
| Report build docs | copilot-report-docs | review | report/README.md now documents the scaffold layout, compile prerequisites, section-to-artifact mapping, and the recommended report-writing workflow |
| Q1 larger-budget comparison | copilot-q1-large-comparison | review | Matched 4k-train/2k-test Q1 comparison artifacts are complete under outputs/q1/run_20260413_152437, ranking DistilBERT ahead of TF-IDF + SVM, TF-IDF + LR, and BiLSTM on test macro-F1 |
| Q1 report draft | copilot-q1-writeup | in_progress | Drafting the Q1 report section from the stable 4k-train/2k-test comparison and existing preprocessing sweep without reopening model-training ownership |
| Q1 report summary refresh | copilot-q1-summary-refresh | in_progress | Refreshing the Q1 summary artifact from the stable 4k-train/2k-test comparison and the finished preprocessing sweep without overlapping the active q1.tex drafting slice |

---

## Current Priorities

1. Run larger-budget Q1 neural experiments and compare TF-IDF, BiLSTM, and DistilBERT on a stable export format.
2. Use the finished Q2 artifacts and the new report scaffold to turn Q2 into final report prose, tables, and figures.
3. Turn the exported Q1 and Q2 artifacts into report-ready analysis, tables, and visualizations.

---

## Open Blockers

- None recorded yet.

---

## Update Rules

- Use `status.json` as the single source of truth.
- Regenerate this board with `python scripts/agent_status.py sync` after manual JSON edits.
- Detailed agent notes are rendered into `active/*.md`.
