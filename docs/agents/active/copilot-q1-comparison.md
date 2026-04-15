# Agent: copilot-q1-comparison

Last updated: 2026-04-15 22:16

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q1-comparison
- Date: 2026-04-13
- Scope: Build matched Q1 smoke-test comparison artifacts for TF-IDF, BiLSTM, and DistilBERT

---

## Current Status

- Status: review
- Owner: copilot-q1-comparison
- Related area: q1_model_comparison
- Depends on: -

---

## Work Summary

### Started

- Reviewed the tracker, current Q1 runs, and report expectations for comparison tables and figures

### In Progress

- None.

### Completed

- Ran a matched 200/100 BiLSTM smoke test under outputs/q1/run_20260413_144941 so TF-IDF, BiLSTM, and DistilBERT had comparable Q1 smoke-test runs
- Added shared metric-comparison plotting and LaTeX table helpers for report-ready comparison outputs
- Added a reusable Q1 comparison builder script that aggregates existing runs into JSON, CSV, LaTeX, and figure artifacts
- Validated matched Q1 smoke-test comparison artifacts under outputs/q1/run_20260413_145244 with TF-IDF + SVM leading the test macro-F1 ranking
- Synced the Q1 expected outputs doc with the new model_comparison CSV and LaTeX artifacts

---

## Decisions

- Kept this slice on matched 200/100 smoke-test runs instead of mixing metrics from runs with different dataset caps

---

## Blockers

- None.

---

## Next Actions

1. Run larger-budget matched BiLSTM and DistilBERT experiments, then rebuild the comparison artifacts for a report-quality Q1 table and figure
