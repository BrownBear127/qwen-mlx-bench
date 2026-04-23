"""SOTA ceiling baseline runner — wraps `claude --print` (via SSH+tmux) and `codex exec`
to give us OpenAI-style result.json compatible with verifier.py + report.py."""
from __future__ import annotations
import argparse
import json
import re
import shlex
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

from verifier import run_all_gates

REPO_ROOT = Path(__file__).resolve().parent
RUNS_DIR = REPO_ROOT / "bench_runs"


@dataclass
class CeilingResult:
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


def make_local_sandbox(model_label: str, topic_id: str) -> Path:
    ts = time.strftime("%Y%m%d-%H%M%S")
    sandbox = RUNS_DIR / model_label / topic_id / ts
    sandbox.mkdir(parents=True, exist_ok=True)
    return sandbox


def run_codex_exec(prompt: str, sandbox: Path, timeout_s: int) -> tuple[str, float, int]:
    """Run codex exec locally, return (output_text, wall_time_s, exit_code)."""
    codex = str(Path.home() / ".npm-global/bin/codex")
    t0 = time.time()
    try:
        r = subprocess.run(
            [codex, "exec", "--skip-git-repo-check", "--color", "never", "--cd", str(sandbox), prompt],
            capture_output=True, text=True, timeout=timeout_s,
        )
        elapsed = time.time() - t0
        return (r.stdout + "\n[STDERR]\n" + r.stderr)[:50000], elapsed, r.returncode
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT after {timeout_s}s]", time.time() - t0, 124


def run_claude_via_tmux(prompt: str, sandbox: Path, timeout_s: int, model: str = "opus") -> tuple[str, float, int]:
    """Send claude --print to ceiling tmux session on franimac, mirror sandbox via /tmp.
    Uses script-file pipeline (no inline quote escape nightmare)."""
    ts = time.strftime("%Y%m%d-%H%M%S-%f")
    remote_sandbox = f"/tmp/bench_ceiling/{sandbox.parent.name}_{ts}"
    output_file = f"{remote_sandbox}/.claude_output.txt"
    sentinel = f"{remote_sandbox}/.done"
    script_path = f"{remote_sandbox}/.run.sh"
    prompt_path = f"{remote_sandbox}/.prompt.txt"

    subprocess.run(["ssh", "franimac", f"mkdir -p {remote_sandbox}"], check=True, timeout=15)

    subprocess.run(
        ["ssh", "franimac", f"cat > {prompt_path}"],
        input=prompt, text=True, check=True, timeout=15,
    )
    script = f"""#!/bin/bash
cd {remote_sandbox}
~/.local/bin/claude --print --model {model} --add-dir . --permission-mode bypassPermissions -p "$(cat {prompt_path})" > {output_file} 2>&1
echo $? > {sentinel}
"""
    subprocess.run(
        ["ssh", "franimac", f"cat > {script_path} && chmod +x {script_path}"],
        input=script, text=True, check=True, timeout=15,
    )

    subprocess.run(
        ["ssh", "franimac", f"/usr/local/bin/tmux send-keys -t ceiling 'bash {script_path}' Enter"],
        check=True, timeout=15,
    )

    t0 = time.time()
    deadline = t0 + timeout_s
    while time.time() < deadline:
        time.sleep(3)
        r = subprocess.run(
            ["ssh", "franimac", f"test -f {sentinel} && cat {sentinel} || echo PENDING"],
            capture_output=True, text=True, timeout=10,
        )
        s = r.stdout.strip()
        if s != "PENDING":
            elapsed = time.time() - t0
            exit_code = int(s) if s.isdigit() else 1

            subprocess.run(
                ["scp", "-q", "-r", f"franimac:{remote_sandbox}/.", str(sandbox)],
                timeout=60,
            )
            subprocess.run(["ssh", "franimac", f"rm -rf {remote_sandbox}"], timeout=15)
            output_path = sandbox / ".claude_output.txt"
            text = output_path.read_text(errors="replace")[:50000] if output_path.exists() else ""
            return text, elapsed, exit_code

    subprocess.run(["ssh", "franimac", f"rm -rf {remote_sandbox}"], timeout=15)
    return f"[TIMEOUT after {timeout_s}s]", time.time() - t0, 124


def parse_metrics(output: str, backend: str) -> dict:
    """Heuristic — pull turn / tool count from CLI output text."""
    metrics = {"turns": 0, "tool_calls": 0, "tool_errors": 0}
    if backend == "codex":
        # codex output has lines like "tokens used  N"
        m = re.search(r"tokens used\s+([\d,]+)", output)
        metrics["turns"] = output.count("\ncodex\n") or 1
        metrics["tool_calls"] = len(re.findall(r"^\s*(?:exec|read|write|edit|bash)", output, re.MULTILINE))
    else:
        # claude --print 預設只有 final response，沒 per-turn breakdown，標 1
        metrics["turns"] = 1
        metrics["tool_calls"] = 0
    return metrics


def run_topic(model_label: str, backend: str, topic_path: Path, model_id: str = "opus") -> CeilingResult:
    topic = yaml.safe_load(topic_path.read_text())
    sandbox = make_local_sandbox(model_label, topic["id"])

    result = CeilingResult(
        model=model_label,
        topic_id=topic["id"],
        sandbox_dir=str(sandbox),
    )

    timeout_s = topic.get("wall_time_limit_s", 480) + 60

    if backend == "codex":
        output, elapsed, exit_code = run_codex_exec(topic["prompt"], sandbox, timeout_s)
    elif backend == "claude":
        output, elapsed, exit_code = run_claude_via_tmux(topic["prompt"], sandbox, timeout_s, model=model_id)
    else:
        raise ValueError(f"unknown backend {backend}")

    transcript = sandbox / "_transcript.txt"
    transcript.write_text(output)
    result.transcript_path = str(transcript)
    result.wall_time_s = round(elapsed, 2)
    result.final_message = output[-2000:]
    if exit_code == 124:
        result.aborted = "wall_time_limit"
    elif exit_code != 0:
        result.aborted = f"exit_{exit_code}"

    metrics = parse_metrics(output, backend)
    result.turns = metrics["turns"]
    result.tool_calls = metrics["tool_calls"]

    ctx = {
        "sandbox_dir": str(sandbox),
        "full_transcript": output,
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
    ap.add_argument("--backend", required=True, choices=["claude", "codex"])
    ap.add_argument("--model-id", default="opus")
    ap.add_argument("--topic", required=True, type=Path)
    args = ap.parse_args()

    r = run_topic(args.model_label, args.backend, args.topic, args.model_id)
    print(json.dumps(asdict(r), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
