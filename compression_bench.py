"""
Compression workload A/B bench — Q8 GGUF (:8810) vs DWQ MLX (:8811).

Measures which backend is faster AT THE COMPRESSION TASK SHAPE specifically:
  - long prompt (~40K tokens of mock research notes)
  - medium output (600-word Chinese summary)
  - prefill-heavy — tests if DWQ's decode advantage still pays off

Uses same streaming technique as pure_decode_bench.py:
  - TTFT = prompt processing cost
  - (total_time - TTFT) / output_tokens = decode tok/s
"""
from __future__ import annotations
import argparse
import asyncio
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
import openai
from rich.console import Console
from rich.table import Table

console = Console()

SYSTEM_PROMPT = (
    "你是一個 research compression agent。你的任務是把使用者給的研究筆記壓縮成一份結構化摘要。"
    "輸出必須：(1) 保留所有關鍵事實 (2) 保留決策和 open questions (3) 去除重複資訊 (4) 保持 URL citation。"
    "目標長度：600 字中文，markdown 結構。"
)

# ~40K tokens of mock research notes — simulates what a Hermes compression call looks like
# built from concatenating 5 blocks of ~8K each, distinct enough to test real compression
RESEARCH_NOTES_TEMPLATE = """
## Source {n}: {title} ({date})

{content}

## 中段研究觀察

原研哉「白」哲學的核心不在於「無色」，而在於「容器」。他在多次訪談中反覆提到：白不是感官的缺席，
而是感知的可能性空間。這種論述將西方極簡主義的「減法美學」跟日本傳統的「餘白」區分開來——
前者是對過剩的反抗，後者是對關係的邀請。MUJI 的設計哲學因此不能被視為「性冷淡風」的分支，
而應該理解為一種認識論立場：物件不主動吸引目光，讓使用者的日常成為敘事主體。

關於「Ma」（間），原研哉借用了黑川雅之對「間」的詮釋：間不是空間也不是時間，是兩者之間的張力。
海報設計中 80% 的留白、茶道中的一靜一動、能劇中演員凝止的瞬間——這些都是「間」的體現。
當代設計常犯的錯是把「留白」當作風格符號（比如 white space in web design），而忽略了「間」
本質上是一種對觀者參與的信任。

## Source reference chain

- Primary: Pendulum Magazine, October 19 2025 review of "DRAW" book
- Secondary: Spoon & Tamago coverage of Kyoto ddd Gallery exhibition (March 2026)
- Tertiary: PPAPER interview (紫綬褒章 reception, November 2024)

關鍵引述：「Each line feels less like a conclusion and more like a question」——強調設計作為
不斷提問的實踐，而非給出結論。這個視角跟 MUJI 的產品設計哲學一致：所有物件都在邀請而非訴說。

## Open questions 累積

1. 原研哉的「白」跟 Dieter Rams 的 "Less, but better" 是同源還是不同傳統？前者強調感知容器，
   後者強調功能節制——這個區分是否本質，或者只是表面語言差異？
2. MUJI 作為全球品牌，其設計哲學在跨文化翻譯中有沒有 loss？西方消費者買的是「日式簡約」還是
   「白哲學」——這兩者很可能在實際品牌溝通中被混淆。
3. 當代 AI 介面設計借用了「無印」視覺語彙（大量留白、最少元素），但這跟原研哉的哲學是形式還是
   精神上的延續？

## Historical context

原研哉 1958 年生，武藏野美術大學畢業。1983 年入選原弘會，1991 年加入日本設計中心。
2001 年接任 MUJI art director 至今。2006 年策劃 House Vision 展覽，2013 年《設計中的設計》
出版繁中版。

## Design decisions documented

- 2024 年 DRAW 書出版，首次公開大量原始草圖。決策原因：希望讓觀者看到「思考過程」而非「完成
  作品」，這呼應他「設計是提問不是回答」的立場。
- Kyoto ddd Gallery 決策 2026 年 4-6 月只展原始草稿不展成品。策展目的是對抗數位設計時代的
  「成品崇拜」。
- MUJI 2025 年新增「無印生活」展覽系列，將產品設計擴展到居住場景。這是否代表品牌從「物件」
  轉向「生活方式」？

"""

