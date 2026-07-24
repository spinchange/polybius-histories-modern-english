"""
Compare section/paragraph structure between the Greek source chapters and the
modern English translations.

For each chapter:
  - source section count  = number of blank-line-separated paragraph blocks in
                            the "## Greek" portion of source/book_XX/chapter_NN.md
  - translation paragraphs = number of blank-line-separated paragraph blocks under
                            the matching "Book N Chapter M" heading in the
                            Polybius_Histories_Book_XX_modern_English.md file

These should be equal when the translation keeps one paragraph per Polybius section.
"""

import re
import sys
import io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = Path(r"C:\Users\executor\AppData\Local\hermes\cache\documents\the_histories_translation")

HEAD_RE = re.compile(r'^#+\s*Book\s+(\d+)\s+Chapter\s+(\d+)\b', re.I)


def paragraphs(block: str):
    """Blank-line separated, non-empty blocks that are not markdown headings."""
    out = []
    for chunk in re.split(r'\n[ \t]*\n', block):
        s = chunk.strip()
        if not s:
            continue
        if s.startswith('#'):  # skip stray headings
            continue
        out.append(s)
    return out


def source_section_count(path: Path) -> int:
    text = path.read_text(encoding='utf-8')
    # Greek portion lies between "## Greek" and the next "## " heading.
    m = re.search(r'##\s*Greek\s*\n(.*?)(?:\n##\s|\Z)', text, re.S)
    if not m:
        return -1
    return len(paragraphs(m.group(1)))


def parse_translation(path: Path):
    """Return {chapter:int -> paragraph_count} for one modern English book file."""
    text = path.read_text(encoding='utf-8')
    lines = text.split('\n')
    chapters = {}
    cur_ch = None
    buf = []

    def flush():
        if cur_ch is not None:
            chapters[cur_ch] = len(paragraphs('\n'.join(buf)))

    for line in lines:
        m = HEAD_RE.match(line)
        if m:
            flush()
            cur_ch = int(m.group(2))
            buf = []
        else:
            buf.append(line)
    flush()
    return chapters


def main():
    total = 0
    matches = 0
    mismatches = []
    missing = []

    for book_dir in sorted((BASE / 'source').glob('book_*')):
        book = int(book_dir.name.split('_')[1])
        trans_path = BASE / f'Polybius_Histories_Book_{book:02d}_modern_English.md'
        if not trans_path.exists():
            missing.append(f'book {book}: no translation file')
            continue
        trans = parse_translation(trans_path)

        for ch_path in sorted(book_dir.glob('chapter_*.md')):
            ch_token = ch_path.stem.split('_', 1)[1]
            m_ch = re.match(r'(\d+)', ch_token)
            if not m_ch:
                continue
            ch = int(m_ch.group(1))
            # skip fragmentary sub-chapters like 11a/11b (letters = no clean 1:1 mapping)
            if not ch_token.isdigit():
                mismatches.append((book, ch_token, source_section_count(ch_path), 'FRAG'))
                continue
            src_n = source_section_count(ch_path)
            tr_n = trans.get(ch)
            total += 1
            if tr_n is None:
                mismatches.append((book, ch, src_n, 'MISSING'))
                continue
            if src_n == tr_n:
                matches += 1
            else:
                mismatches.append((book, ch, src_n, tr_n))

    print(f"Chapters compared : {total}")
    print(f"Exact structural matches : {matches}  ({100*matches/total:.1f}%)")
    print(f"Mismatches : {len(mismatches)}")
    if missing:
        print("\nMissing translation files:")
        for x in missing:
            print("  ", x)

    # Categorize the mismatches.
    frag = [m for m in mismatches if m[3] == 'FRAG']
    missing_ch = [m for m in mismatches if m[3] == 'MISSING']
    numeric = [m for m in mismatches if isinstance(m[3], int)]

    collapsed = [m for m in numeric if m[3] <= 2 and m[2] >= 4]      # sections crushed into 1-2 paras
    exploded = [m for m in numeric if (m[3] - m[2]) >= 4]             # many more paras than sections
    minor = [m for m in numeric if m not in collapsed and m not in exploded]

    print("\n=== Mismatch categories ===")
    print(f"  Fragment sub-chapters (e.g. 11a, 25k) - no 1:1 mapping : {len(frag)}")
    print(f"  Chapter missing from translation                       : {len(missing_ch)}")
    print(f"  COLLAPSED (>=4 sections crushed into <=2 paragraphs)    : {len(collapsed)}")
    print(f"  Exploded  (translation has >=4 more paras than sections): {len(exploded)}")
    print(f"  Minor +/-1..3 (mostly stray source breaks)             : {len(minor)}")

    if collapsed:
        print("\n  -- COLLAPSED (genuine structure loss) --")
        for book, ch, s, t in collapsed:
            print(f"     Book {book} Ch {ch}: {s} sections -> {t} paragraph(s)")
    if missing_ch:
        print("\n  -- MISSING chapters --")
        for book, ch, s, t in missing_ch:
            print(f"     Book {book} Ch {ch}")
    if exploded:
        print("\n  -- EXPLODED (likely fragment consolidation) --")
        for book, ch, s, t in exploded:
            print(f"     Book {book} Ch {ch}: {s} sections -> {t} paragraphs (+{t-s})")

    # Full detail to file
    report = BASE / 'structure_report.txt'
    with report.open('w', encoding='utf-8') as fh:
        fh.write("Book\tCh\tGreekBlocks\tTransParas\tDelta\n")
        for book, ch, s, t in mismatches:
            delta = (t - s) if isinstance(t, int) else ''
            fh.write(f"{book}\t{ch}\t{s}\t{t}\t{delta}\n")
    print(f"\nFull per-chapter detail written to: {report.name}")


if __name__ == '__main__':
    main()
