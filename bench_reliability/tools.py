"""Minimal toolset for reliability bench. Same toolset across all models for fairness."""
from __future__ import annotations
import json
import subprocess
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

SEARXNG_BASE = "http://127.0.0.1:8888"  # direct, no proxy / no scrape — keep bench deterministic


def _http_get(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "bench/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        try:
            return raw.decode("utf-8", errors="replace")
        except Exception:
            return raw.decode("latin-1", errors="replace")


def _http_post_json(url: str, payload: dict, timeout: int = 30) -> str:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "bench/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav", "footer"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "footer"):
            self._skip = max(0, self._skip - 1)

    def handle_data(self, data):
        if self._skip:
            return
        text = data.strip()
        if text:
            self.parts.append(text)


def _html_to_text(html: str, max_chars: int = 8000) -> str:
    p = _TextExtractor()
    try:
        p.feed(html)
    except Exception:
        pass
    return "\n".join(p.parts)[:max_chars]


def web_search(query: str, num_results: int = 5) -> str:
    qs = urllib.parse.urlencode({"q": query, "format": "json"})
    try:
        body = _http_get(f"{SEARXNG_BASE}/search?{qs}", timeout=15)
        data = json.loads(body)
        results = data.get("results", [])[:num_results]
        return json.dumps(
            [{"title": r.get("title"), "url": r.get("url"), "snippet": (r.get("content") or "")[:500]} for r in results],
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"error": f"search failed: {e}"})


def web_fetch(url: str, max_chars: int = 8000) -> str:
    try:
        return _html_to_text(_http_get(url, timeout=20), max_chars)
    except Exception as e:
        return f"fetch error: {e}"


def read_file(path: str, sandbox_dir: str) -> str:
    p = (Path(sandbox_dir) / path).resolve()
    if not str(p).startswith(str(Path(sandbox_dir).resolve())):
        return "error: path escapes sandbox"
    if not p.exists():
        return f"error: {path} not found"
    return p.read_text(errors="replace")[:8000]


def write_file(path: str, content: str, sandbox_dir: str) -> str:
    p = (Path(sandbox_dir) / path).resolve()
    if not str(p).startswith(str(Path(sandbox_dir).resolve())):
        return "error: path escapes sandbox"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"wrote {len(content)} bytes to {path}"


def list_dir(path: str, sandbox_dir: str) -> str:
    p = (Path(sandbox_dir) / (path or ".")).resolve()
    if not str(p).startswith(str(Path(sandbox_dir).resolve())):
        return "error: path escapes sandbox"
    if not p.exists():
        return f"error: {path} not found"
    return "\n".join(sorted(x.name + ("/" if x.is_dir() else "") for x in p.iterdir()))


def run_bash(cmd: str, sandbox_dir: str, timeout: int = 60) -> str:
    try:
        r = subprocess.run(
            cmd, shell=True, cwd=sandbox_dir, capture_output=True, text=True, timeout=timeout
        )
        return f"exit={r.returncode}\nstdout:\n{r.stdout[:3000]}\nstderr:\n{r.stderr[:1500]}"
    except subprocess.TimeoutExpired:
        return f"timeout after {timeout}s"
    except Exception as e:
        return f"error: {e}"


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web. Returns up to 5 results with title/url/snippet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "num_results": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch a URL and return text content (HTML stripped, max 8000 chars).",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}, "max_chars": {"type": "integer", "default": 8000}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file from sandbox dir.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write file to sandbox dir.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files in sandbox directory.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "default": "."}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": "Run shell command in sandbox dir (60s timeout).",
            "parameters": {
                "type": "object",
                "properties": {"cmd": {"type": "string"}, "timeout": {"type": "integer", "default": 60}},
                "required": ["cmd"],
            },
        },
    },
]


def dispatch(name: str, args: dict, sandbox_dir: str) -> str:
    """Dispatch a tool call. Returns string result for the model."""
    if name == "web_search":
        return web_search(args.get("query", ""), args.get("num_results", 5))
    if name == "web_fetch":
        return web_fetch(args.get("url", ""), args.get("max_chars", 8000))
    if name == "read_file":
        return read_file(args.get("path", ""), sandbox_dir)
    if name == "write_file":
        return write_file(args.get("path", ""), args.get("content", ""), sandbox_dir)
    if name == "list_dir":
        return list_dir(args.get("path", "."), sandbox_dir)
    if name == "run_bash":
        return run_bash(args.get("cmd", ""), sandbox_dir, args.get("timeout", 60))
    return f"error: unknown tool {name}"