SOURCES = [
    (1, "Pendulum Magazine — DRAW 書評",
     "2025-10-19",
     "Florence L 撰寫的長篇書評，強調《DRAW》不只是咖啡桌畫冊，而是關於創作者成長的三階段論："
     "初學者追求技術完美、中期在跨界合作中拓展、成熟期以訊息傳達取代形式。書評特別指出 MUJI 的吸引力不在 "
     "'無標籤、低價格'，而在於它所描繪的生活方式。每一條線被框架為 'open question' 而非結論，這是"
     "原研哉跟現代主義 designers 最顯著的差異。"),
    (2, "Spoon & Tamago — DRAW 展覽報導",
     "2026-03-27",
     "京都 ddd Gallery 2026-04-04 到 06-03 展出原研哉所有原始草稿，跨時期、跨專案。策展聲明："
     "'在數位時代替類比過程辯護——不是懷舊，是一種看的方式。' 展覽不展成品海報或品牌識別，"
     "只展思考痕跡。記者特別提到展場沒有文字說明，每張草稿旁邊只有日期編號，強迫觀者自己解讀。"),
    (3, "PPAPER 訪談 — 紫綬褒章受章取材",
     "2024-11-15",
     "原研哉獲頒紫綬褒章後的長篇訪談。談及 MUJI 的 'emptiness container' 概念，強調這不是西方"
     "極簡主義的東方版本，而是基於日本傳統餘白美學的獨立哲學。他也回應了 AI 時代設計師的位置："
     "'設計不是決定形式，是提出感知的可能性。這件事 AI 暫時還做不到。' "
     "訪談後段討論 House Vision 的未來，以及他對年輕設計師的建議：'先學會不設計，再學設計。'"),
    (4, "Dezeen — 原研哉 80 歲大型回顧展前導",
     "2026-02-10",
     "Dezeen 獨家專訪，關於計劃中的大型回顧展。原研哉透露將展出從 1983 年起全部主要作品，"
     "包括早期為武藏野美術大學設計的海報、中期長野冬奧開閉幕式指揮、到 MUJI 20 年演進。他特別"
     "強調想展示 '設計失敗的作品'——那些沒被選用或市場反應不佳的提案，他認為這些展品比成功案例"
     "更能說明設計的本質。"),
    (5, "Wallpaper* — House Vision 2030 前瞻",
     "2026-01-22",
     "關於 House Vision 計畫第六屆（2030 年）的規劃。原研哉將主題定為 'post-ownership house'，"
     "探討共享居住時代的私人空間。展覽將邀請 Muji、Toyota、Sony、Daikin 等公司提案。關鍵設計問題："
     "當物件所有權變薄弱，家還有什麼？他的暫定答案：'家是感知的主場，不是物件的倉庫。' 這個立場"
     "跟他一貫的'容器哲學'一致。"),
]

def build_long_prompt(scale: int = 1) -> str:
    """Assemble long compression input. scale=1 → ~4.5K prompt; scale=15 → ~70K; scale=20 → ~90K."""
    blocks = []
    for iteration in range(scale):
        for n, title, date, content in SOURCES:
            tag = f" [iteration {iteration+1}/{scale}]" if scale > 1 else ""
            blocks.append(RESEARCH_NOTES_TEMPLATE.format(
                n=f"{n}{tag}", title=title, date=date, content=content
            ))
    return "\n\n---\n\n".join(blocks) + "\n\n請根據以上研究筆記，輸出一份 600 字中文結構化摘要。多輪重複的資訊只需壓縮一次。"


@dataclass
class CompressionRun:
    label: str
    endpoint: str
    model: str
    ttft_s: float
    total_elapsed_s: float
    output_tokens: int
    prompt_tokens: int | None
    decode_tok_s: float


