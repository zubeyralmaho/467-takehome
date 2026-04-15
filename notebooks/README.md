# Colab Notebooks

## Canonical vs Exploratory

Each notebook has two paths:

- **Canonical (default)**: Reproduces the exact comparison used in the final report. Run these cells to re-generate the report-facing artifacts.
- **Exploratory (commented out)**: Larger-budget or alternative experiments. Not part of the canonical report.

## Notebooks

| Notebook | Canonical Budget | Models | Report Artifact |
|----------|-----------------|--------|-----------------|
| `Q1_Classification.ipynb` | 4K train / 2K test | TF-IDF LR, TF-IDF SVM, BiLSTM, DistilBERT | `scripts/q1_report_summary.py` |
| `Q2_NER.ipynb` | Full CoNLL-2003 | CRF, BiLSTM-CRF, BERT | `scripts/q2_report_summary.py` |
| `Q3_Summarization.ipynb` | 20/20/20 | TextRank, DistilBART | `scripts/report_comparison_figures.py` |
| `Q4_MachineTranslation.ipynb` | Seq2Seq: 2K/100/100, Transformer: 100/100/100 | Seq2Seq+Attn, Helsinki-NLP | `scripts/q4_report_summary.py` |
| `Q5_LanguageModeling.ipynb` | 3000/400/400 lines | Trigram, LSTM, DistilGPT2 | `scripts/q5_report_summary.py` |

## Run Order (Recommended for T4 GPU)

| Priority | Notebook | Est. Time | Notes |
|----------|----------|-----------|-------|
| 1 | Q5 | ~15 min | Light canonical budget |
| 2 | Q2 | ~25 min | Full CoNLL-2003 is small |
| 3 | Q1 | ~20 min | Capped 4K budget |
| 4 | Q4 | ~15 min | Seq2Seq training + inference |
| 5 | Q3 | ~10 min | Small 20-sample canonical budget |

## Workflow

1. Open notebook in Google Colab
2. Runtime → Change runtime type → T4 GPU
3. Run all cells in order (canonical path runs by default)
4. Outputs are saved to Google Drive under `467-takehome-outputs/`
5. After all runs, regenerate report artifacts locally:
   ```bash
   python scripts/q1_report_summary.py
   python scripts/q2_report_summary.py
   python scripts/q4_report_summary.py
   python scripts/q5_report_summary.py
   python scripts/report_comparison_figures.py
   ```

## Sync: Drive → Local

```bash
cp -r ~/Downloads/467-takehome-outputs/q1/* outputs/q1/
cp -r ~/Downloads/467-takehome-outputs/q2/* outputs/q2/
cp -r ~/Downloads/467-takehome-outputs/q3/* outputs/q3/
cp -r ~/Downloads/467-takehome-outputs/q4/* outputs/q4/
cp -r ~/Downloads/467-takehome-outputs/q5/* outputs/q5/
```

## Shared Features

All notebooks include:
- Colab/local auto-detection (works both on Colab and locally)
- Drive mount + output sync after each model
- GPU memory cleanup between GPU model runs
- Named run variables (`tfidf_run`, `bilstm_run`, etc.) instead of blind `[-1]` indexing
- Report artifact regeneration instructions
- Exploratory section (commented out) for larger-budget runs
