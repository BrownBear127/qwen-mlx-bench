"""Minimal offline Traditional Chinese summarization POC."""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import re


ARTICLE = """
在許多城市裡，設計常常被誤解成最後一道包裝工序：顏色要和諧，字體要好看，海報要足夠醒目，產品的外殼不能太笨重。可是對真正長期工作的設計者而言，設計比較像是一種把混亂重新整理的能力。它要先處理關係，再處理表面；先決定什麼值得被看見，然後才決定如何被看見。當一間小店重新安排動線，讓顧客不必在狹窄走道裡互相閃避，那也是設計。當一本書願意為了閱讀節奏留白，而不是把每一寸紙面都塞滿資訊，那也是設計。好的設計不只在物件上留下風格，也在人的行為裡留下秩序。

這種秩序並不冰冷。很多工藝職人其實很清楚，手感與規格並不是互相排斥的兩端。做陶的人知道杯口如果太厚，喝水時嘴唇會先感到阻礙；做木家具的人知道椅背若只追求俐落線條，久坐後肩頸就會暴露設計者沒有真正坐下來想過。於是工藝的細節常常提醒我們：美感不是抽離身體的判決，而是身體在反覆使用之後所留下的誠實記錄。物件之所以耐看，通常不是因為它搶眼，而是因為它在每一次接觸中都沒有冒犯使用者。

寫作也是相似的工作。很多人以為文字的力量來自華麗句子，彷彿修辭越密，思想就越深。但成熟的寫作者往往更重視節奏、轉折與刪除。他知道一段話若沒有真正推進意思，再漂亮也只是裝飾；他知道某個比喻若讓讀者停下來欣賞技巧，卻忘了原本要說的事，那麼這個比喻就失手了。清楚並不等於平淡，節制也不是退縮。真正困難的是在複雜經驗裡找出可共享的形狀，讓讀者在閱讀時感覺自己被尊重，而不是被作者的自我表演拖著走。

語言與食物的關係也很有意思。一道家常菜之所以讓人記住，未必因為味道驚奇，而是因為它在鹹淡、口感、溫度與份量之間取得了一種剛好的平衡。文字也是如此。太滿，讀者會累；太淡，意思又留不住。真正讓人想回頭重讀的文章，往往像慢火熬出的湯，不急著展示技巧，而是把材料彼此牽連出的層次安靜地送到舌尖。表面看起來簡單，背後其實有很多判斷被小心藏起來。

因此，不論是設計器物、經營店面、寫一篇文章，還是準備一頓飯，核心問題都不是「怎樣才顯得厲害」，而是「怎樣才讓人願意長久相處」。能夠陪伴人的作品，通常都懂得收斂。它們不是沒有個性，而是知道個性應該放在何處；不是沒有野心，而是明白野心若不能轉化成照顧，最後只會留下壓迫感。當我們願意把注意力從炫耀移回使用、從表態移回感受，就比較有機會做出真正成熟的東西。
""".strip()

TARGET_LEN = 100
MIN_LEN = 50
MAX_LEN = 150


def split_sentences(text: str) -> list[str]:
    parts = re.findall(r"[^。！？!?；;]+[。！？!?；;]?", text)
    return [part.strip() for part in parts if part.strip()]


def cjk_chars(text: str) -> list[str]:
    return [ch for ch in text if "\u4e00" <= ch <= "\u9fff"]


def bigrams(chars: list[str]) -> list[str]:
    return ["".join(chars[i : i + 2]) for i in range(len(chars) - 1)]


def sentence_score(sentence: str, index: int, doc_grams: Counter[str]) -> tuple[float, list[str]]:
    grams = bigrams(cjk_chars(sentence))
    if not grams:
        return float("-inf"), []

    coverage = sum(doc_grams[gram] for gram in grams) / len(grams)
    lead_bonus = max(0.0, 1.4 - (index * 0.12))
    length_bonus = 1.0 - (abs(len(sentence) - 48) / 120)
    return coverage + lead_bonus + length_bonus, grams


def summarize(text: str, target_len: int = TARGET_LEN) -> str:
    sentences = split_sentences(text)
    doc_grams = Counter(bigrams(cjk_chars(text)))

    scored = [sentence_score(sentence, i, doc_grams) for i, sentence in enumerate(sentences)]
    best_summary = ""
    best_value = float("-inf")

    for size in range(1, min(3, len(sentences)) + 1):
        for combo in combinations(range(len(sentences)), size):
            summary = "".join(sentences[i] for i in combo)
            length = len(summary)
            if not (MIN_LEN <= length <= MAX_LEN):
                continue

            combo_grams = set()
            combo_score = 0.0
            total_grams = 0
            for i in combo:
                score, grams = scored[i]
                combo_score += score
                combo_grams.update(grams)
                total_grams += len(grams)

            diversity_bonus = len(combo_grams) / max(1, total_grams)
            length_penalty = abs(length - target_len) / 40
            value = combo_score + (diversity_bonus * 2.0) - length_penalty

            if value > best_value:
                best_summary = summary
                best_value = value

    if best_summary:
        return best_summary

    fallback = "".join(sentences[:2]).strip()
    return fallback[:MAX_LEN]


if __name__ == "__main__":
    result = summarize(ARTICLE)
    print(result)
    print(f"Character count: {len(result)}")
