# Colab Notebooks

## Directory Structure

```
notebooks/
├── README.md              ← This file
├── Q1_Classification.ipynb
├── Q2_NER.ipynb
├── Q3_Summarization.ipynb
├── Q4_MachineTranslation.ipynb
└── Q5_LanguageModeling.ipynb
```

## Run Order (Recommended for T4 GPU)

| Priority | Notebook | GPU? | Est. Time | Notes |
|----------|----------|------|-----------|-------|
| 1 | Q5 | GPU | ~20 min | LSTM + GPT-2 (light VRAM) |
| 2 | Q2 | GPU | ~30 min | BiLSTM-CRF + BERT NER |
| 3 | Q1 | GPU | ~45 min | BiLSTM + DistilBERT on full 25K IMDb |
| 4 | Q4 | GPU | ~40 min | Seq2Seq training + Helsinki inference |
| 5 | Q3 | GPU | ~25 min | Lead-3 (CPU) + TextRank (CPU) + BART (GPU) |

## Workflow

1. Open notebook in Google Colab
2. Runtime → Change runtime type → T4 GPU
3. Run all cells in order
4. Outputs are saved to Google Drive under `467-takehome-outputs/`
5. Download outputs folder to local `outputs/` directory

## Sync Strategy

**Colab → Drive:**
Each notebook mounts Google Drive and copies outputs to `My Drive/467-takehome-outputs/qN/`.

**Drive → Local:**
```bash
# After Colab runs complete, download from Google Drive and merge:
cp -r ~/Downloads/467-takehome-outputs/q1/* outputs/q1/
cp -r ~/Downloads/467-takehome-outputs/q2/* outputs/q2/
# ... etc
```

## Session Timeout Handling

- Each notebook has checkpoint cells that save intermediate results
- If a session dies, re-run from the last checkpoint
- Outputs are written to Drive incrementally, not just at the end
- CPU models (TF-IDF, CRF, TextRank, Lead-3, N-gram) run first to bank easy results
