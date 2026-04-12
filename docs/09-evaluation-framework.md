# 09 - Evaluation Framework

> [Ana Sayfa](README.md) | Onceki: [Q5 - Language Modeling](08-q5-language-modeling.md) | Sonraki: [Experiment Config](10-experiment-config.md)

---

## Genel Bakis

Bu dokuman, projede kullanilan tum evaluation metriklerini, hesaplama yontemlerini, kutuphaneleri ve raporlama standartlarini tanimlar. Tum sorular ayni merkezi evaluation engine'i (`src/common/metrics.py` + `src/common/evaluation.py`) kullanir.

---

## Metrik Katalogu

### 1. Accuracy (Q1)

| Ozellik | Deger |
|---------|-------|
| **Kullanildigi Soru** | Q1 - Text Classification |
| **Formul** | `correct_predictions / total_predictions` |
| **Aralik** | [0, 1] |
| **Yuksek = Iyi** | Evet |
| **Kutuphane** | `sklearn.metrics.accuracy_score` |

```python
from sklearn.metrics import accuracy_score
acc = accuracy_score(y_true, y_pred)
```

---

### 2. Macro-F1 (Q1)

| Ozellik | Deger |
|---------|-------|
| **Kullanildigi Soru** | Q1 - Text Classification |
| **Formul** | Her sinif icin F1 hesapla, ortalamalarini al |
| **Aralik** | [0, 1] |
| **Avantaj** | Dengesiz siniflar icin adil |
| **Kutuphane** | `sklearn.metrics.f1_score(average='macro')` |

```python
from sklearn.metrics import f1_score
f1 = f1_score(y_true, y_pred, average='macro')
```

---

### 3. Entity-Level Precision / Recall / F1 (Q2)

| Ozellik | Deger |
|---------|-------|
| **Kullanildigi Soru** | Q2 - NER |
| **Hesaplama Seviyesi** | Entity-level (token degil!) |
| **Kutuphane** | `seqeval` |
| **Onemli Not** | Kismi entity eslesmesi YANLIS sayilir |

```python
from seqeval.metrics import classification_report, f1_score
from seqeval.scheme import IOB2

# y_true ve y_pred: list[list[str]] (BIO tagleri)
report = classification_report(y_true, y_pred, scheme=IOB2)
f1 = f1_score(y_true, y_pred, scheme=IOB2)
```

**Entity-Level vs Token-Level**:
```
Gercek:  [B-LOC, I-LOC, I-LOC]   -> "New York City" (1 entity)
Tahmin:  [B-LOC, I-LOC, O]        -> "New York" (1 entity)

Token-level: 2/3 dogru = %66.7
Entity-level: 0/1 dogru = %0 (entity siniri yanlis!)
```

---

### 4. ROUGE (Q3)

| Varyant | Olctugu Sey | Formul |
|---------|------------|--------|
| **ROUGE-1** | Unigram overlap | F1(unigram_precision, unigram_recall) |
| **ROUGE-2** | Bigram overlap | F1(bigram_precision, bigram_recall) |
| **ROUGE-L** | Longest Common Subsequence | F1(LCS_precision, LCS_recall) |

| Ozellik | Deger |
|---------|-------|
| **Kullanildigi Soru** | Q3 - Summarization |
| **Aralik** | [0, 1] |
| **Kutuphane** | `evaluate` (HuggingFace) veya `rouge_score` |

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

**ROUGE Yorumu**:
| Skor | Anlam |
|------|-------|
| ROUGE-1 > 0.40 | Iyi icerik kapsami |
| ROUGE-2 > 0.18 | Iyi cumle yapisi kapsami |
| ROUGE-L > 0.35 | Iyi genel yapisal benzerlik |

---

### 5. BLEU (Q3, Q4)

| Ozellik | Deger |
|---------|-------|
| **Kullanildigi Sorular** | Q3 - Summarization, Q4 - Translation |
| **Formul** | Geometric mean of n-gram precisions * brevity penalty |
| **Aralik** | [0, 100] (sacrebleu) veya [0, 1] (nltk) |
| **Kutuphane** | `sacrebleu` (Q4, standard) veya `nltk` (Q3) |

```python
# sacrebleu (Q4 icin onerilen)
from sacrebleu import corpus_bleu
bleu = corpus_bleu(predictions, [references])
print(f"BLEU: {bleu.score:.1f}")  # 0-100 arasi

# nltk (Q3 icin alternatif)
from nltk.translate.bleu_score import corpus_bleu
score = corpus_bleu(
    [[ref.split()] for ref in references],
    [pred.split() for pred in predictions]
)
```

**BLEU Bilesenleri**:
```
BLEU = BP * exp(sum(w_n * log(p_n)))

BP = min(1, exp(1 - ref_len/pred_len))   # brevity penalty
p_n = modified n-gram precision           # n=1,2,3,4
w_n = 1/4                                 # uniform weights
```

