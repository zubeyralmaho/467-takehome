

CENG 467 – Natural Language Understanding and Generation
Take-Home Midterm Examination


Deadline: 30 Nisan 2026, 23:59	Type: Individual
Weight: 30%	Instructor: Prof. Dr. Aytug˘ Onan

Each student must submit a single archive named:
CENG467 Midterm <StudentID>.zip
The submission must include a structured report written in LATEX, along with fully reproducible code. The report should clearly describe the problem formulation, methodological decisions, experimental setup, evaluation process, and findings. All claims must be supported with appropriate tables, figures, and concise discussion. A repository link (GitHub / Colab) must be included.
Submission method: Send the midterm via email to aytugonan@iyte.edu.tr and upload it to the designated folder on Microsoft Teams. Both actions are required.
Submission Format and Deliverables
Each student must submit a single archive named:
CENG467 Midterm <StudentID>.zip
The submission must include a structured report written in LATEX, along with fully reproducible code. The report should clearly describe the problem formulation, methodological decisions, experimental setup, evaluation process, and findings. All claims must be supported with appropriate tables, figures, and concise discussion. A repository link (GitHub / Colab) must be included.
Submission method: Send the midterm via email to aytugonan@iyte.edu.tr and upload it to the designated folder on Microsoft Teams. Both actions are required.
Submission Format and Deliverables

Academic Integrity and Experimental Rules
All work must be strictly individual. Any external sources must be properly cited. All experiments must be reproducible, including clearly specified hyperparameters, random seeds, and environment configurations.
Students must use consistent dataset splits and preprocessing pipelines across models unless explicitly performing controlled comparisons. The test set must be used only once for final evaluation.
The objective of this midterm is not only to achieve high performance, but also to demonstrate a clear understanding of model behavior and limitations.

Midterm Questions

Question 1 – Representation Learning in Text Classification

Objective. To analyze how different representation learning strategies—sparse, dense, and contextual—affect classification performance and generalization.
Tasks.

	•	Select a benchmark dataset such as IMDb or SST-2 and briefly describe its key properties.
	•	Design a preprocessing pipeline and compare at least two tokenization strategies. Examine how preprocessing decisions such as normalization, stopword removal, and truncation influence model performance.
	•	Implement and compare at least three models: a classical model based on TF-IDF (Logistic Regression or SVM), a neural model such as BiLSTM, and a transformer-based model such as BERT or DistilBERT. All models must be trained under comparable conditions.
	•	Evaluate performance using Accuracy and Macro-F1. In addition to reporting results, analyze at least five misclassified examples and identify common error patterns.
	•	Provide a concise discussion comparing representation types in terms of performance and interpretability.

Question 2 – Named Entity Recognition

Objective. To examine sequence labeling and contextual modeling in named entity recognition.
Tasks.

	•	Use the CoNLL-2003 dataset and briefly describe its annotation structure. Implement BIO tagging and ensure correct alignment between tokens and labels.
	•	Implement and compare at least two modeling approaches, including one classical or hybrid model (CRF or BiLSTM-CRF) and one transformer-based model (BERT or similar). Train all models under consistent conditions.
	•	Evaluate performance using Precision, Recall, and F1-score. Analyze common error types such as boundary errors and entity confusion, and briefly discuss the role of contextual embeddings.

Question 3 – Text Summarization

Objective. To compare extractive and abstractive summarization methods.
Tasks.

	•	Use the CNN/DailyMail dataset (a subset is acceptable) and briefly describe its structure.

	•	Implement one extractive method (TextRank or LexRank) and one abstractive method (BART or T5).
	•	Evaluate summaries using a comprehensive set of metrics:
	•	ROUGE (ROUGE-1, ROUGE-2, ROUGE-L) for n-gram overlap,
	•	BLEU for translation-style precision,
	•	METEOR for alignment and synonym matching,
	•	BERTScore for contextual semantic similarity,
	•	Provide a small number of qualitative examples (at least three) and analyze differences in fluency, factual consistency, and information coverage between extractive and abstractive methods.
	•	Conclude with a brief discussion comparing extractive and abstractive approaches, highlighting trade-offs in computational cost, readability, and faithfulness to the source.

Question 4 – Machine Translation

Objective. To analyze sequence-to-sequence modeling and attention mechanisms.
Tasks.

	•	Use a dataset such as Multi30k and describe preprocessing steps.
	•	Implement a Seq2Seq model with attention and compare it with a Transformer-based model (or a pre-trained alternative).
	•	Evaluate translation quality using a multi-metric suite:
	•	BLEU (n-gram precision with brevity penalty),
	•	METEOR (aligns with synonymy and stemming),
	•	ChrF (character n-gram F-score, robust for morphologically rich languages),
	•	BERTScore for semantic similarity.
	•	Provide at least one qualitative example (source, reference, and both model outputs) and discuss differences in model behavior, fluency, and handling of rare words or long-range dependencies.
	•	Conclude with a brief analysis of how each metric reflects different aspects of translation quality, and discuss trade-offs between the two architectures.

Question 5 – Language Modeling

Objective. To investigate probabilistic sequence modeling and text generation.
Tasks.

	•	Use Penn Treebank or WikiText-2 dataset.
	•	Implement at least one sequence model (N-gram or LSTM) and optionally a transformer-based model.
	•	Evaluate using perplexity and generate short text samples. Analyze differences in fluency and coherence, and provide a brief discussion of model behavior.





End of Examination
