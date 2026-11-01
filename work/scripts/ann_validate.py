"""Validate every annotation file (ANNOTATIONS_PLAN Phase A1). Reports only.

    python work/scripts/ann_validate.py            # all layers
    python work/scripts/ann_validate.py FILE...    # specific files

Exit 1 if any annotation has errors. Report: work/reports/ann_validate.txt
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from ann_common import check, load_all, parse
from common import report_path


def main(argv: list[str]) -> int:
    anns = [check(parse(Path(p).resolve())) for p in argv] if argv else load_all()
    lines, counts = [], Counter()
    for a in anns:
        counts[a.status] += 1
        if a.errors:
            counts["ERROR"] += 1
        if not (a.errors or a.warnings):
            continue
        lines.append(f"{a.rel}  [{a.status}]")
        lines += [f"  ERROR {e}" for e in a.errors]
        lines += [f"  warn  {w}" for w in a.warnings]
    summary = f"{len(anns)} annotations: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    report_path("ann_validate.txt").write_text(summary + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print(summary)
    for l in lines:
        print(l)
    return 1 if counts["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
