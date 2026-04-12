# 10 - Experiment & Reproducibility

> [Ana Sayfa](README.md) | Onceki: [Evaluation Framework](09-evaluation-framework.md) | Sonraki: [LaTeX Rapor](11-report-structure.md)

---

## Genel Bakis

Deneylerin tekrarlanabilirligi bu projenin zorunlu gereksinimlerinden biridir. Bu dokuman seed yonetimi, config yapisi, ortam ayarlari ve deney calistirma protokolunu tanimlar.

---

## Reproducibility Kontrol Listesi

- [x] Sabit random seed (tum kaynaklar: Python, NumPy, PyTorch, CUDA)
- [x] Deterministic PyTorch ayarlari
- [x] Config dosyasi her run ile birlikte kaydedilir
- [x] Tum hyperparametreler YAML'da, kodda hardcoded deger yok
- [x] Dataset split'leri seed-kontrollü
- [x] DataLoader worker seed'leri deterministik
- [x] Environment bilgileri (Python, CUDA, paket versiyonlari) kaydedilir
- [x] Test seti yalnizca bir kez kullanilir (final evaluation)

---

## Seed Yonetimi

### Kapsam

```python
# src/common/seed.py

import random
import os
import numpy as np
import torch

def set_global_seed(seed: int = 42) -> None:
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)     # multi-GPU
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def worker_init_fn(worker_id: int) -> None:
    """DataLoader worker'lari icin."""
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)
```

### Kullanim Protokolu

```python
# Her main.py'nin baslangici:
config = load_config("configs/q1.yaml")
set_global_seed(config.seed)   # HERSEY'den once
```

---

## Config Sistemi

### base.yaml (Ortak Default'lar)

```yaml
# configs/base.yaml
seed: 42
device: "auto"                # "cuda" | "cpu" | "auto" (otomatik tespit)

output_dir: "outputs"
logging:
  level: "INFO"
  save_logs: true
  log_every_n_steps: 100

data:
  cache_dir: "data/cache"
  num_workers: 4
  pin_memory: true

training:
  early_stopping_patience: 3
  save_best_model: true
  save_every_n_epochs: null     # null = yalnizca best
  gradient_clip: null           # null = clip yok
  mixed_precision: false        # AMP (Automatic Mixed Precision)
```

### Config Merge Mekanizmasi

```
1. base.yaml        (en dusuk oncelik)
2. q{n}.yaml        (soru-ozel ayarlar, base uzerine yazilir)
3. CLI overrides     (en yuksek oncelik)

Ornek:
  python -m src.q1_classification.main \
      --config configs/q1.yaml \
      --override models.bilstm.learning_rate=0.0005 \
      --override seed=123
```

### Config Kaydetme

Her deney calistirmasi, kullanilan config'in bir kopyasini output dizinine kaydeder:

```
outputs/q1/run_20260415_143022/
|-- config.yaml          # Merge sonrasi final config
|-- environment.json     # Python, CUDA, paket versiyonlari
+-- ...
```

### Environment Bilgileri

```python
def save_environment_info(output_dir: str) -> None:
    """
    Kaydedilen bilgiler:
    - Python version
    - PyTorch version + CUDA version
    - Transformers version
    - GPU bilgisi (model, memory)
    - OS bilgisi
    - Tum pip freeze ciktisi
    """
```

Ornek environment.json:
```json
{
    "python": "3.10.12",
    "pytorch": "2.1.0",
    "cuda": "11.8",
    "transformers": "4.36.0",
    "gpu": "NVIDIA Tesla T4 (15GB)",
    "os": "Linux 5.15.0",
    "packages": "... pip freeze ..."
}
```

---

## Deney Calistirma Protokolu

### Adim Adim

```bash
# 1. Ortami hazirla
conda activate ceng467
# veya
pip install -r requirements.txt

# 2. Seed'in dogru ayarlandigini dogrula
python -c "from src.common.seed import set_global_seed; set_global_seed(42); print('OK')"

# 3. Tek soru calistir
python -m src.q1_classification.main --config configs/q1.yaml

# 4. Override ile calistir
python -m src.q1_classification.main \
    --config configs/q1.yaml \
    --override seed=123

# 5. Tum sorulari sirayla calistir
for q in q1_classification q2_ner q3_summarization q4_translation q5_language_model; do
    python -m src.${q}.main --config configs/$(echo $q | cut -d_ -f1).yaml
done
```

