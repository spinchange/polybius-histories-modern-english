"""Phase 6b: build evidence packets for the escalated testimonia attributions.

For each Phase 6 attribution row marked ESCALATE/UNSURE in work/status.csv, locate the
chapter's Greek (from source/) inside an OCR'd 19th-c. critical edition and dump the
surrounding OCR (text + apparatus / bracketed source notes) into a packet.

Editions (OCR text from archive.org, untrusted data, read only):
  Books 7-8   Büttner-Wobst vol. 2 (1889)            polybiihistoriae02poly
  Books 9-19  Didot / Dübner (1859), fallback 1839   bub_gb_EiWxyXqg16EC, polybiihistoria00dbgoog
  Books 20-39 Büttner-Wobst vol. 4 (1904)            polybiihistoria00unkngoog

Usage: python -I phase6b_prep.py <repo_root>
"""
import csv, re, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(sys.argv[1])
RAW = ROOT / "work/phase6b/raw_bw"
OUT = ROOT / "work/phase6b/packets"

EDITIONS = {
    "bw2": ("Büttner-Wobst vol. 2 (Teubner 1889)", "polybiihistoriae02poly.txt"),
    "didot59": ("Didot/Dübner (Paris 1859)", "bub_gb_EiWxyXqg16EC.txt"),
    "didot39": ("Didot/Dübner (Paris 1839)", "polybiihistoria00dbgoog.txt"),
    "bw4": ("Büttner-Wobst vol. 4 (Teubner 1904)", "polybiihistoria00unkngoog.txt"),
}


def editions_for(book):
    if book <= 8:
        return ["bw2"]
    if book <= 19:
        return ["didot59", "didot39"]
    return ["bw4"]


def norm_chars(s):
    s = unicodedata.normalize("NFD", s.lower())
    out = []
    for ch in s:
        if unicodedata.combining(ch):
            continue
        if ch == "ς":
            ch = "σ"
        if "α" <= ch <= "ω":
            out.append(ch)
    return out


class Edition:
    def __init__(self, path):
        self.lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        chars, idx = [], []
        for ln, line in enumerate(self.lines):
            for ch in norm_chars(line):
                chars.append(ch)
                idx.append(ln)
        self.s = "".join(chars)
        self.idx = idx
        self.grams = defaultdict(list)
        for i in range(len(self.s) - 4):
            self.grams[self.s[i:i + 5]].append(i)

    def locate(self, q):
        votes = Counter()
        for j in range(len(q) - 4):
            for p in self.grams.get(q[j:j + 5], ())[:400]:
                votes[(p - j) // 40] += 1
        if not votes:
            return None, 0
        (b, v), = votes.most_common(1)
        start = max(0, b * 40)
        score = v / max(1, len(q) - 4)
        return self.idx[min(start, len(self.idx) - 1)], score


def chapter_greek(book, ch):
    f = ROOT / f"source/book_{book:02d}" / (f"chapter_{int(ch):02d}.md" if ch.isdigit() else f"chapter_{ch}.md")
    if not f.exists():
        return None, f
    t = f.read_text(encoding="utf-8")
    m = re.search(r"## Greek\s*\n(.*?)(\n## |\Z)", t, re.S)
    return (m.group(1) if m else ""), f


def english_chapter(book, ch):
    f = ROOT / f"Polybius_Histories_Book_{book:02d}_modern_English.md"
    t = f.read_text(encoding="utf-8")
    m = re.search(rf"^## Book {book} Chapter {re.escape(ch)}:.*?(?=^## |\Z)", t, re.S | re.M)
    return m.group(0).strip() if m else "(chapter not found)"


def main():
    eds = {}
    rows = []
    with open(ROOT / "work/status.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["phase"] == "6" and r["action"] == "attribution" and r["verdict"] in ("ESCALATE", "UNSURE"):
                rows.append(r)
    OUT.mkdir(parents=True, exist_ok=True)
    seen = set()
    summary = []
    for r in rows:
        book, ch = int(r["book"]), r["chapter"].strip()
        if (book, ch) in seen:
            continue
        seen.add((book, ch))
        greek, gf = chapter_greek(book, ch)
        parts = [f"# Packet {book}.{ch}", "", f"Phase 6 note: {r['verdict']}: {r['notes']}", "",
                 "## Our English chapter (book file)", "", english_chapter(book, ch), ""]
        if greek is None:
            parts += [f"(no source Greek file {gf.name})"]
            summary.append(f"{book}.{ch}\tNO-GREEK")
        else:
            parts += ["## Our Greek (source/, Büttner-Wobst via Perseus)", "", greek.strip(), ""]
            q = "".join(norm_chars(greek))
            head, tail = q[:160], q[-160:]
            for key in editions_for(book):
                if key not in eds:
                    eds[key] = Edition(RAW / EDITIONS[key][1])
                ed = eds[key]
                l1, s1 = ed.locate(head)
                l2, s2 = ed.locate(tail)
                summary.append(f"{book}.{ch}\t{key}\thead={l1}({s1:.2f})\ttail={l2}({s2:.2f})")
                if l1 is None:
                    continue
                if l2 is None or l2 < l1 or l2 - l1 > 400:
                    l2 = l1 + 40
                a, b = max(0, l1 - 25), min(len(ed.lines), l2 + 70)
                parts += [f"## OCR: {EDITIONS[key][0]} — lines {a+1}-{b} (match head {s1:.2f}, tail {s2:.2f})", "",
                          "```", *ed.lines[a:b], "```", ""]
                if key == "didot59" and s1 >= 0.35:
                    break
        (OUT / f"{book:02d}_{ch}.md").write_text("\n".join(parts), encoding="utf-8")
    (OUT / "_summary.tsv").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
