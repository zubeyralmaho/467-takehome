# Notebook Alignment ve Colab Planı — CENG 467 Take-Home

Bu doküman eski “full Colab execution plan” belgesinin yerine geçer.

Amaç artık yalnızca notebook çalıştırma sırası vermek değildir. Yeni amaç:

1. notebook'ların mevcut repo ve report durumuna göre rolünü netleştirmek,
2. notebook–artifact–report drift'ini açıkça kaydetmek,
3. bu uyumsuzlukları agent'lara bölünebilir dar task'lere çevirmektir.

## 1. Canonical Sınırlar

Mevcut projede notebook'lar artık tek başına kaynak gerçeklik değildir. Aşağıdaki sınırlar kullanılmalıdır:

| Alan | Canonical kaynak | Notebook rolü |
|------|------------------|---------------|
| Model implementasyonu | `src/` ve `configs/` | Sadece orkestrasyon ve deney çalıştırma |
| Deney çıktıları | `outputs/q*/run_*` | Çıktı üretir veya yeniden üretir |
| Report-facing karşılaştırmalar | summary/comparison artifact'leri ve `report/README.md` | Bu artifact'leri yeniden üretmeye yardım eder |
| Final anlatı ve figürler | `report/sections/*`, `report/tables/*`, `report/figures/*` | Gerekirse bu zinciri tetikler, kendisi source of truth değildir |
| Operasyonel durum | `docs/agents/status.json` | Hangi notebook refresh işinin açık olduğunu gösterir |

Sonuç: notebook'lar “canonical report state” üretmiyorsa exploratory olarak etiketlenmelidir; canonical gibi sunulmamalıdır.

## 2. Genel Drift Kategorileri

Notebook'ların mevcut repo/report durumundan kopan kısımları birkaç ortak başlıkta toplanıyor.

### 2.1 Colab-Only Bootstrap Drift

- Tüm notebook'lar `google.colab`, Drive mount ve `/content/...` yol yapısına kilitli.
- Repo ise artık lokal artifact, summary script ve temiz Tectonic build etrafında oturuyor.
- Bu yüzden notebook'lar şu an “portable project notebook” değil, “Colab runbook” gibi davranıyor.

### 2.2 Raw Run vs Report Artifact Drift

- Notebook akışları doğrudan ham `outputs/q*/run_*` klasörleri üretip Drive'a kopyalıyor.
- Oysa current report çoğu yerde ham run klasörüne değil, comparison/summary artifact'ine dayanıyor.
- Özellikle Q3, Q4 ve Q5 tarafında notebook çalıştırmak tek başına report refresh için yeterli değil.

### 2.3 Latest-Run Heuristic Drift

- Tüm notebook'larda `sorted(glob.glob('outputs/qN/run_*'))[-1]` kalıbı kullanılıyor.
- Bu yaklaşım birden fazla paralel run veya tekrar deneme olduğunda yanlış klasörün kopyalanmasına yol açabilir.
- Canonical report state için bu kırılgan bir yöntemdir.

### 2.4 Dataset Budget Drift

- Q1, Q3, Q4 ve Q5 notebook varsayılanları ile report'ta kullanılan canonical split/budget aynı değil.
- Bu yüzden notebook çıktısı “başarılı run” olsa bile report'taki iddiayı doğrudan desteklemeyebilir.

### 2.5 Missing Report Refresh Hooks

- Q3, Q4 ve Q5 report'u summary artifact'leri ve report-local figür zinciri ile besleniyor.
- Notebook'larda bu zinciri tetikleyen açık summary / figure regeneration adımları yok.

### 2.6 Stale Markdown Intent Drift

- Bazı notebook markdown hücreleri artık report'ta kullanılan gerçek state ile çelişiyor.
- En kritik örnekler: Q2'de agresif BiLSTM-CRF hedef ifadesi, Q3'te Lead-3 ağırlıklı framing, Q4 ve Q5'te full-data varsayımları.

## 3. Notebook Bazlı Audit

### Q1 — `Q1_Classification.ipynb`

