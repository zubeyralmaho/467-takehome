# Agent: copilot-q4-seq2seq

Last updated: 2026-04-15 22:24

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q4-seq2seq
- Date: 2026-04-13
- Scope: Implement and validate a Q4 seq2seq+attention machine-translation baseline

---

## Current Status

- Status: review
- Owner: copilot-q4-seq2seq
- Related area: q4_seq2seq_baseline
- Depends on: -

---

## Work Summary

### Started

- Claimed the next unowned Q4 modeling slice after the pretrained transformer baseline moved to review.

### In Progress

- None.

### Completed

- Validated the existing Q4 seq2seq training/export path on a small capped run under outputs/q4/run_20260413_214240 and identified greedy-decoding collapse into special tokens as the main runtime issue.
- Fixed seq2seq greedy decoding by suppressing PAD/BOS/UNK outputs during inference and detokenizing generated translations more cleanly.
- Validated a stronger capped seq2seq run under outputs/q4/run_20260413_214538 on 1000/100/100 Multi30k splits with exported validation/test metrics and translation CSVs.
- Verified that outputs/q4/run_20260413_214229 is the strongest current seq2seq reference artifact in the workspace and should be used for future Q4 comparison/report slices instead of the later weaker smoke-style reruns.

---

## Decisions

- Kept this slice focused on the custom seq2seq baseline and its export contract, leaving direct comparison against the reviewed transformer artifact for a separate Q4 analysis or report slice.

---

## Blockers

- None.

---

## Next Actions

1. Claim a Q4 comparison or report-summary slice next and compare outputs/q4/run_20260413_214538 against outputs/q4/run_20260413_212828.
