"""
Offline extractive summarizer for Traditional Chinese (繁體中文).
Uses sentence scoring based on character n-gram frequency — no external dependencies.
"""

import re
import math
from collections import Counter

ARTICLE = (
    "台灣的飲食文化深受多元族群的影響，融合了閩南、客家、原住民以及日本殖民時期留下的烹飪傳統。"
    "夜市是台灣最具代表性的美食場景之一，從北部的士林夜市到南部的六合夜市，每一攤都承載著數十年的手藝與記憶。"
    "滷肉飯被許多人視為台灣的國民美食，一碗看似簡單的米飯上淋著以醬油、五香粉和紅蔥頭慢燉而成的肉燥，"
    "香氣濃郁且層次豐富。珍珠奶茶則是台灣對全球飲品文化最顯著的貢獻，起源於一九八零年代的台中，"
    "如今已風靡世界各地。除了街頭小吃，台灣的辦桌文化同樣值得關注：在婚喪喜慶等重要場合，"
    "總鋪師會在戶外搭起棚架，現場烹製十二道大菜，從佛跳牆到紅蟳米糕，每一道都展現了廚師的功力與對賓客的敬意。"
    "近年來，台灣也興起了一股精緻餐飲的浪潮，不少主廚將在地食材與法式或日式技法結合，"
    "創造出兼具本土風味與國際水準的料理。這種新舊交融的飲食景觀，正是台灣文化活力的最佳寫照。"
)


def summarize(text: str, target_len: int = 100) -> str:
    """Return an extractive summary of roughly *target_len* characters.

    Algorithm
    ---------
    1. Split text into sentences on Chinese punctuation.
    2. Build a TF-IDF-like score per sentence using character bigrams.
    3. Greedily pick top-scoring sentences (in original order) until the
       budget is reached, trimming the last sentence if needed.
    """
    # --- sentence splitting on Chinese full stops / question / exclamation ---
    sentences = [s.strip() for s in re.split(r"[。！？]", text) if s.strip()]

    if not sentences:
        return text[:target_len]

    # --- bigram document frequency ---
    def bigrams(s):
        return [s[i : i + 2] for i in range(len(s) - 1)]

    sent_bigrams = [bigrams(s) for s in sentences]
    doc_freq = Counter()
    for bg_list in sent_bigrams:
        doc_freq.update(set(bg_list))

    n_docs = len(sentences)

    # --- score each sentence via TF-IDF of its bigrams ---
    scores = []
    for idx, (sent, bg_list) in enumerate(zip(sentences, sent_bigrams)):
        if not bg_list:
            scores.append(0.0)
            continue
        tf = Counter(bg_list)
        score = sum(
            (1 + math.log(c)) * math.log(n_docs / doc_freq[bg])
            for bg, c in tf.items()
        )
        # normalise by length so short sentences aren't penalised
        score /= len(bg_list)
        # small positional boost for the first and last sentences
        if idx == 0 or idx == n_docs - 1:
            score *= 1.3
        scores.append(score)

    # --- pick top sentences in original order ---
    ranked = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)

    chosen = []
    budget = target_len
    for idx in sorted(ranked):          # restore original order
        sent = sentences[idx]
        if idx not in ranked[: len(sentences)]:
            continue
        if budget <= 0:
            break
        if len(sent) <= budget:
            chosen.append(sent)
            budget -= len(sent)
        elif not chosen:                # first pick — trim to fit
            chosen.append(sent[:budget])
            budget = 0

    summary = "。".join(chosen)
    # ensure we stay within a comfortable window
    if len(summary) > target_len + 20:
        summary = summary[: target_len]
    return summary


if __name__ == "__main__":
    result = summarize(ARTICLE)
    print(f"Summary ({len(result)} chars):\n{result}")
