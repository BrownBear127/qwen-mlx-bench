# SVG Structural Diff — POC

## What it does

This POC computes a **structural diff** between two SVG files by parsing them as XML trees and comparing element tags, attributes, and text content. It produces a human-readable summary of the differences.

## How to run

```bash
uv run --no-project python poc.py
```

No third-party packages are required — it uses only Python's standard library (`xml.etree.ElementTree`).

## Output example

```
Found 2 difference(s):

  1. [attr_changed] at /svg/circle
     fill changed: 'red' -> 'blue'

  2. [attr_changed] at /svg/circle
     r changed: '50' -> '60'

Compact summary:
  fill changed: 'red' -> 'blue', r changed: '50' -> '60'
```

## Approach: Structural XML Tree Comparison

### How it works

1. **Parse** both SVG files into XML element trees using `xml.etree.ElementTree`.
2. **Traverse** the trees in parallel, comparing elements at each node.
3. **Match children** by tag name (grouped and positionally paired), so that elements are compared semantically rather than by their position in the source text.
4. **Compare** at each node:
   - Tag names (e.g., `<circle>` vs `<rect>`)
   - Attributes (e.g., `fill="red"` vs `fill="blue"`)
   - Text content
   - Child elements (recursively)
5. **Report** all differences with their XPath-like location in the tree.

### Why this is better than text diff

| Aspect | Text diff (difflib) | Structural diff (this POC) |
|---|---|---|
| **Whitespace sensitivity** | Fails if formatting differs (e.g., attribute order, indentation) | Ignores formatting — compares semantic content |
| **Attribute order** | `<circle r="50" fill="red">` vs `<circle fill="red" r="50">` shows as different | Correctly identifies them as identical |
| **Meaningful output** | Shows line-level changes that may not reflect visual/semantic differences | Reports *what* changed (which attribute, from what value to what) |
| **Namespace handling** | Treats `{http://www.w3.org/2000/svg}circle` as opaque text | Strips namespace URIs for readable comparison |
| **Element matching** | Matches by line position in the file | Matches by tag name, so reordered elements are still compared correctly |

### Limitations

- Does not render the SVGs to pixels, so it cannot detect visual differences that arise from computed properties (e.g., CSS transforms, gradient effects).
- Child matching is positional within tag groups; if the same tag appears multiple times in a different order, it may pair them incorrectly.
- Does not handle SVG `<use>` elements or external references.

For a fully visual diff, you would need to render both SVGs to images (e.g., with `cairosvg` or `inkscape`) and compare pixels — but that requires heavier dependencies and is beyond the scope of this minimal POC.
