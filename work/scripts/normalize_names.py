"""Deterministic name normalisation per the style sheet (WORK_PLAN Phase 1.3).
Word-boundary replacements only.  Gauls/Celts/Galatians and Spartans/Lacedaemonians
are deliberately NOT handled here (Phase 6, context-dependent).
Usage: normalize_names.py [--dry-run]
"""
from __future__ import annotations
import re, sys, unicodedata
from common import *

RULES = [
    (r"\bNew Carthagena\b", "New Carthage"),
    (r"\bCarthagena\b", "New Carthage"),
    (r"\bMassanissa\b", "Masinissa"),
    (r"\bGenthius\b", "Gentius"),
    (r"\bAchaia\b", "Achaea"),
    (r"\bPoseidonius\b", "Posidonius"),
    (r"\bPaullus\b", "Paulus"),
    (r"\bTarantines\b", "Tarentines"),
    (r"\bHeronymus\b", "Hieronymus"),
    (r"Moag(?:ĕ|ĕ)[Tt]es", "Moagetes"),
    (r"\bMightly\b", "Mighty"),
    (r"\bIber\b", "Ebro"),
    (r"\bPadus\b", "Po"),
    (r"\bIster\b", "Danube"),
]
COMPILED = [(re.compile(a), b) for a, b in RULES]

def main():
    dry = "--dry-run" in sys.argv
    rep, total = [], 0
    for p in book_files():
        old = read(p)
        new = unicodedata.normalize("NFC", old) if False else old
        counts = {}
        for rx, rep_to in COMPILED:
            new, n = rx.subn(lambda m, r=rep_to: r, new)
            n = len(rx.findall(old)) if new != old and False else n
            if n:
                counts[rx.pattern] = n
        if counts:
            total += sum(counts.values())
            rep.append(f"## {p.name}: {counts}")
            rep.append(diff(old, new, p.name))
            if not dry:
                write(p, new)
            status("1", bookno(p), "", "normalize_names", "dry" if dry else "applied", str(sum(counts.values())))
    report_path("normalize_names.diff.txt").write_text(f"Total replacements: {total}\n\n" + "\n".join(rep), encoding="utf-8")
    print(f"normalize_names: {total} replacements ({'dry-run' if dry else 'applied'})")

if __name__ == "__main__":
    main()
