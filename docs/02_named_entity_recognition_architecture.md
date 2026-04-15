# Task 2: Named Entity Recognition (NER)

## Objective
Analyze sequence labeling and contextual modeling in Named Entity Recognition.

## 1. Dataset Selection
- **Dataset**: `CoNLL-2003` (English NER dataset with four实体 types: PER, ORG, LOC, MISC).
- **Structure**: Tokens with standard `BIO` tagging.

## 2. Preprocessing & Representation Pipeline
- **Representation Strategies**:
  1. Feature Engineering/Word Embeddings + POS tags.
  2. Subword Tokenization (BPE/WordPiece) for Transformer models.
- **Alignment Handling**: Address label alignment issues (e.g., `[CLS]`, `[SEP]`, or split subword tokens `##word` should not receive entity specific tags or should receive `X`/`I-` tags).

## 3. Modeling Architecture
- **Classical / Hybrid Model**: Conditional Random Field (CRF) or BiLSTM + CRF.
  - Features (if CRF only): word shape, prefix/suffix, POS tags.
  - Features (if BiLSTM-CRF): Pre-trained GloVe/FastText word embeddings + Character-level CNN/LSTM embeddings.
- **Transformer Model**: Pre-trained NER Transformer Fine-tuning (e.g., `BERT-base-NER` or `RoBERTa`).

## 4. Evaluation Strategy
- **Quantitative Metrics**: Entity-level Precision, Recall, and F1-score `(seqeval)`.
- **Error Analysis**: Identify common error types (boundary errors: partial overlap vs exact match, entity confusion: mislabeling LOC as ORG).
- **Qualitative Contextual Analysis**: Assess the importance of contextual embeddings in disambiguation.