# Agent: copilot-q1-large-comparison

Last updated: 2026-04-13 23:57

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q1-large-comparison
- Date: 2026-04-13
- Scope: Build refreshed Q1 comparison artifacts from matched 4k-train/2k-test TF-IDF, BiLSTM, and DistilBERT runs

---

## Current Status

- Status: review
- Owner: copilot-q1-large-comparison
- Related area: q1_large_budget_comparison
- Depends on: -

---

## Work Summary

### Started

- Claimed a separate Q1 comparison-refresh slice once matched larger-budget BiLSTM and DistilBERT runs were available

### In Progress

- None.

### Completed

- Ran a matched 4k-train/2k-test TF-IDF reference experiment under outputs/q1/run_20260413_152419
- Built refreshed Q1 comparison artifacts under outputs/q1/run_20260413_152437 from the matched TF-IDF, BiLSTM, and DistilBERT runs
- Validated the comparison CSV, LaTeX table, figure, and manifest with DistilBERT leading test macro-F1 at 0.8793

---

## Decisions

- Kept the comparison slice artifact-only so the report refresh could be claimed separately without mixing ownership

---

## Blockers

- None.

---

## Next Actions

1. Claim the Q1 report draft separately and consume outputs/q1/run_20260413_152437 plus the existing preprocessing sweep artifacts
