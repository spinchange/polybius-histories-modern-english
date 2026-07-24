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
CHUNK_DIR = OUT_DIR / "chunks"

BOOKS = {
    1: 88,
    2: 71,
}

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


def chapter_title_from_english(html_text: str, book: int, chapter: int) -> str:
    m = re.search(r"<title>\s*Polybius,\s*Histories,\s*book\s+%d,\s*(.*?)\s*</title>" % book, html_text, flags=re.S | re.I)
    if m:
        title = re.sub(r"\s+", " ", html.unescape(m.group(1))).strip()
        return title
    return f"Chapter {chapter}"


def fetch_chapter(book: int, chapter: int) -> dict:
    greek_url = f"https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:{GREEK_DOC}:book={book}:chapter={chapter}"
    english_url = f"https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:{ENGLISH_DOC}:book={book}:chapter={chapter}"
    greek_html = fetch(greek_url)
    english_html = fetch(english_url)
    greek = extract_main_text(greek_html, "greek")
    english = extract_main_text(english_html, "en")
    title = chapter_title_from_english(english_html, book, chapter)
    return {
        "book": book,
        "chapter": chapter,
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
        path = book_dir / f"chapter_{ch['chapter']:02d}.md"
        content = []
        content.append(f"# Book {ch['book']} Chapter {ch['chapter']}: {ch['title']}")
        content.append("")
        content.append("## Greek")
        content.append("")
        content.append(ch["greek"])
        content.append("")
        content.append("## English Reference (Perseus / 1889)")
        content.append("")
        content.append(ch["english_reference"])
        content.append("")
        path.write_text("\n".join(content), encoding="utf-8")

    manifest = {
        "book": book,
        "chapter_count": len(chapters),
        "chapters": [
            {
                "chapter": ch["chapter"],
                "title": ch["title"],
                "file": str((book_dir / f"chapter_{ch['chapter']:02d}.md")),
                "greek_chars": ch["greek_chars"],
                "english_chars": ch["english_chars"],
            }
            for ch in chapters
        ],
    }
    (book_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def make_chunks(chapters: list[dict], book: int, chunk_size: int) -> list[dict]:
    chunks = []
    current = []
    current_chars = 0
    for ch in chapters:
        # count both Greek and reference English because both go into the chunk file
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
        path = CHUNK_DIR / f"book_{book:02d}_chunk_{i:02d}_chapters_{start_ch:02d}_{end_ch:02d}.md"
        parts = [f"# Polybius Histories — Book {book} Chapters {start_ch}-{end_ch}", "", "Use the Greek as the source text. Use the older English only as a reference crib, not as final wording.", ""]
        for ch in chunk:
            parts.append(f"## Book {book} Chapter {ch['chapter']}: {ch['title']}")
            parts.append("")
            parts.append("### Greek")
            parts.append("")
            parts.append(ch["greek"])
            parts.append("")
            parts.append("### English Reference (1889)")
            parts.append("")
            parts.append(ch["english_reference"])
            parts.append("")
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
    for book, max_ch in BOOKS.items():
        futures = []
        chapters = []
        with cf.ThreadPoolExecutor(max_workers=6) as ex:
            for ch in range(1, max_ch + 1):
                futures.append(ex.submit(fetch_chapter, book, ch))
            for fut in cf.as_completed(futures):
                chapters.append(fut.result())
        chapters.sort(key=lambda x: x["chapter"])
        write_book_files(chapters, book)
        chunks = make_chunks(chapters, book, chunk_size=120000)
        all_chunks.extend(chunks)
        summary["books"][str(book)] = {
            "chapter_count": len(chapters),
            "greek_chars": sum(ch["greek_chars"] for ch in chapters),
            "english_chars": sum(ch["english_chars"] for ch in chapters),
            "chunks": chunks,
        }
        print(f"book {book}: {len(chapters)} chapters, {len(chunks)} chunks")
    summary["all_chunks"] = all_chunks
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