**Notebook varsayılanı**
- Full IMDb üzerinden TF-IDF, BiLSTM ve DistilBERT sıralı Colab çalıştırması.
- Her model sonrası en son `run_*` klasörünü Drive'a kopyalama.

**Current canonical state**
- Report, matched 4k/2k comparison artifact'lerine ve preprocessing summary zincirine dayanıyor.
- Ana referanslar: `outputs/q1/run_20260413_152558` ve `outputs/q1/run_20260413_185011`.

**Drift**
- Notebook tam veri/full Colab akışını default yapıyor; report ise capped matched comparison kullanıyor.
- Preprocessing comparison ve report-summary yenileme akışı notebook'ta yok.
- Notebook çıktısı report'a doğrudan bağlanmıyor.

**Sonuç etiketi**
- Kısmen uyumlu ama stale. Varsayılan canonical notebook değil.

### Q2 — `Q2_NER.ipynb`

**Notebook varsayılanı**
- Full CoNLL-2003 üzerinde CRF, BiLSTM-CRF ve BERT çalıştırması.

**Current canonical state**
- Report Q2 tam-data artifact'leri ve comparison figure zinciri ile uyumlu.
- Ana referanslar: `outputs/q2/run_20260413_151034`, `outputs/q2/run_20260413_151143`, `figures/q2/entity_f1_comparison.png`.

**Drift**
- Markdown içinde BiLSTM-CRF için “target: 0.85+” gibi artık bitmiş sonuçlarla uyuşmayan beklenti var.
- Q2 comparison summary ve report-facing figure üretimi notebook'a bağlanmıyor.
- Teknik akış büyük ölçüde uygun olsa da report yenileme zinciri eksik.

**Sonuç etiketi**
- En yakın uyumlu notebook, ama anlatı ve report integration tarafı stale.

### Q3 — `Q3_Summarization.ipynb`

**Notebook varsayılanı**
- Lead-3 + TextRank + BART/DistilBART, 10k/1k/1k düzeyinde daha geniş bir Colab akışı.

**Current canonical state**
- Report artık doğrudan capped TextRank vs DistilBART comparison state'ine dayanıyor.
- Ana referans: `outputs/q3/run_20260413_192426`.

**Drift**
- Lead-3 hâlâ notebook framing'inde merkezde; report'ta canonical karşılaştırmanın parçası değil.
- Dataset bütçesi ve decode ayarları current report state ile bire bir hizalı değil.
- Summary artifact ve report figure refresh adımı yok.

**Sonuç etiketi**
- Yüksek drift. Varsayılan yol canonical report Q3 state'ini üretmiyor.

### Q4 — `Q4_MachineTranslation.ipynb`

**Notebook varsayılanı**
- Full Multi30k / uncapped seq2seq training ve uncapped transformer inference.
- Seq2Seq için daha ağır ve farklı hiperparametre seti.

**Current canonical state**
- Report, approved capped comparison zincirini kullanıyor.
- Ana referanslar: `outputs/q4/run_20260413_212828`, `outputs/q4/run_20260413_214229`, `outputs/q4/run_20260413_231508`.

**Drift**
- Notebook “full dataset” anlatısı ile report'taki capped evaluation state çelişiyor.
- Notebook canonical Q4 summary artifact'ini üretmiyor.
- Notebook'tan report'a uzanan comparison-summary refresh zinciri eksik.

**Sonuç etiketi**
- Çok yüksek drift. Varsayılan yol current Q4 report state ile uyumsuz.

### Q5 — `Q5_LanguageModeling.ipynb`

**Notebook varsayılanı**
- Full WikiText-2 / uncapped trigram, LSTM ve GPT-2 akışı.
- LSTM için current report'taki canonical matched run'dan daha ağır ayarlar.

**Current canonical state**
- Report, matched 3000/400/400 trigram–LSTM–distilGPT2 comparison zincirini kullanıyor.
- Ana referanslar: `outputs/q5/run_20260413_202258`, `outputs/q5/run_20260413_211945`, `outputs/q5/run_20260413_213856`, `outputs/q5/run_20260413_214837`.

