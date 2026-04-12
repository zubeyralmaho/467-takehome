# 09 - Evaluation Framework

> [Home](README.md) | Previous: [Q5 - Language Modeling](08-q5-language-modeling.md) | Next: [Experiment Config](10-experiment-config.md)

---

## Overview

This document defines all evaluation metrics used in the project, their computation methods, libraries, and reporting standards. All questions use the same centralized evaluation engine (`src/common/metrics.py` + `src/common/evaluation.py`).

---

## Metric Catalog

### 1. Accuracy (Q1)

| Property | Value |
|----------|-------|
| **Used In** | Q1 - Text Classification |
| **Formula** | `correct_predictions / total_predictions` |
| **Range** | [0, 1] |
| **Higher = Better** | Yes |
| **Library** | `sklearn.metrics.accuracy_score` |

```python
from sklearn.metrics import accuracy_score
acc = accuracy_score(y_true, y_pred)
```

---

### 2. Macro-F1 (Q1)

| Property | Value |
|----------|-------|
| **Used In** | Q1 - Text Classification |
| **Formula** | Compute F1 for each class, take their average |
| **Range** | [0, 1] |
| **Advantage** | Fair for imbalanced classes |
| **Library** | `sklearn.metrics.f1_score(average='macro')` |

```python
from sklearn.metrics import f1_score
f1 = f1_score(y_true, y_pred, average='macro')
```

---

### 3. Entity-Level Precision / Recall / F1 (Q2)

| Property | Value |
|----------|-------|
| **Used In** | Q2 - NER |
| **Computation Level** | Entity-level (not token!) |
| **Library** | `seqeval` |
| **Important Note** | Partial entity matches are counted as WRONG |

```python
from seqeval.metrics import classification_report, f1_score
from seqeval.scheme import IOB2

# y_true and y_pred: list[list[str]] (BIO tags)
report = classification_report(y_true, y_pred, scheme=IOB2)
f1 = f1_score(y_true, y_pred, scheme=IOB2)
```

**Entity-Level vs Token-Level**:
```
Ground truth:  [B-LOC, I-LOC, I-LOC]   -> "New York City" (1 entity)
Prediction:    [B-LOC, I-LOC, O]        -> "New York" (1 entity)

Token-level: 2/3 correct = 66.7%
Entity-level: 0/1 correct = 0% (entity boundary is wrong!)
```

---

### 4. ROUGE (Q3)

| Variant | What It Measures | Formula |
|---------|-----------------|---------|
| **ROUGE-1** | Unigram overlap | F1(unigram_precision, unigram_recall) |
| **ROUGE-2** | Bigram overlap | F1(bigram_precision, bigram_recall) |
| **ROUGE-L** | Longest Common Subsequence | F1(LCS_precision, LCS_recall) |

| Property | Value |
|----------|-------|
| **Used In** | Q3 - Summarization |
| **Range** | [0, 1] |
| **Library** | `evaluate` (HuggingFace) or `rouge_score` |

```python
from evaluate import load
rouge = load("rouge")
results = rouge.compute(
    predictions=predictions,
    references=references,
    use_stemmer=True
)
# results = {"rouge1": 0.44, "rouge2": 0.21, "rougeL": 0.38, "rougeLsum": 0.40}
```

**ROUGE Interpretation**:
| Score | Meaning |
|-------|---------|
| ROUGE-1 > 0.40 | Good content coverage |
| ROUGE-2 > 0.18 | Good sentence structure coverage |
| ROUGE-L > 0.35 | Good overall structural similarity |

---

### 5. BLEU (Q3, Q4)

| Property | Value |
|----------|-------|
| **Used In** | Q3 - Summarization, Q4 - Translation |
| **Formula** | Geometric mean of n-gram precisions * brevity penalty |
| **Range** | [0, 100] (sacrebleu) or [0, 1] (nltk) |
| **Library** | `sacrebleu` (Q4, standard) or `nltk` (Q3) |

```python
# sacrebleu (recommended for Q4)
from sacrebleu import corpus_bleu
bleu = corpus_bleu(predictions, [references])
print(f"BLEU: {bleu.score:.1f}")  # range 0-100

# nltk (alternative for Q3)
from nltk.translate.bleu_score import corpus_bleu
score = corpus_bleu(
    [[ref.split()] for ref in references],
    [pred.split() for pred in predictions]
)
```

**BLEU Components**:
```
BLEU = BP * exp(sum(w_n * log(p_n)))

BP = min(1, exp(1 - ref_len/pred_len))   # brevity penalty
p_n = modified n-gram precision           # n=1,2,3,4
w_n = 1/4                                 # uniform weights
```

---

### 6. METEOR (Q3, Q4)

