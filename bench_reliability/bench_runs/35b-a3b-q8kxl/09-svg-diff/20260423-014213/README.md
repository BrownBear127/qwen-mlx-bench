# SVG Structural Diff POC

## Approach

This POC computes a **structural diff** between two SVG files by parsing them as
XML trees and recursively comparing elements, attributes, and text content.

### How it works

1. **Parse** both SVG files as XML trees using Python's built-in `xml.etree.ElementTree`.
2. **Traverse** both trees in parallel, matching child elements by tag name.
3. **Compare** at each node:
   - **Tag names** — detects element type changes
   - **Attributes** — reports added, removed, or modified attributes with old → new values
   - **Text/tail content** — detects content changes
4. **Report** unmatched children as added or removed elements.

### Why structural diff is better than text diff

| Aspect | Text Diff | Structural Diff |
|---|---|---|
| **Readability** | Shows raw line changes; hard to map to visual meaning | Shows semantic changes: "fill changed: red → blue" |
| **Whitespace tolerance** | Broken by reformatting | Ignores whitespace, indentation, attribute order |
| **Attribute order** | `"r=50 fill=red"` vs `"fill=red r=50"` looks different | Same attributes in different order → no diff |
| **Namespace handling** | Fragile with XML namespaces | Properly strips namespaces |
| **Added/removed elements** | Shows as lines with `+`/`-` | Reports as "Element `<circle>` removed" |

### Example output

```
Found 2 difference(s):

  Attributes of <circle> at /svg/circle[0]:
  ~ r: '50' -> '60'
  ~ fill: 'red' -> 'blue'
```

This clearly communicates that the circle's radius changed from 50 to 60 and its
fill color changed from red to blue — exactly what a human needs to understand
the visual difference.

## Files

- `a.svg` — Source SVG: red circle, radius 50
- `b.svg` — Target SVG: blue circle, radius 60
- `poc.py` — The structural diff implementation
- `README.md` — This file

## Usage

```bash
uv run --no-project python poc.py
```

No third-party dependencies required — uses only Python standard library.
