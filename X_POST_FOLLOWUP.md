# X post follow-up — reply thread

**Reply to**: https://x.com/voiceless2501/status/2045213825788706988
**Attach to tweet 2**: `results_comparison.png`

---

## Tweet 1/4

Ran n=3 + two more workload axes to stress-test this. Stability holds (both 210/210 clean now). Speed story gets a lot more nuanced than 40%.

---

## Tweet 2/4  [📎 attach results_comparison.png]

All n=3, M4 Max 128GB, temp=0.0:

• Prefill-heavy agent bench: Q8 GGUF actually +5% faster (123s vs 130s)
• Pure decode (84t → 1500t out): DWQ +47% (87.6 vs 59.7 tok/s)
• Real research workflow (Hermes + Brave): DWQ -15% wall-clock, -36% tool calls

---

## Tweet 3/4

Lesson: the original bench was a loop of short completions against growing history → prefill-dominant, which favored llama.cpp's Metal kernels. Real agents have long per-turn outputs where DWQ's decode dominates. Bench shape can mislead.

---

## Tweet 4/4

Qwen3.6 flat 4-bit control also didn't classic-degrade — #1011 prose-as-tool-call leaks absent. But 1 empty-response soft-miss in 70 rounds vs DWQ's 0.

Updated repo + data + chart: github.com/BrownBear127/qwen-mlx-bench

Thanks for the patience.

---

## Alternative: Single consolidated post

If 4-tweet thread feels too heavy for a follow-up:

> Follow-up after n=3 + 3 axes on M4 Max:
>
> • Prefill-heavy bench: Q8 GGUF +5%
> • Pure decode: DWQ +47%
> • Real research workflow: DWQ -15% wall, -36% tool calls
>
> Both 210/210 clean. My bench shape was prefill-dominant — misled on headline speed. DWQ still wins real decode-heavy work.
>
> Updated: github.com/BrownBear127/qwen-mlx-bench

---

## Notes for posting

- Thread under original post → author-reply gets visibility boost for original's audience
- Do NOT quote-tweet: would re-amplify the "40%" headline without immediate correction context
- Tag @Prince_Canuma only if calling out new thanks; original already thanked him
- Attach chart on tweet 2 (where the numbers land)
