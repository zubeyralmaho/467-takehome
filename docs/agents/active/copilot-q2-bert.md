# Agent: copilot-q2-bert

Last updated: 2026-04-13 21:45

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q2-bert
- Date: 2026-04-13
- Scope: Implement and smoke-test a self-contained Q2 BERT token-classification baseline on top of the existing Q2 scaffold

---

## Current Status

- Status: review
- Owner: copilot-q2-bert
- Related area: q2_bert_baseline
- Depends on: -

---

## Work Summary

### Started

- Reviewed the live tracker, existing Q2 CRF scaffold, and Q2 model requirements before claiming the next neural slice

### In Progress

- None.

### Completed

- Added a BERT token-classification wrapper with fit, predict, and token-confidence interfaces compatible with the existing Q2 training/export flow
- Wired the BERT model into the Q2 model registry, config, and training factory without touching shared modules
- Validated a capped BERT-only final-eval run on CoNLL under outputs/q2/run_20260413_144034 and confirmed metrics, error analysis, and prediction CSV exports

---

## Decisions

- Kept the BERT path on the existing Q2 token-list pipeline and added word-level alignment guards so truncated tokenizer outputs cannot break seqeval evaluation
- The capped one-epoch smoke test collapses to O tags, so the slice should stay in review until a larger-budget run or targeted tuning confirms meaningful entity predictions

---

## Blockers

- None.

---

## Next Actions

1. Run a larger-budget BERT experiment with more epochs and compare it against outputs/q2/run_20260413_141702; if it still collapses to O tags, claim a focused optimization slice for training schedule or token-label handling
