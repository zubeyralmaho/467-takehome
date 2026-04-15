# Task 5: Language Modeling

## Objective
Investigate probabilistic sequence modeling and text generation coherence.

## 1. Dataset Selection
- **Dataset**: `Penn Treebank` or `WikiText-2` (Small-scale language modeling corpora with `<unk>` tokens and special symbols).
- **Structure**: Continuous text corpus stream.

## 2. Preprocessing & Representation Pipeline
- **Representation Strategies**:
  1. Tokenize into words or subwords. Keep vocabulary limited to typical sizes (e.g., 10k-30k).
  2. Map out-of-vocabulary (OOV) tokens to `<unk>`.
- **Training Strategy**: Chunk into sequence windows (e.g., `BPTT` window size of 35).

## 3. Modeling Architecture
- **Probability/Markov Model**: N-gram language model (e.g., Trigram with Kneser-Ney interpolation or Laplacian smoothing) OR
- **Recurrent Model**: Standard LSTM Language Model predicting the next token $P(x_t | x_{<t})$. Embedding layer $\rightarrow$ LSTM $\rightarrow$ Linear $\rightarrow$ Softmax.
- **Transformer Model (Optional but recommended)**: GPT-style causal language model or `Transformer-XL`.

## 4. Evaluation Strategy
- **Quantitative Metrics**: Perplexity (cross-entropy exponential on the test set).
- **Qualitative Generation**: Seed prompts (temperature sampling, Top-K/Top-p Nucleus sampling). Analyze short generated text samples.
- **Trade-off Analysis**: Fluency vs coherence discussion. Analysis of repetitive loops, grammatical correctness vs semantic meaning.