# Task 4: Machine Translation

## Objective
Analyze sequence-to-sequence modeling, attention mechanisms, and translation quality evaluation.

## 1. Dataset Selection
- **Dataset**: `Multi30k` (Image descriptions translated to multiple languages, relatively small and manageable).
- **Structure**: Sentence pairs (e.g., English -> German).

## 2. Preprocessing & Representation Pipeline
- **Representation Strategies**:
  1. Tokenize per language using appropriate libraries (`spacy` or `BPE`).
  2. Vocabulary building for source and target languages.
  3. Predefined max sequence lengths.

## 3. Modeling Architecture
- **Seq2Seq + Attention Model**: 
  - Standard Encoder-Decoder with Recurrent Units (GRU/LSTM).
  - Bahdanau (Additive) or Luong (Multiplicative) Attention mechanism.
- **Transformer Model**:
  - Full self-attention based Encoder-Decoder architecture (`Transformer` from scratch or pre-trained alternatives like `MarianMT/Helsinki-NLP`).

## 4. Evaluation Strategy
- **Quantitative Metrics**:
  - `BLEU` (n-gram precision and brevity penalty).
  - `METEOR` (alignment constraint with synonymy and stemming matching).
  - `ChrF` (character n-gram F-score for morphologically rich evaluation).
  - `BERTScore` (semantic sentence similarity).
- **Qualitative Analysis**: Analyze at least 1 example containing rare words or long-range dependencies. Include source, reference, and both model outputs.
- **Trade-off Analysis**: Differences in model behaviors, fluency, and handling morphological differences compared to recurrent architectures. How each metric reflects different aspects of translation.