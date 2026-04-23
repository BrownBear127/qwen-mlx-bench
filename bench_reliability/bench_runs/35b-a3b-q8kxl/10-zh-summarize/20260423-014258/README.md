# Traditional Chinese Extractive Summarizer — POC

## Overview

This proof-of-concept summarizes a Traditional Chinese (繁體中文) article to
roughly **100 characters** using only Python's standard library. No network
calls, no external packages, no model downloads.

## How It Works

The summarizer uses **extractive summarization** — it selects the most
important sentences from the original text rather than generating new text.

### Step-by-step

1. **Sentence splitting** — The article is split into sentences using Chinese
   sentence-ending punctuation (。！？；).

2. **Character bigram TF-IDF scoring** — Each sentence is scored using a
   simplified TF-IDF approach on character-level bigrams (2-character sequences):
   - **TF** (term frequency): how often a bigram appears in the sentence
   - **IDF** (inverse document frequency): how rare the bigram is across all
     sentences — rare bigrams are more informative
   - The sentence score is the sum of TF×IDF for all its bigrams

3. **Position bonus** — Sentences near the beginning or end of the article
   receive a small score boost, since they often contain topic sentences or
   conclusions.

4. **Selection** — Sentences are ranked by combined score, and the top ~1/3
   are selected. They are reassembled in their original order.

5. **Truncation** — If the result exceeds the target length (~100 chars), it is
   truncated at a sentence boundary.

## Why This Approach Is Reasonable

- **No network needed**: TF-IDF on character n-grams requires only the text
  itself — no vocabulary, no model weights, no external data.
- **Language-agnostic**: Character bigrams work for any language, including
  Chinese where word boundaries are not trivial to determine without a tokenizer.
- **Extractive = safe**: Since we only select existing sentences, the summary
  is always grammatically coherent and factually faithful to the source.
- **Fast & lightweight**: Runs in milliseconds on a few hundred characters of
  text, with minimal memory usage.

## Limitations

- Does not generate novel phrasing; relies on sentence-level extraction.
- May not capture nuanced relationships between sentences.
- The TF-IDF model is very simple — no semantic similarity, no attention.

## Running

```bash
python poc.py
```

No dependencies required. Python 3.6+.
