# Agent: copilot-q2-crf-experiment

Last updated: 2026-04-13 21:51

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q2-crf-experiment
- Date: 2026-04-13
- Scope: Run and evaluate a larger-budget Q2 CRF experiment using the existing self-contained baseline scaffold

---

## Current Status

- Status: done
- Owner: copilot-q2-crf
- Related area: q2_crf_experiment
- Depends on: -

---

## Work Summary

### Started

- Claimed a separate experiment slice after the Q2 CRF baseline implementation was completed

### In Progress

- None.

### Completed

- Ran the full-config Q2 CRF experiment with final evaluation enabled on tomaarsen/conll2003
- Exported metrics, error analysis, and prediction CSVs under outputs/q2/run_20260413_141702
- Achieved validation precision 0.894, recall 0.860, F1 0.876, accuracy 0.976 and test precision 0.813, recall 0.777, F1 0.795, accuracy 0.957

---

## Decisions

- The full-data CRF baseline substantially improves over the 500-train smoke run and is now stable enough to serve as the Q2 comparison baseline

---

## Blockers

- None.

---

## Next Actions

1. Claim BiLSTM-CRF or BERT as the next Q2 slice and compare against outputs/q2/run_20260413_141702
