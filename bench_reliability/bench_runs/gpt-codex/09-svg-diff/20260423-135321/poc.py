from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from lxml import etree


SVG_A = """<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="50" fill="red" />
</svg>
"""

SVG_B = """<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="60" fill="blue" />
</svg>
"""


def write_sample_svgs(base_dir: Path) -> tuple[Path, Path]:
    a_path = base_dir / "a.svg"
    b_path = base_dir / "b.svg"
    a_path.write_text(SVG_A, encoding="utf-8")
    b_path.write_text(SVG_B, encoding="utf-8")
    return a_path, b_path


def parse_svg(path: Path) -> etree._Element:
    parser = etree.XMLParser(remove_blank_text=True)
    return etree.parse(str(path), parser).getroot()


def local_name(tag: str) -> str:
    return tag.split("}", 1)[-1]


def flatten_tree(root: etree._Element) -> Dict[str, Dict[str, str]]:
    flat: Dict[str, Dict[str, str]] = {}

    def visit(node: etree._Element, path: str) -> None:
        flat[path] = {local_name(key): value for key, value in node.attrib.items()}

        child_counts: Dict[str, int] = {}
        for child in node:
            tag = local_name(child.tag)
            child_counts[tag] = child_counts.get(tag, 0) + 1
            child_path = f"{path}/{tag}[{child_counts[tag]}]"
            visit(child, child_path)

    root_path = f"{local_name(root.tag)}[1]"
    visit(root, root_path)
    return flat


def diff_svg_structures(a_root: etree._Element, b_root: etree._Element) -> List[str]:
    a_nodes = flatten_tree(a_root)
    b_nodes = flatten_tree(b_root)
    changes: List[str] = []

    for path in sorted(set(a_nodes) | set(b_nodes)):
        a_attrs = a_nodes.get(path)
        b_attrs = b_nodes.get(path)

        if a_attrs is None:
            changes.append(f"element added: {path}")
            continue

        if b_attrs is None:
            changes.append(f"element removed: {path}")
            continue

        for attr in sorted(set(a_attrs) | set(b_attrs)):
            before = a_attrs.get(attr)
            after = b_attrs.get(attr)
            if before == after:
                continue

            if before is None:
                changes.append(f"{path} attribute added: {attr} = {after}")
            elif after is None:
                changes.append(f"{path} attribute removed: {attr} (was {before})")
            else:
                changes.append(f"{path} attribute changed: {attr}: {before} -> {after}")

    return changes


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    a_path, b_path = write_sample_svgs(base_dir)

    changes = diff_svg_structures(parse_svg(a_path), parse_svg(b_path))

    print(f"Comparing {a_path.name} vs {b_path.name}")
    print(f"{len(changes)} change(s) detected:")
    for change in changes:
        print(f"- {change}")


if __name__ == "__main__":
    main()
