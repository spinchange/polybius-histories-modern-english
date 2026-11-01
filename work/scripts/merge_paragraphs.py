"""Join paragraph breaks that fall mid-sentence.

Merge para N+1 into N (single space) when N does not end in terminal
punctuation (. ! ? : " ” — optionally followed by closers) OR N+1 starts with a
lowercase letter or one of  ,  )  ”  ;  .
Headings, blank-only lines, block lines (> - * | italics attribution) are never
merged into or out of.  Idempotent.

Usage: merge_paragraphs.py [--dry-run]
"""
from __future__ import annotations

import re
import sys

from common import *

TERMINAL = re.compile(r'([.!?:—…]|\.\.\.)[\'"”’)\]*_]*$|["”]$')
CONT_START = re.compile(r"^[a-z,)”]")


def is_block(line: str) -> bool:
    return line.startswith(("#", ">", "- ", "* ", "|", "*", "---", "<")) or line[:1].isdigit() and bool(re.match(r"\d+\.\s", line))


def process(text: str):
    eol = eol_of(text)
    lines = text.split(eol)
    out: list[str] = []
    merges: list[tuple[int, str, str]] = []
    prev_idx = None  # index in out of the last body paragraph, if immediately previous para
    i = 0
    n = len(lines)
    # paragraphs = runs of nonblank lines; this corpus is one line per paragraph
    last_para = None  # out index of previous paragraph (None after heading/block)
    gap_ok = False
    for ln, line in enumerate(lines, 1):
        if line.strip() == "":
            out.append(line)
            continue
        if is_block(line):
            out.append(line)
            last_para = None
            continue
        if last_para is not None:
            prev = out[last_para]
            if not TERMINAL.search(prev.rstrip()) or CONT_START.match(line):
                reason = "no-terminal" if not TERMINAL.search(prev.rstrip()) else "lowercase/cont-start"
                merges.append((ln, reason, prev[-45:] + " ¶ " + line[:45]))
                out[last_para] = prev.rstrip() + " " + line.lstrip()
                # drop the blank lines between
                while out and out[-1].strip() == "":
                    out.pop()
                continue
        out.append(line)
        last_para = len(out) - 1
    # last_para gets invalid if blanks popped before append -> recompute safe: handled since we only pop trailing blanks
    return eol.join(out), merges


def main() -> None:
    dry = "--dry-run" in sys.argv
    rep = []
    total = 0
    for p in book_files():
        old = read(p)
        # last_para index tracking requires out list integrity; fix: run until stable
        new, merges = process(old)
        while True:
            n2, m2 = process(new)
            if not m2:
                break
            new, merges = n2, merges + m2
        total += len(merges)
        if merges:
            rep.append(f"## {p.name}: {len(merges)} merges")
            rep += [f"  L{ln} [{why}] …{ctx}" for ln, why, ctx in merges]
            if not dry:
                write(p, new)
            status("1", bookno(p), "", "merge_paragraphs", "dry" if dry else "applied", str(len(merges)))
    report_path("merge_paragraphs.txt").write_text(
        f"Total merges: {total}\n\n" + "\n".join(rep), encoding="utf-8"
    )
    print(f"merge_paragraphs: {total} merges ({'dry-run' if dry else 'applied'})")


if __name__ == "__main__":
    main()
