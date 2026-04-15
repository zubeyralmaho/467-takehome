# Agent: copilot-q2-bilstm-crf-experiment

Last updated: 2026-04-15 22:22

This file is generated from `../status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Identity

- Agent name: copilot-q2-bilstm-crf-experiment
- Date: 2026-04-13
- Scope: Run and evaluate a larger-budget Q2 BiLSTM-CRF experiment using the implemented neural baseline path

---

## Current Status

- Status: done
- Owner: copilot-q2-bilstm-crf-experiment
- Related area: q2_bilstm_crf_experiment
- Depends on: -

---

## Work Summary

### Started

- Claimed a separate experiment slice after the Q2 BiLSTM-CRF implementation was validated on a capped run

### In Progress

- None.

### Completed

- Ran the full-config Q2 BiLSTM-CRF experiment with final evaluation enabled on tomaarsen/conll2003
- Exported metrics, error analysis, and prediction CSVs under outputs/q2/run_20260413_144913
- Observed validation precision 0.829, recall 0.763, F1 0.794, accuracy 0.957 and test precision 0.767, recall 0.668, F1 0.714, accuracy 0.937

---

## Decisions

- The full-data BiLSTM-CRF run improves drastically over the capped smoke test but still trails the CRF baseline by roughly 0.08 F1 on both validation and test

---

## Blockers

- None.

---

## Next Actions

1. Compare outputs/q2/run_20260413_144913 against the finished CRF and BERT runs in analysis/reporting, or claim a focused BiLSTM-CRF tuning slice if the recurrent model still needs improvement
