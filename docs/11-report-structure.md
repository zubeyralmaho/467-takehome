# 11 - LaTeX Report Structure

> [Home](README.md) | Previous: [Experiment Config](10-experiment-config.md)

---

## Overview

The report must be written in LaTeX. This document defines the report template, section structure, table/figure standards, and the mapping of each question to its report counterpart.

---

## Report Directory Structure

```
report/
|-- main.tex                   # Main file (includes all sections)
|-- preamble.tex               # Packages, settings, macros
|-- sections/
|   |-- introduction.tex       # Introduction, general approach
|   |-- q1.tex                 # Question 1
|   |-- q2.tex                 # Question 2
|   |-- q3.tex                 # Question 3
|   |-- q4.tex                 # Question 4
|   |-- q5.tex                 # Question 5
|   +-- conclusion.tex         # General conclusion and evaluation
|-- figures/                   # All figures
|   |-- q1/
|   |-- q2/
|   |-- q3/
|   |-- q4/
|   +-- q5/
|-- tables/                    # Large tables (optionally in separate files)
+-- references.bib             # Bibliography
```

---

## main.tex Template

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

## Section Structures

### introduction.tex

```
1. Introduction
   1.1 Scope and Objectives
       - Introduction to the 5 NLU tasks
       - General approach: classical vs neural vs transformer
   1.2 Technical Setup
       - Environment, libraries, reproducibility
       - Dataset summary table
   1.3 Report Organization
       - Contents of each section
```

---

### q1.tex - Representation Learning in Text Classification

Related architecture document: [Q1 Architecture](04-q1-text-classification.md)

```
2. Question 1: Representation Learning in Text Classification

   2.1 Dataset Description
       - IMDb dataset properties
       - Table: Dataset statistics (size, average length, class distribution)
       - Train/Val/Test split information

   2.2 Preprocessing Pipeline
       - Cleaning steps
       - Tokenization strategy comparison
       - Table: Preprocessing experiment results
         (effect of stopword removal, lowercasing, max_features)

   2.3 Models
       2.3.1 TF-IDF + Logistic Regression / SVM
           - Representation explanation
           - Hyperparameters
       2.3.2 BiLSTM
           - Architecture diagram
           - GloVe embeddings
           - Hyperparameters
       2.3.3 DistilBERT
           - Fine-tuning strategy
           - Hyperparameters

   2.4 Results
       - Table: Model comparison (Accuracy, Macro-F1)
       - Training curves (BiLSTM, DistilBERT)
       - Confusion matrices

   2.5 Error Analysis
       - Table of 5 misclassified examples
       - Common error patterns
       - Why were they misclassified?

   2.6 Discussion
       - Comparison of representation types
         (sparse vs dense vs contextual)
       - Performance vs interpretability trade-off
       - Key findings
```

---

### q2.tex - Named Entity Recognition

Related architecture document: [Q2 Architecture](05-q2-ner.md)

```
3. Question 2: Named Entity Recognition

   3.1 Dataset Description
       - CoNLL-2003 properties
       - BIO tagging explanation
       - Entity type distribution table/chart

   3.2 Preprocessing and BIO Alignment
       - CoNLL format explanation
       - BERT subword alignment method
       - CRF feature engineering

   3.3 Models
       3.3.1 CRF (Feature-based)
           - Feature set
           - Training method
       3.3.2 BiLSTM-CRF
           - Architecture diagram
           - Role of the CRF layer
       3.3.3 BERT Token Classification
           - Fine-tuning
           - Subword handling

   3.4 Results
       - Table: Overall P/R/F1
       - Table: Per-entity-type P/R/F1 (PER, ORG, LOC, MISC)

   3.5 Error Analysis
       - Boundary error examples
       - Entity confusion examples
       - Discussion on the contribution of contextual embeddings

   3.6 Discussion
       - CRF vs neural vs transformer
       - Importance of contextual information
```

---

### q3.tex - Text Summarization

