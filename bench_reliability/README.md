# Reliability Bench — Qwen3.6-27B Unattended Workflow Test

A personal-use reliability test harness for **unattended local LLM workflows** on Apple Silicon.

Tests whether a model can be trusted to run autonomously (cron-triggered, no human in the loop) and produce verifiable output, rather than peak coding quality.

This is **not** SWE-bench / Terminal-Bench — those measure peak ability. This measures whether the model **finishes**, **doesn't loop**, **doesn't drift**, and **leaves real artifacts** in a sandbox.

📝 Companion writeup: [pending — link will be added when X post goes live]

---

## What's in this directory

```
bench_reliability/
├── topics/                      10 YAML topics, each probes one fail mode
│   ├── 01-vector-db.yaml
│   ├── 02-pdf-parser.yaml
│   ├── 03-sqlite-migration.yaml
│   ├── 04-md-to-epub.yaml
│   ├── 05-otel-collector-vs-sdk.yaml
│   ├── 06-rss-dedupe.yaml
│   ├── 07-fragile-install-fallback.yaml
│   ├── 08-llm-serving-table.yaml
│   ├── 09-svg-diff.yaml
│   └── 10-zh-summarize.yaml
├── runner.py                    Agent loop (OpenAI tool-calling, sandbox isolation)
├── ceiling_runner.py            Opus 4.7 (via SSH+tmux) + Codex (GPT-5) wrapper
├── verifier.py                  5 hard-gate types (URL reachable, py_compile, exit_code, regex, keyword)
├── tools.py                     6-tool minimal toolset for fairness across models
├── report.py                    Cross-model comparison table
├── run_all.sh                   Run all topics for one (model, endpoint, model_id)
├── run_full_batch.sh            6-model batch driver (main)
├── run_followup_batch.sh        DWQ + mxfp4 + mxfp8 follow-up
├── run_ceiling_batch.sh         Opus / Codex ceiling
└── bench_runs/                  All 80 sandbox results (8 model × 10 topic)
    ├── 27b-6bit/
    ├── 27b-8bit/
    ├── 27b-mxfp4/
    ├── 27b-mxfp8/
    ├── 35b-a3b-q8kxl/           HauhauCS uncensored Q8 (daily 英克 backend)
    ├── 35b-a3b-dwq-vanilla/     mlx-community official 4bit DWQ
    ├── opus-4-7/                Opus 4.7 via Claude Pro subscription
    └── gpt-codex/               GPT-5 via Codex CLI / ChatGPT Pro
```

Each `bench_runs/{model}/{topic}/{timestamp}/` holds:
- `_result.json` — gates passed/failed, turns, wall_time, tool_calls
- `_transcript.jsonl` (or `_transcript.txt` for ceiling) — full agent loop trace
- `poc.py` / `README.md` / `requirements.txt` — agent-generated artifacts

---

## Quick start

```bash
# Install deps (uv)
cd .. && uv sync

# Run a single topic on local mlx-lm.server
.venv/bin/python bench_reliability/runner.py \
  --model-label 27b-8bit \
  --endpoint http://127.0.0.1:8820/v1 \
  --model-id mlx-community/Qwen3.6-27B-8bit \
  --topic bench_reliability/topics/01-vector-db.yaml

# Run all 10 topics for one model
cd bench_reliability && ./run_all.sh 27b-8bit http://127.0.0.1:8820/v1 mlx-community/Qwen3.6-27B-8bit

# View comparison report
.venv/bin/python report.py
```

For ceiling baseline (Opus / Codex):

```bash
# Codex (local, ChatGPT Pro subscription)
./run_ceiling_batch.sh gpt-codex codex

# Opus (SSH+tmux, Claude Pro subscription, requires `tmux ceiling` session on remote)
./run_ceiling_batch.sh opus-4-7 claude opus
```

---

## Design principles

1. **Hard gates only**, no LLM-as-a-judge — judge models bias toward SOTA training distribution
2. **Same 6-tool set across all models** (web_search, web_fetch, read_file, write_file, list_dir, run_bash) — fair comparison
3. **Each POC isolated in `uv run --no-project --with-requirements` sandbox** — install + run + 60s timeout + discard
4. **10 topics each probe one fail mode** (cross-platform trap, misleading same-name tools, error recovery, stdlib only, etc.) — not random
5. **Verifier strips `VIRTUAL_ENV` from subprocess env** — avoids inheriting bench harness venv into POC test

---

## Caveat: framework bias on SOTA models

The `search_quality` gate greps the transcript for reachable URLs. Local mlx-lm models use the explicit `web_search` tool I provide, so URLs end up in the transcript. **Opus 4.7 and Codex use their own builtin WebSearch — those URLs don't reach the final transcript**, so the gate systematically fails.

This means SOTA completion numbers in the report **understate their real ability**. The bench is honest about this in the writeup, and explains why I didn't "fix" it (every fix introduces a new bias). See the writeup for full discussion.

---

## License

Apache 2.0 (matching the Qwen3.6-27B model license).
