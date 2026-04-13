# Report Workspace

This directory contains the LaTeX scaffold for the final take-home report.

## Current State

- `main.tex` wires together the full report structure from `docs/11-report-structure.md`.
- `sections/q2.tex` is the most complete drafted section so far.
- `sections/q1.tex`, `sections/q3.tex`, `sections/q4.tex`, `sections/q5.tex`, and `sections/conclusion.tex` are placeholders that can be expanded by separate write-up slices.
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

- Current stable smoke-test summary: `outputs/q1/run_20260413_150237`
- Current stable smoke-test comparison artifacts: `outputs/q1/run_20260413_145244`
- Current stable preprocessing comparison artifacts: `outputs/q1/run_20260413_145735`
- `sections/q1.tex` should stay provisional until the larger-budget BiLSTM and DistilBERT experiments are finalized.

### Question 2

- Report summary artifact: `outputs/q2/run_20260413_151034`
- Model comparison artifact: `outputs/q2/run_20260413_151143`
- Best model run: `outputs/q2/run_20260413_144742`
- `sections/q2.tex` already uses the finished Q2 results and the copied entity-F1 comparison figure in `figures/q2/entity_f1_comparison.png`.

### Questions 3-5

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
- Draft `sections/q3.tex`, `sections/q4.tex`, and `sections/q5.tex` only after their experiment outputs are available.