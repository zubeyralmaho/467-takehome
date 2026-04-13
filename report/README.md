# Report Workspace

This directory contains the LaTeX scaffold for the final take-home report.

## Current State

- `main.tex` wires together the full report structure from `docs/11-report-structure.md`.
- `sections/q1.tex`, `sections/q2.tex`, `sections/q3.tex`, `sections/q4.tex`, and `sections/q5.tex` are drafted from stable experiment artifacts.
- `sections/q3.tex` now contains a direct capped comparison between TextRank and a pretrained DistilBART baseline.
- `sections/q4.tex` now contains a baseline-first write-up for the pretrained Q4 transformer artifact.
- `sections/conclusion.tex` is drafted, but it still reflects the pre-Q4 report state and should be refreshed after the Q4 section is folded into the final narrative.
- `tables/` stores report-local LaTeX table snippets that can be included from section files.
- `figures/` stores copied figure assets so the report does not depend on deep `outputs/` paths.
- `references.bib` now contains an initial set of foundational dataset and model citations used by the drafted sections.

## Compile Prerequisites

You need a LaTeX toolchain before the report can be compiled. Either of the following is fine:

- `latexmk` with `pdflatex`
- `pdflatex` plus `bibtex`

At the time this scaffold was created, `pdflatex` was not available in the workspace environment, so PDF compilation was not verified here.

## Compile Commands

From the repository root:

```bash
cd report
latexmk -pdf main.tex
```

If `latexmk` is not installed, use the manual sequence:

```bash
cd report
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Section-to-Artifact Mapping

### Question 1

- Larger-budget comparison artifact: `outputs/q1/run_20260413_152558`
- Larger-budget TF-IDF reference run: `outputs/q1/run_20260413_152535`
- Larger-budget BiLSTM run: `outputs/q1/run_20260413_151549`
- Larger-budget DistilBERT run: `outputs/q1/run_20260413_151402`
- Preprocessing comparison artifact: `outputs/q1/run_20260413_145735`
- `sections/q1.tex` now uses the finished larger-budget artifacts, while the older smoke-test summary remains available only as an interim historical reference.

### Question 2

- Report summary artifact: `outputs/q2/run_20260413_151034`
- Model comparison artifact: `outputs/q2/run_20260413_151143`
- Best model run: `outputs/q2/run_20260413_144742`
- `sections/q2.tex` already uses the finished Q2 results and the copied entity-F1 comparison figure in `figures/q2/entity_f1_comparison.png`.

### Question 3

- Direct comparison artifact: `outputs/q3/run_20260413_192426`
- Earlier TextRank-only baseline artifact: `outputs/q3/run_20260413_185438`
- `sections/q3.tex` now uses the direct capped TextRank-versus-DistilBART comparison, while any larger-budget Q3 rerun remains optional follow-up work.

### Question 4

- Pretrained transformer baseline artifact: `outputs/q4/run_20260413_212828`
- `sections/q4.tex` now documents the stable pretrained baseline with BLEU/ChrF metrics from the capped Multi30k export.
- A future seq2seq+attention run should be compared against the same artifact contract rather than replacing it.

### Question 5

- Trigram baseline run: `outputs/q5/run_20260413_202258`
- Matched LSTM comparison run: `outputs/q5/run_20260413_211945`
- GPT-style baseline run: `outputs/q5/run_20260413_213856`
- Refreshed Q5 summary artifact: `outputs/q5/run_20260413_214837`
- Later smaller LSTM rerun: `outputs/q5/run_20260413_212022`
- `sections/q5.tex` now uses the matched trigram-versus-LSTM-versus-GPT-style comparison, while the later smaller LSTM rerun remains a separate reference rather than part of the direct report table.

## Editing Workflow

1. Update experiment artifacts in `outputs/` first.
2. Copy only the figures that the report should reference into `report/figures/`.
3. Put reusable table snippets into `report/tables/` if a section will `\input{...}` them.
4. Write narrative in `report/sections/*.tex` using the stable artifact outputs, not ad hoc terminal observations.
5. Recompile after each question-level write-up slice when a LaTeX toolchain is available.

## Suggested Next Steps

- Finalize `sections/q1.tex` after the active larger-budget Q1 neural runs are summarized.
- Expand `sections/introduction.tex` once Q1 and Q2 write-ups stabilize.
- Fill `references.bib` when citations are added to the final prose.
- Optionally rerun Q3 on a larger matched split if stronger summarization evidence is needed.
- Refresh `sections/introduction.tex` and `sections/conclusion.tex` so they reflect the now-drafted Q4 section and the updated overall report state.
- Only reopen `sections/q5.tex` if a larger matched rerun or actual GPT-style fine-tuning becomes necessary.