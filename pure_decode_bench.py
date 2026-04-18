"""
Pure decode throughput benchmark — isolates generation speed from prompt prefill.

Uses streaming API to measure:
  - TTFT (time to first token)  → prompt processing cost
  - decode tok/s = (N-1) / (elapsed - TTFT)  → pure generation speed

Small prompt (~100 tokens), long output (1500 max_tokens), no tools.
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

PROMPT = (
    "Write a detailed 1200-word essay on the aesthetic philosophy of Kenya Hara, "
    "covering 'white' as emptiness, 'ma' as interval, the sensory design of Muji, "
    "and the concept of 'haptic' in his curated exhibitions. Do not use bullet points; "
    "write flowing prose in the style of a thoughtful design critic. Begin immediately."
)

@dataclass
class DecodeRun:
    label: str
    endpoint: str
    model: str
    ttft_s: float
    total_elapsed_s: float
    output_tokens: int
    prompt_tokens: int | None
    decode_tok_s: float
    prefill_tok_s: float | None


async def one_run(label: str, endpoint: str, model: str, max_tokens: int = 1500) -> DecodeRun:
    client = openai.AsyncOpenAI(base_url=endpoint, api_key="bench")
    t0 = time.time()
    ttft = None
    output_token_count = 0
    usage_prompt_tokens = None
    usage_completion_tokens = None

    stream = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": PROMPT}],
        max_tokens=max_tokens,
        temperature=0.0,
        stream=True,
        stream_options={"include_usage": True},
    )
    async for chunk in stream:
        if ttft is None and chunk.choices and chunk.choices[0].delta.content:
            ttft = time.time() - t0
        if chunk.choices and chunk.choices[0].delta.content:
            output_token_count += 1  # approx — 1 token per chunk
        if getattr(chunk, "usage", None):
            usage_prompt_tokens = chunk.usage.prompt_tokens
            usage_completion_tokens = chunk.usage.completion_tokens

    elapsed = time.time() - t0
    out_tokens = usage_completion_tokens or output_token_count
    decode_time = max(elapsed - (ttft or 0), 0.001)
    decode_tps = (out_tokens - 1) / decode_time if out_tokens > 1 else 0.0
    prefill_tps = (usage_prompt_tokens / ttft) if (usage_prompt_tokens and ttft) else None

    return DecodeRun(
        label=label,
        endpoint=endpoint,
        model=model,
        ttft_s=round(ttft or 0, 3),
        total_elapsed_s=round(elapsed, 3),
        output_tokens=out_tokens,
        prompt_tokens=usage_prompt_tokens,
        decode_tok_s=round(decode_tps, 2),
        prefill_tok_s=round(prefill_tps, 1) if prefill_tps else None,
    )


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", action="append", required=True,
                        help="label=url|model")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=1500)
    parser.add_argument("--out", type=str, default="results_pure_decode.json")
    args = parser.parse_args()

    all_results: list[DecodeRun] = []
    for spec in args.endpoint:
        label, rest = spec.split("=", 1)
        endpoint, model = rest.split("|", 1)
        console.rule(f"[bold]{label}  —  {endpoint}")
        for i in range(1, args.runs + 1):
            r = await one_run(f"{label}_run{i}", endpoint, model, args.max_tokens)
            console.print(
                f"  run {i}: prompt={r.prompt_tokens}t, out={r.output_tokens}t, "
                f"ttft={r.ttft_s}s, total={r.total_elapsed_s}s, "
                f"decode={r.decode_tok_s} tok/s, prefill={r.prefill_tok_s} tok/s"
            )
            all_results.append(r)

    table = Table(title="Pure decode benchmark — Qwen3.6-35B-A3B")
    for col in ["Label", "TTFT (s)", "Prompt tok", "Output tok", "Total (s)", "Decode tok/s", "Prefill tok/s"]:
        table.add_column(col)
    for r in all_results:
        table.add_row(
            r.label,
            f"{r.ttft_s}",
            str(r.prompt_tokens),
            str(r.output_tokens),
            f"{r.total_elapsed_s}",
            f"{r.decode_tok_s}",
            str(r.prefill_tok_s) if r.prefill_tok_s else "—",
        )
    console.rule("Summary")
    console.print(table)

    # Aggregated per label
    by_label: dict[str, list[DecodeRun]] = {}
    for r in all_results:
        key = r.label.rsplit("_run", 1)[0]
        by_label.setdefault(key, []).append(r)
    agg = Table(title="Averages per endpoint")
    for col in ["Endpoint", "Avg decode tok/s", "Avg prefill tok/s", "Avg TTFT (s)"]:
        agg.add_column(col)
    for key, runs in by_label.items():
        avg_dec = sum(r.decode_tok_s for r in runs) / len(runs)
        valid_pref = [r.prefill_tok_s for r in runs if r.prefill_tok_s]
        avg_pref = (sum(valid_pref) / len(valid_pref)) if valid_pref else None
        avg_ttft = sum(r.ttft_s for r in runs) / len(runs)
        agg.add_row(
            key,
            f"{avg_dec:.2f}",
            f"{avg_pref:.1f}" if avg_pref else "—",
            f"{avg_ttft:.2f}",
        )
    console.print(agg)

    Path(args.out).write_text(json.dumps([asdict(r) for r in all_results], indent=2, ensure_ascii=False))
    console.print(f"\nFull log → [cyan]{args.out}[/cyan]")


if __name__ == "__main__":
    asyncio.run(main())
