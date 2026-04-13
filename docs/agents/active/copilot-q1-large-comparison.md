# Agent: copilot-q1-large-comparison

Last updated: 2026-04-13 15:26

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q1-large-comparison
- Date: 2026-04-13
- Scope: Build refreshed Q1 comparison artifacts from matched 4k-train/2k-test TF-IDF, BiLSTM, and DistilBERT runs

---

## Current Status

- Status: done
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

- Ran a matched 4k-train/2k-test TF-IDF reference experiment under outputs/q1/run_20260413_152535 so TF-IDF, BiLSTM, and DistilBERT all had aligned larger-budget artifacts
- Built refreshed Q1 comparison outputs under outputs/q1/run_20260413_152558 from outputs/q1/run_20260413_152535, outputs/q1/run_20260413_151549, and outputs/q1/run_20260413_151402
- Validated the larger-budget ranking with DistilBERT first at test macro-F1 0.879, TF-IDF + SVM second at 0.851, TF-IDF + LR third at 0.840, and BiLSTM fourth at 0.701

---

## Decisions

- Kept this slice artifact-only by reusing the existing comparison builder and generating the one missing matched TF-IDF run instead of editing the stable reporting scripts

---

## Blockers

- None.

---

## Next Actions

1. Use outputs/q1/run_20260413_152558 as the larger-budget Q1 comparison source, or claim a report-summary refresh slice to turn it into final write-up artifacts
