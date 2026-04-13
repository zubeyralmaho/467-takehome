# Agent: copilot-q1-preprocessing

Last updated: 2026-04-13 21:57

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q1-preprocessing
- Date: 2026-04-13
- Scope: Implement and validate the documented Q1 preprocessing sweep for TF-IDF + LR

---

## Current Status

- Status: review
- Owner: copilot-q1-preprocessing
- Related area: q1_preprocessing_comparison
- Depends on: -

---

## Work Summary

### Started

- Reviewed the current Q1 preprocessor, the documented sweep settings, and the available config hooks

### In Progress

- None.

### Completed

- Added a reusable Q1 preprocessing-comparison runner that executes the documented TF-IDF + LR A-D sweep and exports CSV plus JSON artifacts
- Validated the preprocessing sweep on a capped 1000-example training subset and exported artifacts under outputs/q1/run_20260413_145735
- Confirmed that the current lowercase+keep-stopwords default ties for the best validation macro-F1, so no config change is needed

---

## Decisions

- Kept the sweep validation-only so the held-out Q1 test split remains untouched for later final model comparison

---

## Blockers

- None.

---

## Next Actions

1. Reuse the current default preprocessing for larger-budget Q1 neural experiments, or extend the comparison slice later if character n-gram or stopword-heavy variants become necessary
