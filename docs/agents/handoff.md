# Handoff

Last updated: 2026-04-13 18:44

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

1. Use outputs/q1/run_20260413_152558 as the refreshed larger-budget Q1 comparison artifact source, then rebuild the Q1 report summary from it plus the finished preprocessing sweep
2. Use report/ plus outputs/q2/run_20260413_151034 and outputs/q2/run_20260413_144742 as the base for Q2 report drafting; only reopen Q2 modeling if a focused tuning slice is justified
3. Only claim new model-training work if a concrete comparison or report gap remains after consuming the finished Q1 and Q2 artifacts

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
- Agent: copilot-q2-bilstm-crf
  Date: 2026-04-13
  Scope: Q2 BiLSTM-CRF baseline
  Outcome: A self-contained BiLSTM-CRF path now runs end to end through the Q2 pipeline and exports the same metrics plus error-analysis artifacts as the CRF baseline
  Next: Run a larger-budget BiLSTM-CRF experiment against outputs/q2/run_20260413_141702; if performance remains O-heavy, claim a focused tuning slice rather than widening this baseline scope
  Blocker: None
- Agent: copilot-q1-visualization
  Date: 2026-04-13
  Scope: Q1 confusion-matrix figures
  Outcome: Q1 runs now export confusion-matrix PNG figures alongside the existing metrics, CSV, and analysis artifacts
  Next: Consume the new figures in reporting work; if broader charts are needed, claim a separate visualization slice for model-comparison or training-curve plots
  Blocker: None
- Agent: copilot-q2-bert
  Date: 2026-04-13
  Scope: Q2 BERT baseline
  Outcome: A self-contained Q2 BERT token-classification path now runs end to end and exports the same artifact set as the CRF baseline, but the capped smoke test collapsed to O-tag predictions
  Next: Run a larger-budget BERT experiment against outputs/q2/run_20260413_141702; if entity F1 stays at 0, claim a focused tuning slice for schedule, batch size, or label-alignment strategy
  Blocker: None
- Agent: copilot-q2-bert-experiment
  Date: 2026-04-13
  Scope: Q2 BERT experiment
  Outcome: A full-split 2-epoch BERT experiment is currently running on the completed Q2 BERT baseline path; the run directory already exists at outputs/q2/run_20260413_144742
  Next: When metrics.json appears under outputs/q2/run_20260413_144742, compare the finished BERT results against outputs/q2/run_20260413_141702 and decide whether the slice can move to review or needs a focused tuning follow-up
  Blocker: None
- Agent: copilot-q1-preprocessing
  Date: 2026-04-13
  Scope: Q1 preprocessing comparison
  Outcome: The documented TF-IDF + LR preprocessing sweep now runs end to end and exports a ranked comparison artifact; the existing lowercase+keep-stopwords default remains a best validation setting
  Next: Carry the current preprocessing default into larger-budget BiLSTM and DistilBERT experiments; only reopen preprocessing if those neural runs expose a concrete failure mode
  Blocker: None
- Agent: copilot-q1-report
  Date: 2026-04-13
  Scope: Q1 report summary
  Outcome: A report-ready Q1 smoke-test summary now exists with Markdown, JSON, and LaTeX outputs derived from the completed comparison and preprocessing artifacts
  Next: Use outputs/q1/run_20260413_150237 for interim reporting, then rerun the summary builder after larger-budget neural experiments complete
  Blocker: None
- Agent: copilot-q2-bert-experiment
  Date: 2026-04-13
  Scope: Q2 BERT experiment
  Outcome: The larger-budget BERT run completed successfully and now stands as the strongest finished Q2 model, outperforming the full-data CRF baseline on both validation and test F1
  Next: Treat outputs/q2/run_20260413_144742 as the Q2 BERT reference point for report tables and for comparison against the pending BiLSTM-CRF experiment artifacts
  Blocker: None
- Agent: copilot-q2-bilstm-crf-experiment
  Date: 2026-04-13
  Scope: Q2 BiLSTM-CRF experiment
  Outcome: Full-data BiLSTM-CRF experiment completed with exported validation/test artifacts and a usable neural comparison point
  Next: Compare outputs/q2/run_20260413_144913 against the finished CRF and BERT runs in analysis/reporting, or claim a focused BiLSTM-CRF tuning slice if recurrent modeling still needs improvement
  Blocker: None
