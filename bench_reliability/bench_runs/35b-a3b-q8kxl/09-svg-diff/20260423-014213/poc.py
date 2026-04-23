#!/usr/bin/env python3
"""
SVG Structural Diff POC
========================
Parses two SVG files as XML trees and computes a meaningful structural diff:
  - Detects added/removed elements
  - Detects changed attributes (with old -> new values)
  - Detects changed text content
  - Reports element-level changes with XPath-like paths

Usage:
    uv run --no-project python poc.py
"""

import xml.etree.ElementTree as ET
import sys
from pathlib import Path


def get_tag(elem):
    """Extract local tag name from fully-qualified XML tag."""
    # Strip namespace: {http://...}tag -> tag
    if "}" in elem.tag:
        return elem.tag.split("}", 1)[1]
    return elem.tag


def element_path(elem, root=None):
    """Build a simple XPath-like path for an element."""
    parts = []
    current = elem
    while current is not None:
        tag = get_tag(current)
        # Find index among siblings with same tag
        siblings = list(current.getparent().iter(tag)) if current.getparent() else []
        idx = siblings.index(current) if current.getparent() and tag in [get_tag(s) for s in siblings] else 0
        parts.append(f"{tag}[{idx}]")
        current = current.getparent()
    parts.reverse()
    return "/" + "/".join(parts)


def diff_attributes(path, attrs_a, attrs_b):
    """Compare two attribute dicts and return list of change descriptions."""
    changes = []
    all_keys = set(attrs_a.keys()) | set(attrs_b.keys())
    for key in sorted(all_keys):
        val_a = attrs_a.get(key)
        val_b = attrs_b.get(key)
        if val_a == val_b:
            continue
        if val_a is None:
            changes.append(f"  + {key} = {val_b!r}  (new attribute)")
        elif val_b is None:
            changes.append(f"  - {key} = {val_a!r}  (removed attribute)")
        else:
            changes.append(f"  ~ {key}: {val_a!r} -> {val_b!r}")
    return changes


def diff_elements(elem_a, elem_b, path, changes):
    """Recursively diff two XML elements."""
    tag_a = get_tag(elem_a)
    tag_b = get_tag(elem_b)

    # Check for tag name change
    if tag_a != tag_b:
        changes.append(f"  Tag changed: {tag_a} -> {tag_b}  at {path}")

    # Compare attributes
    attrs_a = dict(elem_a.attrib)
    attrs_b = dict(elem_b.attrib)
    attr_changes = diff_attributes(path, attrs_a, attrs_b)
    if attr_changes:
        changes.append(f"  Attributes of <{tag_a}> at {path}:")
        changes.extend(attr_changes)

    # Compare text content
    text_a = (elem_a.text or "").strip()
    text_b = (elem_b.text or "").strip()
    if text_a != text_b:
        changes.append(f"  Text changed at {path}: {text_a!r} -> {text_b!r}")

    # Compare tail content
    tail_a = (elem_a.tail or "").strip()
    tail_b = (elem_b.tail or "").strip()
    if tail_a != tail_b:
        changes.append(f"  Tail changed at {path}: {tail_a!r} -> {tail_b!r}")

    # Recurse into children
    children_a = list(elem_a)
    children_b = list(elem_b)

    # Match children by tag (simple matching)
    used_a = set()
    used_b = set()

    for i, child_a in enumerate(children_a):
        tag_a_child = get_tag(child_a)
        for j, child_b in enumerate(children_b):
            tag_b_child = get_tag(child_b)
            if tag_a_child == tag_b_child and i not in used_a and j not in used_b:
                child_path = f"{path}/{tag_a_child}[{i}]"
                diff_elements(child_a, child_b, child_path, changes)
                used_a.add(i)
                used_b.add(j)
                break

    # Report unmatched children
    for i, child_a in enumerate(children_a):
        if i not in used_a:
            tag = get_tag(child_a)
            changes.append(f"  - Element <{tag}> removed at {path}/{tag}[{i}]")

    for j, child_b in enumerate(children_b):
        if j not in used_b:
            tag = get_tag(child_b)
            changes.append(f"  + Element <{tag}> added at {path}/{tag}[{j}]")


def compute_svg_diff(file_a, file_b):
    """Compute structural diff between two SVG files."""
    tree_a = ET.parse(file_a)
    tree_b = ET.parse(file_b)
    root_a = tree_a.getroot()
    root_b = tree_b.getroot()

    changes = []
    diff_elements(root_a, root_b, "/svg", changes)
    return changes


def main():
    file_a = Path("a.svg")
    file_b = Path("b.svg")

    if not file_a.exists():
        print(f"Error: {file_a} not found", file=sys.stderr)
        sys.exit(1)
    if not file_b.exists():
        print(f"Error: {file_b} not found", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("  SVG Structural Diff")
    print(f"  {file_a}  vs  {file_b}")
    print("=" * 60)
    print()

    changes = compute_svg_diff(file_a, file_b)

    if not changes:
        print("No structural differences found.")
    else:
        print(f"Found {len(changes)} difference(s):")
        print()
        for change in changes:
            print(change)

    print()
    print("=" * 60)

    # Also show a raw text diff for comparison
    print()
    print("--- Raw text diff (for comparison) ---")
    import difflib
    text_a = file_a.read_text()
    text_b = file_b.read_text()
    diff = difflib.unified_diff(
        text_a.splitlines(), text_b.splitlines(),
        fromfile=str(file_a), tofile=str(file_b)
    )
    for line in diff:
        print(line)


if __name__ == "__main__":
    main()
