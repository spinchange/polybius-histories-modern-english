"""Build a standalone single-file HTML edition of the translation.

Reuses the parsing and markup helpers from build_epub.py, so the HTML
edition always reflects the same book files as the EPUB. Output:

    dist/polybius-the-histories-modern-english.html

The page is self-contained (embedded CSS, no external assets except art),
works in light and dark color schemes, and carries print styles so the same
file renders cleanly to PDF (each book starts on a new page; the chapter
lists in the table of contents collapse to book links only).
"""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

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
.hero-banner {
  margin: 2.5rem auto 0;
  max-width: 52rem;
  padding: 0;
}
.hero-banner img {
  width: 100%;
  height: auto;
  display: block;
  border: 1px solid var(--rule);
  border-radius: 2px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.hero-banner figcaption {
  font-size: 0.88rem;
  font-style: italic;
  color: var(--muted);
  margin-top: 0.75rem;
  line-height: 1.4;
}
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
.book-plate {
  margin: 2rem auto 2.5rem;
  text-align: center;
  max-width: 36rem;
  padding: 0;
}
.book-plate img {
  max-width: 100%;
  max-height: 70vh;
  height: auto;
  display: inline-block;
  border: 1px solid var(--rule);
  border-radius: 2px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.book-plate figcaption {
  font-size: 0.88rem;
  font-style: italic;
  color: var(--muted);
  margin-top: 0.65rem;
  line-height: 1.4;
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
  header#titlepage { padding: 12vh 0 0; border: none; page-break-after: always; }
  section.book { page-break-before: always; }
  nav#toc details { display: none; }
  h2 { margin-top: 0; }
  a { color: inherit; text-decoration: none; }
  .hero-banner {
    max-width: 100%;
    margin: 2rem auto 0;
    page-break-inside: avoid;
  }
  .hero-banner img {
    max-width: 100%;
    max-height: 35vh;
    border: none;
    box-shadow: none;
  }
  .book-plate {
    margin: 1.5rem auto 2rem;
    page-break-inside: avoid;
  }
  .book-plate img {
    max-width: 80%;
    max-height: 50vh;
    border: none;
    box-shadow: none;
  }
  .book-plate figcaption,
  .hero-banner figcaption {
    color: #333333;
    font-size: 8.5pt;
  }
}
"""


def load_manifest() -> dict:
    return eb.load_manifest()


def sync_art_to_dist() -> list[str]:
    art_dir = eb.BASE / "art"
    dist_art_dir = eb.DIST / "art"
    copied = []
    if not art_dir.exists():
        return copied
    dist_art_dir.mkdir(parents=True, exist_ok=True)
    for png_path in sorted(art_dir.glob("*.png")):
        dst_path = dist_art_dir / png_path.name
        if (
            not dst_path.exists()
            or dst_path.stat().st_size != png_path.stat().st_size
            or dst_path.stat().st_mtime < png_path.stat().st_mtime
        ):
            shutil.copy2(png_path, dst_path)
        copied.append(png_path.name)
    return copied


def hero_banner_html(manifest: dict) -> str:
    hero_day = eb.BASE / "art" / "hero_day.png"
    if not hero_day.exists():
        return ""
    hero_night = eb.BASE / "art" / "hero_night.png"
    flagships = manifest.get("flagships", {})
    hero_meta = flagships.get("hero_day", {})
    alt_text = hero_meta.get(
        "alt_text",
        "A continuous engraved panoramic frieze chronicling Rome's rise across the Mediterranean.",
    )
    caption = hero_meta.get(
        "caption",
        "The Fifty-Three Years (264–146 BC): Rome's rise from regional Italian republic to Mediterranean master.",
    )

    parts = ['  <figure class="hero-banner">']
    if hero_night.exists():
        parts.append("    <picture>")
        parts.append('      <source srcset="art/hero_night.png" media="(prefers-color-scheme: dark)"/>')
        parts.append(f'      <img src="art/hero_day.png" alt="{html.escape(alt_text)}"/>')
        parts.append("    </picture>")
    else:
        parts.append(f'    <img src="art/hero_day.png" alt="{html.escape(alt_text)}"/>')
    if caption:
        parts.append(f'    <figcaption>{html.escape(caption)}</figcaption>')
    parts.append("  </figure>")
    return "\n".join(parts)


def editorial_note_html() -> str:
    md = (eb.BASE / "PREFACE.md").read_text(encoding="utf-8")
    parts = ['<section id="editorial-note">', "  <h2>Translator's Preface</h2>"]
    in_list = False
    for raw_line in md.splitlines():
        line = raw_line.strip()
        if not line:
            if in_list:
                parts.append("  </ul>")
                in_list = False
            continue
        if line.startswith("## "):
            parts.append(f"<h3>{html.escape(line[3:])}</h3>")
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


def book_html(book: eb.Book, manifest_books: dict[int, dict] | None = None) -> str:
    parts = [f'<section class="book" id="{eb.book_id(book.number)}">', f"  <h2>{book.title}</h2>"]
    plate_file = eb.BASE / "art" / f"book_{book.number:02d}_plate.png"
    if plate_file.exists():
        meta = (manifest_books or {}).get(book.number, {})
        alt_text = meta.get("alt_text", f"Frontispiece illustration for {book.title}")
        caption = meta.get("caption", book.title)
        parts.append('  <figure class="book-plate">')
        parts.append(
            f'    <img src="art/book_{book.number:02d}_plate.png" alt="{html.escape(alt_text)}" loading="lazy"/>'
        )
        if caption:
            parts.append(f'    <figcaption>{html.escape(caption)}</figcaption>')
        parts.append("  </figure>")
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
    copied_art = sync_art_to_dist()
    manifest = load_manifest()
    manifest_books = {b["book"]: b for b in manifest.get("books", []) if "book" in b}

    header_parts = [
        '<header id="titlepage">',
        "  <h1>POLYBIUS</h1>",
        '  <p class="subtitle">The Histories</p>',
        '  <p class="edition">A Modern English Translation &mdash; Books I&ndash;XXXIX</p>',
        '  <p class="edition">Translated from the Greek by Claude, Anthropic&rsquo;s family of AI models. Directed and edited by Christopher Duffy, Sr..</p>',
    ]
    hero = hero_banner_html(manifest)
    if hero:
        header_parts.append(hero)
    header_parts.append("</header>")

    doc_parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8"/>',
        '  <link rel="cc:license" href="https://creativecommons.org/publicdomain/zero/1.0/"/>',
        '  <meta name="viewport" content="width=device-width, initial-scale=1"/>',
        "  <title>Polybius — The Histories (Modern English Translation)</title>",
        '  <meta property="og:title" content="Polybius — The Histories (Modern English Translation)"/>',
        '  <meta property="og:description" content="A modern English translation of Polybius, The Histories, from the Greek."/>',
        '  <meta property="og:type" content="book"/>',
        '  <meta property="og:image" content="art/og_default.png"/>',
        '  <meta name="twitter:card" content="summary_large_image"/>',
        '  <meta name="twitter:title" content="Polybius — The Histories (Modern English Translation)"/>',
        '  <meta name="twitter:description" content="A modern English translation of Polybius, The Histories, from the Greek."/>',
        '  <meta name="twitter:image" content="art/og_default.png"/>',
        f"  <style>{CSS}</style>",
        "</head>",
        "<body>",
        "\n".join(header_parts),
        editorial_note_html(),
        toc_html(books),
        "<main>",
        "\n".join(book_html(book, manifest_books=manifest_books) for book in books),
        "</main>",
        "<footer>Polybius, <i>The Histories</i> &mdash; modern English translation by Claude (Anthropic), edited by Christopher Duffy, Sr.. <a href='https://creativecommons.org/publicdomain/zero/1.0/'>CC0 1.0</a> &middot; <i>Pragmatike Historia</i>.</footer>",
        "</body>",
        "</html>",
    ]
    doc = "\n".join(doc_parts)
    HTML_OUT.write_text(doc, encoding="utf-8")
    return {
        "html": str(HTML_OUT),
        "books": len(books),
        "chapters": sum(len(book.chapters) for book in books),
        "art_synced": len(copied_art),
        "bytes": HTML_OUT.stat().st_size,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(build(), indent=2))
