#!/usr/bin/env python3
"""
SVG Structural Diff POC
========================
Parses two SVG files as XML trees and computes a structural diff,
identifying changes in element attributes, added/removed elements,
and structural differences — far more meaningful than a raw text diff.

Usage:
    uv run --no-project python poc.py
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional


# ── Data model ──────────────────────────────────────────────────────────────

@dataclass
class AttributeChange:
    """A single attribute change on an element."""
    element_tag: str
    attribute: str
    old_value: Optional[str]
    new_value: Optional[str]


@dataclass
class ElementAdded:
    """An element present in the new SVG but not in the old."""
    tag: str
    attributes: dict


@dataclass
class ElementRemoved:
    """An element present in the old SVG but not in the new."""
    tag: str
    attributes: dict


@dataclass
class SvgDiff:
    """Collection of all differences between two SVGs."""
    attribute_changes: list = field(default_factory=list)
    elements_added: list = field(default_factory=list)
    elements_removed: list = field(default_factory=list)


# ── Core diff logic ─────────────────────────────────────────────────────────

def parse_svg(path: str) -> ET.Element:
    """Parse an SVG file and return its root element."""
    return ET.parse(path).getroot()


def _tag_key(elem: ET.Element) -> str:
    """
    Produce a comparable tag name, stripping the XML namespace if present.
    e.g. '{http://www.w3.org/2000/svg}circle' → 'circle'
    """
    return elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag


def _element_signature(elem: ET.Element) -> tuple:
    """
    Create a signature for matching elements across the two SVGs.
    Uses (tag, cx, cy) for circles, (tag, x, y) for rects, etc.
    Falls back to (tag, index) for generic matching.
    """
    tag = _tag_key(elem)
    attrs = elem.attrib

    # Heuristic: use position attributes to match corresponding elements
    if tag == "circle":
        return (tag, attrs.get("cx"), attrs.get("cy"))
    elif tag in ("rect", "ellipse"):
        return (tag, attrs.get("x"), attrs.get("y"))
    elif tag == "text":
        return (tag, attrs.get("x"), attrs.get("y"))
    else:
        return (tag,)


def diff_elements(old: ET.Element, new: ET.Element, diff: SvgDiff,
                  path: str = ""):
    """
    Recursively compare two XML element trees and populate `diff`.
    """
    old_tag = _tag_key(old)
    new_tag = _tag_key(new)

    # ── 1. Compare attributes on the current element ─────────────────
    all_attrs = set(old.attrib.keys()) | set(new.attrib.keys())
    for attr in sorted(all_attrs):
        old_val = old.attrib.get(attr)
        new_val = new.attrib.get(attr)
        if old_val != new_val:
            diff.attribute_changes.append(AttributeChange(
                element_tag=old_tag,
                attribute=attr,
                old_value=old_val,
                new_value=new_val,
            ))

    # ── 2. Compare child elements ────────────────────────────────────
    old_children = list(old)
    new_children = list(new)

    # Build signature → element maps for matching
    old_by_sig = {}
    for i, child in enumerate(old_children):
        sig = _element_signature(child)
        old_by_sig.setdefault(sig, []).append((i, child))

    new_by_sig = {}
    for i, child in enumerate(new_children):
        sig = _element_signature(child)
        new_by_sig.setdefault(sig, []).append((i, child))

    matched_old = set()
    matched_new = set()

    # Match elements by signature
    for sig in old_by_sig:
        if sig in new_by_sig:
            old_list = old_by_sig[sig]
            new_list = new_by_sig[sig]
            for (oi, oelem), (ni, nelem) in zip(old_list, new_list):
                matched_old.add(oi)
                matched_new.add(ni)
                child_path = f"{path}/{_tag_key(oelem)}"
                diff_elements(oelem, nelem, diff, child_path)

    # Elements only in old → removed
    for i, child in enumerate(old_children):
        if i not in matched_old:
            diff.elements_removed.append(ElementRemoved(
                tag=_tag_key(child),
                attributes=dict(child.attrib),
            ))

    # Elements only in new → added
    for i, child in enumerate(new_children):
        if i not in matched_new:
            diff.elements_added.append(ElementAdded(
                tag=_tag_key(child),
                attributes=dict(child.attrib),
            ))


def compute_svg_diff(path_a: str, path_b: str) -> SvgDiff:
    """Compute the structural diff between two SVG files."""
    root_a = parse_svg(path_a)
    root_b = parse_svg(path_b)
    diff = SvgDiff()
    diff_elements(root_a, root_b, diff)
    return diff


# ── Human-readable report ───────────────────────────────────────────────────

def print_report(diff: SvgDiff, file_a: str, file_b: str):
    """Print a human-readable summary of the SVG diff."""
    print("=" * 60)
    print(f"  SVG Structural Diff: {file_a}  →  {file_b}")
    print("=" * 60)

    total_changes = (len(diff.attribute_changes)
                     + len(diff.elements_added)
                     + len(diff.elements_removed))

    if total_changes == 0:
        print("\n  No differences found. The SVGs are structurally identical.\n")
        return

    print(f"\n  Found {total_changes} change(s):\n")

    # Attribute changes
    if diff.attribute_changes:
        print("  ── Attribute Changes ──")
        for ch in diff.attribute_changes:
            if ch.old_value is None:
                print(f"    • [{ch.element_tag}] {ch.attribute}: (added) → {ch.new_value}")
            elif ch.new_value is None:
                print(f"    • [{ch.element_tag}] {ch.attribute}: {ch.old_value} → (removed)")
            else:
                print(f"    • [{ch.element_tag}] {ch.attribute}: {ch.old_value} → {ch.new_value}")
        print()

    # Added elements
    if diff.elements_added:
        print("  ── Elements Added (in new SVG) ──")
        for el in diff.elements_added:
            attrs = ", ".join(f"{k}={v}" for k, v in el.attributes.items())
            print(f"    • <{el.tag}>  ({attrs})")
        print()

    # Removed elements
    if diff.elements_removed:
        print("  ── Elements Removed (from old SVG) ──")
        for el in diff.elements_removed:
            attrs = ", ".join(f"{k}={v}" for k, v in el.attributes.items())
            print(f"    • <{el.tag}>  ({attrs})")
        print()

    print("=" * 60)


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    diff = compute_svg_diff("a.svg", "b.svg")
    print_report(diff, "a.svg", "b.svg")