### Main.py Standart Yapisi

Her sorunun `main.py`'si ayni sablonu takip eder:

```python
"""Q{n} - {Gorev Adi} entry point."""

import argparse
from src.common.config import load_config
from src.common.seed import set_global_seed
from src.common.export import create_run_dir, save_config_copy, save_environment_info

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--override", nargs="*", default=[])
    return parser.parse_args()

def main():
    args = parse_args()

    # 1. Config yukle
    overrides = dict(item.split("=") for item in args.override)
    config = load_config(args.config, overrides)

    # 2. Seed ayarla
    set_global_seed(config.seed)

    # 3. Output dizini olustur
    run_dir = create_run_dir(config.output_dir, config.question)
    save_config_copy(config, run_dir)
    save_environment_info(run_dir)

    # 4. Data yukle + preprocess
    # ...

    # 5. Modelleri egit
    # ...

    # 6. Evaluate
    # ...

    # 7. Sonuclari kaydet
    # ...

if __name__ == "__main__":
    main()
```

---

## Output Dizin Yapisi

```
outputs/
|-- q1/
|   |-- run_20260415_143022/          # Timestamped
|   |   |-- config.yaml               # Kullanilan final config
|   |   |-- environment.json           # Ortam bilgileri
|   |   |-- metrics.json               # Nihai metrikler
|   |   |-- predictions/               # Model tahminleri
|   |   |-- figures/                   # Gorseller
|   |   |-- model_best_bilstm.pt      # Checkpoints
|   |   |-- model_best_distilbert.pt
|   |   +-- training.log              # Training log
|   +-- run_20260416_091530/           # Baska bir run
|
|-- q2/ ...
|-- q3/ ...
|-- q4/ ...
+-- q5/ ...
```

---

## Requirements

### requirements.txt

```
# Core
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
tokenizers>=0.15.0

# Classical ML
scikit-learn>=1.3.0
sklearn-crfsuite>=0.3.6

# NER
seqeval>=1.2.2

# Metrics
evaluate>=0.4.0
rouge-score>=0.1.2
bert-score>=0.3.13
sacrebleu>=2.3.0
nltk>=3.8.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=2.0.0

# Utilities
pyyaml>=6.0
tqdm>=4.66.0
numpy>=1.24.0

# NLP
spacy>=3.6.0
# python -m spacy download en_core_web_sm
# python -m spacy download de_core_news_sm

# CRF for PyTorch
TorchCRF>=1.1.0
```

### Colab Setup (Opsiyonel)

```python
# Google Colab'da calistirmak icin:
!pip install transformers datasets evaluate bert-score sacrebleu
!pip install sklearn-crfsuite seqeval TorchCRF
!pip install rouge-score nltk spacy
!python -m spacy download en_core_web_sm
!python -m spacy download de_core_news_sm

# GPU kontrol
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

---

## Hyperparameter Onemli Notlar

### Model-Arasi Tutarlilik

Odev metninde "comparable conditions" vurgulanmistir. Bu, karsilastirmali deneyler icin:

1. **Ayni dataset split'leri** - Tum modeller ayni train/val/test bolunmesini kullanir
2. **Ayni preprocessing** - Ayni cleaning pipeline (model-ozel tokenization haric)
3. **Ayni evaluation protocol** - Ayni metrikler, ayni test seti
4. **Makul hyperparameter tuning** - Her model icin adil tuning eforu

### Test Seti Kullanimi

```
KURAL: Test seti YALNIZCA BIR KEZ, final evaluation icin kullanilir.

YANLIS:
  for epoch in range(100):
      train(model)
      test_score = evaluate(model, test_set)  # HAYIR!
      if test_score > best:
          save(model)

DOGRU:
  for epoch in range(100):
      train(model)
      val_score = evaluate(model, val_set)    # Val kullan
      if val_score > best:
          save(model)
  # Egitim bittikten sonra:
  final_score = evaluate(best_model, test_set)  # Tek seferlik
```

---

## Iliskili Dokumanlar

- [Ortak Altyapi](03-shared-infrastructure.md) - config.py, seed.py implementasyonu
- [Proje Genel Bakis](01-project-overview.md) - Teknoloji stack
- [Dizin Yapisi](02-project-structure.md) - Dosya organizasyonu
