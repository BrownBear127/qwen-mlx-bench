"""
SVG Structural Diff POC

Compares two SVG files by parsing them as XML trees and performing a
structural/attribute-level diff. This is far more meaningful than a
raw text diff because it understands SVG elements, attributes, and
hierarchy — reporting exactly what changed semantically.

Usage:
    uv run --no-project python poc.py
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional


# ── Data structures ────────────────────────────────────────────────

@dataclass
class AttributeChange:
    """A single attribute change on an element."""
    tag: str
    index: int  # position among siblings (for identification)
    attr: str
    old_value: Optional[str]
    new_value: Optional[str]

    def __str__(self):
        if self.old_value is None:
            return f"  + {self.tag}#{self.index} attribute '{self.attr}' added: '{self.new_value}'"
        elif self.new_value is None:
            return f"  - {self.tag}#{self.index} attribute '{self.attr}' removed (was '{self.old_value}')"
        else:
            return f"  ~ {self.tag}#{self.index} attribute '{self.attr}' changed: '{self.old_value}' -> '{self.new_value}'"


@dataclass
class ElementChange:
    """An element that was added or removed."""
    tag: str
    index: int
    action: str  # "added" or "removed"
    attributes: dict = field(default_factory=dict)

    def __str__(self):
        attrs = ", ".join(f"{k}='{v}'" for k, v in self.attributes.items())
        return f"  {self.action.upper()} <{self.tag}> ({attrs}) at index {self.index}"


@dataclass
class TextChange:
    """A text content change."""
    tag: str
    index: int
    old_text: Optional[str]
    new_text: Optional[str]

    def __str__(self):
        if self.old_text is None:
            return f"  + {self.tag}#{self.index} text added: '{self.new_text}'"
        elif self.new_text is None:
            return f"  - {self.tag}#{self.index} text removed (was '{self.old_text}')"
        else:
            return f"  ~ {self.tag}#{self.index} text changed: '{self.old_text}' -> '{self.new_text}'"


@dataclass
class SVGDifference:
    """Collection of all differences between two SVGs."""
    attribute_changes: list = field(default_factory=list)
    element_changes: list = field(default_factory=list)
    text_changes: list = field(default_factory=list)

    def is_empty(self):
        return not (self.attribute_changes or self.element_changes or self.text_changes)

    def summary(self) -> str:
        lines = []
        if self.attribute_changes:
            lines.append(f"Attribute changes ({len(self.attribute_changes)}):")
            for c in self.attribute_changes:
                lines.append(str(c))
        if self.element_changes:
            lines.append(f"\nElement changes ({len(self.element_changes)}):")
            for c in self.element_changes:
                lines.append(str(c))
        if self.text_changes:
            lines.append(f"\nText changes ({len(self.text_changes)}):")
            for c in self.text_changes:
                lines.append(str(c))
        return "\n".join(lines)


# ── Core diff logic ────────────────────────────────────────────────

def strip_ns(tag: str) -> str:
    """Remove XML namespace from a tag like '{http://www.w3.org/2000/svg}circle'."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def element_key(elem: ET.Element) -> str:
    """Create a key for matching elements: tag + significant attributes."""
    tag = strip_ns(elem.tag)
    eid = elem.get("id")
    if eid:
        return f"id:{eid}"
    return f"tag:{tag}"


def get_children(elem: ET.Element) -> list:
    """Get direct children, ignoring comments and processing instructions."""
    return [child for child in elem if child.tag is not ET.Comment]


def _annotate_indices(root: ET.Element):
    """Walk the tree and store sibling index on each element."""
    for parent in root.iter():
        children = get_children(parent)
        for i, child in enumerate(children):
            child.set("_idx", str(i))


def _sibling_index(elem: ET.Element) -> int:
    idx = elem.get("_idx")
    return int(idx) if idx else 0


def _build_child_map(children: list) -> dict:
    """Build a map from element_key -> list of children."""
    d = {}
    for child in children:
        key = element_key(child)
        d.setdefault(key, []).append(child)
    return d


