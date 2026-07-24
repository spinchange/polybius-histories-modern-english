import concurrent.futures as cf
import html
import json
import re
import sys
import time
from pathlib import Path

import requests

OUT_DIR = Path(r"C:\Users\executor\AppData\Local\hermes\cache\documents\the_histories_translation")
SOURCE_DIR = OUT_DIR / "source"
CHUNK_DIR = OUT_DIR / "chunks_3_5"
DEFAULT_BOOKS = [3, 4, 5]
GREEK_DOC = "1999.01.0233"
ENGLISH_DOC = "1999.01.0234"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HermesAgent/1.0; +https://hermes-agent.nousresearch.com)",
}


def fetch(url: str, attempts: int = 5, timeout: int = 60) -> str:
    last_err = None
    for attempt in range(1, attempts + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_err = e
            if attempt == attempts:
                raise
            time.sleep(min(2 ** attempt, 10))
    raise last_err


def normalize_text(raw: str) -> str:
    raw = re.sub(r"<hr\s*/?>", "\n\n", raw)
    raw = re.sub(r"<p\s*/?>", "\n\n", raw)
    raw = re.sub(r"<br\s*/?>", "\n", raw)
    raw = re.sub(r"</div>|</p>|</h\d>", "\n", raw)
    text = re.sub(r"<[^>]+>", "", raw)
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+([,.;·!?])", r"\1", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def extract_main_text(page_html: str, lang_class: str) -> str:
    start = page_html.find(f'<div class="text_container {lang_class}"')
    if start == -1:
        raise ValueError(f"text_container {lang_class} not found")
    end = page_html.find('<div id="text_footer">', start)
    if end == -1:
        raise ValueError("text_footer not found")
    chunk = page_html[start:end]
    return normalize_text(chunk)


def chapter_title_from_english(html_text: str, book: int, chapter_label: str) -> str:
    m = re.search(r"<title>\s*Polybius,\s*Histories,\s*book\s+%d,\s*(.*?)\s*</title>" % book, html_text, flags=re.S | re.I)
    if m:
        return re.sub(r"\s+", " ", html.unescape(m.group(1))).strip()
    return f"Chapter {chapter_label}"


def chapter_sort_key(label: str):
    m = re.fullmatch(r"(\d+)([a-z]?)", label)
    if not m:
        return (10**9, label)
    n = int(m.group(1))
    suffix = m.group(2)
    return (n, suffix)


def discover_chapters(book: int, doc: str) -> list[str]:
    url = f"https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:{doc}:book={book}"
    text = fetch(url)
    pat = re.compile(rf'\?doc=Perseus%3Atext%3A{re.escape(doc)}%3Abook%3D{book}%3Achapter%3D([^%\"]+)')
    labels = sorted({m for m in pat.findall(text) if re.fullmatch(r"\d+[a-z]?", m)}, key=chapter_sort_key)
    if not labels:
        raise RuntimeError(f"No chapter labels discovered for book {book}, doc {doc}")
    return labels


def file_slug(label: str) -> str:
    return label.replace('/', '_')


def fetch_chapter(book: int, chapter_label: str) -> dict:
    greek_url = f"https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:{GREEK_DOC}:book={book}:chapter={chapter_label}"
    english_url = f"https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:{ENGLISH_DOC}:book={book}:chapter={chapter_label}"
    greek_html = fetch(greek_url)
    english_html = fetch(english_url)
    greek = extract_main_text(greek_html, "greek")
    english = extract_main_text(english_html, "en")
    title = chapter_title_from_english(english_html, book, chapter_label)
    return {
        "book": book,
        "chapter": chapter_label,
        "title": title,
        "greek": greek,
        "english_reference": english,
        "greek_chars": len(greek),
        "english_chars": len(english),
    }


def write_book_files(chapters: list[dict], book: int) -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    book_dir = SOURCE_DIR / f"book_{book:02d}"
    book_dir.mkdir(parents=True, exist_ok=True)
    for ch in chapters:
        path = book_dir / f"chapter_{file_slug(ch['chapter']):0>2}.md"
        content = [
            f"# Book {ch['book']} Chapter {ch['chapter']}: {ch['title']}",
            "",
            "## Greek",
            "",
            ch["greek"],
            "",
            "## English Reference (Perseus / 1889)",
            "",
            ch["english_reference"],
            "",
        ]
        path.write_text("\n".join(content), encoding="utf-8")

    manifest = {
        "book": book,
        "chapter_count": len(chapters),
        "chapters": [
            {
                "chapter": ch["chapter"],
                "title": ch["title"],
                "file": str(book_dir / f"chapter_{file_slug(ch['chapter']):0>2}.md"),
                "greek_chars": ch["greek_chars"],
                "english_chars": ch["english_chars"],
            }
            for ch in chapters
        ],
    }
    (book_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def make_chunks(chapters: list[dict], book: int, chunk_size: int = 120000) -> list[dict]:
    chunks = []
    current = []
    current_chars = 0
    for ch in chapters:
        ch_chars = ch["greek_chars"] + ch["english_chars"]
        if current and current_chars + ch_chars > chunk_size:
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(ch)
        current_chars += ch_chars
    if current:
        chunks.append(current)

    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    for i, chunk in enumerate(chunks, start=1):
        start_ch = chunk[0]["chapter"]
        end_ch = chunk[-1]["chapter"]
        path = CHUNK_DIR / f"book_{book:02d}_chunk_{i:02d}_chapters_{file_slug(start_ch)}_{file_slug(end_ch)}.md"
        parts = [
            f"# Polybius Histories — Book {book} Chapters {start_ch}-{end_ch}",
            "",
            "Use the Greek as the source text. Use the older English only as a reference crib, not as final wording.",
            "",
        ]
        for ch in chunk:
            parts += [
                f"## Book {book} Chapter {ch['chapter']}: {ch['title']}",
                "",
                "### Greek",
                "",
                ch["greek"],
                "",
                "### English Reference (1889)",
                "",
                ch["english_reference"],
                "",
            ]
        path.write_text("\n".join(parts), encoding="utf-8")
        out.append({
            "book": book,
            "chunk_index": i,
            "chapter_start": start_ch,
            "chapter_end": end_ch,
            "file": str(path),
            "estimated_chars": sum(ch["greek_chars"] + ch["english_chars"] for ch in chunk),
            "chapter_count": len(chunk),
        })
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_chunks = []
    summary = {"books": {}}
    books = [int(arg) for arg in sys.argv[1:]] if len(sys.argv) > 1 else DEFAULT_BOOKS
    for book in books:
        greek_labels = discover_chapters(book, GREEK_DOC)
        english_labels = discover_chapters(book, ENGLISH_DOC)
        chapter_labels = [label for label in greek_labels if label in set(english_labels)]
        futures = []
        chapters = []
        failed = []
        with cf.ThreadPoolExecutor(max_workers=2) as ex:
            for label in chapter_labels:
                futures.append((label, ex.submit(fetch_chapter, book, label)))
            for label, fut in futures:
                try:
                    chapters.append(fut.result())
                except Exception as e:
                    failed.append((label, str(e)))
        if failed:
            print(f"book {book}: retrying {len(failed)} failed chapters serially")
            for label, _err in failed:
                chapters.append(fetch_chapter(book, label))
        chapters.sort(key=lambda x: chapter_sort_key(x['chapter']))
        write_book_files(chapters, book)
        chunks = make_chunks(chapters, book, chunk_size=120000)
        all_chunks.extend(chunks)
        summary["books"][str(book)] = {
            "chapter_labels": chapter_labels,
            "chapter_count": len(chapters),
            "greek_chars": sum(ch["greek_chars"] for ch in chapters),
            "english_chars": sum(ch["english_chars"] for ch in chapters),
            "chunks": chunks,
        }
        print(f"book {book}: {len(chapters)} chapters, {len(chunks)} chunks")
    summary["all_chunks"] = all_chunks
    (OUT_DIR / "summary_books_3_5.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
