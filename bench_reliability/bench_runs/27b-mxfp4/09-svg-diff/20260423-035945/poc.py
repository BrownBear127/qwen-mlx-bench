#!/usr/bin/env python3
"""
SVG Structural Diff POC
=======================

Compares two SVG files by parsing them as XML trees and comparing
element structure, attributes, and text content — rather than doing
a naive line-by-line text diff.

This approach is structural: it understands that `<circle r="50">`
and `<circle r="60">` are the same element with a different attribute,
even if the XML formatting (whitespace, attribute order) differs.
"""

from xml.etree import ElementTree as ET


def parse_svg(path: str) -> ET.Element:
    """Parse an SVG file and return the root element."""
    tree = ET.parse(path)
    return tree.getroot()


def _tag_key(elem: ET.Element) -> str:
    """Return a comparable tag string, stripping namespace URIs for readability."""
    tag = elem.tag
    if "}" in tag:
        return tag.split("}")[1]
    return tag


def _diff_elements(a: ET.Element, b: ET.Element, path: str) -> list[dict]:
    """
    Recursively compare two XML elements and return a list of differences.

    Each difference is a dict with keys:
      - path: location in the tree (e.g. "/svg/circle")
      - type: "tag_changed", "attr_changed", "attr_added", "attr_removed",
              "text_changed", "child_added", "child_removed"
      - detail: human-readable description
    """
    diffs: list[dict] = []

    tag_a = _tag_key(a)
    tag_b = _tag_key(b)

    # 1. Compare tags
    if tag_a != tag_b:
        diffs.append({
            "path": path,
            "type": "tag_changed",
            "detail": f"tag changed: '{tag_a}' -> '{tag_b}'",
        })
        return diffs

    # 2. Compare attributes
    attrs_a = dict(a.attrib)
    attrs_b = dict(b.attrib)
    all_keys = sorted(set(attrs_a.keys()) | set(attrs_b.keys()))

    for key in all_keys:
        clean_key = key.split("}")[1] if "}" in key else key
        if key in attrs_a and key in attrs_b:
            if attrs_a[key] != attrs_b[key]:
                diffs.append({
                    "path": path,
                    "type": "attr_changed",
                    "detail": f"{clean_key} changed: '{attrs_a[key]}' -> '{attrs_b[key]}'",
                })
        elif key in attrs_a:
            diffs.append({
                "path": path,
                "type": "attr_removed",
                "detail": f"{clean_key} removed (was '{attrs_a[key]}')",
            })
        else:
            diffs.append({
                "path": path,
                "type": "attr_added",
                "detail": f"{clean_key} added (now '{attrs_b[key]}')",
            })

    # 3. Compare text content
    text_a = (a.text or "").strip()
    text_b = (b.text or "").strip()
    if text_a != text_b:
        diffs.append({
            "path": path,
            "type": "text_changed",
            "detail": f"text changed: '{text_a}' -> '{text_b}'",
        })

    # 4. Compare children — match by tag name (positional pairing within tag groups)
    children_a = list(a)
    children_b = list(b)

    def _group_by_tag(children: list[ET.Element]) -> dict[str, list[ET.Element]]:
        groups: dict[str, list[ET.Element]] = {}
        for c in children:
            t = _tag_key(c)
            groups.setdefault(t, []).append(c)
        return groups

    groups_a = _group_by_tag(children_a)
    groups_b = _group_by_tag(children_b)
    all_tags = sorted(set(groups_a.keys()) | set(groups_b.keys()))

    for tag in all_tags:
        list_a = groups_a.get(tag, [])
        list_b = groups_b.get(tag, [])

        max_len = max(len(list_a), len(list_b))
        for i in range(max_len):
            child_path = f"{path}/{tag}"
            if i < len(list_a) and i < len(list_b):
                diffs.extend(_diff_elements(list_a[i], list_b[i], child_path))
            elif i < len(list_a):
                diffs.append({
                    "path": child_path,
                    "type": "child_removed",
                    "detail": f"element <{tag}> removed",
                })
            else:
                diffs.append({
                    "path": child_path,
                    "type": "child_added",
                    "detail": f"element <{tag}> added",
                })

    return diffs


def diff_svgs(file_a: str, file_b: str) -> list[dict]:
    """Compute structural diff between two SVG files."""
    root_a = parse_svg(file_a)
    root_b = parse_svg(file_b)
    # Start with the root tag as the initial path
    root_path = f"/{_tag_key(root_a)}"
    return _diff_elements(root_a, root_b, root_path)


def print_diff_summary(diffs: list[dict]) -> None:
    """Print a human-readable summary of the differences."""
    if not diffs:
        print("No differences found. The SVGs are structurally identical.")
        return

    print(f"Found {len(diffs)} difference(s):\n")
    for i, d in enumerate(diffs, 1):
        print(f"  {i}. [{d['type']}] at {d['path']}")
        print(f"     {d['detail']}")
        print()


def main() -> None:
    """Main entry point: diff a.svg vs b.svg."""
    print("=" * 60)
    print("  SVG Structural Diff — POC")
    print("=" * 60)
    print()
    print("Comparing: a.svg  vs  b.svg")
    print()

    diffs = diff_svgs("a.svg", "b.svg")
    print_diff_summary(diffs)

    # Compact one-liner summary
    changes = [d["detail"] for d in diffs if d["type"] == "attr_changed"]
    if changes:
        print("Compact summary:")
        print("  " + ", ".join(changes))


if __name__ == "__main__":
    main()
