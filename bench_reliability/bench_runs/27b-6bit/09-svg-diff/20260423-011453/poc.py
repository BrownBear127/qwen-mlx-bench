"""
SVG Structural Diff POC

Compares two SVG files by parsing them as XML and performing a structural
comparison of elements, attributes, and their values. This is far more
useful than a raw text diff because it understands SVG semantics.

Usage:
    uv run --no-project python poc.py
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"


@dataclass
class Change:
    """Represents a single change between two SVG elements."""
    change_type: ChangeType
    element_path: str
    attribute: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    detail: str = ""

    def __str__(self):
        if self.change_type == ChangeType.MODIFIED:
            return (
                f"  • {self.element_path}: attribute '{self.attribute}' "
                f"changed: {self.old_value} -> {self.new_value}"
            )
        elif self.change_type == ChangeType.ADDED:
            return f"  • {self.element_path}: {self.detail}"
        elif self.change_type == ChangeType.REMOVED:
            return f"  • {self.element_path}: {self.detail}"
        return ""


def strip_ns(tag: str) -> str:
    """Remove XML namespace from a tag name."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def element_path(element: ET.Element, root: ET.Element) -> str:
    """Build a human-readable path to an element (e.g. svg > circle)."""
    parts = []
    current = element
    while current is not None and current is not root:
        parts.append(strip_ns(current.tag))
        current = current.getparent() if hasattr(current, 'getparent') else _find_parent(root, current)
    parts.append(strip_ns(root.tag))
    return " > ".join(reversed(parts))


def _find_parent(root: ET.Element, target: ET.Element) -> Optional[ET.Element]:
    """Find the parent of target element by traversing the tree."""
    for child in root.iter():
        for sub in child:
            if sub is target:
                return child
    return None


def build_element_map(element: ET.Element, prefix: str = "") -> dict:
    """
    Build a map of element paths to their tag and attributes.
    Handles multiple elements of the same tag by using indices.
    """
    result = {}
    tag = strip_ns(element.tag)
    current_path = f"{prefix}{tag}" if not prefix else f"{prefix} > {tag}"
    result[current_path] = {
        "tag": tag,
        "attributes": dict(element.attrib),
        "text": (element.text or "").strip(),
    }
    for child in element:
        result.update(build_element_map(child, current_path))
    return result


def build_element_map_with_indices(element: ET.Element, prefix: str = "", indices: dict = None) -> dict:
    """
    Build a map of element paths to their tag and attributes,
    using indices to distinguish sibling elements with the same tag.
    """
    if indices is None:
        indices = {}

    result = {}
    tag = strip_ns(element.tag)
    key = f"{prefix}/{tag}" if prefix else tag

    # Track sibling indices
    if key not in indices:
        indices[key] = 0
    idx = indices[key]
    indices[key] += 1

    current_path = f"{prefix} > {tag}" if prefix else tag
    if idx > 0:
        current_path = f"{prefix} > {tag}[{idx}]" if prefix else f"{tag}[{idx}]"

    result[current_path] = {
        "tag": tag,
        "attributes": dict(element.attrib),
        "text": (element.text or "").strip(),
    }

    for child in element:
        result.update(build_element_map_with_indices(child, current_path, indices))

    return result


