"""Emit dist/annotations/<layer>.json from verified annotations (Phase A1).

Only status: verified AND error-free annotations are emitted; everything else
is silently excluded (run ann_validate.py to see why). Output shape is
deliberately UX-neutral (margin toggles vs endnotes undecided):

  {"layer": "readers",
   "annotations": [{id, anchors:[{book, from, to}], annotator, work, date,
                    tags, source_pub, pd_basis, quote, note}, ...],
   "by_chapter": {"6.3": [id, ...], ...}}   # every chapter a range touches
"""
from __future__ import annotations

import json
import sys

from ann_common import LAYERS, ROOT, chapter_key, chapters, load_all

OUT = ROOT / "dist" / "annotations"


def expand(book: int, start: str, end: str) -> list[str]:
    lo, hi = chapter_key(start), chapter_key(end)
    return [f"{book}.{c}" for c in sorted(chapters()[book], key=chapter_key)
            if lo <= chapter_key(c) <= hi]


def main() -> int:
    anns = [a for a in load_all() if a.ok and a.status == "verified"]
    OUT.mkdir(parents=True, exist_ok=True)
    for layer in LAYERS:
        items = sorted((a for a in anns if a.meta["layer"] == layer),
                       key=lambda a: (a.anchors[0][0], chapter_key(a.anchors[0][1]), a.meta["id"]))
        by_ch: dict[str, list[str]] = {}
        recs = []
        for a in items:
            m = a.meta
            recs.append({
                "id": m["id"],
                "anchors": [{"book": b, "from": s, "to": e} for b, s, e in a.anchors],
                "annotator": m["annotator"], "work": m["work"], "date": m["date"],
                "tags": m["tags"] if isinstance(m["tags"], list) else [m["tags"]],
                "source_pub": m.get("source_pub"), "pd_basis": m["pd_basis"],
                "quote": a.quote, "note": a.note,
            })
            for b, s, e in a.anchors:
                for key in expand(b, s, e):
                    by_ch.setdefault(key, []).append(m["id"])
        by_ch = dict(sorted(by_ch.items(), key=lambda kv: (int(kv[0].split(".")[0]), chapter_key(kv[0].split(".")[1]))))
        (OUT / f"{layer}.json").write_text(
            json.dumps({"layer": layer, "annotations": recs, "by_chapter": by_ch},
                       ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{layer}: {len(recs)} verified -> dist/annotations/{layer}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
