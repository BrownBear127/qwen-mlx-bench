# Traditional Chinese Extractive Summarizer — POC

## What this does

This POC takes a Traditional Chinese (繁體中文) article and produces a
roughly 100-character summary using **extractive summarization** — it selects
the most important sentences from the original text rather than generating
new text.

## Approach

1. **Sentence splitting** — The article is split on common Chinese sentence
   delimiters (`。！？；`).

2. **Character bigram TF-IDF** — Each sentence is represented as a bag of
   character bigrams (e.g. "傳統" → bigrams: "傳", "統", "傳統").
   - **TF** (term frequency) = count of a bigram in the sentence / total bigrams
   - **IDF** (inverse document frequency) = log(N / (1 + doc_freq))
   - The TF-IDF score for a sentence is the sum of TF-IDF values for its
     unique bigrams. Rare but meaningful bigrams get higher scores.

3. **Top-k selection** — The top ~40% of sentences by TF-IDF score are
   selected, preserving their original order in the article.

4. **Truncation** — If the concatenated result exceeds ~120 characters,
   sentences are dropped from the end until it fits within ~100 characters.

## Why this is reasonable under the constraints

- **No network, no downloads** — Everything runs on CPU with only Python
  stdlib (`math`, `re`, `sys`). No model weights, no API calls.
- **Extractive, not abstractive** — We don't try to generate new text (which
  would require a language model). We simply pick the most "informative"
  sentences, which is a well-studied and effective approach for short
  summaries.
- **Character-level n-grams** — Chinese has no spaces, so word-level TF-IDF
  would require a tokenizer. Character bigrams sidestep this entirely while
  still capturing local semantic patterns.
- **Trade-off** — The summary may not be perfect, but it reliably produces
  a 50–150 character excerpt that captures the key ideas of the source text.

## Usage

```bash
python poc.py
```

Output:
```
Summary (X chars):
<traditional chinese summary>

Original article: Y chars
```