**Drift**
- Notebook null sample caps ile full-data varsayımına gidiyor; report matched capped comparison kullanıyor.
- Notebook canonical Q5 summary artifact'ini üretmiyor.
- Q5 report-local comparison figure zinciri notebook akışında yok.

**Sonuç etiketi**
- Çok yüksek drift. Varsayılan yol current Q5 report state ile uyumsuz.

## 4. Karar Ayrımları

Notebook refresh sürecinde aşağıdaki ayrımlar korunmalıdır.

### 4.1 Canonical vs Exploratory

- **Canonical notebook path**: current report'ta kullanılan artifact zincirini yeniden üreten varsayılan yol.
- **Exploratory notebook path**: daha büyük bütçeli, alternatif veya opsiyonel run; report için default kabul edilmez.

### 4.2 Model Code vs Notebook Code

- Yeni model veya düzeltme gerekiyorsa önce `src/` ve `configs/` tarafında yapılmalı.
- Notebook hücreleri sadece mevcut pipeline'ı çağırmalı ve rapor zincirine bağlamalı.

### 4.3 Raw Runs vs Summaries

- Report ile ilişkili notebook'lar sadece ham run üretmekle kalmamalı.
- Gerekli ise comparison/summary script'lerini ve figür regeneration adımlarını da tetiklemeli.

### 4.4 Local Repo vs Remote Clone

- Submission'a yakın durumda notebook'lar uzak repo HEAD'e kör bağımlı olmamalı.
- Hedef, notebook'u mevcut workspace state ile uyumlu hale getirmek; rastgele yeni remote state çekmek değil.

## 5. Agent'lara Bölünebilir Task Planı

Aşağıdaki task'ler dar kapsamlı claim'ler olarak dağıtılabilir.

| Task key | Amaç | Ana dosyalar | Öncelik | Bağımlılık |
|----------|------|--------------|---------|------------|
| `notebook_shared_workflow_refresh` | Tüm notebook'larda ortak Colab/bootstrap/output mantığını güncellemek | `notebooks/*.ipynb`, `notebooks/README.md` | Çok yüksek | Yok |
| `notebooks_readme_sync` | Notebook README'yi canonical vs exploratory akışlarla hizalamak | `notebooks/README.md` | Yüksek | `notebook_shared_workflow_refresh` ile paralel olabilir |
| `q1_notebook_report_alignment` | Q1 notebook'u matched Q1 artifact/report state ile hizalamak | `notebooks/Q1_Classification.ipynb` | Orta | Shared workflow sonrası |
| `q2_notebook_report_alignment` | Q2 notebook'taki stale anlatım ve report hook eksiklerini kapatmak | `notebooks/Q2_NER.ipynb` | Orta | Shared workflow sonrası |
| `q3_notebook_canonical_rewrite` | Q3 notebook varsayılan yolunu direct capped comparison state'e çevirmek | `notebooks/Q3_Summarization.ipynb` | Çok yüksek | Shared workflow sonrası |
| `q4_notebook_canonical_rewrite` | Q4 notebook'u approved capped comparison state ile hizalamak | `notebooks/Q4_MachineTranslation.ipynb` | Çok yüksek | Shared workflow sonrası |
| `q5_notebook_canonical_rewrite` | Q5 notebook'u matched 3000/400/400 comparison state ile hizalamak | `notebooks/Q5_LanguageModeling.ipynb` | Çok yüksek | Shared workflow sonrası |
| `notebook_to_report_integration_hooks` | Summary script ve report figure refresh adımlarını notebook zincirine eklemek | `notebooks/Q3_*.ipynb`, `notebooks/Q4_*.ipynb`, `notebooks/Q5_*.ipynb`, `notebooks/README.md` | Yüksek | Q3/Q4/Q5 rewrite'ları sonrası |

## 6. Claim-Ready Brief'ler

Bu bölümdeki metinler başka bir agent'a doğrudan brief olarak verilebilir.

Her brief için aynı çerçeve kullanılmalıdır:

