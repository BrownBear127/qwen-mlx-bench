"""
Structural SVG Diff — compares two SVG files by parsing their XML tree
and reporting semantic differences (attribute changes, added/removed elements).
"""

import sys
from pathlib import Path
from xml.etree import ElementTree as ET


def strip_ns(tag: str) -> str:
    """Remove XML namespace prefix from a tag name."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def element_signature(el: ET.Element) -> str:
    """A short human-readable label for an element, e.g. 'circle#myid' or 'rect'."""
    tag = strip_ns(el.tag)
    eid = el.get("id")
    return f"{tag}#{eid}" if eid else tag


def collect_elements(root: ET.Element) -> list[tuple[str, ET.Element]]:
    """Flatten the tree into (xpath-like path, element) pairs."""
    results: list[tuple[str, ET.Element]] = []

    def walk(el: ET.Element, path: str, sibling_counts: dict[str, int] | None = None):
        tag = strip_ns(el.tag)
        if sibling_counts and sibling_counts.get(tag, 0) > 1:
            idx = sum(1 for _ in results if _.startswith(f"{path}/{tag}") or True)  # noqa
        full = f"{path}/{tag}" if path else tag
        results.append((full, el))
        # count children by tag for disambiguation
        child_tags: dict[str, int] = {}
        for ch in el:
            t = strip_ns(ch.tag)
            child_tags[t] = child_tags.get(t, 0) + 1
        for ch in el:
            walk(ch, full, child_tags)

    walk(root, "")
    return results


def match_elements(
    a_elems: list[tuple[str, ET.Element]],
    b_elems: list[tuple[str, ET.Element]],
) -> tuple[
    list[tuple[str, ET.Element, ET.Element]],
    list[tuple[str, ET.Element]],
    list[tuple[str, ET.Element]],
]:
    """Match elements between two trees by path. Returns (matched, only_in_a, only_in_b)."""
    a_map: dict[str, list[ET.Element]] = {}
    for path, el in a_elems:
        a_map.setdefault(path, []).append(el)

    b_map: dict[str, list[ET.Element]] = {}
    for path, el in b_elems:
        b_map.setdefault(path, []).append(el)

    matched = []
    only_a = []
    only_b = []

    all_paths = dict.fromkeys([p for p, _ in a_elems] + [p for p, _ in b_elems])

    for path in all_paths:
        a_list = a_map.get(path, [])
        b_list = b_map.get(path, [])
        for i in range(max(len(a_list), len(b_list))):
            if i < len(a_list) and i < len(b_list):
                matched.append((path, a_list[i], b_list[i]))
            elif i < len(a_list):
                only_a.append((path, a_list[i]))
            else:
                only_b.append((path, b_list[i]))

    return matched, only_a, only_b


def diff_attributes(
    path: str, a: ET.Element, b: ET.Element
) -> list[dict]:
    """Compare attributes of two matched elements."""
    changes = []
    a_attrs = dict(a.attrib)
    b_attrs = dict(b.attrib)
    all_keys = dict.fromkeys(list(a_attrs) + list(b_attrs))

    for key in all_keys:
        va = a_attrs.get(key)
        vb = b_attrs.get(key)
        if va == vb:
            continue
        if va is None:
            changes.append({"type": "attr_added", "element": path, "attr": key, "value": vb})
        elif vb is None:
            changes.append({"type": "attr_removed", "element": path, "attr": key, "value": va})
        else:
            change: dict = {
                "type": "attr_changed",
                "element": path,
                "attr": key,
                "old": va,
                "new": vb,
            }
            # If both are numeric, include the delta
            try:
                delta = float(vb) - float(va)
                change["delta"] = delta
            except ValueError:
                pass
            changes.append(change)

    # Compare text content
    at = (a.text or "").strip()
    bt = (b.text or "").strip()
    if at != bt:
        changes.append({
            "type": "text_changed",
            "element": path,
            "old": at or "(empty)",
            "new": bt or "(empty)",
        })

    return changes


def svg_diff(file_a: str, file_b: str) -> list[dict]:
    """Compute a structural diff between two SVG files."""
    tree_a = ET.parse(file_a)
    tree_b = ET.parse(file_b)

    a_elems = collect_elements(tree_a.getroot())
    b_elems = collect_elements(tree_b.getroot())

    matched, only_a, only_b = match_elements(a_elems, b_elems)

    changes: list[dict] = []

    for path, ea, eb in matched:
        changes.extend(diff_attributes(path, ea, eb))

    for path, el in only_a:
        changes.append({
            "type": "element_removed",
            "element": path,
            "tag": strip_ns(el.tag),
            "attrs": dict(el.attrib),
        })

    for path, el in only_b:
        changes.append({
            "type": "element_added",
            "element": path,
            "tag": strip_ns(el.tag),
            "attrs": dict(el.attrib),
        })

    return changes


def format_change(c: dict) -> str:
    """Pretty-print a single change record."""
    t = c["type"]
    el = c.get("element", "")

    if t == "attr_changed":
        line = f"  [{el}] {c['attr']}: {c['old']} -> {c['new']}"
        if "delta" in c:
            line += f"  (delta: {c['delta']:+g})"
        return line
    if t == "attr_added":
        return f"  [{el}] +{c['attr']}={c['value']}"
    if t == "attr_removed":
        return f"  [{el}] -{c['attr']}={c['value']}"
    if t == "text_changed":
        return f"  [{el}] text: {c['old']} -> {c['new']}"
    if t == "element_added":
        return f"  + <{c['tag']}> added at {el}  {c['attrs']}"
    if t == "element_removed":
        return f"  - <{c['tag']}> removed from {el}  {c['attrs']}"
    return f"  {c}"


def main():
    here = Path(__file__).parent
    file_a = here / "a.svg"
    file_b = here / "b.svg"

    if not file_a.exists() or not file_b.exists():
        print("Error: a.svg and b.svg must exist in the same directory as poc.py", file=sys.stderr)
        sys.exit(1)

    changes = svg_diff(str(file_a), str(file_b))

    print(f"SVG Structural Diff: {file_a.name} vs {file_b.name}")
    print(f"{'=' * 50}")

    if not changes:
        print("No structural differences found.")
    else:
        print(f"Found {len(changes)} difference(s):\n")
        for c in changes:
            print(format_change(c))

    print()


if __name__ == "__main__":
    main()
