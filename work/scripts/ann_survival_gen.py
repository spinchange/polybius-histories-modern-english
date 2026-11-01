"""Generate survival-layer provenance entries (ANNOTATIONS_PLAN A5, Option A).

For every chapter in the book files that carries an italic `*Quoted by ...*`
attribution line, write annotations/survival/<book>-<chapter>.md with
pd_basis: none (no quoted text). Existing files are never overwritten unless
--force, so hand-edited entries survive re-runs and new attributions (e.g. from
WORK_PLAN Phase 6b) are picked up by simply running again.

    python work/scripts/ann_survival_gen.py [--force] [--dry-run]

Only facts present in the book files are used for *which* author preserved a
chapter; author blurbs below are standard reference facts, kept deliberately
short and approximate.
"""
from __future__ import annotations

import re
import sys

from ann_common import ANN, ROOT

BOOK_GLOB = "Polybius_Histories_Book_*_modern_English.md"
HEAD_RE = re.compile(r"^## Book (\d+) Chapter (\d+[a-z]?): (.+?)\s*$")
QUOTE_RE = re.compile(r"^\*Quoted by (.+?)\.?\*\s*$")
SCOPE_RE = re.compile(r"\s*\((?:this|the)[^)]*\)\s*$")

# name -> (blurb, date for the frontmatter, canonical work)
AUTHORS = {
    "Athenaeus": ("Athenaeus of Naucratis wrote the *Deipnosophistae*, a banquet dialogue packed with quotations from earlier writers.", "c. AD 200", "Deipnosophistae"),
    "Suidas": ("Suidas is the traditional name of the author of the Suda, a Byzantine encyclopedic lexicon of about 970.", "c. 970", "Lexicon"),
    "Stephanus of Byzantium": ("Stephanus of Byzantium compiled the *Ethnica*, a gazetteer of place-names and peoples, in the 6th century.", "6th century", "Ethnica"),
    "Strabo": ("Strabo wrote the *Geography*, which argues at length with earlier geographers, Polybius among them.", "c. 20 BC", "Geography"),
    "Plutarch": ("Plutarch, the biographer, wrote in the decades around AD 100.", "c. AD 100", None),
    "Josephus": ("Josephus, the historian of the Jews, wrote the *Jewish Antiquities* about AD 94.", "c. AD 94", "Jewish Antiquities"),
    "Livy": ("Livy wrote his history of Rome under Augustus.", "c. 20 BC", "History of Rome"),
    "Harpocration": ("Harpocration compiled a lexicon of the words of the Ten Attic Orators in the 2nd century AD.", "2nd century AD", "Lexicon of the Ten Orators"),
    "Hero of Byzantium": ("Hero of Byzantium wrote the *Poliorcetica*, a siegecraft manual, in the 10th century.", "10th century", "Poliorcetica"),
}


def split_credit(raw: str) -> list[tuple[str, str]]:
    """'Suidas, Lexicon, and Harpocration, Lexicon of ...' -> [(author, work), ...];
    'Athenaeus, Deipnosophistae; the last sentence by Suidas, Lexicon' likewise."""
    raw = SCOPE_RE.sub("", raw)
    raw = re.sub(r";\s*the last sentence by\s+", " and ", raw)
    found = []
    for name in AUTHORS:
        m = re.search(rf"(?<![\w']){re.escape(name)}\b(?:,\s*([^,;]*?))?(?=\s*(?:,\s*and\s|\s+and\s|$))", raw)
        if m:
            found.append((m.start(), name, (m.group(1) or "").strip()))
    return [(n, w) for _, n, w in sorted(found)]


SCOPE_N = {"this paragraph": 1, "this and the next paragraph": 2, "this and the next two paragraphs": 3,
           "this and the next three paragraphs": 4, "this and the next four paragraphs": 5}


def scope_len(raw: str) -> int | None:
    m = re.search(r"\(([^)]*)\)\s*$", raw)
    return SCOPE_N.get(m.group(1).strip()) if m else None


