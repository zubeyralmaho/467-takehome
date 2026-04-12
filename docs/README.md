# CENG 467 - Take-Home Midterm: Architecture Documentation

> Natural Language Understanding and Generation - Prof. Dr. Aytug Onan

Bu dokumantasyon, CENG 467 take-home midterm projesinin teknik mimarisini, veri akislarini, modullerin birbirleriyle iliskilerini ve uygulama planini kapsamli sekilde tanimlar.

---

## Dokumantasyon Haritasi

| # | Dokuman | Aciklama |
|---|---------|----------|
| 1 | [Proje Genel Bakis](01-project-overview.md) | Scope, hedefler, teknoloji secimi |
| 2 | [Dizin Yapisi](02-project-structure.md) | Klasor/dosya organizasyonu, modul haritasi |
| 3 | [Ortak Altyapi](03-shared-infrastructure.md) | Config, data loaders, evaluation engine, logging |
| 4 | [Q1 - Text Classification](04-q1-text-classification.md) | TF-IDF + LR/SVM, BiLSTM, DistilBERT |
| 5 | [Q2 - Named Entity Recognition](05-q2-ner.md) | CRF, BiLSTM-CRF, BERT-NER |
| 6 | [Q3 - Text Summarization](06-q3-summarization.md) | TextRank, BART/T5 |
| 7 | [Q4 - Machine Translation](07-q4-machine-translation.md) | Seq2Seq + Attention, Transformer |
| 8 | [Q5 - Language Modeling](08-q5-language-modeling.md) | N-gram, LSTM, GPT-2 |
| 9 | [Evaluation Framework](09-evaluation-framework.md) | Metrikler, raporlama, karsilastirma |
| 10 | [Experiment & Reproducibility](10-experiment-config.md) | Seed, hyperparameter yonetimi, calistirma |
| 11 | [LaTeX Rapor Yapisi](11-report-structure.md) | Rapor sablonu, section plani |

---

## Bagimlilk Grafi (Dokumantasyon)

```
README.md (bu dosya)
    |
    +-- 01-project-overview.md
    |       |
    |       +-- 02-project-structure.md
    |       |       |
    |       |       +-- 03-shared-infrastructure.md
    |       |               |
    |       |               +-- 09-evaluation-framework.md
    |       |               +-- 10-experiment-config.md
    |       |
    |       +-- 04-q1-text-classification.md ---+
    |       +-- 05-q2-ner.md -------------------+-- Hepsi 03 ve 09'a bagimli
    |       +-- 06-q3-summarization.md ---------+
    |       +-- 07-q4-machine-translation.md ---+
    |       +-- 08-q5-language-modeling.md -----+
    |
    +-- 11-report-structure.md (tum sorulari kapsar)
```

---

## Hizli Baslangic

Her sorunun kendi entry point'i vardir. Detaylar icin ilgili dokumana bakiniz:

```bash
# Q1 - Text Classification
python -m src.q1_classification.main --config configs/q1.yaml

# Q2 - NER
python -m src.q2_ner.main --config configs/q2.yaml

# Q3 - Summarization
python -m src.q3_summarization.main --config configs/q3.yaml

# Q4 - Machine Translation
python -m src.q4_translation.main --config configs/q4.yaml

# Q5 - Language Modeling
python -m src.q5_language_model.main --config configs/q5.yaml
```
