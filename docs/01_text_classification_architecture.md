# Task 1: Representation Learning in Text Classification

## Objective
Analyze the impact of sparse, dense, and contextual representations on text classification performance.

## 1. Dataset Selection
- **Dataset**: `IMDb` or `SST-2` (Hugging Face `datasets`).
- **Data Properties**: Binary sentiment classification, varying text lengths, polarity representation.

## 2. Preprocessing & Representation Pipeline
- **Representation Strategies**:
  1. Sparse Representation (TF-IDF bag-of-words or n-grams).
  2. Dense Representation (GloVe/Word2Vec with BiLSTM).
  3. Contextual Representation (Subword tokenization like WordPiece with BERT).
- **Ablation Studies**: Compare tokenization strategies, normalization (case folding, lemmatization), stopword removal, and maximum sequence truncation.

## 3. Modeling Architecture
- **Baseline Model**: Logistic Regression or Support Vector Machine (SVM) on top of TF-IDF vectors.
- **Neural Model**: Bi-Directional Long Short-Term Memory (BiLSTM) network with fixed dense embeddings.
- **Transformer Model**: Pre-trained transformer architecture (e.g., `BERT-base-uncased` or `DistilBERT`), fine-tuned on the classification objective.

## 4. Evaluation Strategy
- **Quantitative Metrics**: Accuracy and Macro-F1 score.
- **Qualitative Analysis**: Analyze at least 5 misclassified examples. Identify common error patterns (e.g., sarcasm, negation scope, length issues).
- **Comparative Analysis**: Performance vs. Interpretability of sparse vs. contextual embeddings.