def scan():
    """chapter -> {title, credits, partial, n_paras, segments: [(first, last, [(author, work)])]}.

    Convention (user decision 2026-11-01, see phase6b_apply_mixed.py): a line governs
    the paragraph below it unless it states a longer scope; a lone unscoped line
    directly under the heading governs the whole chapter. Unmarked paragraphs in a
    mixed chapter come from other sources (Constantinian excerpts, or Wescher's codex in 8.37).
    """
    chapters: dict[tuple[int, str], dict] = {}
    for path in sorted(ROOT.glob(BOOK_GLOB)):
        cur = None
        pending = []   # [raw, paragraph index it precedes]
        for line in path.read_text(encoding="utf-8").splitlines():
            h = HEAD_RE.match(line)
            if h:
                cur = (int(h.group(1)), h.group(2))
                chapters[cur] = {"title": h.group(3), "credits": [], "partial": False, "n_paras": 0, "lines": []}
                continue
            if cur is None:
                continue
            c = chapters[cur]
            q = QUOTE_RE.match(line)
            if q:
                raw = q.group(1)
                c["lines"].append((c["n_paras"] + 1, raw))
                if SCOPE_RE.search(raw) or "last sentence by" in raw:
                    c["partial"] = True
                for pair in split_credit(raw):
                    if pair not in c["credits"]:
                        c["credits"].append(pair)
            elif line.strip() and not line.startswith(("#", "---")):
                c["n_paras"] += 1
    out = {}
    for k, c in chapters.items():
        if not c["credits"]:
            continue
        segs = []
        lone = len(c["lines"]) == 1 and c["lines"][0][0] == 1 and scope_len(c["lines"][0][1]) is None
        for start, raw in c["lines"]:
            n = c["n_paras"] if lone else (scope_len(raw) or 1)
            segs.append((start, min(start + n - 1, c["n_paras"]), split_credit(raw)))
        c["segments"] = segs
        c["mixed"] = not (len(segs) == 1 and segs[0][0] == 1 and segs[0][1] >= c["n_paras"])
        out[k] = c
    return out


def span(a: int, b: int) -> str:
    return f"paragraph {a}" if a == b else f"paragraphs {a} to {b}"


def render(book: int, ch: str, info: dict, n_lines: int) -> str:
    names = [n for n, _ in info["credits"]]
    works = {n: (w or AUTHORS[n][2]) for n, w in info["credits"]}
    ann = "; ".join(names)
    work = "; ".join(f"{n}, {works[n]}" if works[n] else n for n in names)
    date = "; ".join(AUTHORS[n][1] for n in names)
    label = names[0] if len(names) == 1 else " and ".join([", ".join(names[:-1]), names[-1]] if len(names) > 2 else names)
    if info["mixed"]:
        bits = [f"{span(a_, b_)} {'is' if a_ == b_ else 'are'} quoted by " + " and ".join(n for n, _ in cr)
                for a_, b_, cr in info["segments"]]
        covered = {p for a_, b_, _ in info["segments"] for p in range(a_, b_ + 1)}
        rest = [p for p in range(1, info["n_paras"] + 1) if p not in covered]
        body = ["This chapter has more than one source: " + "; ".join(bits) + "."]
        if rest:
            runs, lo = [], rest[0]
            for x, y in zip(rest, rest[1:] + [None]):
                if y != x + 1:
                    runs.append(str(lo) if lo == x else f"{lo} to {x}"); lo = y
            noun = "paragraph" if len(rest) == 1 else "paragraphs"
            body.append(f"The unmarked {noun} ({' and '.join(runs)}) come{'s' if len(rest) == 1 else ''} from no quoting author; "
                        "by this edition's convention they come from the Constantinian excerpts or another collection (see the Phase 6b findings).")
    else:
        body = [f"What we have of this chapter is preserved by {label}."]
    body += [AUTHORS[n][0] for n in names]
    note = " ".join(body)
    return f"""---
id: survival/{book:02d}-{ch}
layer: survival
anchor: ["{book}.{ch}"]
annotator: {ann}
work: {work}
date: {date}
tags: [survival-story]
pd_basis: none
status: verified
generated: ann_survival_gen.py
---
**Note:** {note}
"""


def main(argv: list[str]) -> int:
    force, dry = "--force" in argv, "--dry-run" in argv
    out = ANN / "survival"
    out.mkdir(parents=True, exist_ok=True)
    made = kept = 0
    for (book, ch), info in sorted(scan().items(), key=lambda kv: (kv[0][0], int(re.match(r"\d+", kv[0][1]).group()), kv[0][1])):
        path = out / f"{book:02d}-{ch}.md"
        if path.exists() and not force:
            kept += 1
            continue
        made += 1
        if not dry:
            path.write_text(render(book, ch, info, 0), encoding="utf-8", newline="\n")
    print(f"survival entries: {made} written, {kept} kept{' (dry run)' if dry else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
