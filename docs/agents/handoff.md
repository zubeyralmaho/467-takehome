# Handoff

Last updated: 2026-04-13 14:20

This file is generated from `status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Current Blockers

- None.

---

## Pending Decisions

- Dataset finalization for each question.
- Exact experiment budget per task.
- Whether optional GPT-2 fine-tuning will be included in Q5.

---

## Next Recommended Actions

1. Claim the DistilBERT Q1 slice as the next separate owner and reuse the verified Q1 export flow
2. Run a larger-budget BiLSTM experiment once the Q1 neural experiment budget is finalized
3. Extend shared evaluation/export only if DistilBERT reveals a concrete gap

---

## Entries

- Agent: copilot-ops
  Date: 2026-04-13
  Scope: Agent tracking automation
  Outcome: JSON state and CLI now generate the board, handoff view, and per-agent log
  Next: Use the CLI as agents pick up Q1-Q5 work
  Blocker: None
- Agent: copilot-tracker
  Date: 2026-04-13
  Scope: Project state sync
  Outcome: docs/agents now reflects the implemented shared scaffold and Q1 classical baseline progress
  Next: Claim the next Q1 neural-model slice before editing implementation files
  Blocker: None
- Agent: copilot-q1-bilstm
  Date: 2026-04-13
  Scope: Q1 BiLSTM implementation
  Outcome: Added an opt-in BiLSTM path, fixed CLI override handling, and validated the end-to-end export flow on a small IMDb run
  Next: Claim DistilBERT as a separate Q1 slice and reuse the same metrics and prediction export path
  Blocker: None
- Agent: copilot-q1-eval
  Date: 2026-04-13
  Scope: Shared Q1 evaluation artifact export
  Outcome: Q1 runs now write structured confusion-matrix data into metrics.json and export per-split confusion_matrices CSV files without changing model-training ownership
  Next: Consume the new artifacts in analysis/reporting work; if figure outputs are required, claim a separate visualization slice
  Blocker: None
- Agent: copilot-q2-crf
  Date: 2026-04-13
  Scope: Q2 CRF baseline
  Outcome: Self-contained Q2 CRF baseline is implemented, smoke-tested end to end, and exports metrics plus token-level prediction CSVs
  Next: Claim a separate larger-budget CRF experiment slice, reuse configs/q2.yaml, and compare future neural Q2 models against the exported CRF artifacts
  Blocker: None
- Agent: copilot-q2-crf-experiment
  Date: 2026-04-13
  Scope: Q2 CRF experiment
  Outcome: Full-split CRF baseline run is complete with strong validation metrics and exported validation/test artifacts
  Next: Claim a separate BiLSTM-CRF or BERT Q2 slice and compare it directly against outputs/q2/run_20260413_141549
  Blocker: None
- Agent: copilot-q2-crf-experiment
  Date: 2026-04-13
  Scope: Q2 CRF experiment
  Outcome: Full-data CRF experiment completed with a stable exported baseline at outputs/q2/run_20260413_141702
  Next: Claim BiLSTM-CRF or BERT as the next Q2 slice and compare against the exported CRF metrics plus error_analysis artifacts
  Blocker: None
- Agent: copilot-q1-distilbert
  Date: 2026-04-13
  Scope: Q1 DistilBERT baseline
  Outcome: A self-contained DistilBERT baseline now runs end to end through the existing Q1 pipeline and exports the same metrics and artifact set as the other Q1 models
  Next: Run a larger-budget DistilBERT experiment for a meaningful comparison against TF-IDF and BiLSTM; if it still predicts one class, claim a focused preprocessing or optimization slice
  Blocker: None