async def one_run(label: str, endpoint: str, model: str, prompt: str, max_tokens: int = 1200) -> CompressionRun:
    client = openai.AsyncOpenAI(base_url=endpoint, api_key="bench")
    t0 = time.time()
    ttft = None
    output_token_count = 0
    usage_prompt_tokens = None
    usage_completion_tokens = None

    stream = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.0,
        stream=True,
        stream_options={"include_usage": True},
    )
    async for chunk in stream:
        if ttft is None and chunk.choices and chunk.choices[0].delta.content:
            ttft = time.time() - t0
        if chunk.choices and chunk.choices[0].delta.content:
            output_token_count += 1
        if getattr(chunk, "usage", None):
            usage_prompt_tokens = chunk.usage.prompt_tokens
            usage_completion_tokens = chunk.usage.completion_tokens

    elapsed = time.time() - t0
    out_tokens = usage_completion_tokens or output_token_count
    decode_time = max(elapsed - (ttft or 0), 0.001)
    decode_tps = (out_tokens - 1) / decode_time if out_tokens > 1 else 0.0

    return CompressionRun(
        label=label,
        endpoint=endpoint,
        model=model,
        ttft_s=round(ttft or 0, 3),
        total_elapsed_s=round(elapsed, 3),
        output_tokens=out_tokens,
        prompt_tokens=usage_prompt_tokens,
        decode_tok_s=round(decode_tps, 2),
    )


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", action="append", required=True,
                        help="label=url|model (repeatable)")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--out", type=str, default="results_compression_bench.json")
    parser.add_argument("--save-outputs", action="store_true",
                        help="Save each run's output text for quality comparison")
    parser.add_argument("--scale", type=int, default=1,
                        help="Prompt length multiplier. 1=~4.5K, 15=~70K, 20=~90K")
    args = parser.parse_args()

    prompt = build_long_prompt(args.scale)
    console.print(f"[dim]Prompt length: {len(prompt):,} chars (scale={args.scale})[/dim]")

    all_results: list[CompressionRun] = []
    output_texts: dict[str, list[str]] = {}
    for spec in args.endpoint:
        label, rest = spec.split("=", 1)
        endpoint, model = rest.split("|", 1)
        console.rule(f"[bold]{label}  —  {endpoint}")
        output_texts[label] = []
        for i in range(1, args.runs + 1):
            # For saving outputs we need a non-streaming path; but streaming gave us stats.
            # Re-invoke once at end with non-stream if save-outputs requested.
            r = await one_run(f"{label}_run{i}", endpoint, model, prompt, args.max_tokens)
            console.print(
                f"  run {i}: prompt={r.prompt_tokens}t out={r.output_tokens}t "
                f"ttft={r.ttft_s}s total={r.total_elapsed_s}s decode={r.decode_tok_s} tok/s"
            )
            all_results.append(r)

    if args.save_outputs:
        console.rule("[bold]Capturing output samples")
        for spec in args.endpoint:
            label, rest = spec.split("=", 1)
            endpoint, model = rest.split("|", 1)
            client = openai.OpenAI(base_url=endpoint, api_key="bench")
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=args.max_tokens,
                temperature=0.0,
            )
            output_texts[label] = [resp.choices[0].message.content or ""]
            console.print(f"  [cyan]{label}:[/cyan] {len(output_texts[label][0])} chars")

    table = Table(title="Compression bench — Qwen3.6-35B-A3B (long prompt + medium output)")
    for col in ["Label", "Prompt tok", "TTFT (s)", "Output tok", "Total (s)", "Decode tok/s"]:
        table.add_column(col)
    for r in all_results:
        table.add_row(r.label, str(r.prompt_tokens), f"{r.ttft_s}",
                      str(r.output_tokens), f"{r.total_elapsed_s}", f"{r.decode_tok_s}")
    console.rule("Summary")
    console.print(table)

    by_label: dict[str, list[CompressionRun]] = {}
    for r in all_results:
        key = r.label.rsplit("_run", 1)[0]
        by_label.setdefault(key, []).append(r)
    agg = Table(title="Averages per endpoint")
    for col in ["Endpoint", "Avg TTFT", "Avg total", "Avg decode tok/s", "Effective tok/s (total work)"]:
        agg.add_column(col)
    for key, runs in by_label.items():
        avg_ttft = sum(r.ttft_s for r in runs) / len(runs)
        avg_tot = sum(r.total_elapsed_s for r in runs) / len(runs)
        avg_dec = sum(r.decode_tok_s for r in runs) / len(runs)
        avg_eff = sum(r.output_tokens / r.total_elapsed_s for r in runs) / len(runs)
        agg.add_row(key, f"{avg_ttft:.2f}s", f"{avg_tot:.2f}s", f"{avg_dec:.2f}", f"{avg_eff:.2f}")
    console.print(agg)

    payload = {"runs": [asdict(r) for r in all_results]}
    if args.save_outputs:
        payload["outputs"] = output_texts
    Path(args.out).write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    console.print(f"\nSaved → [cyan]{args.out}[/cyan]")


if __name__ == "__main__":
    asyncio.run(main())
