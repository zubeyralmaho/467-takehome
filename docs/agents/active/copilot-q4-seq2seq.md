# Agent: copilot-q4-seq2seq

Last updated: 2026-04-13 21:44

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q4-seq2seq
- Date: 2026-04-13
- Scope: Q4 seq2seq+attention baseline

---

## Current Status

- Status: review
- Owner: copilot-q4-seq2seq
- Related area: q4_seq2seq_baseline
- Depends on: -

---

## Work Summary

### Started

- Claimed the missing Q4 seq2seq slice after confirming the current Q4 package is transformer-only and the design doc expects a classical seq2seq-versus-transformer comparison.

### In Progress

- None.

### Completed

- Added a compact word-level GRU encoder-decoder with additive attention under src/q4_machine_translation/models/seq2seq_attention.py and wired it through the existing Q4 config/trainer entrypoint.
- Validated the first seq2seq export path on a 500/100/100 smoke run under outputs/q4/run_20260413_214121, then improved the classical baseline with lowercased preprocessing and min token frequency 1 on outputs/q4/run_20260413_214229.

---

## Decisions

- Use the lowercased 2000/100/100 seq2seq artifact as the initial classical Q4 reference because the smaller case-sensitive smoke run was dominated by unk-heavy translations.

---

## Blockers

- None.

---

## Next Actions

1. Claim a Q4 comparison/report-summary or q4.tex drafting slice next, using outputs/q4/run_20260413_212828 and outputs/q4/run_20260413_214229 as the direct comparison inputs.
