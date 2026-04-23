# SVG Structural Diff — Proof of Concept

## What this does

This POC computes a **structural diff** between two SVG files. Instead of comparing raw text (which is fragile and ignores the document's meaning), it:

1. **Parses** each SVG as an XML tree using Python's built-in `xml.etree.ElementTree`.
2. **Matches** corresponding elements across the two trees using a signature heuristic (e.g., for `<circle>` elements, it matches by `cx`/`cy` coordinates).
3. **Compares** matched elements attribute-by-attribute, detecting:
   - **Changed attributes** (e.g., `fill: red → blue`, `r: 50 → 60`)
   - **Added elements** (present in the new SVG but not the old)
   - **Removed elements** (present in the old SVG but not the new)
4. **Prints** a clean, human-readable report.

## Why this is better than a text diff

| Aspect | Text diff (`difflib`) | Structural diff (this POC) |
|---|---|---|
| **Whitespace sensitivity** | Breaks on reformatting | Ignores formatting; compares meaning |
| **Attribute order** | Detects spurious changes | Compares by attribute name, not position |
| **Element matching** | None — line-by-line | Matches elements by semantic signature (position, tag) |
| **Namespace handling** | Treats `{ns}tag` as different | Strips namespaces for clean comparison |
| **Output** | Raw line diffs | Human-readable: `"fill changed: red → blue"` |

## Example

Given:
- **a.svg**: a red circle with `r="50"`
- **b.svg**: a blue circle with `r="60"`

The output is:

```
============================================================
  SVG Structural Diff: a.svg  →  b.svg
============================================================

  Found 2 change(s):

  ── Attribute Changes ──
    • [circle] fill: red → blue
    • [circle] r: 50 → 60

============================================================
```

## How to run

```bash
uv run --no-project python poc.py
```

No third-party packages are required — it uses only Python's standard library (`xml.etree.ElementTree`, `dataclasses`).

## Files

| File | Purpose |
|---|---|
| `poc.py` | Main script — parses, diffs, and reports |
| `a.svg` | Sample SVG: red circle, r=50 |
| `b.svg` | Sample SVG: blue circle, r=60 |
| `README.md` | This file |
