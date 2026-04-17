"""
Multi-turn tool calling degradation benchmark for Qwen3.6-35B-A3B.

Compares OpenAI-compatible endpoints (e.g. llama-server GGUF vs mlx_lm.server DWQ)
using a deterministic research-agent task with 5 fake tools.

Degradation = round where `message.tool_calls` becomes empty AND/OR a tool-call
pattern leaks into `message.content` as plain text.

Replicates the methodology of mlx-lm issue #1011 for the Qwen3.6 generation.
"""
from __future__ import annotations
import argparse
import asyncio
import json
import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import openai
from rich.console import Console
from rich.table import Table

console = Console()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search the web for relevant sources on a topic. Returns a list of URLs with short snippets.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "search terms"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_page",
            "description": "Fetch and read a page at the given URL. Returns extracted text.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "URL to read"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "take_note",
            "description": "Save a research note. Returns a note_id for later cross-reference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "which topic this note belongs to"},
                    "text": {"type": "string", "description": "note body"},
                },
                "required": ["topic", "text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare",
            "description": "Compare two or more previously-saved notes by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["note_ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish_topic",
            "description": "Signal that research on the current topic is complete. Provide a one-paragraph summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "summary": {"type": "string"},
                },
                "required": ["topic", "summary"],
            },
        },
    },
]

SYSTEM = (
    "You are a research agent. Work through the topic list below in order. "
    "Topics: "
    "(1) Kenya Hara's concept of 'White', "
    "(2) the Japanese aesthetic concept 'Ma' (間), "
    "(3) emptiness and restraint in modern product design, "
    "(4) Dieter Rams' ten principles of good design, "
    "(5) Jasper Morrison's Supernormal, "
    "(6) Tadao Ando's use of light and concrete, "
    "(7) wabi-sabi and imperfection in Japanese aesthetics, "
    "(8) Muji's design philosophy under Kenya Hara, "
    "(9) the concept of 'haptic' in Hara's exhibitions, "
    "(10) negative space (yohaku) in Japanese poster design. "
    "For each topic: call search() once, read_page() on 1-2 results, "
    "take_note() at least once, then finish_topic(). "
    "After every three finished topics, also emit a compare() of those notes. "
    "Always use the tools — never describe what you would do in prose."
)

USER = "Begin the research. Start with topic 1."

FAKE_SEARCH_RESULTS = [
    {"url": "https://design-history.example/kenya-hara-white", "snippet": "Kenya Hara on white as a sensing of emptiness..."},
    {"url": "https://muji-press.example/emptiness-container", "snippet": "White is not a color but a container for perception..."},
    {"url": "https://ma-studies.example/intervals-japanese-aesthetics", "snippet": "Ma (間) denotes the interval between forms..."},
    {"url": "https://arch-journal.example/negative-space-koshino", "snippet": "Tadao Ando's use of Ma in concrete voids..."},
    {"url": "https://dieter-rams.example/restraint-as-principle", "snippet": "Less, but better — the ten principles..."},
    {"url": "https://jasper-morrison-supernormal.example/introduction", "snippet": "Supernormal objects disappear into daily life..."},
]

FAKE_PAGE_BODIES = {
    "white": "White, in Hara's framing, is not a pigment. It is an attentional posture — a cleared surface on which meaning can surface without coercion. The container precedes the content. Tea bowl glazes, rice paper, blank poster margins are not absences but invitations.",
    "ma": "Ma is the interval. The pause between drumbeats in gagaku, the step-back before the torii gate, the blank eighty percent of a Hiroshige print. It is not void but charged silence — a space where relation can form.",
    "emptiness": "Supernormal objects (Fukasawa, Morrison) operate by recessing their own presence. The good teapot is the one you don't notice while pouring. Restraint is not asceticism but functional quietness — design that does not ask for attention.",
    "default": "The page discusses the referenced topic in two paragraphs with supporting examples and historical context.",
}


