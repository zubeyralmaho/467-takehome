# 06 - Q3: Text Summarization

> [Ana Sayfa](README.md) | Onceki: [Q2 - NER](05-q2-ner.md) | Sonraki: [Q4 - Machine Translation](07-q4-machine-translation.md)

---

## Hedef

Extractive ve abstractive ozetleme yontemlerini karsilastirmak. Performansi ROUGE, BLEU, METEOR ve BERTScore ile degerlendirmek. Akicilik, factual tutarlilik ve bilgi kapsami acisindan kalitatif analiz yapmak.

---

## Dataset: CNN/DailyMail

### Ozellikler
- **Boyut**: ~300K makale-ozet cifti (subset kullanilacak)
- **Subset**: 10K train / 1K val / 1K test (yeterli ve verimli)
- **Ortalama makale uzunlugu**: ~780 kelime
- **Ortalama ozet uzunlugu**: ~56 kelime (3-4 cumle)
- **Kaynak**: `datasets.load_dataset("cnn_dailymail", "3.0.0")`

### Subset Olusturma
```python
dataset = load_dataset("cnn_dailymail", "3.0.0")
train_subset = dataset["train"].shuffle(seed=42).select(range(10000))
val_subset = dataset["validation"].shuffle(seed=42).select(range(1000))
test_subset = dataset["test"].shuffle(seed=42).select(range(1000))
```

### Veri Yapisi
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
    - CNN/DailyMail ozel isaret temizligi
    - Fazla whitespace/newline normalizasyonu
    - Encoding sorunlari
    """

def truncate_article(text: str, max_tokens: int = 1024) -> str:
    """BART/T5 icin max input length'e truncate."""

def split_into_sentences(text: str) -> list[str]:
    """
    TextRank icin cumle bolme.
    nltk.sent_tokenize veya spacy sentence segmentation.
    """
```

---

## Model Mimarileri

### Model 1: TextRank (Extractive)

**Dosya**: `models/textrank.py`

```python
class TextRankSummarizer:
    """
    Graph-based extractive summarization.
    PageRank algoritmasinin metin ozetleme uyarlamasi.
    """

    def __init__(self, similarity_method: str = "tfidf",
                 damping: float = 0.85,
                 num_sentences: int = 3):
        """
        similarity_method: "tfidf" veya "embedding"
        damping: PageRank damping faktoru
        num_sentences: secilecek cumle sayisi
        """

    def build_similarity_matrix(self, sentences: list[str]) -> np.ndarray:
        """
        Cmleler arasi benzerlik matrisi:
        - TF-IDF cosine similarity
        - (veya) Sentence embedding cosine similarity
        """

    def rank_sentences(self, similarity_matrix: np.ndarray) -> list[float]:
        """PageRank skoru hesaplar."""

    def summarize(self, text: str) -> str:
        """
        1. Metni cumlelere bol
        2. Benzerlik matrisi olustur
        3. PageRank ile sirala
        4. En yuksek skorlu N cumleyi sec
        5. Orijinal sirayla birlestir
        """
```

**Algoritma Akisi**:
```
Input Article (metin)
        |
        v
[Sentence Segmentation] -> ["S1", "S2", "S3", ..., "Sn"]
        |
        v
[TF-IDF Vectorization] -> Cumle vektorleri
        |
        v
[Cosine Similarity Matrix] -> n x n matris
        |
        v
[PageRank Algorithm] -> Skor: [0.23, 0.15, 0.31, ...]
        |
        v
[Top-K Sentence Selection] -> En yuksek skorlu 3 cumle
        |
        v
[Orijinal Sira ile Birlestirme]
        |
        v
Output Summary
```

**Parametreler**:
| Parametre | Deger |
|-----------|-------|
| similarity | TF-IDF cosine |
| damping | 0.85 |
| convergence_threshold | 1e-5 |
| max_iterations | 100 |
| num_sentences | 3 |

---

### Model 2: BART (Abstractive)

**Dosya**: `models/bart_summarizer.py`

```python
class BARTSummarizer:
    """
    facebook/bart-large-cnn fine-tuned model.
    Encoder-decoder transformer ile abstractive summarization.
    """

    def __init__(self, model_name: str = "facebook/bart-large-cnn",
                 max_input_length: int = 1024,
                 max_output_length: int = 142,
                 min_output_length: int = 56):
        """Pretrained BART modeli ve tokenizer yukler."""

    def summarize(self, text: str, **generate_kwargs) -> str:
        """
        Tek metin icin ozet uretir.
        generate_kwargs: num_beams, length_penalty, etc.
        """

    def summarize_batch(self, texts: list[str],
                        batch_size: int = 8) -> list[str]:
        """Batch inference."""

    def fine_tune(self, train_dataset, val_dataset, config):
        """
        Opsiyonel: Eger pretrained yeterli degilse fine-tune.
        Cogu durumda facebook/bart-large-cnn zaten CNN/DM uzerinde
        fine-tuned, bu yuzden dogrudan kullanilabilir.
        """
