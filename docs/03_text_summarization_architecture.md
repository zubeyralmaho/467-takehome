# Task 3: Text Summarization

## Objective
Compare extractive and abstractive summarization techniques.

## 1. Dataset Selection
- **Dataset**: `CNN/DailyMail` (Subset allowed for computational limits).
- **Structure**: Multi-sentence news articles with multi-sentence human-written highlights (reference summaries).

## 2. Preprocessing & Representation Pipeline
- **Representation Strategies**:
  1. Sentences as nodes in a graph (Extractive).
  2. Subword sequences (Extractive).
- **Extractive Preparation**: Tokenize into sentences, remove stopwords, compute term frequencies or sentence embeddings for similarity matrices.
- **Abstractive Preparation**: Source text encoding + target text decoding using specific prompt formats (e.g., `ss_text` tokenizer configurations).

## 3. Modeling Architecture
- **Extractive Model**: Graph-based ranking (TextRank or LexRank).
  - Implementation using PageRank over cosine similarity between TF-IDF or BERT sentence embeddings.
- **Abstractive Model**: Pre-trained Sequence-to-Sequence (Seq2Seq) Transformer (e.g., `BART-large-cnn` or `T5-small/base`).
  - Target sequence generation via Beam Search or Nucleus Sampling.

## 4. Evaluation Strategy
- **Quantitative Metrics**:
  - `ROUGE` (1, 2, L) for n-gram overlap.
  - `BLEU` (translation-style precision).
  - `METEOR` (alignment constraint with synonym matching).
  - `BERTScore` (contextual semantic similarity).
- **Qualitative Analysis**: Analyze at least 3 examples.
- **Trade-off Analysis**: Compare fluency, factual consistency (hallucinations), coverage vs. computational cost, and readability of extractive vs abstractive.