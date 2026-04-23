# SVG Structural Diff POC

## What it does

This POC computes a **structural diff** between two SVG files by parsing them as XML trees and comparing elements, attributes, and text content at the semantic level.

## Approach

### How it works

1. **Parse both SVGs as XML** using Python's built-in `xml.etree.ElementTree`
2. **Walk the element tree recursively**, matching elements by tag name and `id` attribute
3. **Compare attributes** on matched elements — detecting additions, removals, and value changes
4. **Compare text content** within elements
5. **Detect added/removed elements** that exist in one file but not the other
6. **Report changes** in a human-readable format with semantic labels (e.g., "fill color", "radius")

### Why this is better than text diff

| Aspect | Text Diff (`difflib`) | Structural Diff (this POC) |
|---|---|---|
| **Whitespace sensitivity** | Fails on reformatting | Ignores formatting differences |
| **Attribute order** | Reports spurious changes | Compares by attribute name |
| **Semantic meaning** | Sees only characters | Understands SVG elements & attributes |
| **Output** | Line-by-line `+/-` markers | "fill color: red → blue" |
| **Namespace handling** | Breaks on namespace prefixes | Strips namespaces automatically |
| **Element matching** | None | Matches by `id` or tag name |

A text diff would show every line as changed if attributes were reordered or whitespace was adjusted. This structural diff only reports actual semantic changes.

## Files

- `a.svg` — Red circle (r=50, black stroke)
- `b.svg` — Blue circle (r=60, no stroke)
- `poc.py` — The diff engine and runner
- `requirements.txt` — Dependencies (none needed; uses stdlib only)

## Usage

```bash
uv run --no-project python poc.py
```

## Sample Output

```
============================================================
  SVG STRUCTURAL DIFF REPORT
============================================================

  Total changes detected: 5

  ── Attribute Changes ──
    ~ <circle> fill color: 'red' -> 'blue'
    ~ <circle> radius: '50' -> '60'
    ~ <circle> stroke color: 'black' -> 'none'
    ~ <circle> stroke width: '2' -> '0'

  ── Text Content Changes ──
    ~ <text> text: 'Red Circle' -> 'Blue Circle'

============================================================
```

## Dependencies

None — uses only Python standard library (`xml.etree.ElementTree`, `dataclasses`).
