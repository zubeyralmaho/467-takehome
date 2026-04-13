# Agent Status Board

Last updated: 2026-04-13 21:44

This file is generated from `status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Project Overview

| Area | Owner | Status | Notes |
|------|-------|--------|-------|
| Shared infrastructure | unassigned | in_progress | Initial config, seed, dataset split, metrics, export scaffold, shared evaluator, and confusion-matrix visualization helper are implemented; trainer and broader visualization slices remain |
| Q1 Text Classification | unassigned | in_progress | All finished Q1 model families now have matched 4k-train/2k-test comparison artifacts and a refreshed report summary; the remaining open work is report drafting |
| Q2 Named Entity Recognition | unassigned | in_progress | All three full-data Q2 runs are complete, BERT is the strongest finished model, and a report-ready comparison summary now exists under outputs/q2/run_20260413_151034 |
| Q3 Summarization | unassigned | in_progress | TextRank and a capped distilBART comparison now exist under outputs/q3/run_20260413_192426, and report/sections/q3.tex now reflects that direct comparison; only larger-budget Q3 work remains separate. |
| Q4 Machine Translation | unassigned | in_progress | Pretrained transformer and seq2seq+attention baselines now exist under outputs/q4/run_20260413_212828 and outputs/q4/run_20260413_214229; Q4 comparison/reporting remains the next clean follow-up. |
| Q5 Language Modeling | unassigned | in_progress | The trigram baseline under outputs/q5/run_20260413_202258, a matched 3000/400/400 LSTM comparison artifact under outputs/q5/run_20260413_211945, and a later smaller LSTM rerun under outputs/q5/run_20260413_212022 now exist; refreshed Q5 comparison summary artifacts are ready under outputs/q5/run_20260413_212315. |
| Evaluation and analysis | copilot-q1-eval | review | Shared Q1 evaluation now exports confusion-matrix data, CSVs, and PNG figures; broader reporting and comparison analysis remain separate slices |
| Report preparation | unassigned | in_progress | A minimal LaTeX scaffold now exists under report/, Q1/Q2/Q3/Q4/Q5 sections plus the introduction and conclusion are drafted from stable artifacts, and report/README.md documents the current artifact mapping; compilation still awaits a LaTeX toolchain. |
| Project state sync | copilot-tracker | done | docs/agents state synced with the implemented Q1 baseline and scaffold |
| Q2 CRF baseline | copilot-q2-crf | done | Self-contained CoNLL CRF baseline implemented and validated on a capped run; any larger-budget experiment can now be claimed as a separate slice |
| Q2 CRF experiment | copilot-q2-crf | done | Full-split CRF experiment completed with exported validation/test artifacts under outputs/q2/run_20260413_141702 |
| Q1 DistilBERT baseline | copilot-q1-distilbert | done | DistilBERT baseline path is implemented and validated by the larger-budget run under outputs/q1/run_20260413_151402; comparison work remains separate |
| Q2 BiLSTM-CRF baseline | copilot-q2-bilstm-crf | done | BiLSTM-CRF path is implemented and validated by the full-data run under outputs/q2/run_20260413_144913; any further optimization is a separate slice |
| Q2 BERT baseline | copilot-q2-bert | done | Self-contained BERT token-classification baseline is implemented and now validated by the larger-budget run under outputs/q2/run_20260413_144742 |
| Q1 visualization | copilot-q1-visualization | review | Shared confusion-matrix figure export is implemented and validated on Q1; training curves and model-comparison figures remain separate visualization slices |
| Q2 BERT experiment | copilot-q2-bert-experiment | done | Full-split 2-epoch BERT experiment completed under outputs/q2/run_20260413_144742 and outperformed the CRF baseline on validation/test F1 (0.9517/0.9062 vs 0.8765/0.7948) |
| Q2 BiLSTM-CRF experiment | copilot-q2-bilstm-crf-experiment | done | Full-split BiLSTM-CRF experiment completed with exported validation/test artifacts under outputs/q2/run_20260413_144913; current test F1 0.714 trails the CRF baseline |
| Q1 model comparison | copilot-q1-comparison | review | Matched Q1 smoke-test comparison artifacts were generated under outputs/q1/run_20260413_145244; larger-budget comparison remains a separate slice |
| Q1 preprocessing comparison | copilot-q1-preprocessing | review | The documented TF-IDF+LR preprocessing sweep is implemented and exported under outputs/q1/run_20260413_145735; the current lowercase+keep-stopwords default already matches the best validation setting |
| Q1 report summary | copilot-q1-report | review | Report-ready Q1 summary artifacts were refreshed under outputs/q1/run_20260413_185011 from the stable larger-budget comparison and preprocessing runs |
| Q2 report summary | copilot-q2-report | review | Report-ready Q2 summary artifacts were generated under outputs/q2/run_20260413_151034 from the completed CRF, BiLSTM-CRF, and BERT full-data runs |
| Q2 model comparison | copilot-q2-comparison | review | Report-ready Q2 comparison artifacts were generated under outputs/q2/run_20260413_151143, ranking BERT ahead of the CRF baseline and BiLSTM-CRF on overall and per-entity test F1 |
| Q1 DistilBERT experiment | copilot-q1-distilbert-experiment | done | Larger-budget DistilBERT experiment completed under outputs/q1/run_20260413_151402; validation/test macro-F1 0.875/0.879 on the 4k-train/2k-test run and no one-class collapse |
| Q2 report draft | copilot-q2-writeup | review | A minimal report scaffold now exists and q2.tex is drafted from the completed Q2 summary artifacts, including report-local tables and the entity-F1 comparison figure |
| Q1 BiLSTM experiment | copilot-q1-bilstm-experiment | review | Matched 4000-train/2000-test BiLSTM final-eval run completed under outputs/q1/run_20260413_151549 with validation/test macro-F1 0.7386/0.7011 for later Q1 comparison |
| Report build docs | copilot-report-docs | review | report/README.md now documents the scaffold layout, compile prerequisites, section-to-artifact mapping, and the recommended report-writing workflow |
| Q1 larger-budget comparison | copilot-q1-large-comparison | review | Matched 4k-train/2k-test Q1 comparison artifacts are complete under outputs/q1/run_20260413_152437, ranking DistilBERT ahead of TF-IDF + SVM, TF-IDF + LR, and BiLSTM on test macro-F1 |
| Q1 report draft | copilot-q1-writeup | review | report/sections/q1.tex plus report-local Q1 tables and figure assets now reflect the stable 4k-train/2k-test Q1 artifacts; PDF compilation remains pending because no LaTeX toolchain is installed |
| Q1 report summary refresh | copilot-q1-summary-refresh | review | Refreshed Q1 summary artifacts were generated under outputs/q1/run_20260413_185011 using the matched 4k-train/2k-test comparison and the finished preprocessing sweep |
| Q3 TextRank baseline | copilot-q3-textrank | review | Self-contained extractive TextRank baseline plus lexical evaluation/export pipeline implemented and validated by the capped run under outputs/q3/run_20260413_185438. |
| Report introduction draft | copilot-report-intro | review | report/sections/introduction.tex and report/tables/introduction_task_overview.tex now describe the full five-task scope and current report organization, including drafted Q3/Q4/Q5 sections and provisional later extensions. |
| Q3 report draft | copilot-q3-report-refresh | review | report/sections/q3.tex and report/tables/q3_overall_results.tex now reflect the capped direct TextRank-versus-DistilBART comparison artifact under outputs/q3/run_20260413_192426; larger-budget Q3 work remains optional follow-up. |
| Q3 BART baseline | copilot-q3-bart | review | Pretrained abstractive Q3 summarizer validated on CNN/DailyMail with a direct 20-validation/20-test comparison run under outputs/q3/run_20260413_192426, where distilBART outperformed TextRank on all exported lexical metrics. |
| Q5 N-gram baseline | copilot-q5-ngram | review | Self-contained trigram add-k language model validated on capped WikiText-2 under outputs/q5/run_20260413_202258 with validation/test perplexity 1392.54/1388.72 plus exported generation samples. |
| Q5 report summary | copilot-q5-report | review | Baseline-only Q5 summary artifacts were generated under outputs/q5/run_20260413_211754 from the finished trigram n-gram run and include perplexity plus generation-analysis exports |
| Q5 LSTM baseline | copilot-q5-lstm | review | Existing LSTM language-model path validated on capped WikiText-2 under outputs/q5/run_20260413_212022 with validation/test perplexity 269.12/259.97 plus exported generation samples. |
| Q5 report draft | copilot-q5-writeup | review | report/sections/q5.tex plus report/tables/q5_overall_results.tex now reflect the matched trigram-versus-LSTM comparison sourced from outputs/q5/run_20260413_212315, while the later smaller LSTM rerun remains a separate reference artifact. |
| Q5 report summary refresh | copilot-q5-summary-refresh | review | Refreshed Q5 summary artifacts were generated under outputs/q5/run_20260413_212315 from the matched trigram and LSTM runs at outputs/q5/run_20260413_202258 and outputs/q5/run_20260413_211945, and the builder now rejects mismatched split budgets for direct comparisons. |
| Q4 Transformer baseline | copilot-q4-transformer | review | Pretrained Helsinki-NLP/opus-mt-en-de baseline validated on capped Multi30k under outputs/q4/run_20260413_212828 with validation/test BLEU 0.4008/0.3572 and ChrF 0.6569/0.6380 plus exported translation predictions. |
| Report conclusion draft | copilot-report-conclusion | review | report/sections/conclusion.tex now synthesizes the drafted Q1/Q2/Q3/Q4/Q5 findings, treating Q4 as a baseline-first section and the overall conclusion as provisional where later comparisons may still extend the report. |
| Q5 report draft refresh | copilot-q5-writeup-refresh | review | Refreshed the Q5 report section, local table, and report README mapping from the matched trigram-versus-LSTM summary artifact under outputs/q5/run_20260413_212315 without reopening model-training ownership. |
| Q5 GPT-2 baseline | copilot-q5-gpt2 | in_progress | Implementing a practical GPT-2 Q5 baseline on top of the existing language-modeling package so Question 5 can include a transformer-style comparison beyond the matched trigram-versus-LSTM result. |
| Q4 report draft | copilot-q4-writeup | review | report/sections/q4.tex plus report/tables/q4_overall_results.tex now capture the stable pretrained transformer baseline artifact under outputs/q4/run_20260413_212828; any seq2seq comparison remains separate. |
| Q4 Seq2Seq baseline | copilot-q4-seq2seq | review | Compact GRU seq2seq+attention baseline validated on capped Multi30k under outputs/q4/run_20260413_214229 with validation/test BLEU 0.1284/0.1348 and ChrF 0.3491/0.3548 plus exported translation predictions. |
| Report framing refresh | copilot-report-refresh | review | report/sections/introduction.tex and report/sections/conclusion.tex now reflect the drafted Q3/Q4/Q5 sections and the current report-wide baseline/comparison state. |
| Report bibliography refresh | copilot-report-bib | in_progress | Adding foundational dataset/model citations to the drafted report sections and populating report/references.bib without touching active modeling slices. |

---

## Current Priorities

1. Use the finished larger-budget Q1 artifacts and refreshed summary to complete the Q1 report prose, tables, and figures.
2. Use the finished Q2 artifacts and the new report scaffold to turn Q2 into final report prose, tables, and figures.
3. Turn the exported Q1 and Q2 artifacts into report-ready analysis, tables, and visualizations.

---

## Open Blockers

- None recorded yet.

---

## Update Rules

- Use `status.json` as the single source of truth.
- Regenerate this board with `python scripts/agent_status.py sync` after manual JSON edits.
- Detailed agent notes are rendered into `active/*.md`.
