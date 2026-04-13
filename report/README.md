# Report Workspace

This directory contains the LaTeX scaffold for the final take-home report.

## Current State

- `main.tex` wires together the full report structure from `docs/11-report-structure.md`.
- `sections/q1.tex`, `sections/q2.tex`, `sections/q3.tex`, `sections/q4.tex`, and `sections/q5.tex` are drafted from stable experiment artifacts.
- `sections/q3.tex` now contains a direct capped comparison between TextRank and a pretrained DistilBART baseline.
- `sections/q4.tex` now contains a direct capped comparison between the Q4 pretrained transformer reference and the custom seq2seq baseline.
- `sections/q3.tex`, `sections/q4.tex`, and `sections/q5.tex` now include report-local comparison figures generated from the stable summary artifacts.
- `sections/conclusion.tex` is drafted and now reflects the current Q1/Q2/Q3/Q4/Q5 comparison state, while later matched reruns may still refine the final narrative.
- `tables/` stores report-local LaTeX table snippets that can be included from section files.
- `figures/` stores copied figure assets so the report does not depend on deep `outputs/` paths.
- `references.bib` now contains the foundational dataset and model citations used by the drafted sections, including the current GPT-style Q5 reference.

## Compile Prerequisites

The report now compiles successfully in this workspace. The currently verified build path is:

- `tectonic`

Other LaTeX toolchains may also work, including:

- `latexmk` with `pdflatex`
- `pdflatex` plus `bibtex`

The current workspace already contains a successfully generated `main.pdf` built from `main.tex` with Tectonic, and the latest verified build is clean.

## Compile Commands

From the repository root:

```bash
cd report
tectonic main.tex
```

If you prefer `latexmk` and a full TeX installation is available, use:

```bash
cd report
latexmk -pdf main.tex
```

If neither Tectonic nor `latexmk` is available, use the manual sequence:

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
- Seq2Seq baseline artifact: `outputs/q4/run_20260413_214229`
- Comparison summary artifact: `outputs/q4/run_20260413_231508`
- `sections/q4.tex` now uses the direct capped transformer-versus-seq2seq comparison while explicitly noting that the train budgets are not perfectly matched because the transformer is a pretrained reference.

### Question 5

- Trigram baseline run: `outputs/q5/run_20260413_202258`
- Matched LSTM comparison run: `outputs/q5/run_20260413_211945`
- GPT-style baseline run: `outputs/q5/run_20260413_213856`
- Refreshed Q5 summary artifact: `outputs/q5/run_20260413_214837`
- Later smaller LSTM rerun: `outputs/q5/run_20260413_212022`
- `sections/q5.tex` now uses the matched trigram-versus-LSTM-versus-GPT-style comparison, while the later smaller LSTM rerun remains a separate reference rather than part of the direct report table.

## Editing Workflow

1. Update experiment artifacts in `outputs/` first.
2. Regenerate the report-local Q3/Q4/Q5 comparison figures with `python scripts/report_comparison_figures.py` after the source summary artifacts change.
3. Copy only the figures that the report should reference into `report/figures/`.
4. Put reusable table snippets into `report/tables/` if a section will `\input{...}` them.
5. Write narrative in `report/sections/*.tex` using the stable artifact outputs, not ad hoc terminal observations.
6. Recompile after each question-level write-up slice, preferably with `tectonic main.tex` from `report/`.

## Suggested Next Steps

- Do a final manual proofreading pass on the clean compiled PDF before submission.
- Optionally rerun Q3 on a larger matched split if stronger summarization evidence is needed.
- Only reopen Q4 if a more budget-matched seq2seq rerun or transformer fine-tuning becomes necessary beyond the stronger current seq2seq reference artifact.
- Only reopen `sections/q5.tex` if a larger matched rerun or actual GPT-style fine-tuning becomes necessary.