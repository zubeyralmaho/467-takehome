# Agent: copilot-q4-seq2seq

Last updated: 2026-04-13 21:43

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q4-seq2seq
- Date: 2026-04-13
- Scope: Q4 seq2seq+attention baseline

---

## Current Status

- Status: in_progress
- Owner: copilot-q4-seq2seq
- Related area: q4_seq2seq_baseline
- Depends on: -

---

## Work Summary

### Started

- Claimed the missing Q4 seq2seq slice after confirming the current Q4 package is transformer-only and the design doc expects a classical seq2seq-versus-transformer comparison.

### In Progress

- Add a compact word-level encoder-decoder with attention that reuses the current Multi30k loader, BLEU/ChrF evaluator, and translation export path.

### Completed

- None.

---

## Decisions

- Keep the first classical Q4 slice to a compact GRU-based seq2seq+attention model with greedy decoding so it stays trainable on the current environment.

---

## Blockers

- None.

---

## Next Actions

1. Implement the seq2seq model path, validate it on a capped Multi30k run, and compare it qualitatively against the finished transformer baseline.
