# Colab Notebooks

These notebooks are execution helpers, not the source of truth for the final report.

Canonical truth still lives in:

- `src/` and `configs/` for model behavior
- `outputs/q*/run_*` for experiment artifacts
- `report/README.md` for the report-facing artifact mapping
- `docs/colab-plan.md` for the current notebook drift audit and refresh plan

## Canonical vs Exploratory

Each notebook should be interpreted with this split:

- **Canonical**: the default path intended to reproduce the comparison currently used in the report.
- **Exploratory**: larger-budget or alternative runs that are useful for experimentation but are not part of the final report by default.

## Current Notebook Status

| Notebook | Canonical target | Current status | Report-facing follow-up |
|----------|------------------|----------------|--------------------------|
| `Q1_Classification.ipynb` | Matched 4K train / 2K test comparison | Partial alignment | `scripts/q1_report_summary.py` with explicit run paths |
| `Q2_NER.ipynb` | Full CoNLL-2003 comparison | Mostly aligned, markdown cleanup/report hooks still matter | `scripts/q2_report_summary.py` with explicit run paths |
| `Q3_Summarization.ipynb` | Capped direct TextRank vs DistilBART comparison | Needs canonical rewrite | `scripts/report_comparison_figures.py` after report-facing artifacts change |
| `Q4_MachineTranslation.ipynb` | Approved capped transformer vs seq2seq comparison | Rewrite in progress | `scripts/q4_report_summary.py` with explicit run paths |
| `Q5_LanguageModeling.ipynb` | Matched 3000/400/400 trigram vs LSTM vs distilGPT2 comparison | Canonical rewrite landed | `scripts/q5_report_summary.py` with explicit run paths |

## Recommended Run Order

If you are using free Colab T4 sessions, run the lighter or already-canonical notebooks first:

| Priority | Notebook | Est. Time | Notes |
|----------|----------|-----------|-------|
| 1 | Q5 | ~15 min | Light matched canonical budget |
| 2 | Q2 | ~25 min | Full CoNLL-2003 is still manageable |
| 3 | Q1 | ~20 min | Matched 4K/2K path is lighter than the older full IMDb plan |
| 4 | Q4 | ~15 min | Canonical rewrite is being finalized |
| 5 | Q3 | ~10 min | Canonical rewrite still needed |

## Base Workflow

1. Open the notebook in Google Colab.
2. Set the runtime to T4 GPU when the notebook includes GPU models.
3. Run the canonical cells in order.
4. Sync outputs from Drive back into local `outputs/`.
5. If the notebook is part of the report workflow, run the required summary or figure refresh step locally.

## Drive → Local Sync

```bash
cp -r ~/Downloads/467-takehome-outputs/q1/* outputs/q1/
cp -r ~/Downloads/467-takehome-outputs/q2/* outputs/q2/
cp -r ~/Downloads/467-takehome-outputs/q3/* outputs/q3/
cp -r ~/Downloads/467-takehome-outputs/q4/* outputs/q4/
cp -r ~/Downloads/467-takehome-outputs/q5/* outputs/q5/
```

## Report Refresh Commands

Do not call the summary scripts without explicit input run directories.

Use the canonical artifact mapping in `report/README.md` to choose the correct runs, then execute the matching command shape below.

```bash
# Q1
python scripts/q1_report_summary.py \
   --comparison-run <outputs/q1/comparison-run> \
   --preprocessing-run <outputs/q1/preprocessing-run>

# Q2
python scripts/q2_report_summary.py \
   --crf-run <outputs/q2/crf-run> \
   --bilstm-run <outputs/q2/bilstm-run> \
   --bert-run <outputs/q2/bert-run>

# Q4
python scripts/q4_report_summary.py \
   --run <outputs/q4/transformer-run> \
   --run <outputs/q4/seq2seq-run>

# Q5
python scripts/q5_report_summary.py \
   --run <outputs/q5/ngram-run> \
   --run <outputs/q5/lstm-run> \
   --run <outputs/q5/gpt2-run>

# Q3-Q5 report-local figures
python scripts/report_comparison_figures.py
```

## Notes

- If a notebook still contains a heavier legacy path, treat that path as exploratory unless the notebook explicitly says otherwise.
- Prefer named run variables inside notebook cells over blind `sorted(...)[-1]` selection.
- If notebook behavior and `report/README.md` disagree, trust `report/README.md` and `docs/colab-plan.md` until the notebook refresh slices are complete.