```

**Yaklasim Secenekleri**:

| Yaklasim | Aciklama | Onerilen |
|----------|----------|----------|
| Zero-shot | Pretrained BART-large-CNN dogrudan | Evet (varsayilan) |
| Fine-tune | Subset uzerinde ek fine-tuning | Opsiyonel karsilastirma |

> **Not**: `facebook/bart-large-cnn` zaten CNN/DailyMail uzerinde fine-tune edilmistir. Ek fine-tuning gereksiz olabilir ama karsilastirma amaciyla yapilabilir.

**T5 Alternatifi**:
```python
class T5Summarizer:
    """google/flan-t5-base alternatifi."""
    # Ayni API, farkli model_name
    # Input prefix: "summarize: " eklenmeli
```

**Generation Parametreleri**:
| Parametre | Deger |
|-----------|-------|
| num_beams | 4 |
| length_penalty | 2.0 |
| max_length | 142 |
| min_length | 56 |
| no_repeat_ngram_size | 3 |
| early_stopping | True |

---

## Evaluation

### Metrik Seti

| Metrik | Olctugu Sey | Kutuphane |
|--------|------------|-----------|
| **ROUGE-1** | Unigram overlap | `evaluate` / `rouge_score` |
| **ROUGE-2** | Bigram overlap | `evaluate` / `rouge_score` |
| **ROUGE-L** | Longest common subsequence | `evaluate` / `rouge_score` |
| **BLEU** | N-gram precision + brevity penalty | `nltk.translate.bleu_score` |
| **METEOR** | Alignment + synonym + stemming | `evaluate` / `nltk.translate.meteor` |
| **BERTScore** | Contextual semantic similarity | `bert_score` |

### Metrik Hesaplama Detayi

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

Detaylar icin: [Evaluation Framework](09-evaluation-framework.md)

---

## Qualitative Analysis

### analysis.py

```python
def qualitative_comparison(articles, references, extractive_summaries,
                           abstractive_summaries, n: int = 3) -> list[dict]:
    """
    En az 3 ornek icin:
    - Kaynak metin (truncated)
    - Referans ozet
    - TextRank ciktisi
    - BART ciktisi
    - Her biri icin: fluency, factual consistency, information coverage
    """

def analyze_extractive_vs_abstractive(examples: list[dict]) -> dict:
    """
    Karsilastirma boyutlari:
    1. Fluency (akicilik): Extractive -> kaynak cumleler, Abstractive -> yeni cumleler
    2. Factual Consistency: Extractive daha guvenilir, Abstractive hallucination riski
    3. Information Coverage: Abstractive daha yogun bilgi
    4. Redundancy: Extractive tekrar riski, Abstractive daha ozlu
    """
```

### Ornek Karsilastirma Tablosu (Rapor icin)

| Boyut | TextRank (Extractive) | BART (Abstractive) |
|-------|----------------------|-------------------|
| Akicilik | Kaynak cumleler, dogal | Yeni cumleler, daha ozlu |
| Factual Tutarlilik | Yuksek (kaynak kopyasi) | Risk: hallucination |
| Bilgi Yogunlugu | Dusuk (tam cumleler) | Yuksek (sikilastirma) |
| Hesaplama Maliyeti | Dusuk (CPU yeterli) | Yuksek (GPU gerekli) |
| Okunabilirlik | Parcali olabilir | Daha tutarli |

---

## Beklenen Ciktilar

```
outputs/q3/run_{timestamp}/
|-- config.yaml
|-- metrics.json                      # ROUGE, BLEU, METEOR, BERTScore
|-- predictions/
|   |-- textrank_summaries.csv
|   +-- bart_summaries.csv
|-- qualitative_analysis.json         # 3+ detayli ornek
|-- figures/
|   |-- metric_comparison.png
|   +-- rouge_distribution.png
+-- (opsiyonel) model_bart_finetuned/
```

---

## Config Ornegi (q3.yaml)

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
    fine_tune: false          # Pretrained yeterli

evaluation:
  metrics: ["rouge1", "rouge2", "rougeL", "bleu", "meteor", "bertscore"]
  num_qualitative_examples: 3
```

---

## Iliskili Dokumanlar

- [Ortak Altyapi](03-shared-infrastructure.md) - metrics.py (ROUGE, BLEU, etc.)
- [Evaluation Framework](09-evaluation-framework.md) - Tum metriklerin detayli aciklamasi
- [Q4 - Machine Translation](07-q4-machine-translation.md) - Benzer metrikler (BLEU, METEOR, BERTScore)
