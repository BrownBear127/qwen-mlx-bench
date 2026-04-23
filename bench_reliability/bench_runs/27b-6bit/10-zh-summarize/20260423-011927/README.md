# Offline Traditional Chinese Summarizer (POC)

## What it does

Takes a Traditional Chinese (繁體中文) article and produces an extractive
summary of roughly 100 characters (50–150 range), using **only Python stdlib**
and **zero network calls**.

## How to run

```bash
python3 poc.py
```

No `pip install`, no model downloads, no API keys.

## Approach: TF-IDF on character bigrams

### Why this approach?

Under the constraints (no network, no external libraries, no large models),
we cannot use neural summarizers, LLMs, or even pre-trained tokenizers.
The goal is a simple but *reasonable* heuristic that produces coherent output.

### Algorithm

1. **Sentence segmentation** — Split the article on Chinese sentence-ending
   punctuation (`。！？`). Each resulting segment is a candidate sentence.

2. **Feature extraction** — For each sentence, extract **character bigrams**
   (pairs of consecutive Chinese characters). This is the Chinese equivalent
   of word n-grams, since Chinese text has no whitespace-delimited words.

3. **TF-IDF scoring** —
   - **TF** (Term Frequency): how often each bigram appears in a sentence,
     normalized by sentence length.
   - **IDF** (Inverse Document Frequency): how rare each bigram is across
     all sentences. Rare bigrams get higher weight, capturing topic-specific
     content rather than boilerplate.
   - Each sentence's score = sum of TF×IDF for all its bigrams, normalized
     by √(sentence length) to avoid bias toward longer sentences.

4. **Greedy selection** — Pick the highest-scoring sentences until the total
   character count reaches ~100 (with a ±50 buffer).

5. **Re-ordering** — Selected sentences are sorted by their original position
   in the article, so the summary reads coherently rather than as a random
   bag of sentences.

### Why it's reasonable

- **Extractive, not abstractive**: We copy real sentences from the source,
  so the output is always grammatically correct and factually faithful.
- **TF-IDF captures topic salience**: Sentences with rare, distinctive
  bigrams (e.g., 竹編, 匠人, 傳承) score higher than generic filler.
- **No word segmentation needed**: Character bigrams work directly on raw
  Chinese text, avoiding the need for a tokenizer like `jieba`.
- **Fully offline**: Only `math`, `re`, and `collections` from stdlib.

### Limitations

- No semantic understanding — it's purely statistical.
- May miss the "main idea" if it's expressed in common vocabulary.
- Output is a concatenation of full sentences, so it may slightly exceed
  the target character count.

## Output example

```
============================================================
SUMMARY
============================================================
教育體系也開始重視傳統工藝的傳承。語言與文化密不可分。然而，隨著華語成為主要溝通語言，許多母語逐漸式微。飲食文化同樣是傳統文化的重要組成部分。從夜市小吃到精緻料理，每一道菜餚都蘊含著歷史與記憶。許多老字號餐廳堅持使用傳統工法製作，保留了最道地的味道。在數位時代，如何保存與傳承傳統文化成為重要課題。
============================================================
Character count: 149
Target range:    50-150 chars
Status:          ✓ PASS
============================================================
```
