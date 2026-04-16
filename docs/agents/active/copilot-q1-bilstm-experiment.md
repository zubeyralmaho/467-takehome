# Agent: copilot-q1-bilstm-experiment

Last updated: 2026-04-15 22:24

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q1-bilstm-experiment
- Date: 2026-04-13
- Scope: Q1 BiLSTM experiment

---

## Current Status

- Status: review
- Owner: copilot-q1-bilstm-experiment
- Related area: q1_bilstm_experiment
- Depends on: -

---

## Work Summary

### Started

- Reviewed the live tracker and selected the unowned Q1 BiLSTM larger-budget experiment as the clean parallel follow-up to the active DistilBERT experiment

### In Progress

- None.

### Completed

- Ran a matched 4000-train/2000-test BiLSTM-only final-eval experiment under outputs/q1/run_20260413_151549
- Validated exported metrics, confusion-matrix CSVs, predictions, and misclassification analysis with validation/test macro-F1 0.7386/0.7011

---

## Decisions

- Kept this slice limited to the reusable experiment artifact so the later Q1 comparison refresh can consume it without changing reporting or DistilBERT ownership

---

## Blockers

- None.

---

## Next Actions

1. Reuse outputs/q1/run_20260413_151549 in the larger-budget Q1 comparison once the DistilBERT experiment owner finishes a matching usable run
