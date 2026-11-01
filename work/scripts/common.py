"""Shared helpers for Phase 1 scripts."""
from __future__ import annotations

import csv
import difflib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "work"
REPORTS = WORK / "reports"
STATUS = WORK / "status.csv"
BOOK_GLOB = "Polybius_Histories_Book_[0-9][0-9]_modern_English.md"
HEADING_RE = re.compile(r"^## Book (\d+) Chapter (\d+[a-z]?)(?::\s*(.*))?$")


def book_files() -> list[Path]:
    return sorted(ROOT.glob(BOOK_GLOB))


def read(p: Path) -> str:
    # newline='' preserves existing line endings
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def write(p: Path, text: str) -> None:
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def eol_of(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def diff(old: str, new: str, name: str) -> str:
    return "".join(
        difflib.unified_diff(
            old.splitlines(True), new.splitlines(True), f"a/{name}", f"b/{name}", n=1
        )
    )


def status(phase: str, book: str, chapter: str, action: str, verdict: str, notes: str) -> None:
    WORK.mkdir(exist_ok=True)
    new = not STATUS.exists()
    with open(STATUS, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["phase", "book", "chapter", "action", "verdict", "notes"])
        w.writerow([phase, book, chapter, action, verdict, notes])


def report_path(name: str) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    return REPORTS / name


def bookno(p: Path) -> str:
    return re.search(r"Book_(\d+)_", p.name).group(1)
