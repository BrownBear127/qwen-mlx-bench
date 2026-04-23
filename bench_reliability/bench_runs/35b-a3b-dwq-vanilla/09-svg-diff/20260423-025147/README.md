# SVG Structural Diff POC

## Approach

This POC computes a **structural diff** between two SVG files by:

1. **Parsing** each SVG as an XML tree using Python's `xml.etree.ElementTree`
2. **Recursively comparing** the two trees element by element
3. **Detecting** three kinds of changes:
   - **Attribute changes** — e.g. `fill="red"` → `fill="blue"`, `r="50"` → `r="60"`
   - **Added/removed elements** — e.g. a `<circle>` present in one file but not the other
   - **Text content changes** — e.g. changes to `<text>` element body

## Why This Is Better Than Text Diff

| Aspect | Text Diff (difflib) | Structural Diff (this POC) |
|---|---|---|
| **Relevance** | Reports every whitespace/formatting change | Reports only semantic changes |
| **Readability** | Unified diff with `+`/`-` lines | Human-readable: "fill changed: red → blue" |
| **Robustness** | Breaks if attributes are reordered | Attribute order doesn't matter |
| **Context** | No awareness of SVG semantics | Reports element path, attribute name, old/new values |
| **Additions/Removals** | Hard to distinguish from reformatting | Clearly identified as added/removed elements |

### Example

Given two SVGs that differ only in `fill` and `r` attributes:

```xml
<!-- a.svg -->
<circle cx="100" cy="100" r="50" fill="red" />

<!-- b.svg -->
<circle cx="100" cy="100" r="60" fill="blue" />
```

**Text diff** would show the entire `<circle>` line as changed, making it hard to see *what* changed.

**Structural diff** cleanly reports:
```
~ Attribute 'r' changed in <circle>: '50' -> '60'
~ Attribute 'fill' changed in <circle>: 'red' -> 'blue'
```

## Usage

```bash
# With no extra dependencies (stdlib only):
uv run --no-project python poc.py

# If you add third-party packages later:
uv run --no-project --with lxml python poc.py
```

## Files

- `poc.py` — The diff engine and demo
- `a.svg` — First SVG (red circle, r=50)
- `b.svg` — Second SVG (blue circle, r=60)
- `README.md` — This file
