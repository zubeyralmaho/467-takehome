# Report Workspace

This directory contains the LaTeX scaffold for the final take-home report.

## Current State

- `main.tex` wires together the full report structure from `docs/11-report-structure.md`.
- `sections/q1.tex` and `sections/q2.tex` are drafted from stable experiment artifacts.
- `sections/q3.tex` now contains a provisional baseline-only write-up built from the finished TextRank run.
- `sections/q4.tex`, `sections/q5.tex`, and `sections/conclusion.tex` remain placeholders for later slices.
- `tables/` stores report-local LaTeX table snippets that can be included from section files.
- `figures/` stores copied figure assets so the report does not depend on deep `outputs/` paths.
- `references.bib` is currently an empty placeholder.

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

- TextRank baseline artifact: `outputs/q3/run_20260413_185438`
- `sections/q3.tex` currently documents the capped extractive baseline only and should be expanded after a BART or T5 slice is completed.

### Questions 4-5

- These sections are placeholders until implementations and experiment artifacts exist.

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
- Expand `sections/q3.tex` into a full comparison once a BART or T5 summarization slice is available.
- Draft `sections/q4.tex` and `sections/q5.tex` after their experiment outputs are available.