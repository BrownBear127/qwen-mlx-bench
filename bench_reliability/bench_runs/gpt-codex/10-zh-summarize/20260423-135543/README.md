# Offline Traditional Chinese Summarization POC

This POC stays fully offline and uses only Python's standard library.

## Approach

The summarizer is a tiny extractive method:

1. Split the article into Chinese sentences with punctuation such as `。！？；`.
2. Collect document-wide character bigrams, which work as a rough stand-in for keywords without requiring Chinese word segmentation libraries.
3. Score each sentence by:
   - how many important bigrams it contains,
   - a small lead-sentence bonus,
   - a mild preference for sentence lengths that combine well into a short summary.
4. Try every 1-3 sentence combination and keep the one with the best score while staying between 50 and 150 characters, aiming for about 100.

## Why this is reasonable under the constraints

- No model download is needed.
- No network access is needed.
- No third-party tokenizer or embedding library is needed.
- Character bigrams are a simple compromise for Traditional Chinese, where whitespace tokenization is not reliable.
- The output is extractive, so it tends to stay grammatical and faithful to the source article.

This is not meant to be state of the art. It is a deliberately small baseline that produces a short, readable summary under strict offline constraints.

## Run

```bash
python3 poc.py
```

The script prints:

- the summary text
- its character count
