#!/usr/bin/env python3
"""Extract paragraphs, footnote references and footnote text from a DOCX.

Usage:
    python extract_docx_footnotes.py input.docx --out inventory.json
    python extract_docx_footnotes.py input.docx --format md
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def qn(local: str) -> str:
    return f"{{{W}}}{local}"


def paragraph_text(p: etree._Element) -> str:
    parts: list[str] = []
    for node in p.iter():
        if node.tag == qn("t"):
            parts.append(node.text or "")
        elif node.tag == qn("tab"):
            parts.append("\t")
        elif node.tag in (qn("br"), qn("cr")):
            parts.append("\n")
    return "".join(parts).strip()


def footnote_refs(p: etree._Element) -> list[int]:
    out: list[int] = []
    for ref in p.iter(qn("footnoteReference")):
        fid = ref.get(qn("id"))
        if fid is not None:
            out.append(int(fid))
    return out


def extract(docx_path: Path) -> dict:
    with zipfile.ZipFile(docx_path) as z:
        doc = etree.fromstring(z.read("word/document.xml"))
        fn_root = etree.fromstring(z.read("word/footnotes.xml"))

    paragraphs = []
    for i, p in enumerate(doc.xpath(".//w:body//w:p", namespaces=NS), start=1):
        paragraphs.append(
            {
                "index": i,
                "text": paragraph_text(p),
                "footnote_refs": footnote_refs(p),
            }
        )

    footnotes = {}
    for fn in fn_root.xpath(".//w:footnote", namespaces=NS):
        fid = fn.get(qn("id"))
        if fid is None or fid in ("-1", "0"):
            continue
        footnotes[int(fid)] = "".join(fn.itertext()).strip()

    return {
        "file": str(docx_path),
        "paragraph_count": len(paragraphs),
        "footnote_count": len(footnotes),
        "referenced_ids": sorted({i for p in paragraphs for i in p["footnote_refs"]}),
        "paragraphs": paragraphs,
        "footnotes": footnotes,
    }


def to_markdown(data: dict) -> str:
    lines = [
        f"# Footnote inventory: {data['file']}",
        "",
        f"- Paragraphs: {data['paragraph_count']}",
        f"- Footnotes: {data['footnote_count']}",
        f"- Referenced IDs: {data['referenced_ids']}",
        "",
        "## Paragraphs with footnote references",
        "",
        "| Para | Footnote refs | Text |",
        "|---:|---|---|",
    ]
    for p in data["paragraphs"]:
        if p["footnote_refs"]:
            text = p["text"].replace("|", "\\|")
            lines.append(f"| {p['index']} | {p['footnote_refs']} | {text} |")
    lines.extend(["", "## Footnotes", "", "| ID | Text |", "|---:|---|"])
    for fid, text in sorted(data["footnotes"].items()):
        lines.append(f"| {fid} | {text.replace('|', '\\|')} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("docx")
    parser.add_argument("--out")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    args = parser.parse_args()

    path = Path(args.docx)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    data = extract(path)
    if args.format == "md":
        output = to_markdown(data)
    else:
        output = json.dumps(data, ensure_ascii=False, indent=2)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Written: {args.out}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
