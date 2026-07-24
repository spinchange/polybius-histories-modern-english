"""Normalize the assembled book markdown files to one consistent format.

Target format for every Polybius_Histories_Book_NN_modern_English.md:

    # Polybius — The Histories, Book <ROMAN>

    Modern English translation of the Greek text.

    ## Book N Chapter L: Title
    ...

Rules:
- Chapter headings are uniformly level-2 (books 1-3 used ##, books 4-39 used #).
- Redundant placeholder titles ("Chapter 54: Chapter 54") lose the title part;
  the heading becomes "## Book 4 Chapter 54".
- Stray preamble lines (old title blocks, bare "## Book N" headings) are dropped
  and replaced by the standard title block.
- Book 17 keeps its survival note under the standard title block.
- Body text is left untouched.
"""

from __future__ import annotations

import re
from pathlib import Path

BASE = Path(__file__).resolve().parent

BOOK_RE = re.compile(r"Polybius_Histories_Book_(\d+)_modern_English\.md$")
CHAPTER_RE = re.compile(r"^#+\s+Book\s+(\d+)\s+Chapter\s+(\d+[a-z]?)\s*:?\s*(.*?)\s*$", re.I)
PREAMBLE_RE = re.compile(r"^#+\s*(?:Polybius|Book\s+\d+\s*$)", re.I)
SUBTITLE = "Modern English translation of the Greek text."


def roman(n: int) -> str:
    vals = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    out = []
    for value, numeral in vals:
        while n >= value:
            out.append(numeral)
            n -= value
    return "".join(out)


def normalize(path: Path, number: int) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = [
        f"# Polybius — The Histories, Book {roman(number)}",
        "",
        SUBTITLE,
        "",
    ]
    seen_chapter = False
    for line in lines:
        stripped = line.strip()
        match = CHAPTER_RE.match(stripped)
        if match:
            seen_chapter = True
            label = match.group(2)
            title = match.group(3).strip()
            if not title or title.lower() == f"chapter {label}".lower():
                out.append(f"## Book {number} Chapter {label}")
            else:
                out.append(f"## Book {number} Chapter {label}: {title}")
            continue
        if not seen_chapter:
            # Preamble region: drop old title blocks / bare book headings / subtitle.
            if not stripped:
                continue
            if PREAMBLE_RE.match(stripped) or stripped == SUBTITLE:
                continue
        out.append(line.rstrip())

    # Collapse runs of blank lines to a single blank line.
    collapsed: list[str] = []
    for line in out:
        if line == "" and collapsed and collapsed[-1] == "":
            continue
        collapsed.append(line)
    while collapsed and collapsed[-1] == "":
        collapsed.pop()

    new_text = "\n".join(collapsed) + "\n"
    old_text = path.read_text(encoding="utf-8")
    if new_text != old_text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    files = sorted(BASE.glob("Polybius_Histories_Book_*_modern_English.md"))
    if len(files) != 39:
        raise SystemExit(f"Expected 39 book files, found {len(files)}")
    for path in files:
        number = int(BOOK_RE.search(path.name).group(1))
        if normalize(path, number):
            changed += 1
            print(f"normalized {path.name}")
    print(f"{changed} of {len(files)} files changed")


if __name__ == "__main__":
    main()
