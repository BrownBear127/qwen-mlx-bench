# SVG diff POC

This POC compares two SVG files by parsing their XML structure instead of doing a raw text diff.

## Approach

- `poc.py` writes two sample files:
  - `a.svg`: red circle with `r="50"`
  - `b.svg`: blue circle with `r="60"`
- It parses both SVGs with `lxml`
- It walks the SVG tree and compares attributes at matching element paths
- It prints a human-readable summary such as:
  - `svg[1]/circle[1] attribute changed: fill: red -> blue`
  - `svg[1]/circle[1] attribute changed: r: 50 -> 60`

## Why this is better than text diff

A text diff is sensitive to formatting, whitespace, and attribute order. This approach understands the SVG as a tree of elements and attributes, so it reports the actual semantic changes in the drawing.

For this example, the useful changes are:

- the circle fill changed from red to blue
- the circle radius changed from 50 to 60

That is more meaningful than line-by-line text changes.

## Run

```bash
uv run --no-project --with lxml python poc.py
```

## Dependency

The dependency list is in `requirements.txt`:

```text
lxml
```
