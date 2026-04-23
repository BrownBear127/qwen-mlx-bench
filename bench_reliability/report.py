"""Aggregate bench_runs/ results into a comparison report."""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

from rich.console import Console
from rich.table import Table

REPO_ROOT = Path(__file__).resolve().parent
RUNS_DIR = REPO_ROOT / "bench_runs"


def collect(model: str | None = None) -> dict[str, list[dict]]:
    """Returns {model_label: [latest result per topic]}."""
    out: dict[str, list[dict]] = defaultdict(list)
    if not RUNS_DIR.exists():
        return out
    for model_dir in sorted(RUNS_DIR.iterdir()):
        if not model_dir.is_dir():
            continue
        if model and model_dir.name != model:
            continue
        for topic_dir in sorted(model_dir.iterdir()):
            if not topic_dir.is_dir():
                continue
            runs = sorted(topic_dir.glob("*/_result.json"))
            if not runs:
                continue
            latest = runs[-1]
            try:
                out[model_dir.name].append(json.loads(latest.read_text()))
            except Exception:
                continue
    return out


def model_summary(results: list[dict]) -> dict:
    if not results:
        return {}
    completion = sum(1 for r in results if r.get("completion")) / len(results)
    gates_passed = sum(sum(1 for g in r.get("gates", []) if g.get("passed")) for r in results)
    gates_total = sum(len(r.get("gates", [])) for r in results)
    turns = [r.get("turns", 0) for r in results]
    tool_calls = [r.get("tool_calls", 0) for r in results]
    tool_errors = [r.get("tool_errors", 0) for r in results]
    times = [r.get("wall_time_s", 0) for r in results]
    aborted = [r for r in results if r.get("aborted")]
    fail_first_gate = defaultdict(int)
    for r in results:
        for g in r.get("gates", []):
            if not g.get("passed"):
                fail_first_gate[g["gate_id"]] += 1
                break
    return {
        "topics_run": len(results),
        "completion_rate": round(completion, 3),
        "gate_pass_rate": round(gates_passed / gates_total, 3) if gates_total else 0,
        "mean_turns": round(mean(turns), 1) if turns else 0,
        "mean_tool_calls": round(mean(tool_calls), 1) if tool_calls else 0,
        "tool_error_rate": round(sum(tool_errors) / sum(tool_calls), 3) if sum(tool_calls) else 0,
        "stuck_loop_rate": round(sum(1 for t in turns if t >= 18) / len(turns), 3) if turns else 0,
        "aborted_rate": round(len(aborted) / len(results), 3),
        "mean_wall_time_s": round(mean(times), 1) if times else 0,
        "first_failed_gate": dict(fail_first_gate),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=None, help="Filter to one model label")
    ap.add_argument("--json", action="store_true", help="Emit raw JSON")
    args = ap.parse_args()

    data = collect(args.model)
    summaries = {m: model_summary(rs) for m, rs in data.items()}

    if args.json:
        print(json.dumps(summaries, ensure_ascii=False, indent=2))
        return

    console = Console()

    overview = Table(title="Reliability bench — model overview", show_lines=True)
    overview.add_column("Model")
    overview.add_column("Topics", justify="right")
    overview.add_column("Completion", justify="right")
    overview.add_column("Gate pass", justify="right")
    overview.add_column("Mean turns", justify="right")
    overview.add_column("Tool err %", justify="right")
    overview.add_column("Stuck %", justify="right")
    overview.add_column("Abort %", justify="right")
    overview.add_column("Mean wall (s)", justify="right")
    for model, s in summaries.items():
        if not s:
            continue
        overview.add_row(
            model,
            str(s["topics_run"]),
            f"{s['completion_rate']*100:.0f}%",
            f"{s['gate_pass_rate']*100:.0f}%",
            f"{s['mean_turns']}",
            f"{s['tool_error_rate']*100:.1f}%",
            f"{s['stuck_loop_rate']*100:.0f}%",
            f"{s['aborted_rate']*100:.0f}%",
            f"{s['mean_wall_time_s']}",
        )
    console.print(overview)

    for model, results in data.items():
        per_topic = Table(title=f"{model} — per-topic detail")
        per_topic.add_column("Topic")
        per_topic.add_column("Score", justify="right")
        per_topic.add_column("Pass?")
        per_topic.add_column("Turns", justify="right")
        per_topic.add_column("Wall (s)", justify="right")
        per_topic.add_column("Failed gates")
        for r in sorted(results, key=lambda x: x.get("topic_id", "")):
            failed = [g["gate_id"] for g in r.get("gates", []) if not g.get("passed")]
            per_topic.add_row(
                r.get("topic_id", "?"),
                f"{r.get('score', 0):.2f}",
                "✅" if r.get("completion") else ("🟡" if r.get("score", 0) >= 0.5 else "❌"),
                str(r.get("turns", 0)),
                str(r.get("wall_time_s", 0)),
                ", ".join(failed) or "—",
            )
        console.print(per_topic)


if __name__ == "__main__":
    main()
