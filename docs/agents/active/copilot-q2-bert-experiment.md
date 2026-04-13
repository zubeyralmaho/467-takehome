# Agent: copilot-q2-bert-experiment

Last updated: 2026-04-13 23:20

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q2-bert-experiment
- Date: 2026-04-13
- Scope: Q2 BERT experiment

---

## Current Status

- Status: done
- Owner: copilot-q2-bert-experiment
- Related area: q2_bert_experiment
- Depends on: -

---

## Work Summary

### Started

- Claimed a separate experiment slice after the Q2 BERT implementation was validated on a capped run

### In Progress

- None.

### Completed

- Ran a full-split 2-epoch BERT experiment under outputs/q2/run_20260413_144742 and exported metrics, error analysis, and prediction CSV artifacts
- BERT reached validation F1 0.9517 and test F1 0.9062, beating the CRF baseline at outputs/q2/run_20260413_141702 (validation F1 0.8765, test F1 0.7948)

---

## Decisions

- Closed the experiment slice without opening a tuning follow-up because the larger-budget run resolved the earlier capped-run O-tag collapse concern

---

## Blockers

- None.

---

## Next Actions

1. Use outputs/q2/run_20260413_144742 as the current Q2 best-model reference and compare it against the in-progress BiLSTM-CRF larger-budget run when that slice finishes
