# 07 - Q4: Machine Translation

> [Home](README.md) | Previous: [Q3 - Summarization](06-q3-summarization.md) | Next: [Q5 - Language Modeling](08-q5-language-modeling.md)

---

## Objective

Examine sequence-to-sequence modeling and attention mechanisms. Compare a classical Seq2Seq+Attention model with a Transformer-based model. Evaluate translation quality using a multi-metric suite.

---

## Dataset: Multi30k

### Properties
- **Task**: EN -> DE translation (or DE -> EN)
- **Source**: Flickr30k image captions
- **Size**:
  - Train: ~29,000 sentence pairs
  - Val: ~1,014 sentence pairs
  - Test (2016): ~1,000 sentence pairs
- **Average sentence length**: ~12 tokens (short sentences)
- **Source**: `datasets.load_dataset("bentrevett/multi30k")` or torchtext

### Data Structure
```python
{
    "en": "Two young, White males are outside near many bushes.",
    "de": "Zwei junge weiße Männer sind im Freien in der Nähe vieler Büsche."
}
```

---

## Preprocessing

### preprocess.py

```python
def tokenize_en(text: str) -> list[str]:
    """
    English tokenization:
    - spacy 'en_core_web_sm' or simple whitespace+punct
    - Lowercase
    """

def tokenize_de(text: str) -> list[str]:
    """
    German tokenization:
    - spacy 'de_core_news_sm' or simple whitespace+punct
    - Lowercase
    """

def build_vocab_from_data(tokenized_sentences: list[list[str]],
                          min_freq: int = 2) -> Vocabulary:
    """
    Builds vocabulary using src/common/vocab.py.
    Special tokens: <PAD>, <UNK>, <BOS>, <EOS>
    """

def numericalize(tokens: list[str], vocab: Vocabulary) -> list[int]:
    """Token -> index conversion. Adds <BOS> and <EOS>."""

class TranslationDataset(Dataset):
    """
    Each example: (src_indices, tgt_indices)
    Collate function: dynamic padding + sorting by length
    """
```

### BPE Tokenization (for Transformer)

```python
def build_bpe_tokenizer(texts: list[str],
                        vocab_size: int = 10000) -> tokenizers.Tokenizer:
    """
    BPE training with HuggingFace tokenizers.
    Word-level is used for Seq2Seq, BPE is used for Transformer.
    """
```

### Preprocessing Pipeline Comparison

| Property | Seq2Seq | Transformer |
|---------|---------|-------------|
| Tokenization | Word-level (spacy) | BPE (subword) |
| Vocabulary | Separate src/tgt vocab | Shared or separate BPE |
| Lowercase | Yes | Yes |
| Min freq | 2 | - (BPE handles) |
| Special tokens | PAD, UNK, BOS, EOS | PAD, UNK, BOS, EOS |

---

## Model Architectures

### Model 1: Seq2Seq + Attention

**File**: `models/seq2seq_attention.py`

```python
class Encoder(nn.Module):
    def __init__(self, input_dim: int, embed_dim: int = 256,
                 hidden_dim: int = 512, num_layers: int = 2,
                 dropout: float = 0.5):
        """
        Bidirectional GRU/LSTM encoder.
        Layers:
        1. Embedding
        2. Dropout
        3. Bidirectional RNN
        """

    def forward(self, src, src_len):
        """
        Input: (batch, src_len) token indices
        Output: encoder_outputs (batch, src_len, hidden*2),
                hidden state (num_layers, batch, hidden)
        """


class Attention(nn.Module):
    def __init__(self, hidden_dim: int, attention_type: str = "bahdanau"):
        """
        attention_type: "bahdanau" (additive) or "luong" (multiplicative)
        """

    def forward(self, decoder_hidden, encoder_outputs, mask=None):
        """
        Bahdanau:  score = V * tanh(W1*decoder_hidden + W2*encoder_output)
        Luong:     score = decoder_hidden @ encoder_output.T

        Returns: attention weights (batch, src_len), context (batch, hidden*2)
        """


class Decoder(nn.Module):
    def __init__(self, output_dim: int, embed_dim: int = 256,
                 hidden_dim: int = 512, num_layers: int = 2,
                 dropout: float = 0.5, attention: Attention = None):
        """
        Layers:
        1. Embedding
        2. RNN (GRU/LSTM)
        3. Attention
        4. Output projection (concat -> linear -> vocab)
        """

    def forward(self, input_token, hidden, encoder_outputs, mask):
        """
        Single step decode:
        1. Embed input token
        2. RNN step
        3. Compute attention
        4. Context + hidden concat -> output projection
        """


class Seq2SeqWithAttention(nn.Module):
    def __init__(self, encoder, decoder, device):
        """Encoder + Decoder + Attention composition."""

    def forward(self, src, src_len, tgt, teacher_forcing_ratio=0.5):
        """
        Training with teacher forcing:
        - At each step, the real or predicted token is used with 50% probability
        - Decreasing teacher forcing schedule during training is optional
        """

    def translate(self, src, src_len, max_len=50, bos_idx=2):
        """
        Translation with greedy decode or beam search.
        Continues until <EOS> token or max_len is reached.
        """
```

