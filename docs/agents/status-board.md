# Agent Status Board

Last updated: 2026-04-13 23:57

This file is generated from `status.json`. Edit the JSON or use `scripts/agent_status.py`.

---

## Project Overview

| Area | Owner | Status | Notes |
|------|-------|--------|-------|
| Shared infrastructure | unassigned | in_progress | Initial config, seed, dataset split, metrics, export scaffold, shared evaluator, and confusion-matrix visualization helper are implemented; trainer and broader visualization slices remain |
| Q1 Text Classification | unassigned | in_progress | All finished Q1 model families now have matched 4k-train/2k-test comparison artifacts, a refreshed report summary under outputs/q1/run_20260413_185011, and a drafted q1.tex section included in the clean compiled report; further Q1 work is optional tuning or proofreading. |
| Q2 Named Entity Recognition | unassigned | in_progress | All three full-data Q2 runs are complete, BERT is the strongest finished model, a report-ready comparison summary exists under outputs/q2/run_20260413_151034, and q2.tex is included in the clean compiled report; further Q2 work is optional tuning or proofreading. |
| Q3 Summarization | unassigned | in_progress | TextRank and a capped distilBART comparison now exist under outputs/q3/run_20260413_192426, and report/sections/q3.tex now reflects that direct comparison; only larger-budget Q3 work remains separate. |
| Q4 Machine Translation | unassigned | in_progress | Both the pretrained transformer baseline and the stronger custom seq2seq+attention baseline are now implemented and compared in report-ready artifacts under outputs/q4/run_20260413_231508; future Q4 work should focus only on a more budget-aligned comparison. |
| Q5 Language Modeling | unassigned | in_progress | The trigram, matched LSTM, and practical distilgpt2 baselines now exist, refreshed three-model Q5 summary artifacts are ready under outputs/q5/run_20260413_214837, and q5.tex is included in the clean compiled report; future Q5 work should focus only on larger matched reruns or transformer fine-tuning if needed. |
| Evaluation and analysis | copilot-q1-eval | review | Shared Q1 evaluation now exports confusion-matrix data, CSVs, and PNG figures; broader reporting and comparison analysis remain separate slices |
| Report preparation | unassigned | in_progress | The report compiles successfully with Tectonic, now includes report-local Q3/Q4/Q5 comparison figures, and still builds cleanly with no TeX/BibTeX warnings. |
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
| Report build docs | copilot-report-docs | review | report/README.md now documents the scaffold layout, verified Tectonic compile path, section-to-artifact mapping, and the recommended report-writing workflow. |
| Q1 larger-budget comparison | copilot-q1-large-comparison | review | Matched 4k-train/2k-test Q1 comparison artifacts are complete under outputs/q1/run_20260413_152558, ranking DistilBERT ahead of TF-IDF + SVM, TF-IDF + LR, and BiLSTM on test macro-F1. |
| Q1 report draft | copilot-q1-writeup | review | report/sections/q1.tex plus report-local Q1 tables and figure assets reflect the stable 4k-train/2k-test artifacts and are now included in the successfully compiled Tectonic report. |
| Q1 report summary refresh | copilot-q1-summary-refresh | review | Refreshed Q1 summary artifacts were generated under outputs/q1/run_20260413_185011 using the matched 4k-train/2k-test comparison and the finished preprocessing sweep |
| Q3 TextRank baseline | copilot-q3-textrank | review | Self-contained extractive TextRank baseline plus lexical evaluation/export pipeline implemented and validated by the capped run under outputs/q3/run_20260413_185438. |
| Report introduction draft | copilot-report-intro | review | report/sections/introduction.tex and report/tables/introduction_task_overview.tex now describe the full five-task scope and current report organization, including the finished Q5 trigram-versus-LSTM-versus-GPT-style comparison. |
| Q3 report draft | copilot-q3-report-refresh | review | report/sections/q3.tex and report/tables/q3_overall_results.tex now reflect the capped direct TextRank-versus-DistilBART comparison artifact under outputs/q3/run_20260413_192426; larger-budget Q3 work remains optional follow-up. |
| Q3 BART baseline | copilot-q3-bart | review | Pretrained abstractive Q3 summarizer validated on CNN/DailyMail with a direct 20-validation/20-test comparison run under outputs/q3/run_20260413_192426, where distilBART outperformed TextRank on all exported lexical metrics. |
| Q5 N-gram baseline | copilot-q5-ngram | review | Self-contained trigram add-k language model validated on capped WikiText-2 under outputs/q5/run_20260413_202258 with validation/test perplexity 1392.54/1388.72 plus exported generation samples. |
| Q5 report summary | copilot-q5-report | review | Report-ready Q5 comparison artifacts now exist under outputs/q5/run_20260413_214837, covering the matched trigram, LSTM, and GPT-style runs with refreshed JSON, Markdown, and LaTeX outputs. |
| Q5 LSTM baseline | copilot-q5-lstm | review | Existing LSTM language-model path validated on capped WikiText-2 under outputs/q5/run_20260413_212022 with validation/test perplexity 269.12/259.97 plus exported generation samples. |
| Q5 report draft | copilot-q5-writeup | review | report/sections/q5.tex plus report/tables/q5_overall_results.tex now reflect the matched trigram-versus-LSTM-versus-GPT-style comparison sourced from outputs/q5/run_20260413_214837, while the later smaller LSTM rerun remains a separate reference artifact. |
| Q5 report summary refresh | copilot-q5-summary-gpt2-refresh | review | Refreshed Q5 summary artifacts were generated under outputs/q5/run_20260413_214837 using the matched trigram, LSTM, and GPT-style runs. |
| Q4 Transformer baseline | copilot-q4-transformer | review | Pretrained Helsinki-NLP/opus-mt-en-de baseline validated on capped Multi30k under outputs/q4/run_20260413_212828 with validation/test BLEU 0.4008/0.3572 and ChrF 0.6569/0.6380 plus exported translation predictions. |
| Report conclusion draft | copilot-report-conclusion | review | report/sections/conclusion.tex now synthesizes the drafted Q1/Q2/Q3/Q4/Q5 findings, including the direct Q4 comparison and the GPT-style Q5 reference, while later matched reruns remain optional refinements. |
| Q5 report draft refresh | copilot-q5-writeup-gpt2-refresh | review | report/sections/q5.tex, report/tables/q5_overall_results.tex, and report/README.md now reflect the matched trigram-versus-LSTM-versus-GPT-style comparison sourced from outputs/q5/run_20260413_214837. |
| Q5 GPT-2 baseline | copilot-q5-gpt2 | review | Practical distilgpt2 baseline validated on matched 3000/400/400 WikiText-2 splits under outputs/q5/run_20260413_213856 with validation/test perplexity 109.78/106.44 plus seeded generation samples. |
| Q4 report draft | copilot-q4-writeup-refresh | review | report/sections/q4.tex plus report/tables/q4_overall_results.tex now capture the direct transformer-versus-seq2seq comparison sourced from outputs/q4/run_20260413_231508 using the stronger seq2seq reference run. |
| Q4 Seq2Seq baseline | copilot-q4-seq2seq | review | Custom seq2seq+attention baseline validated on capped Multi30k, with the strongest current reference artifact at outputs/q4/run_20260413_214229 reaching validation/test BLEU 0.1284/0.1348 and ChrF 0.3491/0.3548 plus exported translation predictions. |
| Report framing refresh | copilot-report-refresh | review | report/sections/introduction.tex and report/sections/conclusion.tex now reflect the drafted Q3/Q4/Q5 sections and the current report-wide baseline/comparison state. |
| Report bibliography refresh | copilot-report-bib | review | Foundational dataset and model citations are now added across the drafted report sections, and report/references.bib is populated with the matching BibTeX entries. |
| Q4 report summary | copilot-q4-report | review | Report-ready comparison summary exported to outputs/q4/run_20260413_231508 from the tracker-approved transformer run and the stronger seq2seq run outputs/q4/run_20260413_214229 and outputs/q4/run_20260413_212828. |
| Report build validation | copilot-report-build | review | Installed Tectonic and compiled the full report successfully to PDF; the latest verified build is clean with no overfull-box warnings or TeX/BibTeX failures. |
| Report Q5 GPT refresh | copilot-report-q5-gpt-refresh | review | Q5 report framing, citations, and top-level report text now reflect the finished trigram-versus-LSTM-versus-distilGPT2 comparison without modifying active Q4 summary work. |
| Q4 report draft refresh | copilot-q4-writeup-bestseq-refresh | review | Q4 report section, report-local table, and README mapping were refreshed from outputs/q4/run_20260413_231508 after correcting the seq2seq source artifact to the stronger run_20260413_214229 reference. |
| Report layout cleanup | copilot-report-layout | review | Wrapped the wide report tables with tabularx, reflowed the remaining dense prose paragraphs, added a conservative emergencystretch in the preamble, and verified a clean Tectonic build with no remaining overfull-box warnings. |
| Report build docs refresh | copilot-report-docs-refresh | review | report/README.md now reflects the verified Tectonic-based PDF build instead of the older unverified compile guidance. |
| Q4 report consistency refresh | copilot-q4-consistency | review | Regenerated the Q4 comparison summary and refreshed report files so they now use the tracker-approved stronger seq2seq artifact under outputs/q4/run_20260413_214229 instead of the weaker older report pair. |
| Report layout regression cleanup | copilot-report-layout-refresh | review | Removed the duplicated Q2 results sentence, tightened the remaining warning-producing report prose and tables, and revalidated a clean Tectonic build. |
| Report comparison figures | copilot-report-figures | review | Added a reproducible figure generator for Q3/Q4/Q5, rendered report-local comparison figures from the stable summary artifacts, wired them into the drafted sections, and revalidated a clean Tectonic build. |
| Report state sync refresh | copilot-report-state-sync | review | Tracker priorities, handoff guidance, and report README next steps now reflect the current clean compiled report and the settled canonical Q1/Q4/Q5 artifact paths. |
| Tracker consistency refresh | copilot-tracker-refresh | review | Stale Q5 refresh states, top-level priorities, and handoff guidance were refreshed so docs/agents now matches the current clean-build report state and canonical comparison artifacts. |
| Report proofread pass | copilot-report-proofread | review | A lightweight proofread of the clean compiled PDF found no obvious content or bibliography rendering problems, and the title-page student ID placeholder has now been replaced in both source and compiled output. |
| Report submission metadata | copilot-report-metadata | review | report/main.tex now contains the final student ID and the report PDF was rebuilt successfully with Tectonic. |

---

## Current Priorities

1. Do a final manual proofreading pass on the clean compiled PDF before submission.
2. Only reopen Q3, Q4, or Q5 if stronger budget-aligned evidence is actually required for the final submission.
3. Keep docs/agents and report/README aligned with the current compiled report whenever future edits land.

---

## Open Blockers

- None recorded yet.

---

## Update Rules

- Use `status.json` as the single source of truth.
- Regenerate this board with `python scripts/agent_status.py sync` after manual JSON edits.
- Detailed agent notes are rendered into `active/*.md`.
