# CENG 467 Take-Home

Initial implementation for the take-home project. The repository now contains a working first slice for Q1 text classification with shared infrastructure and TF-IDF baselines.

## Current Scope

- Configuration loading with YAML merge and CLI overrides
- Reproducible seeding utilities
- IMDb loading and deterministic train/validation split
- TF-IDF + Logistic Regression baseline
- TF-IDF + Linear SVM baseline
- Validation metrics, optional final test evaluation, and error analysis export

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Validation-only run:

```bash
python -m src.q1_classification.main --config configs/q1.yaml
```

Final evaluation on the test split:

```bash
python -m src.q1_classification.main --config configs/q1.yaml --final-eval
```

Fast development run with fewer samples:

```bash
python -m src.q1_classification.main \
  --config configs/q1.yaml \
  --override dataset.limit_train_samples=5000 \
  --override dataset.limit_test_samples=2000
```
