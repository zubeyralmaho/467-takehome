# 11 - LaTeX Rapor Yapisi

> [Ana Sayfa](README.md) | Onceki: [Experiment Config](10-experiment-config.md)

---

## Genel Bakis

Raporun LaTeX ile yazilmasi zorunludur. Bu dokuman rapor sablonunu, section yapisini, tablo/sekil standartlarini ve her sorunun rapordaki karsiligini tanimlar.

---

## Rapor Dizin Yapisi

```
report/
|-- main.tex                   # Ana dosya (tum section'lari include eder)
|-- preamble.tex               # Paketler, ayarlar, makrolar
|-- sections/
|   |-- introduction.tex       # Giris, genel yaklasim
|   |-- q1.tex                 # Soru 1
|   |-- q2.tex                 # Soru 2
|   |-- q3.tex                 # Soru 3
|   |-- q4.tex                 # Soru 4
|   |-- q5.tex                 # Soru 5
|   +-- conclusion.tex         # Genel sonuc ve degerledirme
|-- figures/                   # Tum gorseller
|   |-- q1/
|   |-- q2/
|   |-- q3/
|   |-- q4/
|   +-- q5/
|-- tables/                    # Buyuk tablolar (opsiyonel ayri dosya)
+-- references.bib             # Kaynakca
```

---

## main.tex Sablonu

```latex
\documentclass[12pt, a4paper]{article}
\input{preamble}

\title{CENG 467 -- Natural Language Understanding and Generation \\
       Take-Home Midterm Examination}
\author{Ad Soyad \\ Student ID: XXXXXXXX}
\date{Nisan 2026}

\begin{document}
\maketitle
\tableofcontents
\newpage

\input{sections/introduction}
\input{sections/q1}
\input{sections/q2}
\input{sections/q3}
\input{sections/q4}
\input{sections/q5}
\input{sections/conclusion}

\bibliographystyle{plain}
\bibliography{references}

\end{document}
```

---

## preamble.tex

```latex
% Encoding & Language
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[english]{babel}

% Math
\usepackage{amsmath, amssymb}

% Graphics
\usepackage{graphicx}
\usepackage{float}
\usepackage{subcaption}

% Tables
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{adjustbox}

% Code
\usepackage{listings}
\usepackage{xcolor}

% Hyperlinks
\usepackage[colorlinks=true, linkcolor=blue, citecolor=blue]{hyperref}

% Margins
\usepackage[margin=2.5cm]{geometry}

% Bibliography
\usepackage{cite}

% Custom
\usepackage{enumitem}
\usepackage{caption}

% Code style
\lstset{
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    language=Python,
    keywordstyle=\color{blue},
    commentstyle=\color{gray},
    stringstyle=\color{red}
}
```

---

## Section Yapilari

### introduction.tex

```
1. Introduction
   1.1 Scope and Objectives
       - 5 NLU gorevinin tanitimi
       - Genel yaklasim: classical vs neural vs transformer
   1.2 Technical Setup
       - Ortam, kutuphaneler, reproducibility
       - Dataset ozeti tablosu
   1.3 Report Organization
       - Her section'in icerigi
```

---

### q1.tex - Representation Learning in Text Classification

Ilgili mimari dokuman: [Q1 Architecture](04-q1-text-classification.md)

```
2. Question 1: Representation Learning in Text Classification

   2.1 Dataset Description
       - IMDb dataset ozellikleri
       - Tablo: Dataset istatistikleri (boyut, ortalama uzunluk, sinif dagalimi)
       - Train/Val/Test split bilgileri

   2.2 Preprocessing Pipeline
       - Cleaning adimlari
       - Tokenization stratejileri karsilastirmasi
       - Tablo: Preprocessing deneyi sonuclari
         (stopword, lowercase, max_features etkisi)

   2.3 Models
       2.3.1 TF-IDF + Logistic Regression / SVM
           - Representation aciklamasi
           - Hyperparametreler
       2.3.2 BiLSTM
           - Mimari sekil
           - GloVe embeddings
           - Hyperparametreler
       2.3.3 DistilBERT
           - Fine-tuning stratejisi
           - Hyperparametreler

   2.4 Results
       - Tablo: Model karsilastirmasi (Accuracy, Macro-F1)
       - Training curves (BiLSTM, DistilBERT)
       - Confusion matrices

   2.5 Error Analysis
       - 5 misclassified ornek tablosu
       - Ortak hata pattern'leri
       - Neden yanlis siniflandirildi?

   2.6 Discussion
       - Representation turleri karsilastirmasi
         (sparse vs dense vs contextual)
       - Performans vs interpretability trade-off
       - Anahtar bulgular
```

