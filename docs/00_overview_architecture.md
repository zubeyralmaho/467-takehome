# Project Overview & Global Architecture

This document describes the global architecture and experimental setup required for the CENG 467 Midterm project.

## 1. Global Requirements
- **Reproducibility**: All experiments must have fixed random seeds.
- **Environment**: Python environment (likely managed via `requirements.txt` or `environment.yml`).
- **Data Splitting**: Consistent dataset splits (train/val/test) for all models unless testing specific conditions. The **test set** should only be touched once at the very end for final evaluation.
- **Deliverables**: 
  - A structured report in LaTeX.
  - Reproducible code repository (GitHub/Colab link).
  - Single archive `CENG467 Midterm <StudentID>.zip`.

## 2. Experimental Pipeline
Each of the 5 tasks will follow a unified pipeline architecture:
1. **Data Ingestion & Preprocessing**: Loading datasets (via `datasets` library), text cleaning, tokenization, and formatting (e.g., BIO tagging).
2. **Model Formulation**: Defining baseline (classical/statistical) and advanced (neural/transformer) models.
3. **Training & Validation**: Training loops (or `Trainer` API), hyperparameter logging, and validation monitoring to prevent overfitting.
4. **Evaluation & Metric Computation**: Calculating task-specific metrics (Accuracy, F1, ROUGE, BLEU, etc.).
5. **Error Analysis & Reporting**: Qualitative evaluation of misclassifications, fluency, and model limitations to be included in the LaTeX report.