- **Scope**: yapılacak dar iş
- **Primary files**: agent'ın sahip çıkacağı ana dosyalar
- **Non-goals**: özellikle dokunmaması gereken alanlar
- **Validation**: işin hangi kontrol ile tamamlandığı
- **First action**: agent'ın ilk yapacağı somut adım

### `notebook_shared_workflow_refresh`

**Önerilen agent adı**
- `copilot-notebook-shared`

**Primary files**
- `notebooks/Q1_Classification.ipynb`
- `notebooks/Q2_NER.ipynb`
- `notebooks/Q3_Summarization.ipynb`
- `notebooks/Q4_MachineTranslation.ipynb`
- `notebooks/Q5_LanguageModeling.ipynb`
- `notebooks/README.md`

**Non-goals**
- `src/` içindeki model mantığını değiştirmek
- report prose veya report artifact içeriklerini güncellemek

**Validation**
- Notebook JSON yapısı bozulmamalı
- Ortak setup/output hücreleri tüm notebook'larda tutarlı hale gelmeli
- Kırılgan `latest_run` yakalama mantığı azaltılmalı veya açıkça etiketlenmeli

**First action**
- Beş notebook'un setup, clone/pull, pip install ve output copy hücrelerini yan yana karşılaştır

**Kopyala-yapıştır brief**

```text
Task key: notebook_shared_workflow_refresh
Scope: Refresh the shared Colab/bootstrap/output workflow across all notebooks so they no longer drift from the current repo/report workflow.
Primary files: notebooks/Q1_Classification.ipynb, notebooks/Q2_NER.ipynb, notebooks/Q3_Summarization.ipynb, notebooks/Q4_MachineTranslation.ipynb, notebooks/Q5_LanguageModeling.ipynb, notebooks/README.md.
Non-goals: Do not change model logic in src/ or rewrite report prose.
Validation: Notebook structure remains valid JSON, common setup cells are consistent, and output capture is less dependent on blindly copying the last run directory.
First action: Audit the shared setup and output-copy cells across all five notebooks and normalize them into one consistent pattern.
```

### `notebooks_readme_sync`

**Önerilen agent adı**
- `copilot-notebooks-readme`

**Primary files**
- `notebooks/README.md`

**Non-goals**
- Notebook hücrelerini değiştirmek
- Report veya `src/` kodunu düzenlemek

**Validation**
- README canonical vs exploratory ayrımını açıkça söylüyor olmalı
- README notebook çalıştırma ile report refresh arasındaki ilişkiyi yanlış temsil etmemeli

**First action**
- `notebooks/README.md` ile `docs/colab-plan.md` içindeki canonical sınırları hizala

**Kopyala-yapıştır brief**

```text
Task key: notebooks_readme_sync
Scope: Rewrite notebooks/README.md so it explains which notebook paths are canonical for the current report state and which are exploratory only.
Primary files: notebooks/README.md.
Non-goals: Do not edit notebook cells or model code.
Validation: A user reading notebooks/README.md can tell which notebooks feed the final report state and what extra summary/report steps are still required after notebook runs.
First action: Compare notebooks/README.md against docs/colab-plan.md and update the README to match the documented canonical boundaries.
```

### `q1_notebook_report_alignment`

**Önerilen agent adı**
- `copilot-q1-notebook-align`

**Primary files**
- `notebooks/Q1_Classification.ipynb`

**Non-goals**
- Q1 model code veya report section içeriğini değiştirmek
- Yeni Q1 experiment claim'i üretmek

**Validation**
- Notebook default akışı current Q1 report state ile ilişkisini açıkça belirtmeli
- Full IMDb yolu korunuyorsa exploratory olarak etiketlenmeli

**First action**
- Q1 notebook markdown ve komutlarını `report/README.md` içindeki Q1 canonical artifact zinciri ile karşılaştır

**Kopyala-yapıştır brief**

```text
Task key: q1_notebook_report_alignment
Scope: Align the Q1 notebook with the current matched 4k/2k comparison and preprocessing-summary report state, or clearly mark the full-IMDb path as exploratory.
Primary files: notebooks/Q1_Classification.ipynb.
Non-goals: Do not reopen Q1 model training code or rewrite report/sections/q1.tex.
Validation: The notebook's default path is clearly connected to the current Q1 report artifacts, or the heavier path is explicitly marked as exploratory.
First action: Compare the notebook's default run sequence against the canonical Q1 artifacts listed in report/README.md.
```