---

### q2.tex - Named Entity Recognition

Ilgili mimari dokuman: [Q2 Architecture](05-q2-ner.md)

```
3. Question 2: Named Entity Recognition

   3.1 Dataset Description
       - CoNLL-2003 ozellikleri
       - BIO tagging aciklamasi
       - Entity type dagalimi tablosu/grafik

   3.2 Preprocessing and BIO Alignment
       - CoNLL format aciklamasi
       - BERT subword alignment yontemi
       - CRF feature engineering

   3.3 Models
       3.3.1 CRF (Feature-based)
           - Feature set
           - Training yontemi
       3.3.2 BiLSTM-CRF
           - Mimari sekil
           - CRF katmaninin rolu
       3.3.3 BERT Token Classification
           - Fine-tuning
           - Subword handling

   3.4 Results
       - Tablo: Overall P/R/F1
       - Tablo: Per-entity-type P/R/F1 (PER, ORG, LOC, MISC)

   3.5 Error Analysis
       - Boundary error ornekleri
       - Entity confusion ornekleri
       - Contextual embeddings'in katkisi tartismasi

   3.6 Discussion
       - CRF vs neural vs transformer
       - Contextual bilginin onemi
```

---

### q3.tex - Text Summarization

Ilgili mimari dokuman: [Q3 Architecture](06-q3-summarization.md)

```
4. Question 3: Text Summarization

   4.1 Dataset Description
       - CNN/DailyMail ozellikleri
       - Subset boyutu ve secim yontemi

   4.2 Methods
       4.2.1 TextRank (Extractive)
           - Algoritma aciklamasi + diagram
           - Parametreler
       4.2.2 BART (Abstractive)
           - Model aciklamasi
           - Generation parametreleri

   4.3 Evaluation Metrics
       - ROUGE-1/2/L, BLEU, METEOR, BERTScore aciklamasi
       - Her metrigin olctugu boyut

   4.4 Results
       - Tablo: Tum metrikler (TextRank vs BART)

   4.5 Qualitative Analysis
       - 3+ ornek: source, reference, TextRank output, BART output
       - Her ornek icin: fluency, factual consistency, coverage analizi

   4.6 Discussion
       - Extractive vs abstractive trade-off'lar
       - Computational cost, readability, faithfulness
```

---

### q4.tex - Machine Translation

Ilgili mimari dokuman: [Q4 Architecture](07-q4-machine-translation.md)

```
5. Question 4: Machine Translation

   5.1 Dataset Description
       - Multi30k ozellikleri
       - Preprocessing adimlari

   5.2 Models
       5.2.1 Seq2Seq + Attention
           - Encoder-Decoder mimari sekil
           - Attention mekanizmasi aciklamasi
       5.2.2 Transformer
           - Self-attention + cross-attention
           - Positional encoding

   5.3 Evaluation Metrics
       - BLEU, METEOR, ChrF, BERTScore aciklamasi
       - Her metrigin odagi

   5.4 Results
       - Tablo: Tum metrikler (Seq2Seq vs Transformer)
       - Attention heatmap gorselleri

   5.5 Qualitative Analysis
       - 3+ ornek: source, reference, Seq2Seq output, Transformer output
       - Fluency, rare word handling, long-range dependency analizi

   5.6 Discussion
       - Metrik boyutlari analizi (her metrik neyi yakaliyor)
       - Mimari trade-off'lar (paralelizasyon, long-range, hiz)
```

---

### q5.tex - Language Modeling

Ilgili mimari dokuman: [Q5 Architecture](08-q5-language-modeling.md)

