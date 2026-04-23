# Offline Traditional Chinese Summarizer — Minimal POC

## What it does

Takes a Traditional Chinese (繁體中文) article and produces an extractive
summary of roughly **100 characters** (target range: 50–150).

## How to run

```bash
python3 poc.py
```

No network access, no `pip install`, no model downloads. Pure Python stdlib.

## Summarization approach

### 1. Sentence segmentation
Splits the article into sentences using Chinese sentence-ending punctuation
(`。！？`) and newlines.

### 2. TF-IDF on character bigrams
- **Bigrams**: For each sentence, we extract all overlapping 2-character
  sequences (e.g. "設計", "計已", "已是" …).
- **TF (Term Frequency)**: For each bigram in a sentence, how often it
  appears relative to the sentence's total bigrams.
- **IDF (Inverse Document Frequency)**: Across all sentences, how rare a
  bigram is. Bigrams that appear in many sentences get a lower IDF score;
  distinctive/rare bigrams get a higher score.
- **Sentence score**: The average TF-IDF across all bigrams in the sentence.

### 3. Greedy selection
Sentences are ranked by their TF-IDF score (highest first). We greedily
select sentences until the combined character count reaches ~100, with a
small tolerance buffer (±50 chars) to avoid cutting mid-sentence.

## Why this is reasonable under the constraints

| Constraint | How we satisfy it |
|---|---|
| **No network** | Zero HTTP calls. All computation is local. |
| **No external deps** | Only `re`, `math`, `collections.Counter` — all stdlib. |
| **No large models** | No neural nets, no embeddings, no tokenizers. |
| **~100 char output** | Greedy selection with length budgeting keeps output in range. |
| **Traditional Chinese** | Bigram-based TF-IDF works on any script; no language-specific
  tokenizer needed. Chinese characters are naturally tokenized as single
  units. |

### Why TF-IDF on bigrams?

- **No word segmentation needed**: Chinese text doesn't use spaces between
  words. Character bigrams are a simple, language-agnostic n-gram unit that
  captures meaningful collocations (e.g. "設計", "文化", "傳統") without
  requiring a dictionary or NLP library.
- **IDF captures distinctiveness**: Bigrams that appear across many sentences
  (like "的", "在") get down-weighted, while topic-specific bigrams
  (like "工藝", "書法") get up-weighted. This naturally surfaces the most
  informative sentences.
- **Fast & lightweight**: O(n) in text length, runs in milliseconds on
  any machine.

### Limitations

- Extractive only — it selects existing sentences rather than generating new
  ones. The summary may not flow as smoothly as a human-written one.
- Bigrams are a crude unit; trigrams or character-level TF-IDF could be
  alternatives but add little practical benefit for this scale.
- No semantic understanding — it can't detect paraphrases or merge related
  ideas across sentences.

For a production system, you'd want a pre-trained language model. But as a
**zero-dependency, fully offline POC**, this approach demonstrates that
reasonable summarization is achievable with nothing more than basic text
statistics.