### `q2_notebook_report_alignment`

**Önerilen agent adı**
- `copilot-q2-notebook-align`

**Primary files**
- `notebooks/Q2_NER.ipynb`

**Non-goals**
- Q2 model tuning yapmak
- Q2 report proseunu yeniden yazmak

**Validation**
- Stale hedef ifadeleri kaldırılmış olmalı
- Notebook Q2 comparison/report figure zincirine nasıl bağlandığını göstermeli

**First action**
- Q2 markdown hücrelerinde stale performans beklentilerini ve missing summary hooks'ları işaretle

**Kopyala-yapıştır brief**

```text
Task key: q2_notebook_report_alignment
Scope: Remove stale expectations from the Q2 notebook and connect it to the current Q2 comparison-summary and report-figure workflow.
Primary files: notebooks/Q2_NER.ipynb.
Non-goals: Do not retune Q2 models or rewrite the report prose.
Validation: The notebook no longer misstates the expected BiLSTM-CRF outcome and it shows how its outputs relate to the current Q2 comparison/report chain.
First action: Audit the Q2 markdown cells for stale performance claims and compare the current notebook flow to the Q2 artifacts used in report/README.md.
```

### `q3_notebook_canonical_rewrite`

**Önerilen agent adı**
- `copilot-q3-notebook-rewrite`

**Primary files**
- `notebooks/Q3_Summarization.ipynb`

**Non-goals**
- Yeni Q3 model implementasyonu yapmak
- Q3 report anlatısını yeniden tartışmak

**Validation**
- Notebook varsayılanı direct capped TextRank vs DistilBART comparison olmalı
- Lead-3 varsa exploratory/optional yol olarak ayrılmalı

**First action**
- Q3 notebook'un default markdown framing'ini ve override setlerini current capped comparison state ile hizala

**Kopyala-yapıştır brief**

```text
Task key: q3_notebook_canonical_rewrite
Scope: Rewrite the Q3 notebook so the default path reproduces the current capped TextRank-versus-DistilBART comparison instead of the older broader Lead-3-centered Colab plan.
Primary files: notebooks/Q3_Summarization.ipynb.
Non-goals: Do not implement new summarization models or reopen the final Q3 report narrative.
Validation: The notebook's default run path matches the current Q3 report comparison state, and any larger-budget or Lead-3 path is clearly marked exploratory.
First action: Compare the notebook's current default split sizes and decode settings to the Q3 artifact and report state recorded in report/README.md.
```

### `q4_notebook_canonical_rewrite`

**Önerilen agent adı**
- `copilot-q4-notebook-rewrite`

**Primary files**
- `notebooks/Q4_MachineTranslation.ipynb`

**Non-goals**
- Q4 seq2seq veya transformer model code'unu değiştirmek
- Yeni report claim üretmek

**Validation**
- Default akış approved capped Q4 comparison state ile uyumlu olmalı
- Full Multi30k/full-budget anlatımı varsa exploratory dala taşınmalı

**First action**
- Notebook'taki uncapped Q4 varsayımlarını current approved Q4 artifact zinciri ile yan yana koy

**Kopyala-yapıştır brief**

```text
Task key: q4_notebook_canonical_rewrite
Scope: Rewrite the Q4 notebook so its default path matches the approved capped transformer-versus-seq2seq comparison used by the report, rather than the older full-Multi30k plan.
Primary files: notebooks/Q4_MachineTranslation.ipynb.
Non-goals: Do not modify Q4 model code in src/ or change the current report claims.
Validation: The default notebook path aligns with the approved Q4 summary artifact chain, and any uncapped/full-data path is clearly marked exploratory.
First action: Audit the Q4 notebook's split assumptions and overrides against the Q4 artifact mapping in report/README.md.
```

### `q5_notebook_canonical_rewrite`

**Önerilen agent adı**
- `copilot-q5-notebook-rewrite`

