# 06 - Q3: Text Summarization

> [Home](README.md) | Previous: [Q2 - NER](05-q2-ner.md) | Next: [Q4 - Machine Translation](07-q4-machine-translation.md)

---

## Objective

Compare extractive and abstractive summarization methods. Evaluate performance using ROUGE, BLEU, METEOR, and BERTScore. Perform qualitative analysis in terms of fluency, factual consistency, and information coverage.

---

## Dataset: CNN/DailyMail

### Properties
- **Size**: ~300K article-summary pairs (subset will be used)
- **Subset**: 10K train / 1K val / 1K test (sufficient and efficient)
- **Average article length**: ~780 words
- **Average summary length**: ~56 words (3-4 sentences)
- **Source**: `datasets.load_dataset("cnn_dailymail", "3.0.0")`

### Subset Creation
```python
dataset = load_dataset("cnn_dailymail", "3.0.0")
train_subset = dataset["train"].shuffle(seed=42).select(range(10000))
val_subset = dataset["validation"].shuffle(seed=42).select(range(1000))
test_subset = dataset["test"].shuffle(seed=42).select(range(1000))
```

### Data Structure
```python
{
    "article": "LONDON, England (CNN) -- An American tourist...",
    "highlights": "Bullet point summaries from CNN editors...",
    "id": "abc123..."
}
```

---

## Preprocessing

### preprocess.py

```python
def clean_article(text: str) -> str:
    """
    - CNN/DailyMail special marker cleanup
    - Extra whitespace/newline normalization
    - Encoding issues
    """

def truncate_article(text: str, max_tokens: int = 1024) -> str:
    """Truncate to max input length for BART/T5."""

def split_into_sentences(text: str) -> list[str]:
    """
    Sentence splitting for TextRank.
    nltk.sent_tokenize or spacy sentence segmentation.
    """
```

---

## Model Architectures

### Model 1: TextRank (Extractive)

**File**: `models/textrank.py`

```python
class TextRankSummarizer:
    """
    Graph-based extractive summarization.
    Adaptation of the PageRank algorithm for text summarization.
    """

    def __init__(self, similarity_method: str = "tfidf",
                 damping: float = 0.85,
                 num_sentences: int = 3):
        """
        similarity_method: "tfidf" or "embedding"
        damping: PageRank damping factor
        num_sentences: number of sentences to select
        """

    def build_similarity_matrix(self, sentences: list[str]) -> np.ndarray:
        """
        Inter-sentence similarity matrix:
        - TF-IDF cosine similarity
        - (or) Sentence embedding cosine similarity
        """

    def rank_sentences(self, similarity_matrix: np.ndarray) -> list[float]:
        """Computes PageRank scores."""

    def summarize(self, text: str) -> str:
        """
        1. Split text into sentences
        2. Build similarity matrix
        3. Rank with PageRank
        4. Select top-N scored sentences
        5. Combine in original order
        """
```

**Algorithm Flow**:
```
Input Article (text)
        |
        v
[Sentence Segmentation] -> ["S1", "S2", "S3", ..., "Sn"]
        |
        v
[TF-IDF Vectorization] -> Sentence vectors
        |
        v
[Cosine Similarity Matrix] -> n x n matrix
        |
        v
[PageRank Algorithm] -> Scores: [0.23, 0.15, 0.31, ...]
        |
        v
[Top-K Sentence Selection] -> Top 3 scored sentences
        |
        v
[Combine in Original Order]
        |
        v
Output Summary
```

**Parameters**:
| Parameter | Value |
|-----------|-------|
| similarity | TF-IDF cosine |
| damping | 0.85 |
| convergence_threshold | 1e-5 |
| max_iterations | 100 |
| num_sentences | 3 |

---

### Model 2: BART (Abstractive)

**File**: `models/bart_summarizer.py`

```python
class BARTSummarizer:
    """
    facebook/bart-large-cnn fine-tuned model.
    Abstractive summarization with encoder-decoder transformer.
    """

    def __init__(self, model_name: str = "facebook/bart-large-cnn",
                 max_input_length: int = 1024,
                 max_output_length: int = 142,
                 min_output_length: int = 56):
        """Loads pretrained BART model and tokenizer."""

    def summarize(self, text: str, **generate_kwargs) -> str:
        """
        Generates summary for a single text.
        generate_kwargs: num_beams, length_penalty, etc.
        """

    def summarize_batch(self, texts: list[str],
                        batch_size: int = 8) -> list[str]:
        """Batch inference."""

    def fine_tune(self, train_dataset, val_dataset, config):
        """
        Optional: Fine-tune if pretrained is not sufficient.
        In most cases facebook/bart-large-cnn is already
        fine-tuned on CNN/DM, so it can be used directly.
        """
```

**Approach Options**:

| Approach | Description | Recommended |
|----------|-------------|-------------|
| Zero-shot | Pretrained BART-large-CNN directly | Yes (default) |
| Fine-tune | Additional fine-tuning on subset | Optional comparison |

