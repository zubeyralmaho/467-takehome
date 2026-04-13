# Agent: copilot-q2-comparison

Last updated: 2026-04-14 00:44

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q2-comparison
- Date: 2026-04-13
- Scope: Q2 model comparison

---

## Current Status

- Status: review
- Owner: copilot-q2-comparison
- Related area: q2_model_comparison
- Depends on: -

---

## Work Summary

### Started

- Reviewed the live tracker and selected a Q2 comparison slice that only consumes finished run artifacts

### In Progress

- None.

### Completed

- Added a reusable Q2 comparison builder that exports overall and per-entity CSV and LaTeX tables plus an entity-F1 comparison figure
- Validated comparison outputs under outputs/q2/run_20260413_151143 using the finished CRF, BiLSTM-CRF, and BERT full-data runs

---

## Decisions

- Kept this slice focused on reusable comparison artifacts so the separate Q2 report-summary owner can consume them without cross-editing model or summary logic

---

## Blockers

- None.

---

## Next Actions

1. Use outputs/q2/run_20260413_151143 as the report-table source for Q2 and only reopen comparison if a tuned BiLSTM-CRF rerun changes the ranking