**Architecture Diagram**:
```
Source: [<BOS>] Two young males [<EOS>]
           |    |    |     |      |
           v    v    v     v      v
     [   Embedding (256d)         ]
           |    |    |     |      |
           v    v    v     v      v
     [  BiGRU Encoder (512d x 2)  ]
           |    |    |     |      |
           +----+----+-----+------+--- encoder_outputs
                                  |
                            encoder hidden -> decoder hidden init
                                  |
                                  v
                    +---> [Attention] <---+
                    |         |          |
                    |    context vector   |
                    |         |          |
                    |         v          |
Target: [<BOS>] Zwei junge Männer [<EOS>]
           |     |     |     |      |
           v     v     v     v      v
     [   Embedding (256d)          ]
           |     |     |     |      |
           v     v     v     v      v
     [    GRU Decoder (512d)       ]
           |     |     |     |      |
           v     v     v     v      v
     [  Linear -> Vocab Projection ]
           |     |     |     |      |
           v     v     v     v      v
Output: Zwei  junge Männer  sind  [<EOS>]
```

**Hyperparameters**:
| Parameter | Value |
|-----------|-------|
| embed_dim | 256 |
| hidden_dim | 512 |
| num_layers | 2 |
| dropout | 0.5 |
| attention | Bahdanau (additive) |
| teacher_forcing | 0.5 |
| batch_size | 128 |
| learning_rate | 1e-3 |
| optimizer | Adam |
| num_epochs | 30 |
| gradient_clip | 1.0 |
| early_stopping | patience=5 |

---

### Model 2: Transformer

**File**: `models/transformer_mt.py`

```python
class TransformerMT(nn.Module):
    """
    Vanilla Transformer (Vaswani et al., 2017) implementation
    or pretrained model (Helsinki-NLP/opus-mt-en-de).
    """

    def __init__(self, src_vocab_size: int, tgt_vocab_size: int,
                 d_model: int = 256, nhead: int = 8,
                 num_encoder_layers: int = 3,
                 num_decoder_layers: int = 3,
                 dim_feedforward: int = 512,
                 dropout: float = 0.1,
                 max_seq_length: int = 128):
        """
        Layers:
        1. Source/Target Embedding + Positional Encoding
        2. Transformer Encoder (N layers)
        3. Transformer Decoder (N layers)
        4. Output Linear projection
        """

    def generate_square_subsequent_mask(self, sz: int):
        """Causal mask (for decoder)."""

    def create_padding_mask(self, seq, pad_idx: int = 0):
        """Padding mask."""

    def forward(self, src, tgt):
        """
        src: (batch, src_len)
        tgt: (batch, tgt_len)
        Full forward pass with masks.
        """

    def translate(self, src, max_len=50, bos_idx=2):
        """
        Autoregressive generation:
        1. Run encoder once
        2. Start with BOS
        3. Run decoder at each step
        4. Continue until EOS
        """


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding."""
    def __init__(self, d_model: int, max_len: int = 5000,
                 dropout: float = 0.1): ...
```

**Alternative: Pretrained Model**:
```python
class PretrainedTransformerMT:
    """Translation using Helsinki-NLP/opus-mt-en-de."""

    def __init__(self, model_name="Helsinki-NLP/opus-mt-en-de"):
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)

    def translate(self, texts: list[str]) -> list[str]: ...
```

**Hyperparameters (Custom Transformer)**:
| Parameter | Value |
|-----------|-------|
| d_model | 256 |
| nhead | 8 |
| num_encoder_layers | 3 |
| num_decoder_layers | 3 |
| dim_feedforward | 512 |
| dropout | 0.1 |
| batch_size | 128 |
| learning_rate | 5e-4 |
| optimizer | Adam (beta1=0.9, beta2=0.98) |
| scheduler | Noam / warmup + inverse sqrt |
| warmup_steps | 4000 |
| num_epochs | 30 |
| label_smoothing | 0.1 |

---

## Training

### train.py

```python
def train_seq2seq(model, train_loader, val_loader, config):
    """
    Seq2Seq training:
    - Teacher forcing (with decreasing ratio)
    - CrossEntropyLoss (pad_idx ignore)
    - Gradient clipping
    """

def train_transformer(model, train_loader, val_loader, config):
    """
    Transformer training:
    - Label smoothing CrossEntropy
    - Noam learning rate scheduler
    - Padding + causal mask management
    """

def translate_dataset(model, test_loader, vocab_tgt) -> list[str]:
    """Batch translation over the test set. Includes detokenization."""
```

