"""Build a standalone single-file HTML edition of the translation.

Reuses the parsing and markup helpers from build_epub.py, so the HTML
edition always reflects the same book files as the EPUB. Output:

    dist/polybius-the-histories-modern-english.html

The page is self-contained (embedded CSS, no external assets), works in
light and dark color schemes, and carries print styles so the same file
renders cleanly to PDF (each book starts on a new page; the chapter
lists in the table of contents collapse to book links only).
"""

from __future__ import annotations

import html

import build_epub as eb

HTML_OUT = eb.DIST / "polybius-the-histories-modern-english.html"

CSS = """
:root {
  --bg: #faf6ec;
  --ink: #2b2117;
  --accent: #5b3b2b;
  --rule: #d7bd82;
  --muted: #7a6a55;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1d1813;
    --ink: #e8ddc8;
    --accent: #d7bd82;
    --rule: #5b4a33;
    --muted: #a3927a;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.6;
}
header#titlepage {
  text-align: center;
  padding: 5rem 1rem 3rem;
  border-bottom: 2px solid var(--rule);
}
header#titlepage h1 {
  font-size: 2.8rem;
  letter-spacing: 0.35em;
  text-indent: 0.35em;
  margin: 0 0 0.5rem;
  color: var(--accent);
}
header#titlepage .subtitle { font-size: 1.6rem; margin: 0 0 1rem; }
header#titlepage .edition { color: var(--muted); margin: 0; }
main, section#editorial-note, nav#toc {
  max-width: 44rem;
  margin: 0 auto;
  padding: 0 1.25rem;
}
h2 {
  font-size: 1.9rem;
  color: var(--accent);
  border-bottom: 1px solid var(--rule);
  padding-bottom: 0.3rem;
  margin: 3.5rem 0 1.5rem;
}
h3 { font-size: 1.15rem; margin: 2.2rem 0 0.8rem; }
h3 .label {
  color: var(--accent);
  font-variant: small-caps;
  letter-spacing: 0.05em;
  margin-right: 0.4em;
}
p { margin: 0 0 1em; }
p.bridgehead {
  font-variant: small-caps;
  letter-spacing: 0.08em;
  color: var(--muted);
  margin-top: 1.6em;
}
nav#toc ol { list-style: none; padding-left: 0; }
nav#toc > ol > li { margin: 0.35rem 0; }
nav#toc details { margin-left: 1rem; }
nav#toc summary { cursor: pointer; color: var(--muted); font-size: 0.9rem; }
nav#toc details ol { padding-left: 1rem; font-size: 0.95rem; }
nav#toc a { color: inherit; text-decoration: none; border-bottom: 1px dotted var(--rule); }
nav#toc a:hover { color: var(--accent); }
section#editorial-note {
  font-size: 0.95rem;
  color: var(--muted);
  border-bottom: 1px solid var(--rule);
  padding-bottom: 1.5rem;
}
footer {
  text-align: center;
  color: var(--muted);
  font-size: 0.85rem;
  padding: 3rem 1rem;
  border-top: 2px solid var(--rule);
  margin-top: 4rem;
}
.book-note { font-style: italic; color: var(--muted); }
@media print {
  :root {
    --bg: #ffffff;
    --ink: #000000;
    --accent: #000000;
    --rule: #888888;
    --muted: #444444;
  }
  body { font-size: 11pt; }
  header#titlepage { padding: 38vh 0 0; border: none; page-break-after: always; }
  section.book { page-break-before: always; }
  nav#toc details { display: none; }
  h2 { margin-top: 0; }
  a { color: inherit; text-decoration: none; }
}
"""


