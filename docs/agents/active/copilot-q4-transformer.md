# Agent: copilot-q4-transformer

Last updated: 2026-04-15 22:21

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q4-transformer
- Date: 2026-04-13
- Scope: Implement and validate a pretrained transformer Q4 translation baseline

---

## Current Status

- Status: review
- Owner: copilot-q4-transformer
- Related area: q4_transformer_baseline
- Depends on: -

---

## Work Summary

### Started

- Selected the first Q4 slice after confirming that Question 4 was still entirely unimplemented and unowned.

### In Progress

- None.

### Completed

- Added configs/q4.yaml and a new src/q4_machine_translation package with dataset loading, BLEU/ChrF evaluation, qualitative export helpers, and a pretrained transformer wrapper around Helsinki-NLP/opus-mt-en-de.
- Installed the missing MT dependencies needed for tokenizer and BLEU/ChrF evaluation support.
- Validated the full Q4 export path on a capped 100-validation/100-test Multi30k run under outputs/q4/run_20260413_212828.

---

## Decisions

- Start Q4 with a pretrained transformer baseline so a later seq2seq+attention slice can reuse the same dataset, evaluation, and export contract.
- Keep the first Q4 metric suite lightweight with BLEU and ChrF so the baseline remains practical on the current environment.

---

## Blockers

- None.

---

## Next Actions

1. Claim a seq2seq+attention Q4 slice next if modeling should continue, or consume outputs/q4/run_20260413_212828 in a later Q4 report-summary slice.
