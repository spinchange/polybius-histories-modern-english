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


def scan():
    chapters: dict[tuple[int, str], dict] = {}
    for path in sorted(ROOT.glob(BOOK_GLOB)):
        cur = None
        for line in path.read_text(encoding="utf-8").splitlines():
            h = HEAD_RE.match(line)
            if h:
                cur = (int(h.group(1)), h.group(2))
                chapters[cur] = {"title": h.group(3), "credits": [], "partial": False}
                continue
            q = QUOTE_RE.match(line)
            if q and cur:
                c = chapters[cur]
                if SCOPE_RE.search(q.group(1)):
                    c["partial"] = True
                for pair in split_credit(q.group(1)):
                    if pair not in c["credits"]:
                        c["credits"].append(pair)
                if "last sentence by" in q.group(1):
                    c["partial"] = True
    return {k: v for k, v in chapters.items() if v["credits"]}


def render(book: int, ch: str, info: dict, n_lines: int) -> str:
    names = [n for n, _ in info["credits"]]
    works = {n: (w or AUTHORS[n][2]) for n, w in info["credits"]}
    ann = "; ".join(names)
    work = "; ".join(f"{n}, {works[n]}" if works[n] else n for n in names)
    date = "; ".join(AUTHORS[n][1] for n in names)
    label = names[0] if len(names) == 1 else " and ".join([", ".join(names[:-1]), names[-1]] if len(names) > 2 else names)
    s1 = f"What we have of this chapter is preserved by {label}."
    body = [s1] + [AUTHORS[n][0] for n in names]
    if len(names) > 1 or info["partial"]:
        body.append("Not every paragraph has the same source, so the italic lines in the text say which paragraph is whose.")
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
