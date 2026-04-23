#!/usr/bin/env python3
"""
Minimal offline extractive summarizer for Traditional Chinese (繁體中文).

Approach: TF-IDF on character bigrams to rank sentences, then pick the
top-scoring sentences until we reach ~100 characters.

No network, no external dependencies — pure Python stdlib.
"""

import re
import math
from collections import Counter


# ── Sample article (≥500 chars of coherent Traditional Chinese) ──────────

ARTICLE = """
設計是一種將想法轉化為具體形式的過程。在當代的設計領域中，我們不僅要考慮美觀，更要重視功能性與使用者體驗。好的設計應該能夠解決問題，同時帶來愉悅的感受。

文化是一個社會的核心，它影響著人們的行為、價值觀與生活方式。每個地區都有其獨特的文化特色，這些特色透過語言、藝術、食物與傳統節慶等方式傳承下來。在多元文化共存的今天，理解與尊重不同文化變得尤為重要。

寫作是一種表達思想與情感的藝術。透過文字，作者可以將內心的想法傳達給讀者，引發共鳴與思考。無論是小說、散文還是詩歌，寫作都需要作者具備敏銳的觀察力與豐富的想像力。好的作品往往能夠跨越時間與空間，觸動不同時代讀者的內心。

工藝是人類智慧的結晶，它將原材料轉化為具有實用價值與美學價值的成品。從陶瓷、木雕到織布、鑄鐵，每一種工藝都蘊含著匠人的心血與技藝。在機械化生產普及的今天，手工工藝的價值更顯珍貴，因為它代表了人與物之間的情感連結。

語言是人類溝通的橋樑，也是文化傳承的重要載體。世界上有數千種語言，每一種都承載著獨特的思維方式與世界觀。學習不同語言不僅能夠擴展我們的視野，還能增進對其他文化的理解與包容。在全球化的時代，多語能力成為了一種重要的競爭力。

食物是人類生活中不可或缺的一部分，它不僅提供營養，也承載著文化與情感。每一道菜餚都反映了當地的歷史、地理與生活方式。從台灣的夜市小吃到法國的精緻料理，食物成為連接人與人的紐帶，也成為探索不同文化的窗口。

在當代的社會中，設計、文化、寫作、工藝、語言與食物這些領域相互交織，共同構成了我們豐富多彩的生活。理解這些領域的本質，有助於我們更好地欣賞生活中的美好，並在多元世界中找到自己的位置。
"""


def _segment_sentences(text: str) -> list[str]:
    """Split text into sentences using common Chinese punctuation."""
    # Chinese sentence terminators: 。！？
    # Also handle newlines as potential sentence boundaries
    parts = re.split(r'[。！？\n]+', text)
    return [p.strip() for p in parts if p.strip()]


def _char_bigrams(sentence: str) -> list[str]:
    """Extract character bigrams from a sentence."""
    return [sentence[i:i+2] for i in range(len(sentence) - 1)]


def _build_idf(sentences: list[str]) -> dict[str, float]:
    """Build inverse document frequency for character bigrams."""
    n_docs = len(sentences)
    bigram_doc_freq: Counter = Counter()

    for sent in sentences:
        unique_bigrams = set(_char_bigrams(sent))
        for bg in unique_bigrams:
            bigram_doc_freq[bg] += 1

    idf: dict[str, float] = {}
    for bg, df in bigram_doc_freq.items():
        idf[bg] = math.log((n_docs + 1) / (df + 1)) + 1  # smoothed IDF

    return idf


def _score_sentence(sentence: str, idf: dict[str, float]) -> float:
    """Score a sentence by summing IDF values of its bigrams, normalized by length."""
    bigrams = _char_bigrams(sentence)
    if not bigrams:
        return 0.0
    score = sum(idf.get(bg, 1.0) for bg in bigrams)
    # Normalize by sentence length to avoid bias toward longer sentences
    return score / len(sentence)


def summarize(text: str, target_chars: int = 100) -> str:
    """
    Extractive summarization: rank sentences by TF-IDF on character bigrams,
    then greedily pick top-scoring sentences until we reach ~target_chars.
    """
    sentences = _segment_sentences(text)
    if not sentences:
        return ""

    idf = _build_idf(sentences)

    # Score and sort sentences (descending)
    scored = [(s, _score_sentence(s, idf)) for s in sentences]
    scored.sort(key=lambda x: x[1], reverse=True)

    # Greedy selection: pick sentences until we're in the 50-150 char range
    summary_parts: list[str] = []
    total_len = 0
    for sent, _ in scored:
        if total_len + len(sent) > target_chars + 50:
            break
        summary_parts.append(sent)
        total_len += len(sent)

    result = "".join(summary_parts)

    # Safety clamp: if somehow too long, truncate; if too short, pad with next best
    if len(result) > 150:
        result = result[:150]
    elif len(result) < 50 and len(sentences) > len(summary_parts):
        # Add more sentences from the scored list
        for sent, _ in scored:
            if sent not in summary_parts:
                if len(result) + len(sent) > 150:
                    break
                result += sent
                summary_parts.append(sent)
                if len(result) >= 50:
                    break

    return result


def main() -> None:
    result = summarize(ARTICLE)
    print("=" * 60)
    print("Original article length:", len(ARTICLE), "characters")
    print("-" * 60)
    print("Summary:")
    print(result)
    print("-" * 60)
    print("Summary length:", len(result), "characters")
    print("=" * 60)


if __name__ == "__main__":
    main()