**Primary files**
- `notebooks/Q5_LanguageModeling.ipynb`

**Non-goals**
- Yeni Q5 model implementasyonu veya tuning yapmak
- Report conclusion/prose kısmını değiştirmek

**Validation**
- Default akış matched 3000/400/400 trigram–LSTM–distilGPT2 comparison'ı üretmeli
- Full-data/null-cap yol varsa exploratory olarak ayrılmalı

**First action**
- Q5 notebook'un current null-cap/full-data varsayımlarını report'taki matched comparison state ile karşılaştır

**Kopyala-yapıştır brief**

```text
Task key: q5_notebook_canonical_rewrite
Scope: Rewrite the Q5 notebook so its default path reproduces the matched 3000/400/400 trigram-LSTM-distilGPT2 comparison used by the report.
Primary files: notebooks/Q5_LanguageModeling.ipynb.
Non-goals: Do not reopen Q5 model code or change the final report narrative.
Validation: The notebook's default path matches the current Q5 summary artifact chain, and any full-data path is explicitly exploratory.
First action: Compare the notebook's default sample caps and model settings against the Q5 artifact mapping in report/README.md.
```

### `notebook_to_report_integration_hooks`

**Önerilen agent adı**
- `copilot-notebook-report-hooks`

**Primary files**
- `notebooks/Q3_Summarization.ipynb`
- `notebooks/Q4_MachineTranslation.ipynb`
- `notebooks/Q5_LanguageModeling.ipynb`
- `notebooks/README.md`

**Non-goals**
- Summary script mantığını yeniden yazmak
- Report prose değiştirmek

**Validation**
- Q3/Q4/Q5 notebook'larında summary script ve figür regeneration sonrası ne yapılacağı açık olmalı
- Notebook run sonrası report refresh zinciri görünür kalmalı

**First action**
- Q3/Q4/Q5 için mevcut summary script ve `scripts/report_comparison_figures.py` kullanım noktalarını notebook akışına bağlayacak minimum hook listesini çıkar

**Kopyala-yapıştır brief**

```text
Task key: notebook_to_report_integration_hooks
Scope: Add the missing Q3/Q4/Q5 summary-script and report-figure regeneration hooks so notebook runs connect cleanly to the current report refresh workflow.
Primary files: notebooks/Q3_Summarization.ipynb, notebooks/Q4_MachineTranslation.ipynb, notebooks/Q5_LanguageModeling.ipynb, notebooks/README.md.
Non-goals: Do not rewrite the summary scripts themselves or change the report prose.
Validation: After a notebook run, the next summary/report-refresh actions are explicit and the user is not left guessing which command to run next.
First action: Map the existing summary scripts and report_comparison_figures.py into the Q3/Q4/Q5 notebook workflows as explicit post-run steps.
```

## 7. Önerilen Paralel Dalga Planı

### Dalga 1
- `notebook_shared_workflow_refresh`
- `notebooks_readme_sync`

### Dalga 2
- `q3_notebook_canonical_rewrite`
- `q4_notebook_canonical_rewrite`
- `q5_notebook_canonical_rewrite`

### Dalga 3
- `q1_notebook_report_alignment`
- `q2_notebook_report_alignment`

### Dalga 4
- `notebook_to_report_integration_hooks`

## 8. Minimum Kabul Kriteri

Notebook refresh işi tamamlandı sayılmamalıdır, eğer:

- notebook sadece çalışıyor ama current report state ile ilişkisi belirsizse,
- canonical ve exploratory yollar ayrıştırılmadıysa,
- summary/report refresh adımı gerekiyorken eklenmediyse,
- notebook markdown anlatısı mevcut artifact gerçekliğiyle çelişiyorsa.

Tamamlanmış kabul için en az şu netleşmiş olmalıdır:

1. default notebook path hangi artifact'i üretir,
2. bu artifact report'ta kullanılıyor mu,
3. kullanılmıyorsa exploratory olarak nasıl etiketleniyor,
4. report'a gidecek zincirde hangi script veya figür yenileme adımı gerekiyor.
