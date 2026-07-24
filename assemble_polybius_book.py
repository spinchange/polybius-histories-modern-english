from pathlib import Path
import json
import re
import sys

BASE = Path(r"C:\Users\executor\AppData\Local\hermes\cache\documents\the_histories_translation")
TRANSLATIONS = BASE / "translations"


def chapter_sort_key(label: str):
    m = re.fullmatch(r"(\d+)([a-z]?)", label)
    if not m:
        return (10**9, label)
    return (int(m.group(1)), m.group(2))


def manifest_labels_for_book(book: int, last_chapter: int) -> list[str]:
    manifest_path = BASE / "source" / f"book_{book:02d}" / "manifest.json"
    if not manifest_path.exists():
        return [str(n) for n in range(1, last_chapter + 1)]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    labels = []
    for row in manifest.get("chapters", []):
        label = str(row["chapter"])
        m = re.fullmatch(r"(\d+)([a-z]?)", label)
        if not m:
            continue
        if int(m.group(1)) <= last_chapter:
            labels.append(label)

    return labels or [str(n) for n in range(1, last_chapter + 1)]


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python assemble_polybius_book.py <book_number> <last_chapter>")
    book = int(sys.argv[1])
    last_chapter = int(sys.argv[2])
    expected_labels = manifest_labels_for_book(book, last_chapter)
    manifest_path = BASE / "source" / f"book_{book:02d}" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    pat = re.compile(rf"(?m)^# Book {book} Chapter (\d+[a-z]?): .*$")
    chapter_map = {}
    source_map = {}
    for path in sorted(TRANSLATIONS.glob(f"book_{book:02d}*.translation.md")):
        text = path.read_text(encoding="utf-8")
        matches = list(pat.finditer(text))
        for i, m in enumerate(matches):
            chap = m.group(1)
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            segment = text[start:end].strip()
            if chap in chapter_map:
                raise SystemExit(f"duplicate chapter {chap} in {path} and {source_map[chap]}")
            chapter_map[chap] = segment
            source_map[chap] = str(path)
    missing = [label for label in expected_labels if label not in chapter_map]
    if missing:
        raise SystemExit(f"missing chapters: {missing}")
    ordered_labels = sorted(expected_labels, key=chapter_sort_key)
    out = BASE / f"Polybius_Histories_Book_{book:02d}_modern_English.md"
    if not ordered_labels:
        note = manifest.get("book_note_translation") or "No chaptered Greek text survives for this book in the Perseus witness."
        out.write_text(note.rstrip() + "\n", encoding="utf-8")
        print(json.dumps({
            "output": str(out),
            "book": book,
            "chapter_count": 0,
            "missing": [],
            "size_bytes": out.stat().st_size,
            "first_heading": None,
            "last_heading": None,
        }, ensure_ascii=False, indent=2))
        return 0
    merged = "\n\n".join(chapter_map[label] for label in ordered_labels) + "\n"
    out.write_text(merged, encoding="utf-8")
    print(json.dumps({
        "output": str(out),
        "book": book,
        "chapter_count": len(ordered_labels),
        "missing": missing,
        "size_bytes": out.stat().st_size,
        "first_heading": chapter_map[ordered_labels[0]].splitlines()[0],
        "last_heading": chapter_map[ordered_labels[-1]].splitlines()[0],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
