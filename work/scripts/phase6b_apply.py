"""Phase 6b: insert whole-chapter testimonia lines (high-confidence QUOTED verdicts only).

Evidence for each is in work/phase6b/findings_<batch>.md. Idempotent: skips a chapter
whose first line under the heading is already a *Quoted by ...* line. CRLF-preserving.
Usage: python -I phase6b_apply.py <repo_root>
"""
import re, sys
from pathlib import Path

ROOT = Path(sys.argv[1])
A = "*Quoted by Athenaeus, Deipnosophistae.*"
ST = "*Quoted by Stephanus of Byzantium, Ethnica.*"
SU = "*Quoted by Suidas, Lexicon.*"
SR = "*Quoted by Strabo, Geography.*"
LINES = [
    (12, "1", ST), (14, "11", A), (19, "2", "*Quoted by Livy, History of Rome.*"),
    (21, "12", SU), (26, "1", A), (26, "1a", A), (29, "13", A), (29, "16", SU),
    (29, "18", "*Quoted by Plutarch, Aemilius Paullus.*"), (30, "15", SR), (30, "22", A),
    (35, "5", SU), (37, "1", ST), (39, "2", SR),
]

for book, ch, line in LINES:
    f = ROOT / f"Polybius_Histories_Book_{book:02d}_modern_English.md"
    raw = f.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    pat = re.compile(rf"^(## Book {book} Chapter {re.escape(ch)}:[^\r\n]*)(\r?\n)+", re.M)
    m = pat.search(raw)
    if not m:
        print(f"{book}.{ch}: HEADING NOT FOUND"); continue
    after = raw[m.end():m.end() + 200]
    if after.startswith("*Quoted by"):
        print(f"{book}.{ch}: already has {after.splitlines()[0]}"); continue
    new = raw[:m.start()] + m.group(1) + nl + nl + line + nl + nl + raw[m.end():]
    f.write_bytes(new.encode("utf-8"))
    print(f"{book}.{ch}: added {line}")
