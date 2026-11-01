"""Shared schema + checks for the annotation layers (ANNOTATIONS_PLAN Phase A1).

Used by ann_validate.py (report) and ann_build.py (emit JSON). Reads only;
never edits annotation files.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from common import HEADING_RE, book_files, read

ROOT = Path(__file__).resolve().parents[2]
ANN = ROOT / "annotations"
SOURCES = ANN / "sources"

LAYERS = ("readers", "parallels", "survival")
STATUSES = ("verified", "UNVERIFIED", "stub")
TAGS = {"constitutional", "military", "historiographical", "fortune", "survival-story"}
PD_BASES = {
    "pre-1930",         # published before 1930 (US public domain)
    "us-gov",           # US government / founders' papers
    "our-translation",  # our own CC0 translation of a public-domain original
}
REQUIRED = (
    "id", "layer", "anchor", "annotator", "work", "date", "tags",
    "source_file", "source_lines", "source_pub", "pd_basis", "status",
)
MAX_NOTE_SENTENCES = 4

# "6.3", "6.3-18", "6.11a", "7.14b-14d"
ANCHOR_RE = re.compile(r"^(\d+)\.(\d+[a-z]?)(?:-(\d+[a-z]?))?$")
ELISION_RE = re.compile(r"\s*(?:\[\s*\.\.\.\s*\]|\.\.\.|…)\s*")  # adjacent dots only, so "word. ..." keeps its period
NOTE_RE = re.compile(r"^\*\*Note:\*\*\s*", re.M)


# ---------------------------------------------------------------- translation

def chapter_key(ch: str) -> tuple[int, str]:
    m = re.match(r"(\d+)([a-z]?)$", ch)
    return (int(m.group(1)), m.group(2))


_CHAPTERS: dict[int, set[str]] | None = None


def chapters() -> dict[int, set[str]]:
    """{book: {chapter ids}} from the translation headings."""
    global _CHAPTERS
    if _CHAPTERS is None:
        _CHAPTERS = {}
        for p in book_files():
            for line in read(p).splitlines():
                m = HEADING_RE.match(line)
                if m:
                    _CHAPTERS.setdefault(int(m.group(1)), set()).add(m.group(2))
    return _CHAPTERS


def parse_anchor(s: str) -> tuple[int, str, str]:
    """'6.3-18' -> (6, '3', '18'); raises ValueError."""
    m = ANCHOR_RE.match(str(s).strip())
    if not m:
        raise ValueError(f"bad anchor {s!r} (want 'B.C' or 'B.C-C')")
    book, start, end = int(m.group(1)), m.group(2), m.group(3) or m.group(2)
    if chapter_key(end) < chapter_key(start):
        raise ValueError(f"anchor {s!r}: range runs backwards")
    have = chapters().get(book)
    if have is None:
        raise ValueError(f"anchor {s!r}: no Book {book} in the translation")
    for ch in {start, end}:
        if ch not in have:
            raise ValueError(f"anchor {s!r}: Book {book} has no Chapter {ch}")
    return book, start, end


# ---------------------------------------------------------------- quotes

_TRANS = str.maketrans({
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "–": "-", "—": "-", "‐": "-", "‑": "-",
    " ": " ", "*": "", "_": "",
})


def normalize(text: str) -> str:
    """Whitespace/quote/dash-insensitive form used for containment."""
    t = unicodedata.normalize("NFC", text).translate(_TRANS)
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r" ?- ?", "-", t)  # OCR often spaces dashes: "Macedonians — which"


def quote_segments(quote: str) -> list[str]:
    """Split a trimmed quote on elision marks ('...', '…', '[...]')."""
    return [s for s in (normalize(x) for x in ELISION_RE.split(quote)) if s]


def contained(quote: str, slice_text: str) -> str | None:
    """None if every segment occurs in order in slice_text; else the first miss."""
    hay = normalize(slice_text)
    pos = 0
    for seg in quote_segments(quote):
        i = hay.find(seg, pos)
        if i < 0:
            return seg
        pos = i + len(seg)
    return None


def sentence_count(text: str) -> int:
    t = re.sub(r"\b(?:[A-Z]|cf|ed|tr|vol|ch|e\.g|i\.e|c)\.", "", text)
    return len([s for s in re.split(r"(?<=[.!?])[\"”’)]*\s+", t.strip()) if s])


# ---------------------------------------------------------------- records

@dataclass
class Annotation:
    path: Path
    meta: dict = field(default_factory=dict)
    quote: str = ""
    note: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    anchors: list[tuple[int, str, str]] = field(default_factory=list)

    @property
    def rel(self) -> str:
        return self.path.relative_to(ROOT).as_posix()

    @property
    def status(self) -> str:
        return self.meta.get("status", "?")

    @property
    def ok(self) -> bool:
        return not self.errors


def parse(path: Path) -> Annotation:
    a = Annotation(path)
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        a.errors.append("no YAML frontmatter")
        return a
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        a.errors.append(f"frontmatter YAML: {e}")
        return a
    if not isinstance(meta, dict):
        a.errors.append("frontmatter is not a mapping")
        return a
    a.meta = meta
    body = m.group(2)
    parts = NOTE_RE.split(body, maxsplit=1)
    a.quote = parts[0].strip()
    a.note = parts[1].strip() if len(parts) > 1 else ""
    return a


def check(a: Annotation) -> Annotation:
    """Fill a.errors / a.warnings. Only verified annotations must be clean;
    on stub/UNVERIFIED files, errors are downgraded to warnings."""
    if not a.errors:
        _check(a)
    st = a.meta.get("status")
    if st in ("stub", "UNVERIFIED") and a.errors:
        a.warnings.extend(f"[{st}] {e}" for e in a.errors)
        a.errors = []
    return a


def _check(a: Annotation) -> None:
    m = a.meta
    for k in REQUIRED:
        if k not in m or m[k] in (None, "", []):
            a.errors.append(f"missing field: {k}")
    if a.errors:
        return

    layer = a.path.parent.name
    if m["layer"] not in LAYERS:
        a.errors.append(f"layer {m['layer']!r} not in {LAYERS}")
    elif m["layer"] != layer:
        a.errors.append(f"layer {m['layer']!r} but file is in {layer}/")
    if m["id"] != f"{layer}/{a.path.stem}":
        a.errors.append(f"id {m['id']!r} should be {layer}/{a.path.stem!r}")
    if m["status"] not in STATUSES:
        a.errors.append(f"status {m['status']!r} not in {STATUSES}")
    if m["pd_basis"] not in PD_BASES:
        a.errors.append(f"pd_basis {m['pd_basis']!r} not in {sorted(PD_BASES)}")

    tags = m["tags"] if isinstance(m["tags"], list) else [m["tags"]]
    bad = [t for t in tags if t not in TAGS]
    if bad:
        a.errors.append(f"unknown tags {bad} (allowed: {sorted(TAGS)})")

    anchors = m["anchor"] if isinstance(m["anchor"], list) else [m["anchor"]]
    for s in anchors:
        try:
            a.anchors.append(parse_anchor(s))
        except ValueError as e:
            a.errors.append(str(e))

    # source file + line slice
    src = (ANN / str(m["source_file"])).resolve()
    if SOURCES.resolve() not in src.parents:
        a.errors.append(f"source_file must live under annotations/sources/: {m['source_file']}")
        return
    if not src.is_file():
        a.errors.append(f"source_file not found: {m['source_file']}")
        return
    sl = m["source_lines"]
    if not (isinstance(sl, list) and len(sl) == 2 and all(isinstance(x, int) for x in sl)):
        a.errors.append(f"source_lines must be [start, end] ints, got {sl!r}")
        return
    lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
    lo, hi = sl
    if not (1 <= lo <= hi <= len(lines)):
        a.errors.append(f"source_lines {sl} out of range (file has {len(lines)} lines)")
        return
    slice_text = "\n".join(lines[lo - 1:hi])

    # Optional, auditable OCR repairs: ocr_fixes: [["mo one", "no one"], ...].
    # Each 'from' must occur in the (normalized) slice; fixes are surfaced as
    # warnings so A6 review sees every one.
    fixes = m.get("ocr_fixes") or []
    if fixes:
        slice_text = normalize(slice_text)
        for fx in fixes:
            if not (isinstance(fx, list) and len(fx) == 2 and all(isinstance(x, str) for x in fx)):
                a.errors.append(f"ocr_fixes entry must be [from, to] strings: {fx!r}")
                continue
            src_s, dst_s = normalize(fx[0]), normalize(fx[1])
            if src_s not in slice_text:
                a.errors.append(f"ocr_fixes: {fx[0]!r} not found in source slice")
                continue
            slice_text = slice_text.replace(src_s, dst_s)
            a.warnings.append(f"ocr_fix applied: {fx[0]!r} -> {fx[1]!r}")

    if not a.quote:
        a.errors.append("empty quote body")
    elif m["pd_basis"] == "our-translation":
        # Quote is our English; source slice is the original. Containment can't
        # apply — the slice must exist and be non-empty, and a human/Opus pass
        # owns fidelity (Phase A4/A6).
        if not slice_text.strip():
            a.errors.append("source_lines slice is empty")
        a.warnings.append("our-translation: quote not containment-checked (A4/A6 review)")
    else:
        miss = contained(a.quote, slice_text)
        if miss is not None:
            a.errors.append(f"quote not found in {m['source_file']}:{lo}-{hi}: {miss[:70]!r}")

    if not a.note:
        a.errors.append("missing **Note:** lede")
    else:
        n = sentence_count(a.note)
        if n > MAX_NOTE_SENTENCES:
            a.warnings.append(f"lede has {n} sentences (max {MAX_NOTE_SENTENCES})")


def load_all() -> list[Annotation]:
    out = []
    for layer in LAYERS:
        d = ANN / layer
        if d.is_dir():
            out.extend(check(parse(p)) for p in sorted(d.glob("*.md")))
    # duplicate ids
    seen: dict[str, str] = {}
    for a in out:
        i = a.meta.get("id")
        if i in seen:
            a.errors.append(f"duplicate id {i!r} (also {seen[i]})")
        elif i:
            seen[i] = a.rel
    return out
