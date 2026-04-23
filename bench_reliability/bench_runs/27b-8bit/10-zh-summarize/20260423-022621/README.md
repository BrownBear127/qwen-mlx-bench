# Offline Traditional Chinese Summarizer (POC)

A minimal proof-of-concept that summarizes Traditional Chinese (繁體中文) text
to ~100 characters using **only Python stdlib** — no network, no external
packages, no model downloads.

## Approach: Extractive Summarization via TF-IDF on Character Bigrams

### How it works

1. **Sentence splitting** — The article is split on Chinese sentence-ending
   punctuation (`。！？\n`).

2. **Feature extraction** — For each sentence, character bigrams (2-character
   sequences) are extracted after stripping punctuation. Chinese has no spaces,
   so character n-grams are a natural unit of analysis.

3. **TF-IDF scoring** — Each sentence is scored using Term Frequency–Inverse
   Document Frequency computed over character bigrams:
   - **TF** (term frequency): how often a bigram appears in the sentence.
   - **IDF** (inverse document frequency): how rare a bigram is across all
     sentences. Rare bigrams carry more distinctive information.
   - Scores are normalized by sentence length to avoid bias toward longer
     sentences.

4. **Greedy selection** — Sentences are ranked by TF-IDF score. The top-scoring
   sentences are greedily selected until the total character count reaches the
   target (~100 chars, with a small tolerance). Selected sentences are returned
   in their original order for readability.

### Why this is reasonable under the constraints

| Constraint | How we handle it |
|---|---|
| No network / offline | All logic is pure Python math — no HTTP calls, no model loading |
| No external deps | Only `re`, `math`, `collections.Counter` from stdlib |
| No large models | TF-IDF is a lightweight statistical method, not a neural network |
| 50–150 char output | Greedy selection with a target + tolerance ensures the range |
| Traditional Chinese | Character bigrams work naturally for CJK text (no word boundaries) |

### Limitations (by design)

- **Extractive only** — The summary consists of verbatim sentences from the
  original. It does not generate new phrasing.
- **No semantic understanding** — TF-IDF captures statistical distinctiveness,
  not meaning. A sentence about a rare topic will score higher than a common
  one, which often correlates with importance but isn't guaranteed.
- **No word segmentation** — We use character bigrams instead of words because
  Chinese word segmentation requires external libraries (e.g., `jieba`). Bigrams
  are a reasonable approximation.

### Running

```bash
python3 poc.py
```

### Sample output

```
============================================================
SUMMARY
============================================================
傳統工藝在現代社會中面臨著前所未有的挑戰與機遇。語言與文字作為文化傳承的重要載體，同樣面臨著數位時代的衝擊。飲食文化亦是傳統與現代交融的重要場域。只有在尊重傳統基礎上的創新，才能真正讓文化薪火相傳，生生不息。
============================================================
Character count: 104
Original length: 605
Compression ratio: 17.2%
```

The summary captures the article's core themes: traditional crafts facing
modern challenges, language/cultural preservation, food culture, and the
need for innovation rooted in tradition.
