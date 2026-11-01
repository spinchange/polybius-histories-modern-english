"""Heading report (read-only) -> work/reports/heading_report.csv + .txt
Per heading: format-exact?, has-title?, title-case violations, duplicate title in
book, Olympiad rubric in source vs translation (translation = chapter body).
"""
from __future__ import annotations
import csv, re
from collections import Counter, defaultdict
from common import *

SMALL = {"a","an","and","as","at","but","by","for","from","in","into","of","on","or","the","to","with","vs","over","upon","against","after","before","between","under","during","about","not","nor","is","are","its","his","her","their","whom","so","than"}
EXACT = re.compile(r"^## Book (\d+) Chapter (\d+[a-z]?): (\S.*\S|\S)$")
OLY = re.compile(r"olympiad", re.I)

def case_violations(title: str):
    bad = []
    words = title.split()
    for i, w in enumerate(words):
        core = re.sub(r"^[^\w]+|[^\w]+$", "", w)
        if not core or not core[0].isalpha():
            continue
        if i == 0 or i == len(words) - 1:
            if core[0].islower():
                bad.append(core)
        elif core.lower() not in SMALL and core[0].islower() and "-" not in core:
            bad.append(core)
    return bad

def source_has_olympiad(bk, ch):
    f = ROOT / "source" / f"book_{int(bk):02d}" / f"chapter_{int(re.match(r'\d+',ch).group()):02d}.md"
    if not f.exists():
        return ""
    return "yes" if OLY.search(f.read_text(encoding="utf-8")) else "no"

rows = []
titles = defaultdict(list)
for p in book_files():
    bn = bookno(p)
    lines = read(p).splitlines()
    heads = [(i, l) for i, l in enumerate(lines) if l.startswith("## ")]
    for k, (i, l) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        body = "\n".join(lines[i + 1:end])
        m = re.match(r"^## Book (\d+) Chapter (\d+[a-z]?)(?::\s*(.*))?\s*$", l)
        if not m:
            rows.append((bn, "?", "", "unparsed-heading", l, "", ""))
            continue
        b, c, t = m.group(1), m.group(2), (m.group(3) or "").strip()
        issues = []
        if not EXACT.match(l):
            issues.append("format")
        if int(b) != int(bn):
            issues.append("book-mismatch")
        if not t:
            issues.append("no-title")
        else:
            cv = case_violations(t)
            if cv:
                issues.append("case:" + "/".join(cv))
            titles[(bn, t.lower())].append(c)
            if len(t.split()) > 12:
                issues.append("long-title")
        s_oly = source_has_olympiad(b, c)
        t_oly = "yes" if OLY.search(body) else "no"
        if s_oly == "yes" and t_oly == "no":
            issues.append("olympiad-rubric-missing")
        rows.append((bn, c, t, ";".join(issues), l, s_oly, t_oly))
dups = {k: v for k, v in titles.items() if len(v) > 1}
dupflag = {(k[0], c) for k, v in dups.items() for c in v}
out = []
for r in rows:
    iss = r[3]
    if (r[0], r[1]) in dupflag:
        iss = (iss + ";" if iss else "") + "duplicate-title"
    out.append((*r[:3], iss, *r[4:]))
with open(report_path("heading_report.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["book", "chapter", "title", "issues", "heading", "src_olympiad", "tr_olympiad"]); w.writerows(out)
cnt = Counter()
for r in out:
    for x in filter(None, r[3].split(";")):
        cnt[x.split(":")[0]] += 1
report_path("heading_report.txt").write_text(
    f"Headings: {len(out)}\nIssue counts: {dict(cnt)}\n\nDuplicate titles within a book:\n" +
    "\n".join(f"  Book {k[0]}: '{k[1]}' -> ch {', '.join(v)}" for k, v in sorted(dups.items())) +
    "\n\nNo-title headings (book: chapters):\n" +
    "\n".join(f"  Book {b}: {', '.join(r[1] for r in out if r[0]==b and 'no-title' in r[3])}" for b in sorted({r[0] for r in out if 'no-title' in r[3]})), encoding="utf-8")
status("1", "", "", "heading_report", "report", f"{len(out)} headings; {dict(cnt)}")
print(len(out), dict(cnt))
