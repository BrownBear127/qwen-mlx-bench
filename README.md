# Qwen3.6-35B-A3B Multi-turn Tool Calling: DWQ MLX vs Q8_K_XL GGUF

**Date**: 2026-04-18
**Hardware**: Apple M4 Max, 128GB unified memory
**Methodology**: Replicates [mlx-lm issue #1011](https://github.com/ml-explore/mlx-lm/issues/1011) on the newer Qwen3.6 generation.

## TL;DR

**`mlx-community/Qwen3.6-35B-A3B-4bit-DWQ` does NOT exhibit the multi-turn tool-calling degradation that issue #1011 reported for Qwen3.5-35B-A3B flat 4-bit/8-bit MLX checkpoints.** Over 70 synthetic research-agent rounds, DWQ emitted structured `tool_calls` in every single round with zero plain-text tool-call leakage, matching Q8_K_XL GGUF (llama-server) stability while running **40% faster** end-to-end.

## Results

| Config | Rounds clean | First degradation | Total time | Avg/turn | Tool calls |
|---|---|---|---|---|---|
| Q8_K_XL GGUF (llama-server, `--jinja`, `preserve_thinking=true`) | **70/70** | none | 129.0 s | 1.8 s | 70 |
| **4-bit DWQ MLX (mlx_lm.server 0.31.2)** | **70/70** | **none** | **77.0 s** | **1.1 s** | 73 |

For reference, issue #1011 on Qwen3.5-35B-A3B:
- mlx-community 4-bit: degraded at **round 5**
- mlx-community 8-bit: degraded at **round 13**
- unsloth UD Q4_K_XL GGUF: 70/70 clean
- Cloud full-precision: 70/70 clean

## Method

Synthetic research-agent task with 5 fake tools (`search`, `read_page`, `take_note`, `compare`, `finish_topic`) over 10 topics (Kenya Hara's white, Ma, wabi-sabi, Dieter Rams, etc.). Temperature 0.0, max_tokens 2000.

Per round, the harness sends the conversation (system + user + assistant + tool messages so far), receives the assistant's next message, and classifies it as:

- **Structured**: `message.tool_calls` array populated
- **Degraded**: no structured tool_calls AND `message.content` matches one of 5 leak regexes (e.g. `\[Tool call:`, prose `I will call search(...)`, code-fence JSON pretending to be a tool call)

Fake tool responses are deterministic JSON keyed by query/URL so the model has a consistent state machine to reason over.

Harness: [`bench.py`](./bench.py). Full logs: [`results_q8kxl_70rounds.json`](./results_q8kxl_70rounds.json), [`results_dwq_70rounds.json`](./results_dwq_70rounds.json).

## Key signals

- **Finish reasons**: 70/70 `tool_calls` for both configs (never `length`, `stop`, or `content_filter`)
- **Content leakage regexes**: zero matches across 140 total rounds
- **Parallel tool calls**: DWQ emitted 2 tool_calls in 3 rounds (2, 5, 11); Q8 strictly 1 per round
- **Time stability**: DWQ avg stayed flat ~1.0-1.1s from round 11-70 (no runaway growth). Q8 drifted from 1.5s early to 2.0s late — normal KV cache growth.

## Hypothesis

DWQ (Dynamic Weight Quantization) works as a distillation-based calibration: the quantized weights are fine-tuned to match the full-precision teacher's logits on a calibration dataset. This appears to be sufficient to preserve MoE gate layer precision well enough that structured output (including `<tool_call>` XML tags parsed by the Qwen chat template) stays intact under multi-turn accumulation.

Flat 4-bit/8-bit quantization (issue #1011) applied naive uniform quantization across all weights, which likely destabilized gate routing in the MoE — the `num_experts_activated=8` gate outputs amplify small numerical errors into wrong-expert selection, which cascades into degraded structured-output discipline.

## Reproduction

```bash
git clone https://github.com/your-fork/qwen-mlx-bench  # or copy bench.py
cd qwen-mlx-bench

# Terminal 1: Q8_K_XL via llama-server (your preferred GGUF backend)
llama-server -m /path/to/Qwen3.6-35B-A3B-UD-Q8_K_XL.gguf \
  --jinja --chat-template-kwargs '{"preserve_thinking":true}' \
  --port 8810 -c 262144 --temp 0.0

# Terminal 2: DWQ via mlx_lm.server
uv run mlx_lm.server --model mlx-community/Qwen3.6-35B-A3B-4bit-DWQ \
  --host 127.0.0.1 --port 8811

# Terminal 3: bench
uv run python bench.py \
  --endpoint "Q8_K_XL_GGUF=http://127.0.0.1:8810/v1|qwen3.6-q8kxl" \
  --endpoint "DWQ_MLX=http://127.0.0.1:8811/v1|mlx-community/Qwen3.6-35B-A3B-4bit-DWQ" \
  --rounds 70 \
  --out results.json
```

## Caveats

- **M4 Max** benchmarks; M5 with Neural Accelerators likely widens the MLX speed advantage further (Ollama 0.19 reports 93% decode speedup on M5 for Qwen3.5 NVFP4)
- **Synthetic task** — fake tools, deterministic responses. Real-world agents with Brave/scrape tools may stress different failure modes (network latency, long tool outputs, tool error paths)
- **Single run per config** — would benefit from n=3 to get error bars, but degradation in #1011 was deterministic and early (round 5), so single runs are indicative
- **Not rigorously seed-controlled**: temperature 0.0 should be deterministic but mlx_lm/llama.cpp sampling determinism can vary under thread scheduling
- Q8_K_XL vs 4-bit DWQ is not quant-for-quant — a fair counterpart for DWQ on the GGUF side would be unsloth UD Q4_K_XL, which memory limits prevented testing here but #1011 already confirmed 70/70 clean

## Credits

- DWQ technique by [Prince Canuma (@Prince_Canuma)](https://x.com/Prince_Canuma/status/1978581825615216712) and the mlx-lm team
- Qwen3.6 by the Alibaba Qwen team
- Unsloth UD quant scheme (GGUF side) by Unsloth.AI
- Issue #1011 original reporter: [LotusDecoder](https://github.com/ml-explore/mlx-lm/issues/1011)
