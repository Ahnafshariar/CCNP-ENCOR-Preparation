#!/usr/bin/env python3
"""Regenerate the lab index table in README.md by scanning labs/*/README.md.

Pulls the H1 title and the "ENCOR v1.2 mapping" line from each lab and rewrites
the table between the LAB-INDEX markers. Idempotent and safe to run anytime.
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LABS = ROOT / "labs"
README = ROOT / "README.md"
START = "<!-- LAB-INDEX:START -->"
END = "<!-- LAB-INDEX:END -->"


def lab_meta(readme: pathlib.Path):
    title = readme.parent.name
    domain = "—"
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


def main():
    block = f"{START}\n{build_table()}\n{END}"
    content = README.read_text(encoding="utf-8")
    if START in content and END in content:
        content = re.sub(
            re.escape(START) + r".*?" + re.escape(END), block, content, flags=re.S
        )
    else:
        content = content.rstrip() + "\n\n## Lab index\n\n" + block + "\n"
    README.write_text(content, encoding="utf-8")
    print("Lab index updated.")


if __name__ == "__main__":
    main()