def editorial_note_html() -> str:
    md = (eb.BASE / "EDITORIAL_NOTE.md").read_text(encoding="utf-8")
    parts = ['<section id="editorial-note">', "  <h2>Editorial Note</h2>"]
    in_list = False
    for raw_line in md.splitlines():
        line = raw_line.strip()
        if not line:
            if in_list:
                parts.append("  </ul>")
                in_list = False
            continue
        if line.startswith("#"):
            continue
        if line.startswith("- "):
            if not in_list:
                parts.append("  <ul>")
                in_list = True
            parts.append(f"    <li>{eb.inline_note_markup(line[2:])}</li>")
        else:
            if in_list:
                parts.append("  </ul>")
                in_list = False
            parts.append(f"  <p>{eb.inline_note_markup(line)}</p>")
    if in_list:
        parts.append("  </ul>")
    parts.append("</section>")
    return "\n".join(parts)


def chapter_heading(book: eb.Book, chapter: eb.Chapter) -> str:
    label = f'<span class="label">Chapter {html.escape(chapter.label)}</span>'
    if chapter.title == f"Chapter {chapter.label}":
        return label
    return f"{label} {html.escape(chapter.title)}"


def toc_html(books: list[eb.Book]) -> str:
    parts = ['<nav id="toc">', "  <h2>Contents</h2>", "  <ol>"]
    for book in books:
        parts.append(f'    <li><a href="#{eb.book_id(book.number)}">{book.title}</a>')
        if book.chapters:
            parts.append("      <details><summary>Chapters</summary><ol>")
            for chapter in book.chapters:
                nav_label = f"Chapter {chapter.label}"
                if chapter.title != nav_label:
                    nav_label += f": {chapter.title}"
                parts.append(
                    f'        <li><a href="#{eb.chapter_id(book.number, chapter.label)}">'
                    f"{html.escape(nav_label)}</a></li>"
                )
            parts.append("      </ol></details>")
        parts.append("    </li>")
    parts.extend(["  </ol>", "</nav>"])
    return "\n".join(parts)


def book_html(book: eb.Book) -> str:
    parts = [f'<section class="book" id="{eb.book_id(book.number)}">', f"  <h2>{book.title}</h2>"]
    if book.note is not None:
        parts.append(f'  <p class="book-note">{html.escape(book.note)}</p>')
    else:
        for chapter in book.chapters:
            parts.append(f'  <section class="chapter" id="{eb.chapter_id(book.number, chapter.label)}">')
            parts.append(f"    <h3>{chapter_heading(book, chapter)}</h3>")
            for paragraph in chapter.paragraphs:
                parts.append(eb.paragraph_markup(paragraph))
            parts.append("  </section>")
    parts.append("</section>")
    return "\n".join(parts)


def build() -> dict[str, object]:
    book_paths = sorted(eb.BASE.glob("Polybius_Histories_Book_*_modern_English.md"))
    books = [eb.parse_book(path) for path in book_paths]
    if len(books) != 39:
        raise RuntimeError(f"Expected 39 book files, found {len(books)}")

    eb.DIST.mkdir(exist_ok=True)
    doc = "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8"/>',
            '  <meta name="viewport" content="width=device-width, initial-scale=1"/>',
            "  <title>Polybius — The Histories (Modern English Translation)</title>",
            f"  <style>{CSS}</style>",
            "</head>",
            "<body>",
            '<header id="titlepage">',
            "  <h1>POLYBIUS</h1>",
            '  <p class="subtitle">The Histories</p>',
            '  <p class="edition">A Modern English Translation &mdash; Books I&ndash;XXXIX</p>',
            "</header>",
            editorial_note_html(),
            toc_html(books),
            "<main>",
            "\n".join(book_html(book) for book in books),
            "</main>",
            "<footer>Polybius, <i>The Histories</i> &mdash; modern English translation of the extant local source corpus.</footer>",
            "</body>",
            "</html>",
        ]
    )
    HTML_OUT.write_text(doc, encoding="utf-8")
    return {
        "html": str(HTML_OUT),
        "books": len(books),
        "chapters": sum(len(book.chapters) for book in books),
        "bytes": HTML_OUT.stat().st_size,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(build(), indent=2))
