# Agent: copilot-q2-crf

Last updated: 2026-04-13 19:14

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q2-crf
- Date: 2026-04-13
- Scope: Implement the self-contained Q2 CRF baseline slice: CoNLL data loading, BIO preprocessing, token features, CRF model, and Q2 entrypoint

---

## Current Status

- Status: done
- Owner: copilot-q2-crf
- Related area: q2_crf_baseline
- Depends on: -

---

## Work Summary

### Started

- Reviewed board, protocol, Q2 NER design doc, and shared/Q1 pipeline patterns

### In Progress

- None.

### Completed

- Verified that a standard-format CoNLL-2003 mirror loads with the current datasets version and preserves the expected BIO label set
- Implemented a self-contained Q2 pipeline with CoNLL loading, BIO label materialization, token-level CRF features, seqeval-based metrics, and a Q2 CLI entrypoint
- Validated a capped 500-train/200-validation CRF run on tomaarsen/conll2003 with precision 0.753, recall 0.600, F1 0.668, accuracy 0.934, and exported artifacts under outputs/q2/run_20260413_140953

---

## Decisions

- Use tomaarsen/conll2003 because the installed datasets 4.8.4 stack rejects the script-based conll2003 loader
- Default the Q2 dataset to tomaarsen/conll2003 and keep a fallback from conll2003 for environments that reject dataset scripts

---

## Blockers

- None.

---

## Next Actions

1. Claim a separate larger-budget Q2 CRF experiment slice and use the existing outputs as the baseline scaffold for later BiLSTM-CRF and BERT comparisons