| Property | Value |
|----------|-------|
| **Used In** | Q3, Q4 |
| **Advantage** | Synonym matching, stemming, word order |
| **Range** | [0, 1] |
| **Library** | `evaluate` or `nltk.translate.meteor_score` |

```python
from evaluate import load
meteor = load("meteor")
results = meteor.compute(predictions=predictions, references=references)
```

**METEOR vs BLEU**:
| Dimension | BLEU | METEOR |
|-----------|------|--------|
| Matching | Exact n-gram | Exact + stem + synonym + paraphrase |
| Recall | Indirect (brevity penalty) | Direct |
| Word order | None | With penalty |
| Correlation | Medium | High (with human evaluation) |

---

### 7. BERTScore (Q3, Q4)

| Property | Value |
|----------|-------|
| **Used In** | Q3, Q4 |
| **Method** | Cosine similarity with BERT embeddings |
| **Output** | Precision, Recall, F1 |
| **Range** | [0, 1] |
| **Library** | `bert_score` |

```python
from bert_score import score

P, R, F1 = score(
    cands=predictions,
    refs=references,
    lang="en",           # "en" for Q3, "de" for Q4
    verbose=True,
    model_type="microsoft/deberta-xlarge-mnli"  # optional
)
# Average F1:
avg_f1 = F1.mean().item()
```

**BERTScore Advantage**: Measures semantic similarity instead of n-gram overlap. Gives a high score for "The dog ran" and "The canine sprinted".

---

### 8. ChrF (Q4)

| Property | Value |
|----------|-------|
| **Used In** | Q4 - Translation |
| **Method** | Character n-gram F-score |
| **Advantage** | Robust for morphologically rich languages (German!) |
| **Range** | [0, 100] |
| **Library** | `sacrebleu` |

```python
from sacrebleu import corpus_chrf
chrf = corpus_chrf(predictions, [references])
print(f"ChrF: {chrf.score:.1f}")
```

**Why ChrF?** Word-level metrics are weak for compound-word languages like German. ChrF performs character-level matching to capture morphological variations.

---

### 9. Perplexity (Q5)

| Property | Value |
|----------|-------|
| **Used In** | Q5 - Language Modeling |
| **Formula** | `exp(average_cross_entropy_loss)` |
| **Range** | [1, vocab_size] |
| **Lower = Better** | Yes |

```python
import math

def compute_perplexity(total_loss: float, num_tokens: int) -> float:
    avg_loss = total_loss / num_tokens
    return math.exp(avg_loss)
```

**Intuitive Meaning of Perplexity**: How many tokens the model is "uncertain" between at each step. If PP=100, the model is choosing among an average of 100 tokens.

---

## Evaluation Pipeline

### General Flow

```
Model.predict(test_data)
        |
        v
    predictions[]  +  references[]
        |
        v
    compute_metrics(task, predictions, references)
        |
        v
    {
      "accuracy": 0.93,
      "macro_f1": 0.92,
      ...
    }
        |
        v
    export.save_metrics()  +  visualization.plot_comparison()
```

### Evaluation Checklist (For Each Question)

- [ ] Test set was used only once, for final evaluation
- [ ] All models were evaluated on the same test set
- [ ] Metrics were computed at the correct level (entity vs token, corpus vs sentence)
- [ ] Results were saved as JSON + CSV
- [ ] Comparison table was created
- [ ] Visualizations were generated

---

## Reporting Standard

### Result Table Format

```
| Model          | Metric_1 | Metric_2 | ... |
|----------------|----------|----------|-----|
| Baseline       | 0.XX     | 0.XX     |     |
| Model A        | 0.XX     | 0.XX     |     |
| Model B        | **0.XX** | **0.XX** |     |

Bold = best score
```

### JSON Output Format

```json
{
    "question": "q1",
    "timestamp": "2026-04-15T14:30:22",
    "models": {
        "tfidf_lr": {
            "accuracy": 0.8856,
            "macro_f1": 0.8854
        },
        "bilstm": {
            "accuracy": 0.8712,
            "macro_f1": 0.8708
        },
        "distilbert": {
            "accuracy": 0.9301,
            "macro_f1": 0.9299
        }
    },
    "best_model": "distilbert",
    "config_hash": "abc123..."
}
```

---

## Related Documents

- [Shared Infrastructure](03-shared-infrastructure.md) - metrics.py and evaluation.py implementation
- [Q1](04-q1-text-classification.md) - Accuracy, Macro-F1
- [Q2](05-q2-ner.md) - Entity-level P/R/F1
- [Q3](06-q3-summarization.md) - ROUGE, BLEU, METEOR, BERTScore
- [Q4](07-q4-machine-translation.md) - BLEU, METEOR, ChrF, BERTScore
- [Q5](08-q5-language-modeling.md) - Perplexity
- [LaTeX Report](11-report-structure.md) - How to present in the report
