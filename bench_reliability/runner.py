"""Run a single (model, topic) pair through agent loop + verification."""
from __future__ import annotations
import argparse
import json
import shutil
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml
import openai

from tools import TOOL_SCHEMAS, dispatch
from verifier import run_all_gates

REPO_ROOT = Path(__file__).resolve().parent
RUNS_DIR = REPO_ROOT / "bench_runs"

SYSTEM_PROMPT = """You are an autonomous coding agent. You complete the user's task by using the provided tools.

Rules:
- All file operations are in your sandbox directory. Use relative paths.
- When running shell commands, prefer `uv run --no-project --with <lib> python <script>` for Python work.
- When you have completed all required deliverables, respond with a brief summary and stop.
- Do not call tools you don't need. Be efficient.
- If a tool call fails, try one alternative approach before giving up.
"""


@dataclass
class RunResult:
    model: str
    topic_id: str
    sandbox_dir: str
    turns: int = 0
    tool_calls: int = 0
    tool_errors: int = 0
    wall_time_s: float = 0.0
    finish_reason: str = ""
    final_message: str = ""
    transcript_path: str = ""
    gates: list[dict] = field(default_factory=list)
    completion: bool = False
    score: float = 0.0
    aborted: str = ""


def _serialize(msg: dict) -> dict:
    """Clean message dict for JSON dump (drop non-serializable openai objects)."""
    out: dict = {"role": msg["role"]}
    for k in ("content", "tool_call_id", "name"):
        if k in msg:
            out[k] = msg[k]
    if "tool_calls" in msg and msg["tool_calls"]:
        out["tool_calls"] = [
            {
                "id": tc.id if hasattr(tc, "id") else tc.get("id"),
                "type": "function",
                "function": {
                    "name": tc.function.name if hasattr(tc, "function") else tc["function"]["name"],
                    "arguments": tc.function.arguments if hasattr(tc, "function") else tc["function"]["arguments"],
                },
            }
            for tc in msg["tool_calls"]
        ]
    return out


def run_one(
    model_label: str,
    endpoint: str,
    model_id: str,
    topic_path: Path,
    api_key: str = "bench",
    extra_request_args: dict | None = None,
) -> RunResult:
    topic = yaml.safe_load(topic_path.read_text())
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    sandbox = RUNS_DIR / model_label / topic["id"] / timestamp
    sandbox.mkdir(parents=True, exist_ok=True)

    result = RunResult(
        model=model_label,
        topic_id=topic["id"],
        sandbox_dir=str(sandbox),
    )
    transcript_path = sandbox / "_transcript.jsonl"
    full_text_buf: list[str] = []

    client = openai.OpenAI(base_url=endpoint, api_key=api_key)
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": topic["prompt"]},
    ]
    full_text_buf.append(topic["prompt"])

    max_turns = topic.get("max_turns", 20)
    deadline = time.time() + topic.get("wall_time_limit_s", 300)
    t0 = time.time()

    for turn in range(1, max_turns + 1):
        result.turns = turn
        if time.time() > deadline:
            result.aborted = "wall_time_limit"
            break
        try:
            resp = client.chat.completions.create(
                model=model_id,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.0,
                max_tokens=4096,
                extra_body={
                    "chat_template_kwargs": {"enable_thinking": False},
                },
                **(extra_request_args or {}),
            )
        except Exception as e:
            result.aborted = f"api_error: {type(e).__name__}: {str(e)[:200]}"
            break

        choice = resp.choices[0]
        msg = choice.message
        msg_dict: dict = {"role": "assistant", "content": msg.content}
        if msg.tool_calls:
            msg_dict["tool_calls"] = msg.tool_calls
        messages.append(msg_dict)

        with transcript_path.open("a") as f:
            f.write(json.dumps(_serialize(msg_dict), ensure_ascii=False) + "\n")
        if msg.content:
            full_text_buf.append(msg.content)

        if not msg.tool_calls:
            result.finish_reason = choice.finish_reason or "stop"
            result.final_message = (msg.content or "")[:2000]
            break

        for tc in msg.tool_calls:
            result.tool_calls += 1
            try:
                args = json.loads(tc.function.arguments or "{}")
            except Exception:
                args = {}
                result.tool_errors += 1
            tool_result = dispatch(tc.function.name, args, str(sandbox))
            tool_msg = {
                "role": "tool",
                "tool_call_id": tc.id,
                "name": tc.function.name,
                "content": tool_result,
            }
            messages.append(tool_msg)
            with transcript_path.open("a") as f:
                f.write(json.dumps(_serialize(tool_msg), ensure_ascii=False) + "\n")
            full_text_buf.append(tool_result[:2000])
            if tool_result.startswith("error:") or tool_result.startswith("fetch error:"):
                result.tool_errors += 1
    else:
        result.aborted = "max_turns"

    result.wall_time_s = round(time.time() - t0, 2)
    result.transcript_path = str(transcript_path)

    ctx = {
        "sandbox_dir": str(sandbox),
        "full_transcript": "\n".join(full_text_buf),
        "poc_stdout": "",
        "poc_stderr": "",
    }
    gates = run_all_gates(topic, ctx)
    result.gates = [asdict(g) for g in gates]
    passed = sum(1 for g in gates if g.passed)
    total = len(gates)
    result.score = round(passed / total, 3) if total else 0.0
    result.completion = passed >= topic.get("scoring", {}).get("pass_threshold", total)

    (sandbox / "_result.json").write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-label", required=True)
    ap.add_argument("--endpoint", required=True, help="OpenAI-compatible base URL")
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--topic", required=True, type=Path)
    ap.add_argument("--api-key", default="bench")
    args = ap.parse_args()

    r = run_one(args.model_label, args.endpoint, args.model_id, args.topic, args.api_key)
    print(json.dumps(asdict(r), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
