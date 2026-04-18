# X post — "Don't pick one quant, split by role" (architecture proposal)

**When to post**: after yesterday's follow-up thread (https://x.com/voiceless2501/status/2045213825788706988 reply) has been live a day or two — lets the numeric correction settle before introducing the architecture story.

**Standalone thread** — do not reply-chain to previous. Different narrative (constructive architecture proposal, not defensive number correction).

**Attach**: `results_comparison.png` on tweet 2.

---

## Tweet 1/5

Follow-up to my Qwen3.6-A3B DWQ vs Q8 thread — the practical upshot: don't pick one quant, split by role.

Q8_K_XL as main agent + DWQ as compression sidekick = 44% faster compression wait, full feature set preserved.

## Tweet 2/5  [📎 attach results_comparison.png]

Compression bench (68K prompt + 1.2K output, n=3, M4 Max):
• Q8: 84.6s avg
• DWQ: 47.3s avg
−44% wall-clock

Cold-prefill run alone: 180s → 100s. DWQ wins the long-prompt cold-prefill regime, not just decode.

## Tweet 3/5

Why? Metal GPU is memory-bandwidth-bound on Apple Silicon. 4-bit weights halve read bandwidth vs 8-bit → prefill of fresh long prompts finishes faster on DWQ. Q8's kernel advantage only shows through when prefill is already KV-cached (short-turn agent loops).

## Tweet 4/5

The deployment split, all via Hermes Agent config:

- Q8 on :8810 → main model (vision/mmproj, agent quality, KV cache)
- DWQ on :8811 as launchd daemon → auxiliary.compression.base_url
- RAM cost: ~19GB resident on 128GB Mac. Both stable 210/210 on tool-calling bench.

## Tweet 5/5

Practical rule: Q8 wins only on prefill-cached short-turn loops (agent bench: +5%). Everything else — pure decode, real research workflow, long cold-prefill compression — DWQ.

Takeaway: run both, assign by workload.

Repo + bench code: github.com/BrownBear127/qwen-mlx-bench

---

## Notes

- Tag @Prince_Canuma? Only if new to him (already thanked in original + follow-up).
- Hermes Agent (@NousResearch) might engage — the architectural split is exactly what their `auxiliary.compression` field was designed for, and this is probably the first public bench proving it pays off. Consider mentioning @NousResearch.
- Chart (panel 4 specifically) is the headline image. Could also just post panel 4 alone for punchier visual — but full 4-panel gives context and shows this is one branch of a larger bench story.
