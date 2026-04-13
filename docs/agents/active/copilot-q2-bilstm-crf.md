# Agent: copilot-q2-bilstm-crf

Last updated: 2026-04-13 14:54

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q2-bilstm-crf
- Date: 2026-04-13
- Scope: Implement and validate a self-contained Q2 BiLSTM-CRF baseline using the existing CoNLL data and Q2 evaluation/export flow

---

## Current Status

- Status: review
- Owner: copilot-q2-bilstm-crf
- Related area: q2_bilstm_crf_baseline
- Depends on: -

---

## Work Summary

### Started

- Reviewed the board and claimed the next Q2 neural slice after the CRF baseline was stabilized

### In Progress

- None.

### Completed

- Added an opt-in Q2 BiLSTM-CRF model path with token vocabulary building, padded sequence batching, neural CRF decoding, and early-stopping support on the existing CoNLL data/evaluation scaffold
- Added the pytorch-crf dependency, exposed BiLSTM-CRF hyperparameters in configs/q2.yaml, and extended environment export to record the CRF-layer package version
- Validated a capped BiLSTM-CRF-only final-eval run on Q2 and confirmed metrics, prediction CSVs, and error analysis under outputs/q2/run_20260413_142615

---

## Decisions

- Kept the Q2 default config CRF-only and made BiLSTM-CRF opt-in so the existing baseline run remains stable while the neural slice is tuned

---

## Blockers

- None.

---

## Next Actions

1. Run a larger-budget BiLSTM-CRF experiment and compare it directly against outputs/q2/run_20260413_141702; revisit optimization only if the larger run still collapses toward O-heavy tagging
