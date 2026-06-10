#!/usr/bin/env python3
"""Auto-maintain the README.

1. Lab index  : scans labs/*/README.md -> table between LAB-INDEX markers.
2. Repo tree  : walks the repo -> folder tree between REPO-TREE markers.

Both are idempotent and safe to run anytime. CI runs this on every push.
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LABS = ROOT / "labs"
README = ROOT / "README.md"

INDEX_START, INDEX_END = "<!-- LAB-INDEX:START -->", "<!-- LAB-INDEX:END -->"
TREE_START, TREE_END = "<!-- REPO-TREE:START -->", "<!-- REPO-TREE:END -->"
SKIP = {".git", "__pycache__", "node_modules", ".pytest_cache", ".gitkeep", ".DS_Store"}
MAX_DEPTH = 2  # how many levels deep to show in the tree


# ---------- lab index ----------
def lab_meta(readme: pathlib.Path):
    title, domain = readme.parent.name, "—"
    text = readme.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    m = re.search(r"\*\*ENCOR v1\.2 mapping:\*\*\s*(.+)", text)
    if m:
        domain = m.group(1).split("—")[0].strip()
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
            branch = "└── " if last else "├── "
            lines.append(f"{prefix}{branch}{e.name}{'/' if e.is_dir() else ''}")
            if e.is_dir() and depth < max_depth:
                walk(e, prefix + ("    " if last else "│   "), depth + 1)

    walk(root, "", 1)
    return "\n".join(lines)


# ---------- shared writer ----------
def replace_block(content, start, end, body):
    if start in content and end in content:
        return re.sub(re.escape(start) + r".*?" + re.escape(end),
                      f"{start}\n{body}\n{end}", content, flags=re.S)
    return content


def main():
    content = README.read_text(encoding="utf-8")
    content = replace_block(content, INDEX_START, INDEX_END, build_table())
    content = replace_block(content, TREE_START, TREE_END,
                            f"```\n{build_tree(ROOT)}\n```")
    README.write_text(content, encoding="utf-8")
    print("README lab index + repo tree updated.")


if __name__ == "__main__":
    main()
