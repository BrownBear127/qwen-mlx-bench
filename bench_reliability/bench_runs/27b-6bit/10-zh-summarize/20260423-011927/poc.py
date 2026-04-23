"""
Minimal offline Traditional Chinese (繁體中文) summarizer.
Uses extractive summarization via TF-IDF on character bigrams,
ranked by sentence importance. No network, no external deps.
"""

import math
import re
from collections import Counter


# ── Sample article (≥500 chars of coherent Traditional Chinese) ──

ARTICLE = """
傳統工藝在現代社會中面臨著前所未有的挑戰與機遇。隨著工業化與數位化的快速發展，許多手工技藝逐漸被機械生產所取代，導致匠人數量銳減，傳統技藝面臨失傳的危機。然而，近年來隨著人們對文化認同與生活品質的重視，傳統工藝重新受到關注。

在臺灣，竹編、陶藝、木雕等傳統工藝不僅是文化資產，更是匠人世代傳承的心血結晶。一位竹編師傅通常需要花費十年以上的時間才能精通各種編織技法，從選竹、剖竹到編織，每一個步驟都需要極高的專注與耐心。這些技藝無法透過書本學習，必須透過師徒制的口傳心授才能傳承。

現代設計師開始將傳統工藝元素融入當代產品設計中，創造出兼具美學與實用性的作品。這種跨界合作不僅為傳統工藝注入新生命，也為年輕一代提供了接觸與學習傳統技藝的機會。許多文創品牌透過網路平台將手工藝品推向國際市場，讓世界看見東方工藝的獨特魅力。

教育體系也開始重視傳統工藝的傳承。多所大學設立了工藝設計相關科系，培養兼具傳統技藝與現代設計思維的新一代匠人。同時，各地方政府積極舉辦工藝節慶與工作坊，鼓勵民眾親手體驗傳統技藝的樂趣。

語言與文化密不可分。在臺灣，閩南語、客家語、原住民語等多元語言承載著豐富的文化內涵。然而，隨著華語成為主要溝通語言，許多母語逐漸式微。近年來，政府推動母語教育政策，鼓勵學生學習本土語言，以保存文化多樣性。

飲食文化同樣是傳統文化的重要組成部分。臺灣的飲食融合了閩南、客家、原住民與外省等多種文化特色，形成了獨特的風味。從夜市小吃到精緻料理，每一道菜餚都蘊含著歷史與記憶。許多老字號餐廳堅持使用傳統工法製作，保留了最道地的味道。

在數位時代，如何保存與傳承傳統文化成為重要課題。數位典藏計畫將珍貴的文化資產數位化，讓更多人能夠接觸與了解。同時，社群媒體與網路平台為文化傳承提供了新的管道，讓年輕一代能夠以他們熟悉的方式接觸傳統文化。

總體而言，傳統工藝與文化的保存需要社會各界的共同努力。從政策支持到教育推廣，從產業創新到民眾參與，每一個環節都至關重要。只有在尊重傳統的基礎上進行創新，才能讓文化在現代社會中持續發光發熱。
"""


def tokenize_sentences(text: str) -> list[str]:
    """Split text into sentences using Chinese sentence-ending punctuation."""
    # First normalize: collapse whitespace/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    # Split on 。！？ keeping the delimiter attached to the preceding clause
    raw = re.split(r'([。！？])', text)
    sentences: list[str] = []
    for i in range(0, len(raw) - 1, 2):
        combined = (raw[i] + raw[i + 1]).strip()
        # Only keep sentences with meaningful Chinese characters
        if len(re.findall(r'[\u4e00-\u9fff]', combined)) >= 8:
            sentences.append(combined)
    return sentences


def char_bigrams(sentence: str) -> list[str]:
    """Extract character bigrams from a sentence (Chinese chars only)."""
    chars = re.findall(r'[\u4e00-\u9fff]', sentence)
    return [chars[i] + chars[i + 1] for i in range(len(chars) - 1)]


def compute_tf(sentence: str) -> dict[str, float]:
    """Term frequency: count of each bigram / total bigrams in sentence."""
    bigrams = char_bigrams(sentence)
    if not bigrams:
        return {}
    counts = Counter(bigrams)
    total = len(bigrams)
    return {b: c / total for b, c in counts.items()}


def compute_idf(sentences: list[str]) -> dict[str, float]:
    """Inverse document frequency across all sentences."""
    n = len(sentences)
    doc_freq: Counter = Counter()
    for s in sentences:
        unique_bigrams = set(char_bigrams(s))
        for b in unique_bigrams:
            doc_freq[b] += 1
    return {b: math.log(n / df) for b, df in doc_freq.items()}


def rank_sentences(sentences: list[str], idf: dict[str, float]) -> list[tuple[int, str, float]]:
    """Score each sentence by sum of TF-IDF of its bigrams."""
    scored: list[tuple[int, str, float]] = []
    for idx, s in enumerate(sentences):
        tf = compute_tf(s)
        score = sum(tf.get(b, 0) * idf.get(b, 0) for b in tf)
        # Normalize by sqrt of length to avoid bias toward long sentences
        chars = len(re.findall(r'[\u4e00-\u9fff]', s))
        if chars > 0:
            score /= math.sqrt(chars)
        scored.append((idx, s, score))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored


def summarize(text: str, target_chars: int = 100) -> str:
    """
    Extractive summarizer:
    1. Split into sentences.
    2. Score via TF-IDF on character bigrams.
    3. Greedily pick top-scored sentences until we reach ~target_chars.
    4. Re-order selected sentences by original position for coherence.
    """
    sentences = tokenize_sentences(text)
    if not sentences:
        return text[:target_chars]

    idf = compute_idf(sentences)
    ranked = rank_sentences(sentences, idf)

    # Greedy selection: pick highest-scoring sentences until we hit target
    selected: list[tuple[int, str]] = []
    total_chars = 0
    for idx, s, _ in ranked:
        char_count = len(re.findall(r'[\u4e00-\u9fff]', s))
        if total_chars + char_count > target_chars + 50:
            break
        selected.append((idx, s))
        total_chars += char_count

    # Sort by original position for readability
    selected.sort(key=lambda x: x[0])
    summary = ''.join(s for _, s in selected)

    return summary


def main():
    result = summarize(ARTICLE)
    char_count = len(result)
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(result)
    print("=" * 60)
    print(f"Character count: {char_count}")
    print(f"Target range:    50-150 chars")
    print(f"Status:          {'✓ PASS' if 50 <= char_count <= 150 else '✗ OUT OF RANGE'}")
    print("=" * 60)


if __name__ == '__main__':
    main()
