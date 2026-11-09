#!/usr/bin/env python3
r"""Search for an exact quote across local text corpora.

This is a first-pass screening tool, not proof of citation accuracy. A hit
still requires checking the document identity, pinpoint, and proposition fit.

Usage:
    python search_exact_quote.py "The occupying State shall be regarded..." --root "D:\ICCWork"
    python search_exact_quote.py "quote" --root "D:\ICCWork" "C:\...\\Obsidian Vault" --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path


QUOTE_TRANSLATION = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": "'",
        "\u201b": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00a0": " ",
        "\u00ad": "",
    }
)


def normalize(text: str, case_sensitive: bool = False) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(QUOTE_TRANSLATION)
    text = re.sub(r"\s+", " ", text).strip()
    if not case_sensitive:
        text = text.casefold()
    return text


def iter_files(roots: list[str], extensions: set[str]):
    seen = set()
    for root in roots:
        base = Path(root)
        if not base.exists():
            continue
        if base.is_file():
            candidates = [base]
        else:
            candidates = base.rglob("*")
        for path in candidates:
            if not path.is_file():
                continue
            if path.suffix.lower() not in extensions:
                continue
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            try:
                if path.stat().st_size > 80 * 1024 * 1024:
                    continue
            except OSError:
                continue
            yield path


def search_file(path: Path, needle: str, case_sensitive: bool, context_lines: int = 2):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    if not needle:
        return []

    norm_text = normalize(text, case_sensitive)
    positions = []
    cursor = 0
    step = max(1, len(needle))
    while True:
        idx = norm_text.find(needle, cursor)
        if idx == -1:
            break
        positions.append(idx)
        cursor = idx + step

    if not positions:
        return []

    lines = text.splitlines()
    norm_lines = [normalize(line, case_sensitive) for line in lines]
    token = needle[:60].strip()

    def approximate_line(pos: int) -> int:
        if not norm_text:
            return 0
        ratio = pos / len(norm_text)
        original_pos = min(len(text), max(0, int(ratio * len(text))))
        return text.count("\n", 0, original_pos)

    def find_start_line(pos: int) -> int:
        approx = approximate_line(pos)
        lo = max(0, approx - 12)
        hi = min(len(lines), approx + 13)
        if token:
            for i in range(lo, hi):
                if token in norm_lines[i]:
                    return i
        return min(max(approx, 0), max(0, len(lines) - 1))

    hits = []
    seen_lines = set()
    for pos in positions:
        start = find_start_line(pos)
        if start in seen_lines:
            continue
        seen_lines.add(start)
        lo = max(0, start - context_lines)
        hi = min(len(lines), start + context_lines + 1)
        hits.append(
            {
                "file": str(path),
                "line": start + 1,
                "context": "\n".join(lines[lo:hi]),
            }
        )
    return hits


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("quote")
    parser.add_argument("--root", nargs="+", required=True)
    parser.add_argument("--extensions", default=".txt,.md")
    parser.add_argument("--case-sensitive", action="store_true")
    parser.add_argument("--context-lines", type=int, default=2)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    needle = normalize(args.quote, args.case_sensitive)
    extensions = {
        ("." + e.strip().lstrip(".")).lower()
        for e in args.extensions.split(",")
        if e.strip()
    }

    all_hits = []
    for path in iter_files(args.root, extensions):
        all_hits.extend(
            search_file(path, needle, args.case_sensitive, args.context_lines)
        )

    if args.json:
        print(json.dumps({"quote": args.quote, "hits": all_hits}, ensure_ascii=False, indent=2))
    else:
        if not all_hits:
            print("NOT FOUND")
        else:
            for hit in all_hits:
                print(f"\n{hit['file']}:{hit['line']}")
                print(hit["context"])

    return 0 if all_hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