```
6. Question 5: Language Modeling

   6.1 Dataset Description
       - WikiText-2 ozellikleri

   6.2 Models
       6.2.1 N-gram (Trigram + Smoothing)
           - Model aciklamasi
           - Smoothing yontemi
       6.2.2 LSTM Language Model
           - Mimari detaylari
           - Weight tying
       6.2.3 (Opsiyonel) GPT-2
           - Fine-tuning yaklasimi

   6.3 Results
       - Tablo: Perplexity karsilastirmasi
       - Training curves

   6.4 Generated Text Samples
       - Her modelden 2-3 ornek
       - Farkli temperature/sampling ayarlari

   6.5 Discussion
       - Fluency ve coherence analizi
       - Model davranisi farkliliklari
```

---

### conclusion.tex

```
7. Conclusion
   - 5 gorev uzerinden ogrenilenler
   - Ortak temalar: klasik vs neural vs transformer
   - Her gorevde en iyi yaklasimin neden ustun geldigi
   - Limitasyonlar ve gelecek calisma
```

---

## Tablo ve Sekil Standartlari

### Tablo Ornegi

```latex
\begin{table}[H]
\centering
\caption{Q1: Model performance comparison on IMDb test set.}
\label{tab:q1-results}
\begin{tabular}{lcc}
\toprule
\textbf{Model} & \textbf{Accuracy} & \textbf{Macro-F1} \\
\midrule
TF-IDF + LR     & 0.886 & 0.885 \\
TF-IDF + SVM    & 0.889 & 0.888 \\
BiLSTM           & 0.871 & 0.871 \\
DistilBERT       & \textbf{0.930} & \textbf{0.930} \\
\bottomrule
\end{tabular}
\end{table}
```

### Sekil Ornegi

```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.8\textwidth]{figures/q1/training_curves.png}
\caption{Training and validation loss curves for BiLSTM and DistilBERT.}
\label{fig:q1-training}
\end{figure}
```

### Qualitative Ornek Ornegi

```latex
\begin{table}[H]
\centering
\caption{Q3: Qualitative comparison of summarization outputs.}
\label{tab:q3-qualitative}
\small
\begin{tabular}{p{3cm}p{10cm}}
\toprule
\textbf{Component} & \textbf{Text} \\
\midrule
Source (truncated) & LONDON (CNN) -- An American tourist who ... \\
Reference & An American tourist was found dead ... \\
TextRank & An American tourist who was visiting London ... \\
BART & An American tourist was found dead in a London hotel ... \\
\bottomrule
\end{tabular}
\end{table}
```

---

## Kaynakca (references.bib) Ornekleri

```bibtex
@article{devlin2019bert,
  title={BERT: Pre-training of Deep Bidirectional Transformers},
  author={Devlin, Jacob and Chang, Ming-Wei and Lee, Kenton and Toutanova, Kristina},
  journal={NAACL},
  year={2019}
}

@article{vaswani2017attention,
  title={Attention is All You Need},
  author={Vaswani, Ashish and others},
  journal={NeurIPS},
  year={2017}
}

@article{mihalcea2004textrank,
  title={TextRank: Bringing Order into Texts},
  author={Mihalcea, Rada and Tarau, Paul},
  journal={EMNLP},
  year={2004}
}

@article{lewis2020bart,
  title={BART: Denoising Sequence-to-Sequence Pre-training},
  author={Lewis, Mike and others},
  journal={ACL},
  year={2020}
}

@article{lafferty2001crf,
  title={Conditional Random Fields: Probabilistic Models for Segmenting and Labeling Sequence Data},
  author={Lafferty, John and McCallum, Andrew and Pereira, Fernando},
  journal={ICML},
  year={2001}
}
```

---

## Derleme

```bash
cd report/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

veya `latexmk`:

```bash
latexmk -pdf main.tex
```

---

## Iliskili Dokumanlar

- [Proje Genel Bakis](01-project-overview.md) - Proje scopu
- [Evaluation Framework](09-evaluation-framework.md) - Raporda sunulacak metrikler
- Her soru dokumani -> rapordaki karsiligi:
  - [Q1](04-q1-text-classification.md) -> `sections/q1.tex`
  - [Q2](05-q2-ner.md) -> `sections/q2.tex`
  - [Q3](06-q3-summarization.md) -> `sections/q3.tex`
  - [Q4](07-q4-machine-translation.md) -> `sections/q4.tex`
  - [Q5](08-q5-language-modeling.md) -> `sections/q5.tex`
