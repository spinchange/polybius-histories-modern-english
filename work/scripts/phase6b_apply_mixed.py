"""Phase 6b, MIXED chapters (convention (a), user decision 2026-11-01).

In a chapter whose paragraphs come from different witnesses, a *Quoted by ...* line stands
before each quoted paragraph and governs that paragraph only, unless it states a longer
scope ("this and the next N paragraphs"). Unmarked paragraphs in these chapters are
Constantinian excerpts (or, in 8.37, Wescher's siege codex). Evidence: work/phase6b/findings_*.md.
Idempotent, CRLF-preserving. Usage: python -I phase6b_apply_mixed.py <repo_root>
"""
import re, sys
from pathlib import Path

ROOT = Path(sys.argv[1])
A = "Athenaeus, Deipnosophistae"; ST = "Stephanus of Byzantium, Ethnica"; SU = "Suidas, Lexicon"
def q(src, n=0):
    scope = {0: "", 1: " (this and the next paragraph)", 2: " (this and the next two paragraphs)",
             3: " (this and the next three paragraphs)"}[n]
    return f"*Quoted by {src}{scope}.*"

# (book, chapter, paragraph prefix, line)
ITEMS = [
    (8, "22", "Yet this Cauarus the Gaul", q(A)),
    (8, "24", "When news of this reached Tarentum", q(SU)),
    (8, "37", "He counted the courses of stone", q(SU)),
    (8, "37", "None of the citizens realized", q(SU, 1)),
    (9, "9", "Atella is a city of the Opici", q(ST)),
    (9, "9", "When the Romans were besieging Tarentum, Bomilcar", q("Hero of Byzantium, Poliorcetica")),
    (9, "27", "Polybius says that both the river and the city", q(ST)),
    (9, "27", "Marcus, after giving guarantees of safety", q(SU)),
    (9, "45", "Polybius in the ninth book of his Histories", q(A)),
    (9, "45", "Arsinoe is a city of Libya", q(ST, 1)),
    (13, "5", "The prytaneis, already distrustful", q(f"{SU}, and Harpocration, Lexicon of the Ten Orators")),
    (13, "5", "But when he came before them", q(SU, 1)),
    (13, "9", "Labae, like Sabae", q(ST, 3)),
    (13, "9", "The Gerrhaeans asked the king", q(SU, 1)),
    (16, "39", "Polybius of Megalopolis gives witness", q("Josephus, Jewish Antiquities")),
    (16, "39", "But since the siege had been conducted", q(SU)),
    (16, "39", "And in the same book Polybius says", q("Josephus, Jewish Antiquities", 2)),
    (21, "6", "At Phocaea there was civil strife", q(SU)),
    (21, "6", "Then two Galli came out", q(SU)),
    (23, "12", "Polybius says that he rose and went on ahead", q(SU, 1)),
    (29, "14", "The first man to volunteer", q("Plutarch, Aemilius Paullus", 2)),
    (29, "14", "The Romans were holding their own stoutly", q(SU)),
    (32, "11", "Polybius says in Book 32 that after ruling", q(A)),
]

for book, ch, prefix, line in ITEMS:
    f = ROOT / f"Polybius_Histories_Book_{book:02d}_modern_English.md"
    raw = f.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    h = re.search(rf"^## Book {book} Chapter {re.escape(ch)}:", raw, re.M)
    if not h:
        print(f"{book}.{ch}: HEADING NOT FOUND"); continue
    nxt = re.search(r"^## ", raw[h.end():], re.M)
    end = h.end() + (nxt.start() if nxt else len(raw) - h.end())
    p = raw.find(nl + nl + prefix, h.start(), end)
    if p < 0:
        print(f"{book}.{ch}: PARAGRAPH NOT FOUND: {prefix}"); continue
    p += 2 * len(nl)
    before = raw[h.start():p].rstrip("\r\n").rsplit(nl, 1)[-1]
    if before.startswith("*Quoted by"):
        print(f"{book}.{ch}: already marked before '{prefix[:30]}'"); continue
    raw = raw[:p] + line + nl + nl + raw[p:]
    f.write_bytes(raw.encode("utf-8"))
    print(f"{book}.{ch}: {line}  <- {prefix[:40]}")
