import html
import json
import re
import sys
import time
from pathlib import Path

import requests

OUT_DIR = Path(r"C:\Users\executor\AppData\Local\hermes\cache\documents\the_histories_translation")
SOURCE_DIR = OUT_DIR / "source"
GREEK_DOC = "1999.01.0233"
ENGLISH_DOC = "1999.01.0234"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HermesAgent/1.0; +https://hermes-agent.nousresearch.com)"}


def fetch(url: str, attempts: int = 8, timeout: int = 90) -> str:
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
            time.sleep(min(2 * attempt, 15))
    raise last_err


def fetch_any(urls: list[str], attempts_per_url: int = 6, timeout: int = 90) -> str:
    last_err = None
    for url in urls:
        try:
            return fetch(url, attempts=attempts_per_url, timeout=timeout)
        except Exception as e:
            last_err = e
            time.sleep(2)
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
    return normalize_text(page_html[start:end])


def chapter_title_from_english(html_text: str, book: int, chapter_label: str) -> str:
    m = re.search(r"<title>\s*Polybius,\s*Histories,\s*book\s+%d,\s*(.*?)\s*</title>" % book, html_text, flags=re.S | re.I)
    if m:
        title = re.sub(r"<[^>]+>", "", m.group(1))
        title = re.sub(r"\s+", " ", html.unescape(title)).strip()
        return title
    return f"Chapter {chapter_label}"


def chapter_sort_key(label: str):
    m = re.fullmatch(r"(\d+)([a-z]?)", label)
    if not m:
        return (10**9, label)
    return (int(m.group(1)), m.group(2))


def file_slug(label: str) -> str:
    return label.replace('/', '_')


def discover_chapters(book: int, doc: str) -> list[str]:
    urls = [
        f"https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:{doc}",
        f"https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:{doc}:book={book}",
    ]
    pat = re.compile(rf'\?doc=Perseus%3Atext%3A{re.escape(doc)}%3Abook%3D{book}%3Achapter%3D([^%\"]+)')
    last_err = None
    for url in urls:
        try:
            text = fetch(url, timeout=45)
            labels = sorted({m for m in pat.findall(text) if re.fullmatch(r"\d+[a-z]?", m)}, key=chapter_sort_key)
            if labels:
                return labels
        except Exception as e:
            last_err = e
            continue
    if last_err:
        raise RuntimeError(f"No chapter labels discovered for book {book}, doc {doc}; last error: {last_err}")
    return []


def write_manifest(book: int, rows: list[dict], failures: list[dict] | None = None) -> None:
    book_dir = SOURCE_DIR / f"book_{book:02d}"
    manifest = {
        "book": book,
        "chapter_count": len(rows),
        "chapters": rows,
        "failures": failures or [],
    }
    (book_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit("usage: python extract_polybius_book_incremental.py <book_number>")
    book = int(sys.argv[1])
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    book_dir = SOURCE_DIR / f"book_{book:02d}"
    book_dir.mkdir(parents=True, exist_ok=True)

    greek_labels = discover_chapters(book, GREEK_DOC)
    english_labels = set(discover_chapters(book, ENGLISH_DOC))
    labels = list(greek_labels)

    rows = []
    failures = []
    for label in labels:
        chapter_path = book_dir / f"chapter_{file_slug(label):0>2}.md"
        if chapter_path.exists():
            text = chapter_path.read_text(encoding='utf-8', errors='replace')
            m = re.match(r'^# Book (\d+) Chapter ([^:]+): (.*)$', text.splitlines()[0])
            title = m.group(3) if m else f"Chapter {label}"
            rows.append({
                "chapter": label,
                "title": title,
                "file": str(chapter_path),
                "greek_chars": len(text),
                "english_chars": 0,
            })
            print(f"SKIP chapter {label}")
            continue

        greek_urls = [
            f"https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:{GREEK_DOC}:book={book}:chapter={label}",
            f"https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A{GREEK_DOC}%3Abook%3D{book}%3Achapter%3D{label}",
        ]
        english_urls = [
            f"https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:{ENGLISH_DOC}:book={book}:chapter={label}",
            f"https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A{ENGLISH_DOC}%3Abook%3D{book}%3Achapter%3D{label}",
        ]
        try:
            greek_html = fetch_any(greek_urls)
            greek = extract_main_text(greek_html, "greek")

            english_html = None
            english = ""
            if label in english_labels:
                english_html = fetch_any(english_urls)
                english = extract_main_text(english_html, "en")

            title = chapter_title_from_english(english_html, book, label) if english_html else f"Chapter {label}"
            content = [
                f"# Book {book} Chapter {label}: {title}",
                "",
                "## Greek",
                "",
                greek,
            ]
            if english_html:
                content.extend([
                    "",
                    "## English Reference (Perseus / 1889)",
                    "",
                    english,
                ])
            else:
                content.extend([
                    "",
                    "## English Reference (Perseus / 1889)",
                    "",
                    "[No matching English chapter is available in the Perseus witness for this chapter.]",
                ])
            content.append("")
            chapter_path.write_text("\n".join(content), encoding="utf-8")
            rows.append({
                "chapter": label,
                "title": title,
                "file": str(chapter_path),
                "greek_chars": len(greek),
                "english_chars": len(english),
            })
            write_manifest(book, rows, failures)
            print(f"WROTE chapter {label}")
            time.sleep(1)
        except Exception as e:
            failures.append({"chapter": label, "error": f"{type(e).__name__}: {e}"})
            write_manifest(book, rows, failures)
            print(f"FAIL chapter {label}: {type(e).__name__}: {e}")
            time.sleep(3)
            continue

    rows.sort(key=lambda r: chapter_sort_key(r['chapter']))
    write_manifest(book, rows, failures)
    summary = {"book": book, "chapter_count": len(rows), "first": rows[0]['chapter'], "last": rows[-1]['chapter'], "failure_count": len(failures)} if rows else {"book": book, "chapter_count": 0, "failure_count": len(failures)}
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
