# Offline Traditional Chinese Summarizer (POC)

## Run

```bash
python3 poc.py       # Python 3.8+ / stdlib only / no network
```

## Approach

**Extractive summarization via character-bigram TF-IDF scoring.**

1. **Sentence splitting** — split on Chinese punctuation (`。！？`).
2. **Feature extraction** — character bigrams (pairs of consecutive characters).
   Bigrams are a natural unit for Chinese because most words are 1-3 characters,
   so bigrams capture meaningful sub-word and word-level signals without a
   tokeniser or dictionary.
3. **Scoring** — each sentence gets a TF-IDF score:
   - *TF* = log-smoothed bigram count within the sentence.
   - *IDF* = log(N / df) where df is the number of sentences containing the bigram.
   - Score is normalised by bigram count so longer sentences don't dominate.
   - A small positional boost (×1.3) is applied to the first and last sentences,
     since lead/tail sentences tend to carry topic and conclusion info.
4. **Selection** — sentences are ranked by score and greedily added (in original
   document order) until the ~100-character budget is filled.

## Why this is reasonable under the constraints

- **No segmentation dictionary needed.** Unlike English where TF-IDF operates on
  whitespace-delimited words, Chinese has no spaces. A proper word segmenter
  (jieba, pkuseg) would require external data. Character bigrams sidestep this
  entirely while still capturing most two-character words — the most common word
  length in Chinese.
- **TF-IDF naturally highlights topical sentences.** Sentences that use rare,
  distinctive bigrams score higher, which is exactly what we want for a summary.
- **Positional heuristic adds robustness.** Journalistic and expository Chinese
  text tends to front-load key information (similar to English), so boosting the
  first sentence is a well-known baseline improvement.
- **Pure stdlib.** Only `re`, `math`, and `collections.Counter` are used.
