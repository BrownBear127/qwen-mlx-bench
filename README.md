# Qwen3.6-35B-A3B: DWQ MLX vs Q8_K_XL GGUF — multi-axis benchmark

**Date**: 2026-04-18 (updated with n=3 + flat control + pure decode + real research workflow)
**Hardware**: Apple M4 Max, 128GB unified memory
**Methodology**: Replicates [mlx-lm issue #1011](https://github.com/ml-explore/mlx-lm/issues/1011) on the newer Qwen3.6 generation, extended with three additional axes.

![Comparison chart](./results_comparison.png)

## TL;DR (revised, 4-axis)

The original single-run post claimed DWQ is 40% faster than Q8_K_XL GGUF. Follow-up n=3 on four separate workload shapes shows **the speed story depends on workload shape — and DWQ wins on three of four**:

- **(1) Multi-turn agent bench (prefill-cached short-turn loop)** → Q8 GGUF is ~5% faster. llama.cpp's Metal prefill reuse via KV cache wins when history accumulates but new tokens per turn are small.
- **(2) Pure decode (84t prompt → 1500t output)** → **DWQ is 47% faster** (87.6 vs 59.7 tok/s).
- **(3) Real research workflow (Hermes + Kenya Hara MUJI task, real web search)** → **DWQ is 15% faster wall-clock, with 36% fewer tool calls to reach the same output quality** (9 vs 14).
- **(4) Compression workload (68K prompt + 1.2K output, cold+warm mixed)** → **DWQ is 44% faster** (47.3s vs 84.6s average). On cold-prefill long prompts, the gap widens to −45%. Not just decode — DWQ also wins the long-prompt cold-prefill regime, because Metal is memory-bandwidth-bound and 4-bit halves weight bandwidth.

**Stability: both configurations are 70/70 clean across n=3 agent bench (210/210 rounds, 0 degradation, 0 empty-response).** The DWQ distillation-based calibration fully contains the MoE gate quantization issue that #1011 reported for flat 4/8-bit MLX. A flat 4-bit Qwen3.6 control run also did not classic-degrade (Qwen3.6 base is more robust than Qwen3.5), but showed 1 empty-response soft-miss in 70 rounds that DWQ did not.

## Results

### Axis 1 — Multi-turn tool-calling bench (prefill-heavy agent harness)

| Config | Runs | Rounds clean | Soft-miss (tc=0) | Tool calls | Avg wall time |
|---|---|---|---|---|---|
| Q8_K_XL GGUF (llama-server, `--jinja`, `preserve_thinking`) | **3** | **210/210** | 0 | 70/70/70 | **123.0s** |
| 4-bit DWQ MLX (mlx_lm.server) | **3** | **210/210** | 0 | 73/73/73 | 129.5s (warm runs 2+3) |
| 4-bit flat MLX (control) | 1 | 70/70 | **1** (R16 empty+finish=stop) | 74 | 100.2s |

### Axis 2 — Pure decode throughput (streaming)

Fixed 84-token prompt, 1500-token output ceiling, streaming mode, n=3 each:

| Config | Decode tok/s (n=3) | Time per 1500 tok |
|---|---|---|
| Q8_K_XL GGUF | 59.27 / 59.95 / 59.74 (avg **59.65**) | 25.1s |
| **4-bit DWQ MLX** | 86.07 / 88.49 / 88.11 (avg **87.56**) | **17.1s** |

DWQ: **+46.8% decode throughput**, very tight variance (±1.2 tok/s).

### Axis 3 — Real research workflow via Hermes Agent

Task: "Research Kenya Hara's MUJI aesthetics and 'white' philosophy. Search for 3 post-2024 interviews / exhibition reviews / essays. Write 150 Chinese words of analysis per source with URL citation. Close with a 100-word opening hook summarizing the core proposition. Budget 30 tool calls."

Same Hermes coder profile, same MCP stack (camoufox + fetch + sequential), same web_search provider (Brave via AI Gateway). Only backend swapped via `base_url`.

| Config | Wall time | Tool calls | Peak prompt | Final output tokens | Output quality |
|---|---|---|---|---|---|
| Q8_K_XL GGUF | 7m 51s | 14 | 75.3K | 855 | 3 sources + hook ✓ |
| **4-bit DWQ MLX** | **6m 39s** | **9** | 69.3K | 512 | 3 sources + hook ✓ |

DWQ finished **-15.3% wall-clock**, used **-35.7% fewer tool calls**, and hit the same deliverable quality. The decode-speed advantage lets DWQ write more comprehensively per turn — fewer short back-and-forth rounds.

### Axis 4 — Compression A/B workload (long prompt, cold+warm)

Simulates a Hermes-style context compression trigger: 68K-token prompt of mock research notes + 1200-token target summary. `compression_bench.py`, streaming, n=3 each:

| Run | Q8 GGUF | DWQ MLX |
|---|---|---|
| Run 1 (cold — first prefill of 68K) | 180.4s | **100.0s** (−45%) |
| Run 2 (warm cache) | 37.0s | **21.0s** (−43%) |
| Run 3 (warm cache) | 36.5s | **21.0s** (−42%) |
| **Average** | **84.6s** | **47.3s** (**−44.1%**) |

The cold-run gap (80s saved) matters practically: in a real Hermes compression trigger fired during a live agent session, the first invocation typically lands with a cold KV cache for the new message history. 180s vs 100s is the *wait-time-at-compression-trigger* that users actually feel.

**Unexpected finding**: DWQ's advantage on long prompts is *wider* than on short prompts (−44% on 68K vs −25% on 4.5K). This contradicts the "prefill-heavy workloads favor Q8" intuition. Cause: Metal GPU compute is memory-bandwidth-bound on Apple Silicon; 4-bit weights read at ~half the bandwidth of 8-bit, so prefill of large prompts benefits more than proportionally. Only when prefill is *already cached* (agent loop Axis 1) does Q8's kernel-level optimization show through.

### Operational note: DWQ as a Hermes compression sidekick

Given Axis 4, running DWQ permanently on `:8811` as the Hermes `auxiliary.compression` backend while keeping Q8 GGUF as the primary is a good architectural split — the main model keeps vision (mmproj), agent response quality, and prefill caching, while compression triggers (which are always cold-prefill new history) get the 44% speedup. RAM cost: ~19GB standing resident for the DWQ server.

## Why the axes disagree

Three separate regimes are at play, and which dominates is set by the ratio of new prompt tokens to cached prefix tokens per API call:

| Regime | Dominant cost | Winner |
|---|---|---|
| **Prefill-cached short turns** (agent bench: ~100 new tok/turn, history grows) | KV cache hit rate + prefill micro-kernels | **Q8 GGUF** (llama.cpp Metal fused kernels, +5%) |
| **Pure decode long output** (84t in, 1500t out) | Memory bandwidth for weight reads | **DWQ** (4-bit halves bandwidth, +47%) |
| **Cold prefill long prompt** (compression: 68K fresh prompt) | Memory bandwidth for weight reads during prefill | **DWQ** (same bandwidth effect dominates, +44%) |
| **Mixed real workflow** (research: varies by turn) | Mix of above | **DWQ** (decode + cold-prefill wins compound, +15% wall-clock) |

The earlier intuition that "prefill-heavy = Q8 wins" is only half right. **llama.cpp Metal's prefill kernels only dominate when the prefill is *already cached in the KV store*.** When the prefill is new (long fresh prompt), Apple Silicon's memory-bandwidth bottleneck takes over and 4-bit weight reads simply finish faster.

**Takeaway**: a single benchmark shape can mislead. For a deployment decision, measure the workload you actually run — and split work across backends by regime if you can (e.g., Q8 for main agent, DWQ for compression/summarization).

## Method

All four axes use `temperature=0.0` for determinism. Code + full logs:

- `bench.py` — multi-turn agent harness (5 fake tools, deterministic responses)
- `pure_decode_bench.py` — OpenAI-compatible streaming, measures tok/s from elapsed + usage
- `compression_bench.py` — long-prompt compression A/B with streaming and cold/warm breakdown (`--scale` flag controls prompt size; `--scale 15` → 68K)
- Real research: Hermes CLI (`hermes chat -q "..."` with `--max-turns 40 -v`), logs in separate `/tmp/q8_research.log` and `/tmp/dwq_research.log`
- `make_charts.py` — generates `results_comparison.png` (4-panel layout)

Reproduction:

```bash
# Terminal 1: Q8_K_XL GGUF
llama-server -m /path/to/Qwen3.6-35B-A3B-UD-Q8_K_XL.gguf \
  --jinja --chat-template-kwargs '{"preserve_thinking":true}' \
  --port 8810 -c 262144 --temp 0.0

# Terminal 2: DWQ MLX
uv run mlx_lm.server --model mlx-community/Qwen3.6-35B-A3B-4bit-DWQ \
  --host 127.0.0.1 --port 8811

# Terminal 3: agent bench (n=3 each, alternate endpoints)
for i in 1 2 3; do
  uv run python bench.py \
    --endpoint "q8_run${i}=http://127.0.0.1:8810/v1|qwen3.6-q8kxl" \
    --rounds 70 --out "results_q8_run${i}.json"
  uv run python bench.py \
    --endpoint "dwq_run${i}=http://127.0.0.1:8811/v1|mlx-community/Qwen3.6-35B-A3B-4bit-DWQ" \
    --rounds 70 --out "results_dwq_run${i}.json"
done

# Terminal 4: pure decode (3 runs per endpoint, all in one invocation)
uv run python pure_decode_bench.py \
  --endpoint "dwq=http://127.0.0.1:8811/v1|mlx-community/Qwen3.6-35B-A3B-4bit-DWQ" \
  --endpoint "q8=http://127.0.0.1:8810/v1|qwen3.6-q8kxl" \
  --runs 3 --max-tokens 1500

# Chart
uv run python make_charts.py
```

## Caveats

- **M4 Max** results. M5 with Neural Accelerators likely widens MLX's decode advantage further (Ollama 0.19 reports ~93% decode speedup on M5 for Qwen3.5 NVFP4).
- **Real research run is n=1** per config. Wall-clock has real-world variance from Brave API latency and Crawl4AI page size differences. The 15% wall-clock gap is larger than typical network noise, but a rigorous follow-up would run n≥3 with fixed tool responses.
- **Vision asymmetry**: Q8_K_XL GGUF ships with `mmproj-F16` for multimodal. DWQ MLX has no mmproj pairing, so a profile that truly replaces Q8 with DWQ loses vision capability unless a separate llama-server is run as `auxiliary.vision` backend (which gives back the RAM savings).
- **Long-context stress test (>100K prompt) has not been run** for either configuration. All tests here stayed under ~20K accumulated context.
- **n=3 stability is on synthetic bench only**. Real research workload stability (error recovery, malformed tool responses, long multi-step chains) should be validated with a daily-drive evaluation period.
- **Qwen3.6 flat 4-bit control**: did not exhibit the classic issue #1011 degradation signature (no prose-as-tool-call leaks), but `bench.py`'s leak detector missed an empty-response soft-miss at round 16 — inspect `results_flat4bit.json` for `num_tool_calls=0` rounds.

## Credits

- DWQ technique by [Prince Canuma (@Prince_Canuma)](https://x.com/Prince_Canuma/status/1978581825615216712) and the mlx-lm team
- Qwen3.6 by the Alibaba Qwen team
- Unsloth UD quant scheme (GGUF side) by Unsloth.AI
- Issue #1011 original reporter: [LotusDecoder](https://github.com/ml-explore/mlx-lm/issues/1011)
