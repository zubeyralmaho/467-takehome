# 01 - Proje Genel Bakis

> [Ana Sayfa](README.md) | Sonraki: [Dizin Yapisi](02-project-structure.md)

---

## Amac

Bu proje, NLP'nin bes temel gorevini (text classification, NER, summarization, machine translation, language modeling) farkli mimari yaklasimlarla (klasik, neural, transformer) implement edip karsilastirmali olarak degerlendirmeyi amaclar.

---

## Soru Haritas ve Gorev Ozeti

| Soru | Gorev | Dataset | Modeller | Ana Metrikler |
|------|-------|---------|----------|---------------|
| Q1 | Text Classification | IMDb (veya SST-2) | TF-IDF+LR, TF-IDF+SVM, BiLSTM, DistilBERT | Accuracy, Macro-F1 |
| Q2 | Named Entity Recognition | CoNLL-2003 | CRF, BiLSTM-CRF, BERT-NER | Precision, Recall, F1 (entity-level) |
| Q3 | Text Summarization | CNN/DailyMail (subset) | TextRank, BART (veya T5) | ROUGE-1/2/L, BLEU, METEOR, BERTScore |
| Q4 | Machine Translation | Multi30k (EN-DE) | Seq2Seq+Attention, Transformer | BLEU, METEOR, ChrF, BERTScore |
| Q5 | Language Modeling | WikiText-2 (veya PTB) | N-gram, LSTM, (opsiyonel: GPT-2) | Perplexity |

---

## Teknoloji Stack'i

### Core Framework

| Katman | Teknoloji | Versiyon | Kullanim |
|--------|-----------|----------|----------|
| Deep Learning | PyTorch | >=2.0 | Tum neural modeller |
| Transformers | HuggingFace Transformers | >=4.35 | BERT, DistilBERT, BART, T5 |
| Tokenization | HuggingFace Tokenizers | >=0.15 | Subword tokenization |
| Classical ML | scikit-learn | >=1.3 | TF-IDF, LR, SVM, CRF |
| NER CRF | sklearn-crfsuite / TorchCRF | - | CRF ve BiLSTM-CRF |
| Data | HuggingFace Datasets | >=2.14 | Dataset yukleme/bolme |
| Metrics | evaluate + custom | - | ROUGE, BLEU, METEOR, BERTScore |

### Yardimci Araclar

| Arac | Kullanim |
|------|----------|
| PyYAML | Config yonetimi |
| matplotlib / seaborn | Gorsellestirme |
| pandas | Sonuc tablolari |
| tqdm | Progress bar |
| LaTeX (texlive) | Rapor yazimi |

### Ortam

- **Python**: 3.10+
- **GPU**: CUDA destekli (Colab T4/V100 veya lokal)
- **Reproducibility**: Her deneyde seed=42 (ayarlanabilir)

---

## Tasarim Ilkeleri

### 1. Modularite
Her soru kendi alt paketi (`src/q{n}_*/`) icerisinde yasayan bagimsiz bir modul olarak tasarlanir. Ortak islevler `src/common/` altinda merkezlestirilir.

### 2. Konfigurasyona Dayali Calistirma
Tum hyperparameter'ler, dataset ayarlari ve model secenekleri YAML config dosyalari uzerinden yonetilir. Hardcoded deger bulunmaz.

### 3. Tekrarlanabilirlik (Reproducibility)
- Sabit random seed (global + per-worker)
- Deterministic PyTorch ayarlari
- Config dosyalari sonuc klasorleriyle birlikte saklanir
- Her deney ciktisi timestamped klasorde tutulur

### 4. Tutarli Evaluation
Tum sorular ayni evaluation engine'i kullanir. Metrikler merkezi olarak hesaplanir, sonuclar standart formatta (JSON + CSV) kaydedilir.

### 5. Incremental Gelistirme
Her soru bagimsiz olarak gelistirilip test edilebilir. Birinin hatasi digerlerini etkilemez.

---

## Gelistirme Sirasi (Onerilen)

```
Hafta 1:  [03-shared-infrastructure.md] -> Ortak altyapi (config, data, eval)
          [04-q1-text-classification.md] -> Q1 (en basit, altyapiyi dogrular)

Hafta 2:  [05-q2-ner.md] -> Q2 NER
          [06-q3-summarization.md] -> Q3 Summarization

Hafta 3:  [07-q4-machine-translation.md] -> Q4 Translation
          [08-q5-language-modeling.md] -> Q5 Language Modeling

Hafta 4:  [09-evaluation-framework.md] -> Final evaluation, error analysis
          [11-report-structure.md] -> LaTeX rapor yazimi
```

---

## Iliskili Dokumanlar

- [Dizin Yapisi](02-project-structure.md) - Dosya ve klasor organizasyonu
- [Ortak Altyapi](03-shared-infrastructure.md) - Paylasilan kod detaylari
- [Experiment Config](10-experiment-config.md) - Reproducibility detaylari
