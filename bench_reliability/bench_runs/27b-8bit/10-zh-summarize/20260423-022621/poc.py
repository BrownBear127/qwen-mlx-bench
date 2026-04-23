"""
Minimal offline Traditional Chinese (繁體中文) summarizer.
Uses extractive summarization via TF-IDF on character bigrams,
ranked by sentence importance. No network, no external deps.
"""

import math
import re
from collections import Counter


# ── Sample article (≥500 chars of coherent Traditional Chinese) ──────────
ARTICLE = """
傳統工藝在現代社會中面臨著前所未有的挑戰與機遇。隨著工業化與數位化的快速發展，許多手工技藝逐漸被機械生產所取代，導致匠人精神與文化傳承出現斷層。然而，近年來人們開始重新審視手工製品的獨特價值，認為每一件手工作品都承載著匠人的心血與情感，這是量產商品無法取代的。

在設計領域，許多創作者開始將傳統工藝元素融入現代產品中，創造出兼具文化底蘊與實用性的作品。例如，將傳統木雕技藝應用於家具設計，或是將刺繡圖案轉化為時尚配飾的靈感來源。這種跨領域的融合不僅讓傳統工藝獲得新的生命力，也為現代設計注入了深厚的文化內涵。

語言與文字作為文化傳承的重要載體，同樣面臨著數位時代的衝擊。繁體中文作為華人社會的重要文化資產，其獨特的字形結構與書寫美學蘊含著深厚的歷史底蘊。在數位排版與字型設計中，如何保留繁體字的藝術美感，同時兼顧閱讀的便利性，成為設計師們持續探索的課題。

飲食文化亦是傳統與現代交融的重要場域。台灣的美食文化融合了閩南、客家、原住民以及日本等多種文化元素，形成了獨具特色的飲食傳統。從夜市小吃到精緻料理，每一道菜餚都承載著世代累積的烹飪智慧與文化記憶。近年來，許多年輕廚師開始重新詮釋傳統菜色，以創新的手法呈現經典風味，讓傳統美食在當代社會中煥發新的光彩。

總體而言，傳統文化在現代社會中的傳承與創新，需要我們以開放的心態去接納與實踐。只有在尊重傳統基礎上的創新，才能真正讓文化薪火相傳，生生不息。
"""


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using common Chinese punctuation."""
    # Split on Chinese sentence-ending punctuation
    parts = re.split(r'([。！？\n])', text)
    sentences: list[str] = []
    for i in range(0, len(parts) - 1, 2):
        s = parts[i].strip() + (parts[i + 1] if i + 1 < len(parts) else '')
        s = s.strip()
        if s:
            sentences.append(s)
    # Handle trailing text without punctuation
    if len(parts) % 2 == 1 and parts[-1].strip():
        sentences.append(parts[-1].strip())
    return sentences


def _char_bigrams(sentence: str) -> list[str]:
    """Extract character bigrams from a sentence (ignoring punctuation)."""
    cleaned = re.sub(r'[^\u4e00-\u9fff\u3400-\u4dbf]', '', sentence)
    return [cleaned[i:i + 2] for i in range(len(cleaned) - 1)]


def _tfidf_rank(sentences: list[str]) -> list[tuple[str, float]]:
    """
    Rank sentences by TF-IDF score on character bigrams.
    Higher score = more distinctive/important content.
    """
    if not sentences:
        return []

    # Build document frequency: how many sentences contain each bigram
    df: Counter = Counter()
    sentence_bigrams: list[list[str]] = []
    for s in sentences:
        bgs = _char_bigrams(s)
        sentence_bigrams.append(bgs)
        for bg in set(bgs):
            df[bg] += 1

    n_docs = len(sentences)

    # Score each sentence
    scored: list[tuple[str, float]] = []
    for s, bgs in zip(sentences, sentence_bigrams):
        if not bgs:
            scored.append((s, 0.0))
            continue
        tf: Counter = Counter(bgs)
        score = 0.0
        for bg, count in tf.items():
            tf_val = count / len(bgs)
            idf_val = math.log((1 + n_docs) / (1 + df[bg])) + 1  # smoothed IDF
            score += tf_val * idf_val
        # Normalize by sentence length to avoid bias toward long sentences
        score /= math.sqrt(len(bgs))
        scored.append((s, score))

    return scored


def summarize(text: str, target_chars: int = 100) -> str:
    """
    Extractive summarizer: pick the most informative sentences
    (by TF-IDF on character bigrams) until we reach ~target_chars.
    Returns sentences in original order for readability.
    """
    sentences = _split_sentences(text)
    if not sentences:
        return ""

    # Rank by TF-IDF
    ranked = _tfidf_rank(sentences)

    # Sort by score descending, pick top sentences
    ranked.sort(key=lambda x: x[1], reverse=True)

    # Greedily pick sentences until we approach target
    selected: set[int] = set()
    total_chars = 0
    for s, _ in ranked:
        if total_chars + len(s) <= target_chars + 50:  # allow some overshoot
            selected.add(s)
            total_chars += len(s)
        if total_chars >= target_chars:
            break

    # Return selected sentences in original order
    result_parts = [s for s in sentences if s in selected]
    return "".join(result_parts)


def main():
    result = summarize(ARTICLE)
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(result)
    print("=" * 60)
    print(f"Character count: {len(result)}")
    print(f"Original length: {len(ARTICLE)}")
    print(f"Compression ratio: {len(result) / len(ARTICLE) * 100:.1f}%")


if __name__ == "__main__":
    main()