def fake_tool_response(name: str, args: dict[str, Any], state: dict[str, Any]) -> str:
    if name == "search":
        q = (args.get("query") or "").lower()
        topic_key = "ma" if "ma" in q or "間" in q else "emptiness" if "empt" in q or "restraint" in q or "supernormal" in q else "white"
        state["current_topic_key"] = topic_key
        results = FAKE_SEARCH_RESULTS[:2] if topic_key == "white" else FAKE_SEARCH_RESULTS[2:4] if topic_key == "ma" else FAKE_SEARCH_RESULTS[4:6]
        return json.dumps({"results": results})
    if name == "read_page":
        url = args.get("url", "")
        key = "white" if "white" in url else "ma" if "ma" in url or "ando" in url else "emptiness" if "rams" in url or "supernormal" in url else "default"
        return json.dumps({"url": url, "text": FAKE_PAGE_BODIES[key]})
    if name == "take_note":
        state["note_counter"] = state.get("note_counter", 0) + 1
        nid = f"note_{state['note_counter']}"
        state.setdefault("notes", {})[nid] = {"topic": args.get("topic"), "text": args.get("text", "")[:200]}
        return json.dumps({"note_id": nid, "saved": True})
    if name == "compare":
        ids = args.get("note_ids", [])
        return json.dumps({"comparison": f"Across notes {ids}, the common thread is attentional restraint."})
    if name == "finish_topic":
        state.setdefault("finished_topics", []).append(args.get("topic"))
        return json.dumps({"acknowledged": True, "topic": args.get("topic")})
    return json.dumps({"error": f"unknown tool {name}"})


# Patterns indicating tool-call leaked as plain text instead of structured call
LEAK_PATTERNS = [
    re.compile(r"\[Tool call\s*:", re.I),
    re.compile(r"<tool_call>", re.I),  # should have been parsed if model is healthy
    re.compile(r"```\s*(json|tool)?\s*\n\s*\{\s*['\"]?(name|function)['\"]?\s*:", re.I),
    re.compile(r"\b(search|read_page|take_note|compare|finish_topic)\s*\(\s*['\"]", re.I),
    re.compile(r"I (?:will|would|should|need to) (?:now )?(?:call|invoke|use) (?:the )?(?:search|read_page|take_note|compare|finish_topic)", re.I),
]


def detect_degradation(message) -> tuple[bool, list[str]]:
    """Returns (is_degraded, leak_types_detected)."""
    leaks = []
    content = (message.content or "") if hasattr(message, "content") else ""
    for pat in LEAK_PATTERNS:
        if pat.search(content):
            leaks.append(pat.pattern[:50])

    has_structured = bool(getattr(message, "tool_calls", None))
    # "degraded" = no structured tool_calls AND content looks like the model tried to call a tool
    is_degraded = (not has_structured) and len(leaks) > 0
    return is_degraded, leaks


@dataclass
class RoundResult:
    round: int
    has_structured_tool_calls: bool
    num_tool_calls: int
    leaks: list[str]
    content_preview: str
    elapsed_s: float
    degraded: bool
    finish_reason: str | None = None


@dataclass
class RunResult:
    endpoint: str
    model: str
    total_rounds: int
    first_degradation_round: int | None
    rounds_completed_clean: int
    total_tool_calls: int
    total_elapsed_s: float
    rounds: list[RoundResult] = field(default_factory=list)


