"""Seam report for Phase 6 (read-only).  Writes work/reports/seam_report.txt (+ .csv).
Categories:
  bracket-repeat   paragraph starts with '[A-Z' (bracketed repeat of previous chapter's tail)
  unterminated     paragraph without terminal punctuation followed by a heading / EOF
  stray-marker     markers like [7;8], U+FFFD, '<' tags, leftover roman-numeral rubrics
  heading-spacing  heading not preceded by a blank line (or not followed by one)
  known            WORK_PLAN known one-offs
"""
from __future__ import annotations
import csv, re
from common import *

TERMINAL = re.compile(r'([.!?:—]|\.\.\.|\[\.\.\.\])[\'"”’)\]*_]*$|["”]$')
KNOWN = {  # file number -> list of (line, note)
    "03": [395, 445, 479, 1043, 1579], "04": [1435], "06": [449], "16": [207], "22": [111], "35": [121],
}
rows = []
for p in book_files():
    bn = bookno(p)
    lines = read(p).splitlines()
    for i, l in enumerate(lines):
        ln = i + 1
        if l.startswith("#"):
            if i and lines[i - 1].strip() != "":
                rows.append((bn, ln, "heading-spacing", "no blank line before heading", l[:80]))
            if i + 1 < len(lines) and lines[i + 1].strip() != "" and not l.startswith("# "):
                rows.append((bn, ln, "heading-spacing", "no blank line after heading", l[:80]))
            # unterminated paragraph immediately before heading
            j = i - 1
            while j >= 0 and lines[j].strip() == "":
                j -= 1
            if j >= 0 and not lines[j].startswith(("#", ">", "*", "---")) and not TERMINAL.search(lines[j].rstrip()):
                rows.append((bn, j + 1, "unterminated", "paragraph ends without terminal punctuation before heading", lines[j][-80:]))
            continue
        if re.match(r"^\[[A-Z]", l):
            rows.append((bn, ln, "bracket-repeat", "starts with bracketed text", l[:90]))
        for m in re.finditer(r"\[\d+;\d+\]|�|</?[a-z]+>|^\s*[IVXL]+\.\s+On\b", l):
            rows.append((bn, ln, "stray-marker", repr(m.group(0)), l[:90]))
    # EOF unterminated
    k = len(lines) - 1
    while k >= 0 and lines[k].strip() == "":
        k -= 1
    if k >= 0 and not lines[k].startswith(("#", ">", "*", "---")) and not TERMINAL.search(lines[k].rstrip()):
        rows.append((bn, k + 1, "unterminated", "last paragraph of book unterminated", lines[k][-80:]))
    for kl in KNOWN.get(bn, []):
        # line numbers predate cleanup: record context (+-0) for the human
        if kl <= len(lines):
            rows.append((bn, kl, "known", "WORK_PLAN one-off (line numbers pre-cleanup; verify)", lines[kl - 1][:90]))
rows.sort(key=lambda r: (r[0], r[1]))
with open(report_path("seam_report.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["book", "line", "category", "detail", "context"]); w.writerows(rows)
from collections import Counter
c = Counter(r[2] for r in rows)
report_path("seam_report.txt").write_text(
    "Seam report\n" + "\n".join(f"  {k}: {v}" for k, v in sorted(c.items())) + "\n\n" +
    "\n".join(f"B{b} L{l} [{cat}] {d} | {ctx}" for b, l, cat, d, ctx in rows), encoding="utf-8")
status("1", "", "", "seam_report", "report", str(dict(c)))
print("seam_report:", dict(c))
