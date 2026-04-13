# Handoff

Last updated: 2026-04-13 21:45

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

1. Use outputs/q1/run_20260413_185011, outputs/q1/run_20260413_152558, and the finished preprocessing sweep while finalizing the Q1 report draft
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
- Agent: copilot-q1-writeup
  Date: 2026-04-13
  Scope: Q1 report draft
  Outcome: The Q1 report section is now drafted with larger-budget results, local tables, and figure assets that match the finished Q1 comparison artifacts
  Next: Use report/sections/q1.tex together with the copied Q1 figures and tables during final report assembly, then run a real LaTeX compile when pdflatex or latexmk becomes available
  Blocker: The current environment does not have pdflatex or latexmk, so PDF compilation could not be verified here
- Agent: copilot-q1-writeup
  Date: 2026-04-13
  Scope: Q1 report draft
  Outcome: The Q1 report section, report-local tables, and figure references now reflect the stable larger-budget artifacts and are ready for report compilation
  Next: Install or provide latexmk/pdflatex, compile report/main.tex, and incorporate the separate Q1 summary-refresh outputs only if they improve wording or reuse
  Blocker: No LaTeX toolchain is installed in the current workspace environment
- Agent: copilot-q1-summary-refresh
  Date: 2026-04-13
  Scope: Q1 report summary refresh
  Outcome: A refreshed larger-budget Q1 summary now exists with Markdown, JSON, and LaTeX outputs that reflect the finished 4k-train/2k-test comparison and the preprocessing sweep
  Next: Consume outputs/q1/run_20260413_185011 in the active Q1 report-draft slice and keep the preprocessing recommendation unchanged unless a later report pass needs more detail
  Blocker: None
- Agent: copilot-report-intro
  Date: 2026-04-13
  Scope: Report introduction draft
  Outcome: The introduction now matches the current project state and gives the report a proper overview section instead of a placeholder paragraph
  Next: Use report/sections/introduction.tex and report/tables/introduction_task_overview.tex during final report assembly, or update only if the remaining question scopes change materially
  Blocker: None
- Agent: copilot-q3-textrank
  Date: 2026-04-13
  Scope: Q3 TextRank baseline + evaluation/export pipeline
  Outcome: Implemented the first Q3 baseline and exported capped validation/test artifacts at outputs/q3/run_20260413_185438.
  Next: Use outputs/q3/run_20260413_185438 as the extractive baseline reference, then claim BART/T5 or a larger-budget Q3 slice separately.
  Blocker: None
- Agent: copilot-q3-writeup
  Date: 2026-04-13
  Scope: Q3 report draft
  Outcome: The Q3 section now has a stable baseline-only write-up tied to the finished TextRank run and a report-local metric table
  Next: Use report/sections/q3.tex as the extractive baseline subsection now, then refresh it after a BART or T5 slice is completed
  Blocker: The main comparative Q3 claim remains incomplete until an abstractive model is implemented and evaluated
- Agent: copilot-q3-bart
  Date: 2026-04-13
  Scope: Q3 pretrained abstractive summarizer
  Outcome: A pretrained abstractive Q3 baseline is now validated and directly comparable to TextRank via outputs/q3/run_20260413_192426.
  Next: Use outputs/q3/run_20260413_192426 to refresh the provisional Q3 report section or build a report-summary artifact; only reopen modeling if a larger-budget Q3 comparison is justified.
  Blocker: None
- Agent: copilot-q3-bart
  Date: 2026-04-13
  Scope: Q3 BART baseline
  Outcome: Implemented and smoke-validated the new abstractive summarization path; the stable smoke artifact is outputs/q3/run_20260413_191614.
  Next: If outputs/q3/run_20260413_192158 finishes cleanly, use it to refresh report/sections/q3.tex and report/tables/q3_overall_results.tex with a true TextRank-vs-DistilBART comparison.
  Blocker: None; the longer cached benchmark is still running in the background and may simply take several more minutes on this machine.
- Agent: copilot-q3-report-refresh
  Date: 2026-04-13
  Scope: Q3 report refresh
  Outcome: The Q3 report section and table now use the direct TextRank-versus-DistilBART comparison artifact under outputs/q3/run_20260413_192426, and the report no longer describes Q3 as extractive-only.
  Next: Only reopen Q3 reporting if a larger matched comparison run is completed or if final report compilation reveals wording or table-format issues.
  Blocker: None
- Agent: copilot-q5-ngram
  Date: 2026-04-13
  Scope: Q5 trigram baseline
  Outcome: A stable Q5 trigram n-gram baseline now exists under outputs/q5/run_20260413_202258 with capped validation/test perplexity and generation exports.
  Next: Reuse configs/q5.yaml and src/q5_language_modeling as the base for a Q5 LSTM slice or a Q5 report-summary slice; do not reopen the classical baseline unless a larger-budget rerun is needed.
  Blocker: None
- Agent: copilot-q5-report
  Date: 2026-04-13
  Scope: Q5 report summary
  Outcome: A baseline-only Q5 report summary now exists with Markdown, JSON, and LaTeX outputs covering perplexity, configuration, and generation examples for the trigram model
  Next: Consume outputs/q5/run_20260413_211754 in a later Q5 report-draft slice, or add an LSTM baseline next if Q5 should move beyond the classical model
  Blocker: None
