"""
Minimal POC: Extractive summarization of Traditional Chinese articles.
Uses sentence-level TF-IDF on character bigrams to rank importance,
then selects top sentences and concatenates them into a ~100-char summary.
Fully offline, stdlib only.
"""

import math
import re
import sys

# ── Sample Traditional Chinese article (≥500 chars) ──────────────────────
ARTICLE = """
傳統工藝在現代社會中扮演著重要的角色，它不僅是文化傳承的載體，
更是人類智慧與創造力的體現。許多匠人終其一生專精於一項技藝，
從選材、設計到製作，每一個步驟都凝聚著他們的心血與堅持。
在臺灣，傳統工藝的發展與地方文化緊密相連，例如竹編、陶藝、木雕
等技藝，都是當地居民世代相傳的珍貴資產。隨著時代的變遷，
許多傳統工藝面臨著傳承斷層的危機，但也同時孕育出新的契機。
一些年輕設計師開始將傳統元素融入現代產品中，讓古老技藝重新
獲得關注。政府與民間團體也積極推動文化保存計畫，透過教育、
展覽與工作坊等方式，讓更多人認識並體驗傳統工藝的魅力。
除了工藝之外，傳統食物的製作同樣承載著深厚的文化意義。
從手工釀造的醬油到古法烘焙的糕餅，每一道料理背後都有著
不可取代的故事。這些飲食文化不僅是味蕾的享受，更是家族記憶
與鄉土情感的連結。在快節奏的現代生活中，放慢腳步品味傳統
美食，成為許多人重新認識自己文化根源的方式。未來，傳統工藝
與飲食文化能否在現代社會中持續發揚光大，取決於我們是否
願意投入資源與心力，讓這些珍貴的文化遺產得以延續。
此外，數位科技的進步也為傳統工藝帶來新的可能，
透過網路平台，匠人們可以將作品展示給全世界的觀眾。
"""

# ── Helpers ──────────────────────────────────────────────────────────────

def split_sentences(text: str) -> list[str]:
    """Split Chinese text into sentences on common delimiters."""
    parts = re.split(r'([。！？；\n])', text)
    sentences: list[str] = []
    buf = ""
    for part in parts:
        buf += part
        if part.strip() and part.strip() in "。！？；\n":
            sentences.append(buf.strip())
            buf = ""
    if buf.strip():
        sentences.append(buf.strip())
    return sentences


def char_bigrams(text: str) -> list[str]:
    """Return character bigrams (sliding window of 2)."""
    return [text[i:i+2] for i in range(len(text) - 1)]


def build_tfidf(sentences: list[str]) -> dict[int, float]:
    """
    Compute a simple TF-IDF score per sentence using character bigrams.
    TF  = count of bigram in sentence / total bigrams in sentence
    IDF = log(N / (1 + doc_freq))
    """
    N = len(sentences)
    # document frequency for each bigram
    df: dict[str, int] = {}
    for sent in sentences:
        bgs = set(char_bigrams(sent))
        for bg in bgs:
            df[bg] = df.get(bg, 0) + 1

    scores: dict[int, float] = {}
    for idx, sent in enumerate(sentences):
        bgs = char_bigrams(sent)
        total = len(bgs)
        if total == 0:
            scores[idx] = 0.0
            continue
        tfidf = 0.0
        seen: set[str] = set()
        for bg in bgs:
            if bg in seen:
                continue
            seen.add(bg)
            tf = bgs.count(bg) / total
            idf = math.log(N / (1 + df[bg]))
            tfidf += tf * idf
        scores[idx] = tfidf
    return scores


def summarize(text: str, target_chars: int = 100) -> str:
    """
    Extractive summarizer:
      1. Split text into sentences.
      2. Rank sentences by TF-IDF (char bigrams).
      3. Pick top sentences (greedy, preserving original order).
      4. Truncate to ~target_chars.
    """
    sentences = split_sentences(text)
    if not sentences:
        return ""
    if len(sentences) == 1:
        return sentences[0][:target_chars]

    scores = build_tfidf(sentences)

    # Select top ~40% of sentences (at least 1)
    n_select = max(1, len(sentences) * 40 // 100)
    ranked = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)
    selected = sorted(ranked[:n_select])  # keep original order

    summary = "".join(sentences[i] for i in selected)

    # If too long, truncate at a sentence boundary
    if len(summary) > target_chars + 20:
        trimmed = ""
        for s in sentences:
            if s in [sentences[i] for i in selected]:
                if len(trimmed) + len(s) > target_chars:
                    break
                trimmed += s
        summary = trimmed

    return summary


# ── Main ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    summary = summarize(ARTICLE)
    print(f"Summary ({len(summary)} chars):")
    print(summary)
    print(f"\nOriginal article: {len(ARTICLE)} chars")
