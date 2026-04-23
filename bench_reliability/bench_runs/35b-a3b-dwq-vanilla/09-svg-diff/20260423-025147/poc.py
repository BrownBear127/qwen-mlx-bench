#!/usr/bin/env python3
"""
SVG Structural Diff POC
=======================
Parses two SVG files as XML trees and computes a meaningful structural diff:
- Detects added/removed elements
- Detects changed attributes (with old -> new values)
- Detects changed text content
- Reports element-level changes with context (tag name, path)

No third-party dependencies — uses only Python stdlib (xml.etree.ElementTree).
"""

import copy
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_svg(path: str) -> ET.Element:
    """Parse an SVG file and return its root element."""
    tree = ET.parse(path)
    return tree.getroot()


def element_path(elem: ET.Element, parent_path: str = "") -> str:
    """Build a human-readable path for an element, e.g. /svg/circle[0]."""
    tag = elem.tag.split("}")[-1]  # strip namespace
    if parent_path:
        return f"{parent_path}/{tag}"
    return f"/{tag}"


def get_attributes(elem: ET.Element) -> dict:
    """Return a dict of an element's attributes (excluding namespace)."""
    return {k.split("}")[-1]: v for k, v in elem.attrib.items()}


def diff_attributes(old_attrs: dict, new_attrs: dict, path: str) -> list[dict]:
    """Compare two attribute dicts and return a list of changes."""
    changes = []
    all_keys = sorted(set(old_attrs.keys()) | set(new_attrs.keys()))
    for key in all_keys:
        old_val = old_attrs.get(key)
        new_val = new_attrs.get(key)
        if old_val != new_val:
            if old_val is None:
                changes.append({"path": path, "type": "added", "attr": key, "old": None, "new": new_val})
            elif new_val is None:
                changes.append({"path": path, "type": "removed", "attr": key, "old": old_val, "new": None})
            else:
                changes.append({"path": path, "type": "changed", "attr": key, "old": old_val, "new": new_val})
    return changes


def diff_elements(old_elem: ET.Element, new_elem: ET.Element, path: str, changes: list) -> None:
    """Recursively diff two elements and collect changes."""
    old_attrs = get_attributes(old_elem)
    new_attrs = get_attributes(new_elem)

    # Check for changed attributes on this element
    changes.extend(diff_attributes(old_attrs, new_attrs, path))

    # Compare children
    old_children = list(old_elem)
    new_children = list(new_elem)

    old_tags = [c.tag.split("}")[-1] for c in old_children]
    new_tags = [c.tag.split("}")[-1] for c in new_children]

    # Find added/removed child elements by tag
    all_tags = sorted(set(old_tags) | set(new_tags))
    for tag in all_tags:
        old_matches = [c for c in old_children if c.tag.split("}")[-1] == tag]
        new_matches = [c for c in new_children if c.tag.split("}")[-1] == tag]

        # If counts differ, report added/removed
        if len(old_matches) != len(new_matches):
            for i in range(len(new_matches) - len(old_matches)):
                changes.append({
                    "path": f"{path}/{tag}",
                    "type": "added",
                    "attr": None,
                    "old": None,
                    "new": new_matches[len(old_matches) + i].tag.split("}")[-1],
                })
            for i in range(len(old_matches) - len(new_matches)):
                changes.append({
                    "path": f"{path}/{tag}",
                    "type": "removed",
                    "attr": None,
                    "old": old_matches[len(new_matches) + i].tag.split("}")[-1],
                    "new": None,
                })

        # Recurse into matching children (pair by index)
        for i in range(min(len(old_matches), len(new_matches))):
            child_path = f"{path}/{tag}[{i}]"
            diff_elements(old_matches[i], new_matches[i], child_path, changes)

    # Compare text content
    old_text = (old_elem.text or "").strip()
    new_text = (new_elem.text or "").strip()
    if old_text != new_text:
        changes.append({
            "path": path,
            "type": "text_changed",
            "attr": None,
            "old": old_text or "(empty)",
            "new": new_text or "(empty)",
        })


def compute_svg_diff(svg_a: str, svg_b: str) -> list[dict]:
    """Compute a structural diff between two SVG files."""
    root_a = parse_svg(svg_a)
    root_b = parse_svg(svg_b)

    changes: list[dict] = []
    diff_elements(root_a, root_b, "/", changes)
    return changes


def format_change(change: dict) -> str:
    """Format a single change for human-readable output."""
    path = change["path"]
    tag = path.split("/")[-1].split("[")[0]

    if change["type"] == "added":
        return f"  + Added element: <{tag}> at {path}"
    elif change["type"] == "removed":
        return f"  - Removed element: <{tag}> at {path}"
    elif change["type"] == "text_changed":
        return f"  ~ Text changed in <{tag}> at {path}: {change['old']!r} -> {change['new']!r}"
    elif change["type"] == "changed":
        attr = change["attr"]
        old_val = change["old"]
        new_val = change["new"]
        return f"  ~ Attribute '{attr}' changed in <{tag}> at {path}: {old_val!r} -> {new_val!r}"
    return f"  ? Unknown change in <{tag}> at {path}"


def main():
    svg_a = "a.svg"
    svg_b = "b.svg"

    print("=" * 60)
    print("SVG Structural Diff POC")
    print("=" * 60)
    print(f"\nComparing: {svg_a}  vs  {svg_b}")
    print()

    changes = compute_svg_diff(svg_a, svg_b)

    if not changes:
        print("No differences found.")
        return

    print(f"Found {len(changes)} structural change(s):\n")
    for change in changes:
        print(format_change(change))

    print()
    print("=" * 60)
    print("Summary:")
    print("=" * 60)

    # Group by type
    attr_changes = [c for c in changes if c["type"] == "changed"]
    added = [c for c in changes if c["type"] == "added"]
    removed = [c for c in changes if c["type"] == "removed"]
    text_changes = [c for c in changes if c["type"] == "text_changed"]

    if attr_changes:
        for c in attr_changes:
            tag = c["path"].split("/")[-1].split("[")[0]
            print(f"  • {tag}: {c['attr']} changed from {c['old']!r} to {c['new']!r}")

    if added:
        for c in added:
            print(f"  • Added element: {c['new']} at {c['path']}")

    if removed:
        for c in removed:
            print(f"  • Removed element: {c['old']} at {c['path']}")

    if text_changes:
        for c in text_changes:
            print(f"  • Text changed in {c['path']}: {c['old']!r} -> {c['new']!r}")

    print()


if __name__ == "__main__":
    main()