Related architecture document: [Q3 Architecture](06-q3-summarization.md)

```
4. Question 3: Text Summarization

   4.1 Dataset Description
       - CNN/DailyMail properties
       - Subset size and selection method

   4.2 Methods
       4.2.1 TextRank (Extractive)
           - Algorithm explanation + diagram
           - Parameters
       4.2.2 BART (Abstractive)
           - Model explanation
           - Generation parameters

   4.3 Evaluation Metrics
       - ROUGE-1/2/L, BLEU, METEOR, BERTScore explanation
       - What each metric measures

   4.4 Results
       - Table: All metrics (TextRank vs BART)

   4.5 Qualitative Analysis
       - 3+ examples: source, reference, TextRank output, BART output
       - For each example: fluency, factual consistency, coverage analysis

   4.6 Discussion
       - Extractive vs abstractive trade-offs
       - Computational cost, readability, faithfulness
```

---

### q4.tex - Machine Translation

Related architecture document: [Q4 Architecture](07-q4-machine-translation.md)

```
5. Question 4: Machine Translation

   5.1 Dataset Description
       - Multi30k properties
       - Preprocessing steps

   5.2 Models
       5.2.1 Seq2Seq + Attention
           - Encoder-Decoder architecture diagram
           - Attention mechanism explanation
       5.2.2 Transformer
           - Self-attention + cross-attention
           - Positional encoding

   5.3 Evaluation Metrics
       - BLEU, METEOR, ChrF, BERTScore explanation
       - Focus of each metric

   5.4 Results
       - Table: All metrics (Seq2Seq vs Transformer)
       - Attention heatmap visualizations

   5.5 Qualitative Analysis
       - 3+ examples: source, reference, Seq2Seq output, Transformer output
       - Fluency, rare word handling, long-range dependency analysis

   5.6 Discussion
       - Analysis of metric dimensions (what each metric captures)
       - Architectural trade-offs (parallelization, long-range, speed)
```

---

### q5.tex - Language Modeling

Related architecture document: [Q5 Architecture](08-q5-language-modeling.md)

```
6. Question 5: Language Modeling

   6.1 Dataset Description
       - WikiText-2 properties

   6.2 Models
       6.2.1 N-gram (Trigram + Smoothing)
           - Model explanation
           - Smoothing method
       6.2.2 LSTM Language Model
           - Architecture details
           - Weight tying
       6.2.3 (Optional) GPT-2
           - Fine-tuning approach

   6.3 Results
       - Table: Perplexity comparison
       - Training curves

   6.4 Generated Text Samples
       - 2-3 examples from each model
       - Different temperature/sampling settings

   6.5 Discussion
       - Fluency and coherence analysis
       - Differences in model behavior
```

---

### conclusion.tex

```
7. Conclusion
   - Lessons learned across 5 tasks
   - Common themes: classical vs neural vs transformer
   - Why the best approach excelled in each task
   - Limitations and future work
```

---

## Table and Figure Standards

### Table Example

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

### Figure Example

```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.8\textwidth]{figures/q1/training_curves.png}
\caption{Training and validation loss curves for BiLSTM and DistilBERT.}
\label{fig:q1-training}
\end{figure}
```

### Qualitative Example

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

## Bibliography (references.bib) Examples

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

## Compilation

```bash
cd report/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

or using `latexmk`:

```bash
latexmk -pdf main.tex
```

---

## Related Documents

- [Project Overview](01-project-overview.md) - Project scope
- [Evaluation Framework](09-evaluation-framework.md) - Metrics to be presented in the report
- Each question document -> its report counterpart:
  - [Q1](04-q1-text-classification.md) -> `sections/q1.tex`
  - [Q2](05-q2-ner.md) -> `sections/q2.tex`
  - [Q3](06-q3-summarization.md) -> `sections/q3.tex`
  - [Q4](07-q4-machine-translation.md) -> `sections/q4.tex`
  - [Q5](08-q5-language-modeling.md) -> `sections/q5.tex`