> **Note**: `facebook/bart-large-cnn` is already fine-tuned on CNN/DailyMail. Additional fine-tuning may be unnecessary but can be done for comparison purposes.

**T5 Alternative**:
```python
class T5Summarizer:
    """google/flan-t5-base alternative."""
    # Same API, different model_name
    # Input prefix: "summarize: " must be added
```

**Generation Parameters**:
| Parameter | Value |
|-----------|-------|
| num_beams | 4 |
| length_penalty | 2.0 |
| max_length | 142 |
| min_length | 56 |
| no_repeat_ngram_size | 3 |
| early_stopping | True |

---

## Evaluation

### Metric Set

| Metric | What It Measures | Library |
|--------|-----------------|---------|
| **ROUGE-1** | Unigram overlap | `evaluate` / `rouge_score` |
| **ROUGE-2** | Bigram overlap | `evaluate` / `rouge_score` |
| **ROUGE-L** | Longest common subsequence | `evaluate` / `rouge_score` |
| **BLEU** | N-gram precision + brevity penalty | `nltk.translate.bleu_score` |
| **METEOR** | Alignment + synonym + stemming | `evaluate` / `nltk.translate.meteor` |
| **BERTScore** | Contextual semantic similarity | `bert_score` |

### Metric Computation Details

```python
# ROUGE
from evaluate import load
rouge = load("rouge")
results = rouge.compute(predictions=preds, references=refs)
# -> {"rouge1": 0.44, "rouge2": 0.21, "rougeL": 0.38}

# BLEU
from nltk.translate.bleu_score import corpus_bleu
score = corpus_bleu([[ref.split()] for ref in refs],
                    [pred.split() for pred in preds])

# METEOR
from evaluate import load
meteor = load("meteor")
results = meteor.compute(predictions=preds, references=refs)

# BERTScore
from bert_score import score
P, R, F1 = score(preds, refs, lang="en", verbose=True)
```

For details see: [Evaluation Framework](09-evaluation-framework.md)

---

## Qualitative Analysis

### analysis.py

```python
def qualitative_comparison(articles, references, extractive_summaries,
                           abstractive_summaries, n: int = 3) -> list[dict]:
    """
    For at least 3 examples:
    - Source text (truncated)
    - Reference summary
    - TextRank output
    - BART output
    - For each: fluency, factual consistency, information coverage
    """

def analyze_extractive_vs_abstractive(examples: list[dict]) -> dict:
    """
    Comparison dimensions:
    1. Fluency: Extractive -> source sentences, Abstractive -> new sentences
    2. Factual Consistency: Extractive more reliable, Abstractive has hallucination risk
    3. Information Coverage: Abstractive provides denser information
    4. Redundancy: Extractive has repetition risk, Abstractive more concise
    """
```

### Example Comparison Table (For Report)

| Dimension | TextRank (Extractive) | BART (Abstractive) |
|-----------|----------------------|-------------------|
| Fluency | Source sentences, natural | New sentences, more concise |
| Factual Consistency | High (source copy) | Risk: hallucination |
| Information Density | Low (full sentences) | High (compression) |
| Computational Cost | Low (CPU sufficient) | High (GPU required) |
| Readability | Can be fragmented | More coherent |

---

## Expected Outputs

```
outputs/q3/run_{timestamp}/
|-- config.yaml
|-- metrics.json                      # ROUGE, BLEU, METEOR, BERTScore
|-- predictions/
|   |-- textrank_summaries.csv
|   +-- bart_summaries.csv
|-- qualitative_analysis.json         # 3+ detailed examples
|-- figures/
|   |-- metric_comparison.png
|   +-- rouge_distribution.png
+-- (optional) model_bart_finetuned/
```

---

## Config Example (q3.yaml)

```yaml
question: "q3"
task: "summarization"

dataset:
  name: "cnn_dailymail"
  version: "3.0.0"
  train_subset_size: 10000
  val_subset_size: 1000
  test_subset_size: 1000

preprocess:
  max_article_length: 1024    # token
  clean_html: true

models:
  textrank:
    similarity_method: "tfidf"
    damping: 0.85
    num_sentences: 3

  bart:
    model_name: "facebook/bart-large-cnn"
    max_input_length: 1024
    max_output_length: 142
    min_output_length: 56
    num_beams: 4
    length_penalty: 2.0
    no_repeat_ngram_size: 3
    fine_tune: false          # Pretrained is sufficient

evaluation:
  metrics: ["rouge1", "rouge2", "rougeL", "bleu", "meteor", "bertscore"]
  num_qualitative_examples: 3
```

---

## Related Documents

- [Shared Infrastructure](03-shared-infrastructure.md) - metrics.py (ROUGE, BLEU, etc.)
- [Evaluation Framework](09-evaluation-framework.md) - Detailed explanation of all metrics
- [Q4 - Machine Translation](07-q4-machine-translation.md) - Similar metrics (BLEU, METEOR, BERTScore)