- Agent: copilot-q2-report
  Date: 2026-04-13
  Scope: Q2 report summary
  Outcome: A report-ready Q2 comparison summary now exists with Markdown, JSON, and LaTeX outputs derived from the completed CRF, BiLSTM-CRF, and BERT runs
  Next: Use outputs/q2/run_20260413_151034 alongside outputs/q2/run_20260413_144742 when drafting Q2 report tables and discussion; only claim more Q2 modeling work if BiLSTM-CRF tuning is worth the budget
  Blocker: None
- Agent: copilot-q2-comparison
  Date: 2026-04-13
  Scope: Q2 model comparison
  Outcome: A finished Q2 comparison run now aggregates CRF, BiLSTM-CRF, and BERT into overall and per-entity report-ready artifacts, with BERT leading every entity type on the test split
  Next: Reuse outputs/q2/run_20260413_151143 for Q2 report tables and discussion, or rerun the comparison builder later if a tuned BiLSTM-CRF experiment supersedes outputs/q2/run_20260413_144913
  Blocker: None
- Agent: copilot-q2-writeup
  Date: 2026-04-13
  Scope: Q2 report draft
  Outcome: A buildable report skeleton now exists and the Q2 section is drafted with tables, figure support, and narrative aligned to the finished experiment artifacts
  Next: Draft the remaining report sections as separate slices and compile the report once pdflatex or an equivalent LaTeX toolchain is available
  Blocker: pdflatex is not installed in the current environment, so full PDF compilation could not be verified
- Agent: copilot-q1-bilstm-experiment
  Date: 2026-04-13
  Scope: Q1 BiLSTM experiment
  Outcome: A larger-budget Q1 BiLSTM run now exists with full exported artifacts and substantially improved metrics over the earlier smoke test
  Next: Compare outputs/q1/run_20260413_151549 against the TF-IDF baseline and the finished DistilBERT larger-budget run once that slice produces stable metrics
  Blocker: The active DistilBERT experiment currently owns the matching second neural run, and its latest visible artifacts are not yet comparison-ready
- Agent: copilot-report-docs
  Date: 2026-04-13
  Scope: Report build docs
  Outcome: The report scaffold now includes local usage documentation, compile commands, and artifact mapping so future write-up slices can extend it consistently
  Next: Draft the remaining report sections against stable experiment artifacts and run a real LaTeX compile when a toolchain is installed
  Blocker: latexmk/pdflatex are not installed in the current environment, so the documented compile commands were not executed here
- Agent: copilot-q1-distilbert-experiment
  Date: 2026-04-13
  Scope: Q1 DistilBERT experiment
  Outcome: A larger-budget DistilBERT run completed successfully after restoring the Q1 trainer wiring, and the resulting 4k-train/2k-test artifact is strong enough to feed the next Q1 comparison pass
  Next: Use outputs/q1/run_20260413_151402 in larger-budget Q1 comparison work, or claim a focused BiLSTM experiment so the neural models can be compared on a closer footing
  Blocker: None
- Agent: copilot-q1-compare-refresh
  Date: 2026-04-13
  Scope: Q1 larger-budget comparison
  Outcome: A matched larger-budget Q1 comparison now exists and shows DistilBERT as the strongest finished model on the shared 4k-train/2k-test budget
  Next: Refresh the Q1 report summary and q1.tex using outputs/q1/run_20260413_152437 together with the stable preprocessing comparison artifacts
  Blocker: None
- Agent: copilot-q1-large-comparison
  Date: 2026-04-13
  Scope: Q1 large-budget comparison
  Outcome: A refreshed larger-budget Q1 comparison now exists with matched 4k-train/2k-test TF-IDF, BiLSTM, and DistilBERT results plus report-ready table/figure artifacts
  Next: Use outputs/q1/run_20260413_152558 to refresh the Q1 report summary and drafting artifacts, or only reopen modeling if a concrete metric gap still needs explanation
  Blocker: None
- Agent: copilot-q1-large-comparison
  Date: 2026-04-13
  Scope: Q1 large-budget comparison
  Outcome: A stable matched 4k-train/2k-test Q1 comparison now exists with report-ready CSV, LaTeX, and figure artifacts showing DistilBERT as the strongest model
  Next: Use outputs/q1/run_20260413_152437 and outputs/q1/run_20260413_145735 to draft the final Q1 report section and report-local tables or figures
  Blocker: None
