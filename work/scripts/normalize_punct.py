"""Punctuation normalisation. Idempotent.  Usage: normalize_punct.py [--dry-run]

 - straight " and ' -> curly; context rule (open after start/space/([—–“‘, else close).
   Per-file unbalanced counts are REPORTED, never "fixed" by guesswork.
 - em-dash: spaced " — " / " – " / " -- " -> unspaced "—" (headings untouched)
 - "B. C. 215" / ", B.C. 213" -> "215 BC"; "B.C. 210-206" -> "210–206 BC"
 - full-width parens （） -> ()
 - standalone lacunae  ***  ****  ...  …  -> "[...]"
   (not touching ... inside existing [...] brackets, nor '…' glued to words)
"""
from __future__ import annotations

import re
import sys

from common import *

OPENERS = "([{—–“‘ \t "


def curly_quotes(line: str) -> str:
    out = []
    for i, ch in enumerate(line):
        prev = line[i - 1] if i else " "
        nxt = line[i + 1] if i + 1 < len(line) else " "
        if ch == '"':
            out.append("“" if (i == 0 or prev in OPENERS) and nxt not in " \t" else "”")
        elif ch == "'":
            if prev.isalnum() and nxt.isalnum():
                out.append("’")  # apostrophe
            elif (i == 0 or prev in OPENERS) and nxt.isalnum():
                out.append("‘")
            else:
                out.append("’")
        else:
            out.append(ch)
    return "".join(out)


BC_RANGE = re.compile(r"\bB\.\s?C\.\s*(\d+)\s*[-–]\s*(\d+)")
BC_ONE = re.compile(r"\bB\.\s?C\.\s*(\d+)")
LACUNA = re.compile(r"(?:(?<=\s)|(?<=—)|^)(?:\*{3,}|\.\.\.|…)(?=[\s,;:)—]|$)")


def fix_lacunae(line: str) -> str:
    # skip when line already holds "[...]" pieces only at those positions
    return LACUNA.sub("[...]", line)


def process_line(line: str, is_heading: bool) -> str:
    line = line.replace("（", "(").replace("）", ")")
    line = BC_RANGE.sub(lambda m: f"{m.group(1)}–{m.group(2)} BC", line)
    line = BC_ONE.sub(lambda m: f"{m.group(1)} BC", line)
    if not is_heading:
        line = re.sub(r"\s+(?:—|–|--)\s+", "—", line)
        line = re.sub(r"(?<=\w)--(?=\w)", "—", line)
    line = fix_lacunae(line)
    line = curly_quotes(line)
    return line


def balance(text: str):
    """Return per-paragraph unbalanced double-quote counts."""
    bad = []
    for ln, l in enumerate(text.split("\n"), 1):
        o, c = l.count("“"), l.count("”")
        if o != c:
            bad.append((ln, o, c, l[:70]))
    return bad


def main() -> None:
    dry = "--dry-run" in sys.argv
    rep, unb = [], []
    for p in book_files():
        old = read(p)
        eol = eol_of(old)
        lines = old.split(eol)
        new = [process_line(l, l.startswith("#")) for l in lines]
        newt = eol.join(new)
        changed = sum(a != b for a, b in zip(lines, new))
        if changed:
            rep.append(f"## {p.name}: {changed} lines changed")
            rep.append(diff(old, newt, p.name))
            if not dry:
                write(p, newt)
            status("1", bookno(p), "", "normalize_punct", "dry" if dry else "applied", str(changed))
        bad = balance(newt)
        unb.append(f"## {p.name}: {len(bad)} paragraphs with unbalanced “/”")
        unb += [f"  L{ln} open={o} close={c}  {t}" for ln, o, c, t in bad]
    report_path("normalize_punct.diff.txt").write_text("\n".join(rep), encoding="utf-8")
    report_path("quote_balance.txt").write_text("\n".join(unb), encoding="utf-8")
    print(f"normalize_punct: {len(rep)//2} files changed ({'dry-run' if dry else 'applied'})")


if __name__ == "__main__":
    main()