---

### 6. METEOR (Q3, Q4)

| Ozellik | Deger |
|---------|-------|
| **Kullanildigi Sorular** | Q3, Q4 |
| **Avantaj** | Synonym matching, stemming, word order |
| **Aralik** | [0, 1] |
| **Kutuphane** | `evaluate` veya `nltk.translate.meteor_score` |

```python
from evaluate import load
meteor = load("meteor")
results = meteor.compute(predictions=predictions, references=references)
```

**METEOR vs BLEU**:
| Boyut | BLEU | METEOR |
|-------|------|--------|
| Matching | Exact n-gram | Exact + stem + synonym + paraphrase |
| Recall | Dolayili (brevity penalty) | Dogrudan |
| Word order | Yok | Penalty ile |
| Korelasyon | Orta | Yuksek (insan degerlendirmesiyle) |

---

### 7. BERTScore (Q3, Q4)

| Ozellik | Deger |
|---------|-------|
| **Kullanildigi Sorular** | Q3, Q4 |
| **Yontem** | BERT embeddings ile cosine similarity |
| **Cikti** | Precision, Recall, F1 |
| **Aralik** | [0, 1] |
| **Kutuphane** | `bert_score` |

```python
from bert_score import score

P, R, F1 = score(
    cands=predictions,
    refs=references,
    lang="en",           # Q3 icin "en", Q4 icin "de"
    verbose=True,
    model_type="microsoft/deberta-xlarge-mnli"  # opsiyonel
)
# Ortalama F1:
avg_f1 = F1.mean().item()
```

**BERTScore Avantaji**: N-gram overlap yerine semantik benzerlik olcer. "The dog ran" ve "The canine sprinted" icin yuksek skor verir.

---

### 8. ChrF (Q4)

| Ozellik | Deger |
|---------|-------|
| **Kullanildigi Soru** | Q4 - Translation |
| **Yontem** | Character n-gram F-score |
| **Avantaj** | Morfolojik zengin diller (Almanca!) icin robust |
| **Aralik** | [0, 100] |
| **Kutuphane** | `sacrebleu` |

```python
from sacrebleu import corpus_chrf
chrf = corpus_chrf(predictions, [references])
print(f"ChrF: {chrf.score:.1f}")
```

**Neden ChrF?** Almanca gibi bileşik kelimeli dillerde word-level metrikler zayif kalir. ChrF karakter seviyesinde esleme yaparak morfolojik varyasyonlari yakalayabilir.

---

### 9. Perplexity (Q5)

| Ozellik | Deger |
|---------|-------|
| **Kullanildigi Soru** | Q5 - Language Modeling |
| **Formul** | `exp(average_cross_entropy_loss)` |
| **Aralik** | [1, vocab_size] |
| **Dusuk = Iyi** | Evet |

```python
import math

def compute_perplexity(total_loss: float, num_tokens: int) -> float:
    avg_loss = total_loss / num_tokens
    return math.exp(avg_loss)
```

**Perplexity Sezgisel Anlami**: Modelin her adimda kac token arasinda "kararsiz" kaldigi. PP=100 ise model ortalama 100 token arasindan sec.

---

## Evaluation Pipeline

### Genel Akis

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

### Evaluation Kontrol Listesi (Her Soru icin)

- [ ] Test seti yalnizca bir kez, final evaluation icin kullanildi
- [ ] Tum modeller ayni test seti uzerinde degerlendirildi
- [ ] Metrikler dogru seviyede hesaplandi (entity vs token, corpus vs sentence)
- [ ] Sonuclar JSON + CSV olarak kaydedildi
- [ ] Karsilastirma tablosu olusturuldu
- [ ] Gorseller uretildi

---

## Raporlama Standardi

### Sonuc Tablosu Formati

```
| Model          | Metric_1 | Metric_2 | ... |
|----------------|----------|----------|-----|
| Baseline       | 0.XX     | 0.XX     |     |
| Model A        | 0.XX     | 0.XX     |     |
| Model B        | **0.XX** | **0.XX** |     |

Bold = en iyi skor
```

### JSON Cikti Formati

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

## Iliskili Dokumanlar

- [Ortak Altyapi](03-shared-infrastructure.md) - metrics.py ve evaluation.py implementasyonu
- [Q1](04-q1-text-classification.md) - Accuracy, Macro-F1
- [Q2](05-q2-ner.md) - Entity-level P/R/F1
- [Q3](06-q3-summarization.md) - ROUGE, BLEU, METEOR, BERTScore
- [Q4](07-q4-machine-translation.md) - BLEU, METEOR, ChrF, BERTScore
- [Q5](08-q5-language-modeling.md) - Perplexity
- [LaTeX Rapor](11-report-structure.md) - Raporda nasil sunulacagi