---

## Evaluation

### Multi-Metric Suite

| Metric | What It Measures | Strength | Weakness |
|--------|------------|-----|----------|
| **BLEU** | N-gram precision + brevity penalty | Standard MT metric | Cannot capture synonyms |
| **METEOR** | Alignment + synonym + stemming | Semantic matching | Slow computation |
| **ChrF** | Character n-gram F-score | Good for morphologically rich languages | May miss word-level structures |
| **BERTScore** | Contextual embedding similarity | Semantic similarity | Model-dependent |

### Computation

```python
# BLEU
from sacrebleu import corpus_bleu
bleu = corpus_bleu(predictions, [references])

# METEOR
from nltk.translate.meteor_score import meteor_score

# ChrF
from sacrebleu import corpus_chrf
chrf = corpus_chrf(predictions, [references])

# BERTScore
from bert_score import score as bert_score
P, R, F1 = bert_score(predictions, references, lang="de")
```

For details see: [Evaluation Framework](09-evaluation-framework.md)

---

## Qualitative Analysis

### analysis.py

```python
def qualitative_translation_examples(sources, references,
                                      seq2seq_outputs,
                                      transformer_outputs,
                                      n: int = 3) -> list[dict]:
    """
    For each example:
    - Source (EN)
    - Reference (DE)
    - Seq2Seq output
    - Transformer output
    - Analysis: fluency, rare word handling, long-range deps
    """

def analyze_attention_patterns(model, src_tokens, tgt_tokens):
    """
    Attention weight visualization.
    Shows alignment quality.
    """

def analyze_error_types(sources, references, predictions) -> dict:
    """
    Error categories:
    - Word order errors
    - Missing/extra words
    - Incorrect gender/case (for DE)
    - Rare word failures (UNK)
    - Long-range dependency failures
    """
```

---

## Expected Outputs

```
outputs/q4/run_{timestamp}/
|-- config.yaml
|-- metrics.json                    # BLEU, METEOR, ChrF, BERTScore
|-- predictions/
|   |-- seq2seq_translations.txt
|   +-- transformer_translations.txt
|-- qualitative_analysis.json
|-- figures/
|   |-- attention_heatmap_seq2seq.png
|   |-- attention_heatmap_transformer.png
|   |-- metric_comparison.png
|   +-- training_curves.png
+-- model_best_*.pt
```

---

## Config Example (q4.yaml)

```yaml
question: "q4"
task: "translation"

dataset:
  name: "multi30k"
  src_lang: "en"
  tgt_lang: "de"

preprocess:
  tokenization: "spacy"           # for seq2seq
  bpe_vocab_size: 10000           # for transformer
  min_freq: 2
  max_seq_length: 50

models:
  seq2seq:
    embed_dim: 256
    hidden_dim: 512
    num_layers: 2
    dropout: 0.5
    attention_type: "bahdanau"
    teacher_forcing_ratio: 0.5
    batch_size: 128
    learning_rate: 1e-3
    num_epochs: 30
    gradient_clip: 1.0

  transformer:
    d_model: 256
    nhead: 8
    num_encoder_layers: 3
    num_decoder_layers: 3
    dim_feedforward: 512
    dropout: 0.1
    batch_size: 128
    learning_rate: 5e-4
    warmup_steps: 4000
    num_epochs: 30
    label_smoothing: 0.1

evaluation:
  metrics: ["bleu", "meteor", "chrf", "bertscore"]
  num_qualitative_examples: 3
  beam_size: 5
```

---

## Architecture Comparison Summary

| Dimension | Seq2Seq + Attention | Transformer |
|-------|-------------------|-------------|
| Parallelization | Sequential (RNN) | Fully parallel |
| Long-range deps | Weak (RNN bottleneck) | Strong (self-attention) |
| Training speed | Slow | Fast |
| Parameter count | ~15M | ~12M (small config) |
| Attention | Encoder-decoder only | Self + cross attention |
| Positional info | Implicit (RNN order) | Explicit (positional encoding) |
| Rare words | UNK problem | Better with BPE |

---

## Related Documents

- [Shared Infrastructure](03-shared-infrastructure.md) - Vocabulary, Trainer
- [Q3 - Summarization](06-q3-summarization.md) - Shared BLEU, METEOR, BERTScore
- [Evaluation Framework](09-evaluation-framework.md) - Metric details
- [Q5 - Language Modeling](08-q5-language-modeling.md) - Similar sequence modeling