async def run_rounds(endpoint: str, model: str, n_rounds: int, temperature: float = 0.0) -> RunResult:
    client = openai.AsyncOpenAI(base_url=endpoint, api_key="bench")
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER},
    ]
    state: dict[str, Any] = {}
    result = RunResult(endpoint=endpoint, model=model, total_rounds=n_rounds,
                       first_degradation_round=None, rounds_completed_clean=0,
                       total_tool_calls=0, total_elapsed_s=0.0)

    for rnd in range(1, n_rounds + 1):
        t0 = time.time()
        try:
            resp = await client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                temperature=temperature,
                max_tokens=2000,
            )
        except Exception as e:
            console.print(f"[red]Round {rnd} API error:[/red] {e}")
            rr = RoundResult(round=rnd, has_structured_tool_calls=False, num_tool_calls=0,
                             leaks=[f"api_error:{type(e).__name__}"], content_preview=str(e)[:200],
                             elapsed_s=time.time() - t0, degraded=True)
            result.rounds.append(rr)
            if result.first_degradation_round is None:
                result.first_degradation_round = rnd
            break

        elapsed = time.time() - t0
        msg = resp.choices[0].message
        finish_reason = resp.choices[0].finish_reason
        degraded, leaks = detect_degradation(msg)
        tool_calls = msg.tool_calls or []

        rr = RoundResult(
            round=rnd,
            has_structured_tool_calls=bool(tool_calls),
            num_tool_calls=len(tool_calls),
            leaks=leaks,
            content_preview=(msg.content or "")[:150],
            elapsed_s=round(elapsed, 2),
            degraded=degraded,
            finish_reason=finish_reason,
        )
        result.rounds.append(rr)
        result.total_elapsed_s += elapsed
        result.total_tool_calls += len(tool_calls)

        status = "[green]✓[/green]" if not degraded else "[red]✗ DEGRADED[/red]"
        console.print(f"  Round {rnd:2d} {status} tool_calls={len(tool_calls)} elapsed={elapsed:.1f}s finish={finish_reason}")
        if leaks:
            console.print(f"    [yellow]leaks:[/yellow] {leaks}")

        if degraded and result.first_degradation_round is None:
            result.first_degradation_round = rnd

        if not degraded:
            result.rounds_completed_clean += 1

        # Append assistant message (structured)
        assistant_msg: dict[str, Any] = {"role": "assistant", "content": msg.content or None}
        if tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in tool_calls
            ]
        messages.append(assistant_msg)

        # Append tool responses
        if tool_calls:
            for tc in tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except Exception:
                    args = {}
                tool_response = fake_tool_response(tc.function.name, args, state)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_response,
                })
        else:
            # If model went prose-only, nudge it back; this is a real-world agent pattern
            messages.append({
                "role": "user",
                "content": "Continue. Use the available tools — do not describe actions in prose.",
            })

        # Early exit: if model called finish_topic on all 3 topics and we've seen compare
        finished = set(state.get("finished_topics", []))
        if len(finished) >= 3 and any(
            tc.function.name == "compare"
            for rnd_record in result.rounds
            for tc in [] # placeholder; can't inspect past tool_calls from here cleanly
        ):
            pass  # don't early-exit; keep going to stress-test

    return result


def print_summary(results: list[RunResult]):
    table = Table(title="Multi-turn tool calling benchmark — Qwen3.6-35B-A3B")
    table.add_column("Endpoint", style="cyan")
    table.add_column("Model")
    table.add_column("Rounds")
    table.add_column("First degradation")
    table.add_column("Clean rounds")
    table.add_column("Tool calls")
    table.add_column("Total time (s)")
    table.add_column("Avg t/turn")
    for r in results:
        first_deg = str(r.first_degradation_round) if r.first_degradation_round else "none"
        avg = f"{r.total_elapsed_s / max(len(r.rounds), 1):.1f}"
        table.add_row(
            r.endpoint,
            r.model,
            str(len(r.rounds)),
            first_deg,
            f"{r.rounds_completed_clean}/{r.total_rounds}",
            str(r.total_tool_calls),
            f"{r.total_elapsed_s:.1f}",
            avg,
        )
    console.print(table)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", action="append", required=True,
                        help="Format: label=http://host:port/v1|model_name (repeatable)")
    parser.add_argument("--rounds", type=int, default=20)
    parser.add_argument("--out", type=str, default="results.json")
    parser.add_argument("--temperature", type=float, default=0.0)
    args = parser.parse_args()

    results = []
    for spec in args.endpoint:
        label, rest = spec.split("=", 1)
        endpoint, model = rest.split("|", 1)
        console.rule(f"[bold]{label}  —  {endpoint}  model={model}")
        r = await run_rounds(endpoint, model, args.rounds, args.temperature)
        results.append(r)

    console.rule("[bold]Summary")
    print_summary(results)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(
        [asdict(r) for r in results], indent=2, ensure_ascii=False,
    ))
    console.print(f"\nFull log → [cyan]{out_path.resolve()}[/cyan]")


if __name__ == "__main__":
    asyncio.run(main())
