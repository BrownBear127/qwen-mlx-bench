# SVG Structural Diff — POC

## Approach

This POC computes a **structural diff** between two SVG files by parsing them as XML trees and comparing elements and attributes semantically.

### How it works

1. **Parse** both SVGs into XML element trees (using Python's built-in `xml.etree.ElementTree`).
2. **Flatten** each tree into a list of `(path, element)` pairs, where the path encodes the element's position in the hierarchy (e.g. `svg/circle`).
3. **Match** elements between the two trees by their structural path.
4. **Compare** matched elements attribute-by-attribute, reporting:
   - **Changed attributes** — with old/new values and numeric deltas where applicable.
   - **Added/removed attributes**.
   - **Added/removed elements** (present in one tree but not the other).
   - **Text content changes**.

### Why this is better than a text diff

| Text diff (difflib) | Structural diff (this POC) |
|---|---|
| Reports changed *lines* — mixes meaningful changes with whitespace/formatting noise | Reports changed *attributes and elements* — every reported change is semantically meaningful |
| "Line 3 differs" tells you nothing about *what* changed | `fill: red -> blue` tells you exactly what changed |
| Reordering attributes produces a false diff | Attribute order is irrelevant — only values matter |
| No understanding of numeric values | Numeric deltas computed automatically (e.g. `r: 50 -> 60 (delta: +10)`) |
| Cannot distinguish structural changes (added element) from attribute tweaks | Categorizes changes by type: attr change, element add/remove, text change |

## Running

```bash
python poc.py
```

No third-party packages required — uses only Python's standard library.

## Example output

```
SVG Structural Diff: a.svg vs b.svg
==================================================
Found 3 difference(s):

  [svg/circle] r: 50 -> 60  (delta: +10)
  [svg/circle] fill: red -> blue
  [svg/circle] stroke-width: 2 -> 4  (delta: +2)
```
