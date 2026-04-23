"""Hard-gate verification for reliability bench."""
from __future__ import annotations
import re
import subprocess
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

URL_RE = re.compile(r"https?://[^\s\)\]\}\"<>]+")


@dataclass
class GateResult:
    gate_id: str
    passed: bool
    detail: str


def _url_reachable(url: str, timeout: int = 5) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "bench/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return 200 <= r.status < 400
    except Exception:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "bench/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return 200 <= r.status < 400
        except Exception:
            return False


def gate_url_reachable(spec: dict, ctx: dict) -> GateResult:
    text = ctx.get(spec.get("extract_from", "full_transcript"), "")
    urls = list(dict.fromkeys(URL_RE.findall(text)))
    timeout = spec.get("timeout_per_url", 5)
    reachable = [u for u in urls if _url_reachable(u, timeout)]
    need = spec.get("required_count", 3)
    return GateResult(
        spec["id"],
        len(reachable) >= need,
        f"{len(reachable)}/{len(urls)} reachable, need {need}",
    )


def gate_py_compile(spec: dict, ctx: dict) -> GateResult:
    sandbox = Path(ctx["sandbox_dir"])
    file = sandbox / spec["file"]
    if not file.exists():
        return GateResult(spec["id"], False, f"{spec['file']} missing")
    import sys
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(file)], capture_output=True, text=True
    )
    return GateResult(
        spec["id"], r.returncode == 0, (r.stderr or "compiled").strip()[:200]
    )


def gate_run_command(spec: dict, ctx: dict) -> GateResult:
    import os
    sandbox = Path(ctx["sandbox_dir"])
    cmd = spec["cmd_template"]
    fallback = spec.get("fallback_cmd_template")
    timeout = spec.get("timeout_s", 60)
    expect = spec.get("expect_exit_code", 0)

    clean_env = {k: v for k, v in os.environ.items()
                 if k not in ("VIRTUAL_ENV", "PYTHONHOME", "PYTHONPATH")}

    def _run(c: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            c, shell=True, cwd=sandbox, capture_output=True, text=True,
            timeout=timeout, env=clean_env,
        )

    try:
        r = _run(cmd)
        if r.returncode != expect and fallback:
            r = _run(fallback)
        ctx["poc_stdout"] = (r.stdout or "")[:5000]
        ctx["poc_stderr"] = (r.stderr or "")[:2000]
        ok = r.returncode == expect
        stderr_tail = (r.stderr or "").strip().splitlines()[-1:] if r.stderr else []
        detail = f"exit={r.returncode} (want {expect})"
        if not ok and stderr_tail:
            detail += f" | last_stderr: {stderr_tail[0][:120]}"
        return GateResult(spec["id"], ok, detail)
    except subprocess.TimeoutExpired:
        return GateResult(spec["id"], False, f"timeout after {timeout}s")
    except Exception as e:
        return GateResult(spec["id"], False, f"exception: {e}")


def gate_regex_any(spec: dict, ctx: dict) -> GateResult:
    target = ctx.get(spec.get("against", "poc_stdout"), "")
    patterns = spec["patterns"]
    matched = [p for p in patterns if re.search(p, target)]
    need = spec.get("required_matches", 1)
    return GateResult(
        spec["id"],
        len(matched) >= need,
        f"matched {len(matched)}/{len(patterns)}, need {need}",
    )


def gate_keyword_any(spec: dict, ctx: dict) -> GateResult:
    sandbox = Path(ctx["sandbox_dir"])
    file = sandbox / spec["file"]
    if not file.exists():
        return GateResult(spec["id"], False, f"{spec['file']} missing")
    text = file.read_text(errors="replace")
    if spec.get("case_insensitive"):
        text = text.lower()
        keywords = [k.lower() for k in spec["keywords"]]
    else:
        keywords = spec["keywords"]
    hit = [k for k in keywords if k in text]
    return GateResult(spec["id"], bool(hit), f"hit: {hit}")


GATES = {
    "url_reachable": gate_url_reachable,
    "py_compile": gate_py_compile,
    "run_command": gate_run_command,
    "regex_any": gate_regex_any,
    "keyword_any": gate_keyword_any,
}


def run_all_gates(topic: dict, ctx: dict) -> list[GateResult]:
    results = []
    for spec in topic.get("gates", []):
        fn = GATES.get(spec["type"])
        if not fn:
            results.append(GateResult(spec["id"], False, f"unknown type {spec['type']}"))
            continue
        try:
            results.append(fn(spec, ctx))
        except Exception as e:
            results.append(GateResult(spec["id"], False, f"verifier crash: {e}"))
    return results
