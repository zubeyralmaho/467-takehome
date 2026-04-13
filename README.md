# CENG 467 Take-Home

Comparative NLP project and final report for CENG 467. The repository now contains working pipelines, exported experiment artifacts, and drafted report sections for five tasks: text classification, named entity recognition, summarization, machine translation, and language modeling.

## Implemented Tasks

| Question | Task | Dataset | Implemented baselines |
|----------|------|---------|------------------------|
| Q1 | Text classification | IMDb | TF-IDF + Logistic Regression, TF-IDF + Linear SVM, BiLSTM, DistilBERT |
| Q2 | Named entity recognition | CoNLL-2003 | CRF, BiLSTM-CRF, BERT token classification |
| Q3 | Summarization | CNN/DailyMail subset | TextRank, DistilBART reference |
| Q4 | Machine translation | Multi30k EN-DE | Seq2Seq + Attention, Opus-MT transformer reference |
| Q5 | Language modeling | WikiText-2 | Trigram add-k, LSTM, distilGPT-2 reference |

## Repository Highlights

- Shared config loading, seeding, export, metrics, and plotting utilities live under `src/common/`.
- Every question has its own config file under `configs/` and entrypoint under `src/q*/main.py`.
- Experiment outputs are written to timestamped directories under `outputs/` with copied config and environment metadata.
- The final report lives under `report/`, including local tables, copied figure assets, and a verified Tectonic build path.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Datasets are downloaded and cached automatically on first use.

## Running Experiments

All question entrypoints follow the same pattern:

```bash
python -m src.<question_module>.main --config configs/<question>.yaml [--final-eval] [--override key=value ...]
```

Examples:

```bash
python -m src.q1_classification.main --config configs/q1.yaml --final-eval
python -m src.q2_ner.main --config configs/q2.yaml --final-eval
python -m src.q3_summarization.main --config configs/q3.yaml --final-eval
python -m src.q4_machine_translation.main --config configs/q4.yaml --final-eval
python -m src.q5_language_modeling.main --config configs/q5.yaml --final-eval
```

Use repeated `--override` flags to enable or adjust specific models, dataset caps, or decoding/training parameters without editing YAML files directly.

## Report Workflow

Build the current report PDF with Tectonic:

```bash
cd report
tectonic main.tex
```

Regenerate the report-local Q3/Q4/Q5 comparison figures from the stable summary artifacts:

```bash
python scripts/report_comparison_figures.py
```

The detailed report-to-artifact mapping lives in `report/README.md`.

## Repository Layout

- `configs/`: per-question YAML configs plus shared defaults
- `src/`: shared infrastructure and question-specific pipelines
- `outputs/`: timestamped experiment runs and summary artifacts
- `report/`: LaTeX report source, local tables, figures, and bibliography
- `scripts/`: artifact summary, comparison, plotting, and agent-state utilities
- `docs/`: project notes plus the live multi-agent coordination workspace

## Current Status

- Stable experiment or summary artifacts exist for all five questions.
- The report builds cleanly with Tectonic and the compiled PDF is available under `report/`.
- Q3, Q4, and Q5 now include reproducible report-local comparison figures generated from approved summary artifacts.
