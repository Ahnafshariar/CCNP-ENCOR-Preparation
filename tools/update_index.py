#!/usr/bin/env python3
"""Auto-maintain the README.

1. Lab index  : scans labs/*/README.md -> table between LAB-INDEX markers.
2. Repo tree  : walks the repo -> folder tree between REPO-TREE markers.
3. Topology   : reads the latest lab's topology section -> TOPOLOGY markers.

All are idempotent and safe to run anytime. CI runs this on every push.
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LABS = ROOT / "labs"
README = ROOT / "README.md"

INDEX_START, INDEX_END = "<!-- LAB-INDEX:START -->", "<!-- LAB-INDEX:END -->"
TREE_START, TREE_END = "<!-- REPO-TREE:START -->", "<!-- REPO-TREE:END -->"
TOPO_START, TOPO_END = "<!-- TOPOLOGY:START -->", "<!-- TOPOLOGY:END -->"
SKIP = {".git", "__pycache__", "node_modules", ".pytest_cache", ".gitkeep", ".DS_Store"}
MAX_DEPTH = 2


# ---------- lab index ----------
def lab_meta(readme: pathlib.Path):
    title, domain = readme.parent.name, "\u2014"
    text = readme.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    m = re.search(r"\*\*ENCOR v1\.2 mapping:\*\*\s*(.+)", text)
    if m:
        domain = m.group(1).split("\u2014")[0].strip()
    return title, domain


def build_table():
    rows = []
    if LABS.exists():
        for d in sorted(p for p in LABS.iterdir() if p.is_dir()):
            rd = d / "README.md"
            if rd.exists():
                title, domain = lab_meta(rd)
                rows.append(f"| [{title}](labs/{d.name}/) | {domain} |")
    if not rows:
        return "_No labs documented yet._"
    return "| Lab | Domain |\n|-----|--------|\n" + "\n".join(rows)


# ---------- repo tree ----------
def build_tree(root: pathlib.Path, max_depth: int = MAX_DEPTH):
    lines = [root.name + "/"]

    def walk(d, prefix, depth):
        entries = sorted(
            (e for e in d.iterdir() if e.name not in SKIP),
            key=lambda p: (p.is_file(), p.name.lower()),
        )
        for i, e in enumerate(entries):
            last = i == len(entries) - 1
            branch = "\u2514\u2500\u2500 " if last else "\u251c\u2500\u2500 "
            lines.append(f"{prefix}{branch}{e.name}{'/' if e.is_dir() else ''}")
            if e.is_dir() and depth < max_depth:
                walk(e, prefix + ("    " if last else "\u2502   "), depth + 1)

    walk(root, "", 1)
    return "\n".join(lines)


# ---------- topology from latest lab ----------
def build_topology():
    """Extract the topology section from the most recent lab's README."""
    if not LABS.exists():
        return "_No labs yet._"

    lab_dirs = sorted(
        (p for p in LABS.iterdir() if p.is_dir() and (p / "README.md").exists()),
        key=lambda p: p.name,
    )
    if not lab_dirs:
        return "_No labs yet._"

    latest = lab_dirs[-1]
    readme = latest / "README.md"
    text = readme.read_text(encoding="utf-8")

    # Get the lab title from H1
    title = latest.name
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Extract from "## Topology" to the next "## " heading
    topo_match = re.search(
        r"(## Topology\s*\n)(.*?)(?=\n## |\Z)",
        text,
        re.S,
    )
    if not topo_match:
        return f"**Currently shown: {title}**\n\n_No topology section found in this lab._"

    topo_content = topo_match.group(2).strip()

    # Scan for topology images in the lab folder (png, jpg, jpeg, gif, webp)
    img_exts = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    images = sorted(
        f for f in latest.iterdir()
        if f.is_file() and f.suffix.lower() in img_exts
    )
    # Also check a configs/ or images/ subfolder
    for subdir_name in ("configs", "images", "screenshots"):
        subdir = latest / subdir_name
        if subdir.is_dir():
            images.extend(sorted(
                f for f in subdir.iterdir()
                if f.is_file() and f.suffix.lower() in img_exts
            ))

    img_block = ""
    if images:
        img_lines = []
        for img in images:
            rel_path = img.relative_to(ROOT)
            # Use the filename (without extension) as alt text, cleaned up
            alt = img.stem.replace("_", " ").replace("-", " ").title()
            img_lines.append(f"![{alt}]({rel_path})")
        img_block = "\n\n" + "\n\n".join(img_lines)

    # Extract from "## Addressing" to the next "## " heading (if exists)
    addr_match = re.search(
        r"(## Addressing\s*\n)(.*?)(?=\n## |\Z)",
        text,
        re.S,
    )
    addr_content = ""
    if addr_match:
        addr_content = "\n\n## Addressing\n\n" + addr_match.group(2).strip()

    return (
        f"**Currently shown: [{title}](labs/{latest.name}/)**"
        f"{img_block}\n\n"
        f"{topo_content}"
        f"{addr_content}\n\n"
        f"*Each lab folder documents its own topology, so the full history stays intact as the network grows.*"
    )


# ---------- shared writer ----------
def replace_block(content, start, end, body):
    if start in content and end in content:
        return re.sub(
            re.escape(start) + r".*?" + re.escape(end),
            f"{start}\n{body}\n{end}",
            content,
            flags=re.S,
        )
    return content


def main():
    content = README.read_text(encoding="utf-8")
    content = replace_block(content, INDEX_START, INDEX_END, build_table())
    content = replace_block(content, TREE_START, TREE_END,
                            f"```\n{build_tree(ROOT)}\n```")
    content = replace_block(content, TOPO_START, TOPO_END, build_topology())
    README.write_text(content, encoding="utf-8")
    print("README updated: lab index + repo tree + topology.")


if __name__ == "__main__":
    main()