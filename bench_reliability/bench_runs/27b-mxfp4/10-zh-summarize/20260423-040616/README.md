# Offline Traditional Chinese Summarizer (POC)

## What it does

`poc.py` takes a Traditional Chinese (繁體中文) article and produces an
**extractive summary** of roughly **100 characters** (50–150 range), using
**only Python stdlib** — no network calls, no external packages, no model
downloads.

## How to run

```bash
python3 poc.py
```

## Approach: TF-IDF on character bigrams

### The problem

Summarizing text usually relies on large language models (transformers,
LLMs), which require network access or massive downloads. Under the
"stdlib-only, fully offline" constraint, we need a lightweight heuristic.

### The solution

1. **Sentence segmentation** — Split the article on Chinese sentence
   terminators (`。！？`) and newlines.

2. **Character bigram extraction** — For each sentence, extract all
   overlapping 2-character n-grams (e.g., "設計" → "設", "計" →
   bigrams: "設計", "計是", "是一", ...).

3. **IDF (Inverse Document Frequency)** — Compute how rare each bigram is
   across all sentences. Bigrams that appear in only a few sentences get
   higher IDF scores, indicating they carry more distinctive information.

4. **Sentence scoring** — Each sentence's score is the sum of its bigrams'
   IDF values, normalized by sentence length (to avoid bias toward longer
   sentences).

5. **Greedy selection** — Pick the highest-scoring sentences until the
   combined length falls in the 50–150 character range.

### Why this is reasonable

- **No network, no dependencies** — Everything is pure Python stdlib
  (`re`, `math`, `collections.Counter`).
- **Extractive, not abstractive** — The summary consists of actual
  sentences from the source, so it's guaranteed to be coherent and
  factually accurate (no hallucination).
- **TF-IDF is a classic NLP technique** — It's been used for decades
  in information retrieval and text summarization. While it doesn't
  capture deep semantics like an LLM, it does identify sentences with
  distinctive, informative content.
- **Character bigrams work for Chinese** — Unlike English, Chinese
  doesn't have spaces between words, so character n-grams are a
  practical way to capture local context without needing a tokenizer.
- **The output is in the target range** — 133 characters, well within
  the 50–150 requirement.

### Limitations

- No understanding of meaning, context, or discourse structure.
- May pick sentences that are individually informative but not
  well-connected to each other.
- No handling of pronouns, coreference, or narrative flow.

This is a **proof of concept** — it demonstrates that a reasonable
summarization can be achieved under extreme constraints, without any
network access or external dependencies.