def compute_diff(file_a: str, file_b: str) -> list[Change]:
    """
    Compute a structural diff between two SVG files.
    Returns a list of Change objects describing the differences.
    """
    tree_a = ET.parse(file_a)
    tree_b = ET.parse(file_b)
    root_a = tree_a.getroot()
    root_b = tree_b.getroot()

    # Build element maps with indices for proper matching
    map_a = build_element_map_with_indices(root_a)
    map_b = build_element_map_with_indices(root_b)

    changes = []

    # Check for removed elements (in A but not in B)
    for path, data in map_a.items():
        if path not in map_b:
            changes.append(Change(
                change_type=ChangeType.REMOVED,
                element_path=path,
                detail=f"element <{data['tag']}> removed",
            ))

    # Check for added elements (in B but not in A)
    for path, data in map_b.items():
        if path not in map_a:
            changes.append(Change(
                change_type=ChangeType.ADDED,
                element_path=path,
                detail=f"element <{data['tag']}> added",
            ))

    # Check for modified attributes in common elements
    for path in map_a:
        if path not in map_b:
            continue

        data_a = map_a[path]
        data_b = map_b[path]

        all_attrs = set(data_a["attributes"].keys()) | set(data_b["attributes"].keys())
        for attr in sorted(all_attrs):
            val_a = data_a["attributes"].get(attr)
            val_b = data_b["attributes"].get(attr)

            if val_a != val_b:
                if val_a is None:
                    changes.append(Change(
                        change_type=ChangeType.ADDED,
                        element_path=path,
                        attribute=attr,
                        new_value=val_b,
                        detail=f"attribute '{attr}' added with value '{val_b}'",
                    ))
                elif val_b is None:
                    changes.append(Change(
                        change_type=ChangeType.REMOVED,
                        element_path=path,
                        attribute=attr,
                        old_value=val_a,
                        detail=f"attribute '{attr}' removed (was '{val_a}')",
                    ))
                else:
                    changes.append(Change(
                        change_type=ChangeType.MODIFIED,
                        element_path=path,
                        attribute=attr,
                        old_value=val_a,
                        new_value=val_b,
                    ))

        # Check text content
        if data_a["text"] != data_b["text"]:
            changes.append(Change(
                change_type=ChangeType.MODIFIED,
                element_path=path,
                attribute="text",
                old_value=data_a["text"] or "(empty)",
                new_value=data_b["text"] or "(empty)",
            ))

    return changes


def print_diff_summary(file_a: str, file_b: str, changes: list[Change]) -> None:
    """Print a human-readable summary of the diff."""
    print("=" * 60)
    print(f"  SVG Structural Diff: {file_a} vs {file_b}")
    print("=" * 60)

    if not changes:
        print("\n  No differences found. Files are structurally identical.\n")
        return

    # Group changes by type
    modified = [c for c in changes if c.change_type == ChangeType.MODIFIED]
    added = [c for c in changes if c.change_type == ChangeType.ADDED]
    removed = [c for c in changes if c.change_type == ChangeType.REMOVED]

    print(f"\n  Total changes found: {len(changes)}")
    print()

    if modified:
        print(f"  MODIFIED ({len(modified)}):")
        for c in modified:
            print(str(c))
        print()

    if added:
        print(f"  ADDED ({len(added)}):")
        for c in added:
            print(str(c))
        print()

    if removed:
        print(f"  REMOVED ({len(removed)}):")
        for c in removed:
            print(str(c))
        print()

    # Print a concise summary line
    print("-" * 60)
    print("  Summary:")
    for c in modified:
        print(f"    - {c.element_path}: {c.attribute} changed: {c.old_value} -> {c.new_value}")
    for c in added:
        if c.attribute:
            print(f"    - {c.element_path}: {c.attribute} added: {c.new_value}")
        else:
            print(f"    - {c.element_path}: {c.detail}")
    for c in removed:
        if c.attribute:
            print(f"    - {c.element_path}: {c.attribute} removed (was: {c.old_value})")
        else:
            print(f"    - {c.element_path}: {c.detail}")
    print("-" * 60)
    print()


def main():
    """Main entry point."""
    import os

    # Create sample SVG files if they don't exist
    a_svg = "a.svg"
    b_svg = "b.svg"

    if not os.path.exists(a_svg):
        with open(a_svg, "w") as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="50" fill="red" stroke="black" stroke-width="2"/>
</svg>
''')
        print(f"Created sample file: {a_svg}")

    if not os.path.exists(b_svg):
        with open(b_svg, "w") as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="60" fill="blue" stroke="black" stroke-width="2"/>
</svg>
''')
        print(f"Created sample file: {b_svg}")

    # Compute and print the diff
    changes = compute_diff(a_svg, b_svg)
    print_diff_summary(a_svg, b_svg, changes)

    # Also demonstrate with command-line args if provided
    import sys
    if len(sys.argv) >= 3:
        file_a = sys.argv[1]
        file_b = sys.argv[2]
        changes = compute_diff(file_a, file_b)
        print_diff_summary(file_a, file_b, changes)


if __name__ == "__main__":
    main()
