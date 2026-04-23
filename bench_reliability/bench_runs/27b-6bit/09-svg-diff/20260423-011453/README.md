# SVG Structural Diff POC

## Overview

This POC demonstrates a **structural diff** approach for comparing SVG files. Instead of treating SVGs as plain text (which produces noisy, hard-to-read diffs), it parses them as XML and compares their element trees — matching elements by their path in the document and reporting attribute-level changes.

## Approach: Structural/XML-aware Diff

### How it works

1. **Parse both SVGs as XML** using Python's built-in `xml.etree.ElementTree`
2. **Build element maps** — each element is identified by its path in the tree (e.g., `svg > circle`)
3. **Compare element-by-element**:
   - Detect **added** elements (present in B but not A)
   - Detect **removed** elements (present in A but not B)
   - Detect **modified attributes** (same element, different attribute values)
4. **Output a human-readable summary** grouped by change type

### Why this is better than text diff

| Aspect | Text Diff (`difflib`) | Structural Diff (this POC) |
|---|---|---|
| **Whitespace sensitivity** | Fails on reformatting | Ignores formatting differences |
| **Attribute order** | Flags reordered attributes as changes | Compares by attribute name |
| **Namespace handling** | Shows raw namespace URIs | Strips namespaces for readability |
| **Semantic meaning** | No understanding of SVG structure | Understands element hierarchy |
| **Output** | Line-by-line `+`/`-` markers | "fill changed: red -> blue" |
| **Scalability** | Breaks on large reformatting | Works regardless of formatting |

### Example output

```
============================================================
  SVG Structural Diff: a.svg vs b.svg
============================================================

  Total changes found: 2

  MODIFIED (2):
  • svg > circle: attribute 'fill' changed: red -> blue
  • svg > circle: attribute 'r' changed: 50 -> 60

------------------------------------------------------------
  Summary:
    - svg > circle: fill changed: red -> blue
    - svg > circle: r changed: 50 -> 60
------------------------------------------------------------
```

## Usage

```bash
# Run with default sample files (a.svg and b.svg are created automatically)
uv run --no-project python poc.py

# Run with custom SVG files
uv run --no-project python poc.py file1.svg file2.svg
```

## Files

- **`poc.py`** — Main script with the structural diff engine
- **`a.svg`** — Sample SVG: red circle (r=50)
- **`b.svg`** — Sample SVG: blue circle (r=60)
- **`README.md`** — This file

## Dependencies

None beyond Python's standard library (`xml.etree.ElementTree`, `dataclasses`, `enum`).

## Limitations & Future Improvements

- **No visual/pixel diff** — This compares structure, not rendered output. For pixel-level comparison, you'd need a rendering engine (e.g., `cairosvg` + `PIL`).
- **Sibling ordering** — Uses index-based matching for same-tag siblings. A more sophisticated approach could use element properties (id, class) for matching.
- **No CSS/style diff** — Inline styles and `<style>` blocks are not parsed.
- **No transform diff** — `transform` attributes are compared as strings, not decomposed into individual operations.