- Agent: copilot-q5-lstm
  Date: 2026-04-13
  Scope: Q5 LSTM baseline
  Outcome: A stable Q5 LSTM baseline now exists under outputs/q5/run_20260413_211945 and beats the matched trigram baseline by a wide margin on capped WikiText-2 perplexity.
  Next: Use outputs/q5/run_20260413_211945 and outputs/q5/run_20260413_202258 as the base for Q5 comparison/reporting work, or only reopen Q5 modeling if a GPT-2 comparison is worth the extra budget.
  Blocker: None
- Agent: copilot-q5-lstm
  Date: 2026-04-13
  Scope: Q5 LSTM baseline
  Outcome: A stable Q5 LSTM baseline now exists under outputs/q5/run_20260413_212022 with capped validation/test perplexity and generation exports.
  Next: Use outputs/q5/run_20260413_202258 and outputs/q5/run_20260413_212022 for a Q5 comparison/report slice, or rerun the LSTM baseline on a larger capped split if stronger evidence is needed.
  Blocker: None
- Agent: copilot-q5-writeup
  Date: 2026-04-13
  Scope: Q5 report draft
  Outcome: The Q5 report section now documents the finished trigram baseline with a report-local perplexity table and baseline-only narrative ready for compilation
  Next: Compile the report once a LaTeX toolchain is available, or extend q5.tex after the active LSTM slice finishes with stable metrics and generations
  Blocker: No LaTeX toolchain is installed in the current workspace environment
- Agent: copilot-q5-summary-refresh
  Date: 2026-04-13
  Scope: Q5 report summary refresh
  Outcome: A report-ready Q5 comparison summary now exists under outputs/q5/run_20260413_212315 and captures the matched trigram-versus-LSTM comparison.
  Next: Use outputs/q5/run_20260413_212315 to refresh q5.tex or other Q5 report artifacts; only reopen Q5 modeling if a GPT-2 baseline or a larger matched LSTM run is justified.
  Blocker: None
- Agent: copilot-report-conclusion
  Date: 2026-04-13
  Scope: Report conclusion draft
  Outcome: report/sections/conclusion.tex now provides an interim synthesis across Q1/Q2/Q3/Q5, emphasizing that pretrained models lead the finished comparisons while Q4 remains unfinished.
  Next: Revisit the conclusion after Q4 results stabilize and any final Q5 comparison is merged into the written report.
  Blocker: No LaTeX build toolchain is installed locally, so validation is currently limited to file diagnostics.
- Agent: copilot-q5-writeup-refresh
  Date: 2026-04-13
  Scope: Q5 report draft refresh
  Outcome: The Q5 report section and local table now reflect the matched trigram-versus-LSTM comparison summarized under outputs/q5/run_20260413_212315.
  Next: Use the refreshed q5.tex as the current Q5 report section, and only reopen it if a GPT-2 baseline or a larger matched LSTM comparison becomes available.
  Blocker: None
- Agent: copilot-q4-transformer
  Date: 2026-04-13
  Scope: Q4 pretrained transformer baseline
  Outcome: A stable Q4 transformer baseline now exists under outputs/q4/run_20260413_212828 with capped validation/test BLEU and ChrF plus translation CSV exports.
  Next: Reuse the Q4 package and artifact for a seq2seq+attention comparison slice or for a future Q4 report-summary/write-up slice.
  Blocker: None
- Agent: copilot-q4-writeup
  Date: 2026-04-13
  Scope: Q4 report draft
  Outcome: The Q4 report section and a local BLEU/ChrF table now document the stable pretrained transformer baseline under outputs/q4/run_20260413_212828, and report/README.md now treats Q4 as drafted rather than empty.
  Next: Refresh sections/introduction.tex and sections/conclusion.tex for report-wide consistency, or compare the baseline against a later seq2seq+attention run.
  Blocker: No LaTeX toolchain is installed locally, so validation is currently limited to file diagnostics.
- Agent: copilot-report-refresh
  Date: 2026-04-13
  Scope: Report framing refresh
  Outcome: The report introduction and conclusion now align with the drafted Q3/Q4/Q5 sections, including the Q4 transformer baseline and the matched Q5 trigram-versus-LSTM comparison.
  Next: Only revisit the top-level framing if later Q4 or Q5 comparisons materially change the report-wide conclusions.
  Blocker: No LaTeX toolchain is installed locally, so validation is currently limited to file diagnostics.
- Agent: copilot-q4-seq2seq
  Date: 2026-04-13
  Scope: Q4 seq2seq+attention baseline
  Outcome: A stable classical Q4 seq2seq baseline now exists under outputs/q4/run_20260413_214229 and can be compared directly against the finished transformer baseline.
  Next: Use outputs/q4/run_20260413_212828 and outputs/q4/run_20260413_214229 for a Q4 comparison summary or report-draft slice; only reopen Q4 modeling if a larger-budget seq2seq run is justified.
  Blocker: None
- Agent: copilot-q5-gpt2
  Date: 2026-04-13
  Scope: Q5 GPT-2 baseline
  Outcome: A stable Q5 GPT-style baseline now exists under outputs/q5/run_20260413_213856 with matched perplexity and generation exports.
  Next: Use outputs/q5/run_20260413_202258, outputs/q5/run_20260413_211945, and outputs/q5/run_20260413_213856 to refresh the Q5 comparison summary and report section.
  Blocker: None
