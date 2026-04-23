#!/usr/bin/env python3
"""
Minimal offline extractive summarizer for Traditional Chinese (繁體中文).

Approach:
  1. Split the article into sentences using Chinese sentence-ending punctuation
     (。！？；).
  2. Score each sentence by:
     - TF-IDF on character bigrams (2-grams) to capture topical importance.
     - Position bonus: sentences near the beginning and end of the article
       tend to contain topic sentences or conclusions.
  3. Rank sentences by combined score, pick the top ones, and reassemble
     them in original order.
  4. Truncate / pad to roughly 100 characters.

Constraints met:
  - Pure Python stdlib (re, math, collections)
  - No network calls, no external packages
  - Works on Traditional Chinese text
"""

import re
import math
from collections import Counter

# ── Sample Traditional Chinese article (≥500 chars) ──────────────────────────
SAMPLE_ARTICLE = """
台灣的文化資產非常豐富，從傳統工藝到現代藝術都有獨特的發展軌跡。
在台北的巷弄裡，你可以找到百年歷史的老店，這些店家傳承了數代人的技藝，
將傳統美食與文化完美結合。例如，傳統的糕餅製作工藝，從選材、調配到烘烤，
每一個步驟都經過精心設計，確保最終成品的口感與風味達到最佳狀態。

除了美食之外，台灣的傳統音樂與舞蹈也是文化資產的重要組成部分。
北管音樂、歌仔戲、原住民的祭典舞蹈，都展現了台灣多元文化的特色。
近年來，政府積極推動文化復興計畫，補助各地舉辦傳統節慶活動，
讓年輕一代有機會接觸並了解這些珍貴的文化遺產。

在設計領域，台灣設計師將傳統元素融入現代產品中，創造出獨特的風格。
他們善用台灣的自然景觀與人文特色，將文化符號轉化為視覺語言，
讓國際市場看到台灣設計的創新與美感。這種文化與設計的結合，
不僅提升了產品的附加價值，也加深了人們對台灣文化的認識。

總之，台灣的文化資產涵蓋了飲食、音樂、舞蹈、工藝、設計等多個面向，
每一項都是台灣人民智慧與創意的結晶。保護與傳承這些文化資產，
是每個台灣人的責任，也是我們面向未來的重要基礎。
"""


# ── Helpers ──────────────────────────────────────────────────────────────────

def split_sentences(text: str) -> list[str]:
    """Split text into sentences on Chinese sentence-ending punctuation."""
    # Split on 。！？； and keep the delimiter attached
    raw = re.split(r'([。！？；])', text)
    sentences: list[str] = []
    for i in range(0, len(raw), 2):
        s = raw[i]
        if i + 1 < len(raw):
            s += raw[i + 1]  # reattach the punctuation
        s = s.strip()
        if s:
            sentences.append(s)
    return sentences


def char_bigrams(text: str) -> list[str]:
    """Return character-level bigrams from text."""
    return [text[i:i+2] for i in range(len(text) - 1)]


def compute_tfidf(sentences: list[str]) -> dict[int, float]:
    """
    Compute a simple TF-IDF score for each sentence using character bigrams.
    TF  = count of bigram in sentence / total bigrams in sentence
    IDF = log(N / df) where df = number of sentences containing the bigram
    Score = sum of TF*IDF for all bigrams in the sentence
    """
    N = len(sentences)
    if N == 0:
        return {}

    # Document frequency for each bigram
    df: Counter = Counter()
    for sent in sentences:
        bigrams = set(char_bigrams(sent))
        df.update(bigrams)

    # Per-sentence scores
    scores: dict[int, float] = {}
    for idx, sent in enumerate(sentences):
        bigrams = char_bigrams(sent)
        if not bigrams:
            scores[idx] = 0.0
            continue
        total_bigrams = len(bigrams)
        sent_score = 0.0
        for bg in bigrams:
            tf = 1.0 / total_bigrams  # normalize by sentence length
            idf = math.log(N / df[bg]) if df[bg] > 0 else 0.0
            sent_score += tf * idf
        scores[idx] = sent_score
    return scores


def position_bonus(idx: int, total: int) -> float:
    """
    Give a small bonus to sentences near the beginning or end of the article,
    since they often contain topic sentences or conclusions.
    """
    if total <= 1:
        return 0.0
    norm = idx / (total - 1)  # 0..1
    # Peak at both ends (0 and 1), minimum in the middle
    return max(0.0, 1.0 - abs(norm - 0.5) * 2) * 0.3


def summarize(text: str, target_chars: int = 100) -> str:
    """
    Extractive summarizer for Traditional Chinese text.

    Returns a summary of roughly `target_chars` characters.
    """
    sentences = split_sentences(text)
    if not sentences:
        return ""

    # If the article is already short enough, return it as-is
    full_len = sum(len(s) for s in sentences)
    if full_len <= target_chars:
        return text.strip()

    # Score sentences
    tfidf_scores = compute_tfidf(sentences)
    total = len(sentences)

    # Combined score = TF-IDF + position bonus
    combined: list[tuple[float, int]] = []
    for idx in range(total):
        score = tfidf_scores.get(idx, 0.0) + position_bonus(idx, total)
        combined.append((score, idx))

    # Sort by score descending; pick top-K sentences
    combined.sort(key=lambda x: x[0], reverse=True)
    k = max(1, len(sentences) // 3)  # pick roughly top third
    selected_indices = sorted([idx for _, idx in combined[:k]])

    # Reassemble in original order
    summary = "".join(sentences[i] for i in selected_indices)

    # Truncate to target length (prefer complete sentences)
    if len(summary) > target_chars:
        # Try to cut at a sentence boundary
        cut = 0
        for i, s in enumerate(sentences):
            if i not in selected_indices:
                continue
            if cut + len(s) > target_chars:
                break
            cut += len(s)
        summary = summary[:cut]

    return summary.strip()


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    result = summarize(SAMPLE_ARTICLE, target_chars=100)
    print("=== Summary ===")
    print(result)
    print(f"\n=== Character count: {len(result)} ===")