def diff_elements(old_elem: ET.Element, new_elem: ET.Element) -> SVGDifference:
    """
    Recursively diff two XML elements and their children.
    Returns a SVGDifference with all detected changes.
    """
    diff = SVGDifference()
    old_tag = strip_ns(old_elem.tag)
    new_tag = strip_ns(new_elem.tag)

    if old_tag != new_tag:
        diff.element_changes.append(ElementChange(
            tag=old_tag, index=0, action="removed",
            attributes=dict(old_elem.attrib)
        ))
        diff.element_changes.append(ElementChange(
            tag=new_tag, index=0, action="added",
            attributes=dict(new_elem.attrib)
        ))
        return diff

    # ── Compare attributes ──────────────────────────────────────
    all_attrs = set(old_elem.attrib.keys()) | set(new_elem.attrib.keys())
    for attr in sorted(all_attrs):
        # Skip our internal annotation attribute
        if attr == "_idx":
            continue
        old_val = old_elem.attrib.get(attr)
        new_val = new_elem.attrib.get(attr)
        if old_val != new_val:
            diff.attribute_changes.append(AttributeChange(
                tag=old_tag,
                index=_sibling_index(old_elem),
                attr=attr,
                old_value=old_val,
                new_value=new_val,
            ))

    # ── Compare text content ────────────────────────────────────
    old_text = (old_elem.text or "").strip()
    new_text = (new_elem.text or "").strip()
    if old_text != new_text:
        diff.text_changes.append(TextChange(
            tag=old_tag,
            index=_sibling_index(old_elem),
            old_text=old_text if old_text else None,
            new_text=new_text if new_text else None,
        ))

    # ── Compare children ────────────────────────────────────────
    old_children = get_children(old_elem)
    new_children = get_children(new_elem)

    old_map = _build_child_map(old_children)
    new_map = _build_child_map(new_children)

    all_keys = set(old_map.keys()) | set(new_map.keys())

    for key in sorted(all_keys):
        if key in old_map and key not in new_map:
            for child in old_map[key]:
                diff.element_changes.append(ElementChange(
                    tag=strip_ns(child.tag),
                    index=_sibling_index(child),
                    action="removed",
                    attributes=dict(child.attrib),
                ))
        elif key not in old_map and key in new_map:
            for child in new_map[key]:
                diff.element_changes.append(ElementChange(
                    tag=strip_ns(child.tag),
                    index=_sibling_index(child),
                    action="added",
                    attributes=dict(child.attrib),
                ))
        else:
            for old_child, new_child in zip(old_map[key], new_map[key]):
                child_diff = diff_elements(old_child, new_child)
                diff.attribute_changes.extend(child_diff.attribute_changes)
                diff.element_changes.extend(child_diff.element_changes)
                diff.text_changes.extend(child_diff.text_changes)

    return diff


# ── Pretty-print helpers ───────────────────────────────────────────

def _humanize_attr(attr: str) -> str:
    """Make attribute names more readable."""
    mapping = {
        "fill": "fill color",
        "stroke": "stroke color",
        "stroke-width": "stroke width",
        "r": "radius",
        "cx": "center X",
        "cy": "center Y",
        "font-size": "font size",
        "text-anchor": "text anchor",
        "width": "width",
        "height": "height",
    }
    return mapping.get(attr, attr)


def print_visual_summary(diff: SVGDifference):
    """Print a human-readable, structured summary of changes."""
    print("=" * 60)
    print("  SVG STRUCTURAL DIFF REPORT")
    print("=" * 60)

    if diff.is_empty():
        print("\n  No differences found. The SVGs are structurally identical.")
        return

    total = len(diff.attribute_changes) + len(diff.element_changes) + len(diff.text_changes)
    print(f"\n  Total changes detected: {total}\n")

    if diff.attribute_changes:
        print("  ── Attribute Changes ──")
        for c in diff.attribute_changes:
            readable_attr = _humanize_attr(c.attr)
            if c.old_value is None:
                print(f"    + <{c.tag}> {readable_attr} ADDED: '{c.new_value}'")
            elif c.new_value is None:
                print(f"    - <{c.tag}> {readable_attr} REMOVED (was '{c.old_value}')")
            else:
                print(f"    ~ <{c.tag}> {readable_attr}: '{c.old_value}' -> '{c.new_value}'")
        print()

    if diff.element_changes:
        print("  ── Element Changes ──")
        for c in diff.element_changes:
            print(f"    {c.action.upper()}: <{c.tag}>")
        print()

    if diff.text_changes:
        print("  ── Text Content Changes ──")
        for c in diff.text_changes:
            if c.old_text is None:
                print(f"    + <{c.tag}> text ADDED: '{c.new_text}'")
            elif c.new_text is None:
                print(f"    - <{c.tag}> text REMOVED (was '{c.old_text}')")
            else:
                print(f"    ~ <{c.tag}> text: '{c.old_text}' -> '{c.new_text}'")
        print()

    print("=" * 60)


# ── Main ───────────────────────────────────────────────────────────

def main():
    # Parse both SVGs
    tree_a = ET.parse("a.svg")
    tree_b = ET.parse("b.svg")
    root_a = tree_a.getroot()
    root_b = tree_b.getroot()

    # Annotate sibling indices for better reporting
    _annotate_indices(root_a)
    _annotate_indices(root_b)

    # Compute structural diff
    diff = diff_elements(root_a, root_b)

    # Print results
    print_visual_summary(diff)

    # Also print raw structured output for programmatic use
    print("\n  Structured output (raw):")
    print(f"    {diff.summary()}")


if __name__ == "__main__":
    main()
