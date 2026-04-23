"""
Minimal offline Traditional Chinese (繁體中文) summarizer.

Approach: Extractive summarization via TF-IDF on character bigrams.
- Splits text into sentences (by 。！？\n).
- Scores each sentence by the average TF-IDF of its character bigrams.
- Selects the top-k sentences whose combined length is ~100 characters.
- No network calls, no external dependencies — pure Python stdlib.
"""

import re
from collections import Counter


# ── Sample article (≥500 chars of coherent Traditional Chinese) ──────────
ARTICLE = """
在當今數位時代，設計已不再僅是美學的追求，更是文化與功能的橋樑。
好的設計能夠在無聲中傳達訊息，讓使用者在不知不覺中感受到便利與溫暖。
從傳統工藝到現代科技，設計的演變反映了人類對美好生活的不懈追求。

台灣作為一個多元文化交融的島嶼，其設計風格獨具特色。
從台北的現代建築到台南的傳統街區，每一處都蘊含著深厚的歷史底蘊。
設計師們在保留傳統元素的同時，也不斷融入創新理念，創造出既具本土特色又符合國際趨勢的作品。

在設計教育方面，台灣的多所大學都設有相關科系，培養新一代的設計人才。
這些學生不僅學習技術技能，更被鼓勵去思考設計背後的社會意義。
他們的作品常常展現出對環境、文化與人性的深刻關懷。

語言是文化的載體，而文字則是語言的具體呈現。
繁體中文作為華人社會的重要文化資產，其書寫系統承載了數千年的歷史與智慧。
每一個漢字都蘊含著豐富的意象與哲理，是中華文化不可或缺的一部分。

在數位化浪潮中，如何保存與傳承繁體中文的書寫美學，成為了一個重要的課題。
許多設計師與學者致力於將傳統書法與現代設計相結合，創造出新的視覺語言。
這種跨領域的嘗試不僅豐富了設計的可能性，也為文化傳承開闢了新的途徑。

總而言之，設計、文化與語言三者相互交織，共同構成了人類文明的瑰麗圖景。
在追求創新的同時，我們也應不忘回望傳統，從中汲取靈感與智慧。
唯有如此，我們才能在變遷的世界中，找到屬於自己的文化根脈。
"""


def split_sentences(text: str) -> list[str]:
    """Split text into sentences using common Chinese punctuation."""
    # Split on Chinese sentence-ending punctuation and newlines
    parts = re.split(r'[。！？\n]', text)
    # Filter out empty/whitespace-only parts
    return [s.strip() for s in parts if s.strip()]


def get_bigrams(sentence: str) -> list[str]:
    """Extract character bigrams from a sentence."""
    return [sentence[i:i+2] for i in range(len(sentence) - 1)]


def compute_tf(sentence: str) -> dict[str, float]:
    """Term frequency: count of each bigram / total bigrams in sentence."""
    bigrams = get_bigrams(sentence)
    if not bigrams:
        return {}
    counts = Counter(bigrams)
    total = len(bigrams)
    return {b: c / total for b, c in counts.items()}


def compute_idf(sentences: list[str]) -> dict[str, float]:
    """Inverse document frequency across all sentences."""
    n_docs = len(sentences)
    if n_docs == 0:
        return {}
    # Count how many sentences contain each bigram
    bigram_doc_freq: dict[str, int] = Counter()
    for s in sentences:
        unique_bigrams = set(get_bigrams(s))
        for b in unique_bigrams:
            bigram_doc_freq[b] += 1
    # IDF = log(N / df) + 1  (smoothed to avoid zero)
    import math
    return {b: math.log(n_docs / df) + 1 for b, df in bigram_doc_freq.items()}


def score_sentence(sentence: str, idf: dict[str, float]) -> float:
    """Score a sentence by average TF-IDF of its bigrams."""
    tf = compute_tf(sentence)
    if not tf:
        return 0.0
    score = sum(tf[b] * idf.get(b, 1.0) for b in tf)
    return score / len(tf)  # average TF-IDF


def summarize(text: str, target_chars: int = 100) -> str:
    """
    Extractive summarizer: pick top sentences by TF-IDF bigram score
    until we reach roughly target_chars characters.
    """
    sentences = split_sentences(text)
    if not sentences:
        return ""

    # Compute IDF across all sentences
    idf = compute_idf(sentences)

    # Score each sentence
    scored = [(score_sentence(s, idf), s) for s in sentences]

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # Greedily pick sentences until we reach target length
    selected: list[str] = []
    total_len = 0
    for _, s in scored:
        if total_len + len(s) > target_chars + 50:  # allow some overshoot
            break
        selected.append(s)
        total_len += len(s)

    # If we still have room, add one more sentence
    if total_len < target_chars - 20:
        for _, s in scored:
            if s not in selected:
                selected.append(s)
                total_len += len(s)
                break

    return " ".join(selected)


def main():
    result = summarize(ARTICLE)
    print("=== 摘要 (Summary) ===")
    print(result)
    print(f"\n字數 (Character count): {len(result)}")


if __name__ == "__main__":
    main()
