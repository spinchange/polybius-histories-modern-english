from __future__ import annotations

import html
import re
import shutil
import uuid
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


BASE = Path(__file__).resolve().parent
DIST = BASE / "dist"
EPUB_SRC = DIST / "polybius-histories-epub-src"
EPUB_OUT = DIST / "polybius-the-histories-modern-english.epub"

BOOK_RE = re.compile(r"Polybius_Histories_Book_(\d+)_modern_English\.md$")
CHAPTER_RE = re.compile(r"^#+\s+Book\s+(\d+)\s+Chapter\s+(\d+[a-z]?)\s*:?\s*(.*?)\s*$", re.I)
PREAMBLE_RE = re.compile(r"^#+\s*(?:Polybius|Book\s+\d+\s*$)", re.I)
BRIDGEHEAD_RE = re.compile(r"^(?:[IVXLCDM]+\.|[A-Z][A-Za-z .,'-]{2,60}:)$")

NS_XHTML = "http://www.w3.org/1999/xhtml"
NS_EPUB = "http://www.idpf.org/2007/ops"


@dataclass
class Chapter:
    label: str
    title: str
    paragraphs: list[str] = field(default_factory=list)


@dataclass
class Book:
    number: int
    filename: str
    title: str
    chapters: list[Chapter] = field(default_factory=list)
    note: str | None = None


def roman(n: int) -> str:
    vals = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]
    out = []
    for value, numeral in vals:
        while n >= value:
            out.append(numeral)
            n -= value
    return "".join(out)


def book_id(book: int) -> str:
    return f"book-{book:02d}"


def chapter_id(book: int, label: str) -> str:
    safe = label.lower().replace("a", "-a").replace("b", "-b").replace("c", "-c").replace("d", "-d")
    return f"book-{book:02d}-chapter-{safe}"


def text_to_paragraphs(lines: list[str]) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            continue
        if PREAMBLE_RE.match(stripped) or stripped == "Modern English translation of the Greek text.":
            continue
        current.append(stripped)
    if current:
        paragraphs.append(" ".join(current).strip())
    return paragraphs


def parse_book(path: Path) -> Book:
    match = BOOK_RE.match(path.name)
    if not match:
        raise ValueError(f"Unexpected book filename: {path}")
    number = int(match.group(1))
    title = f"Book {roman(number)}"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    book = Book(number=number, filename=f"book-{number:02d}.xhtml", title=title)

    chapter_matches = [(idx, CHAPTER_RE.match(line)) for idx, line in enumerate(lines) if CHAPTER_RE.match(line)]
    if not chapter_matches:
        note_lines = [
            line.strip()
            for line in lines
            if line.strip()
            and not PREAMBLE_RE.match(line.strip())
            and line.strip() != "Modern English translation of the Greek text."
        ]
        note = "\n".join(note_lines)
        book.note = note or "No chaptered text is present for this book."
        return book

    for pos, (line_index, chapter_match) in enumerate(chapter_matches):
        assert chapter_match is not None
        label = chapter_match.group(2)
        chapter_title = chapter_match.group(3) or f"Chapter {label}"
        next_index = chapter_matches[pos + 1][0] if pos + 1 < len(chapter_matches) else len(lines)
        body_lines = lines[line_index + 1 : next_index]
        book.chapters.append(
            Chapter(label=label, title=chapter_title, paragraphs=text_to_paragraphs(body_lines))
        )
    return book


def xhtml_doc(title: str, body: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="{NS_XHTML}" xmlns:epub="{NS_EPUB}" xml:lang="en-US" lang="en-US">
<head>
  <title>{html.escape(title)}</title>
  <link href="../css/core.css" rel="stylesheet" type="text/css"/>
  <link href="../css/local.css" rel="stylesheet" type="text/css"/>
</head>
<body>
{body}
</body>
</html>
"""


def paragraph_markup(text: str) -> str:
    klass = ' class="bridgehead"' if BRIDGEHEAD_RE.match(text) else ""
    return f"    <p{klass}>{html.escape(text)}</p>"


def inline_note_markup(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", escaped)
    return escaped


def write_book(book: Book, text_dir: Path) -> None:
    parts = [f'  <section id="{book_id(book.number)}" epub:type="chapter">', f"    <h2>{book.title}</h2>"]
    if book.note is not None:
        parts.append(f"    <p>{html.escape(book.note)}</p>")
    else:
        for chapter in book.chapters:
            cid = chapter_id(book.number, chapter.label)
            parts.append(f'    <section id="{cid}" epub:type="division">')
            if chapter.title == f"Chapter {chapter.label}":
                heading = f"      <h3><span class=\"label\">Chapter {html.escape(chapter.label)}</span></h3>"
            else:
                heading = (
                    f"      <h3><span class=\"label\">Chapter {html.escape(chapter.label)}</span> "
                    f"{html.escape(chapter.title)}</h3>"
                )
            parts.append(heading)
            for paragraph in chapter.paragraphs:
                parts.append(paragraph_markup(paragraph))
            parts.append("    </section>")
    parts.append("  </section>")
    body = "\n".join(parts)
    (text_dir / book.filename).write_text(xhtml_doc(f"Polybius, The Histories: {book.title}", body), encoding="utf-8")


def editorial_note_body() -> str:
    md = (BASE / "EDITORIAL_NOTE.md").read_text(encoding="utf-8")
    parts = ['  <section id="editorial-note" epub:type="preface">', "    <h2>Editorial Note</h2>"]
    in_list = False
    for raw_line in md.splitlines():
        line = raw_line.strip()
        if not line:
            if in_list:
                parts.append("    </ul>")
                in_list = False
            continue
        if line.startswith("#"):
            continue
        if line.startswith("- "):
            if not in_list:
                parts.append("    <ul>")
                in_list = True
            parts.append(f"      <li>{inline_note_markup(line[2:])}</li>")
        else:
            if in_list:
                parts.append("    </ul>")
                in_list = False
            parts.append(f"    <p>{inline_note_markup(line)}</p>")
    if in_list:
        parts.append("    </ul>")
    parts.append("  </section>")
    return "\n".join(parts)


def write_frontmatter(text_dir: Path, books: list[Book]) -> None:
    cover_body = """  <section id="cover" epub:type="cover">
    <h1>Cover</h1>
    <figure>
      <img src="../images/cover.svg" alt="Cover for Polybius, The Histories"/>
    </figure>
  </section>"""
    (text_dir / "cover.xhtml").write_text(xhtml_doc("Cover", cover_body), encoding="utf-8")

    title_body = """  <section id="titlepage" epub:type="titlepage">
    <h1>Polybius</h1>
    <p class="subtitle">The Histories</p>
    <p class="edition">Modern English translation of the extant local source corpus</p>
  </section>"""
    (text_dir / "titlepage.xhtml").write_text(xhtml_doc("Titlepage", title_body), encoding="utf-8")
    (text_dir / "editorial-note.xhtml").write_text(xhtml_doc("Editorial Note", editorial_note_body()), encoding="utf-8")
    (text_dir / "nav.xhtml").write_text(xhtml_doc("Table of Contents", nav_body(books)), encoding="utf-8")


def nav_body(books: list[Book]) -> str:
    parts = ['  <nav epub:type="toc" id="toc">', "    <h2>Table of Contents</h2>", "    <ol>"]
    parts.append('      <li><a href="titlepage.xhtml">Titlepage</a></li>')
    parts.append('      <li><a href="editorial-note.xhtml">Editorial Note</a></li>')
    for book in books:
        parts.append(f'      <li><a href="{book.filename}">{book.title}</a>')
        if book.chapters:
            parts.append("        <ol>")
            for chapter in book.chapters:
                nav_label = f"Chapter {chapter.label}"
                if chapter.title != nav_label:
                    nav_label += f": {chapter.title}"
                parts.append(
                    f'          <li><a href="{book.filename}#{chapter_id(book.number, chapter.label)}">'
                    f'{html.escape(nav_label)}</a></li>'
                )
            parts.append("        </ol>")
        parts.append("      </li>")
    parts.extend(
        [
            "    </ol>",
            "  </nav>",
            '  <nav epub:type="landmarks" id="landmarks" hidden="hidden">',
            "    <h2>Landmarks</h2>",
            "    <ol>",
            '      <li><a epub:type="cover" href="cover.xhtml">Cover</a></li>',
            '      <li><a epub:type="titlepage" href="titlepage.xhtml">Titlepage</a></li>',
            '      <li><a epub:type="bodymatter" href="book-01.xhtml">Text</a></li>',
            "    </ol>",
            "  </nav>",
        ]
    )
    return "\n".join(parts)


def write_css(css_dir: Path) -> None:
    core = """@namespace epub "http://www.idpf.org/2007/ops";

html {
  font-family: serif;
  line-height: 1.45;
}

body {
  margin: 0;
  padding: 0;
}

h1,
h2,
h3,
p {
  margin-left: 0;
  margin-right: 0;
}

p {
  margin-bottom: 0;
  margin-top: 0;
  text-align: justify;
  text-indent: 1.25em;
}

h1,
h2,
h3,
.subtitle,
.edition,
.bridgehead {
  text-align: center;
  text-indent: 0;
}

section {
  page-break-before: always;
}

section section {
  page-break-before: auto;
}
"""
    local = """body {
  color: #1f1b16;
}

#titlepage {
  margin: 18vh auto 0 auto;
  max-width: 34em;
  text-align: center;
}

#titlepage h1 {
  font-size: 2.6em;
  font-weight: normal;
  letter-spacing: 0;
  margin: 0 0 .5em 0;
  text-transform: uppercase;
}

.subtitle {
  font-size: 1.8em;
  font-variant: small-caps;
  margin: 0 0 1.8em 0;
}

.edition {
  font-size: .95em;
  margin-top: 2em;
}

h2 {
  font-size: 1.7em;
  font-weight: normal;
  margin: 4em 0 2em 0;
  text-transform: uppercase;
}

h3 {
  font-size: 1.05em;
  font-weight: normal;
  margin: 2.5em 0 1em 0;
}

h3 .label {
  display: block;
  font-size: .82em;
  font-variant: small-caps;
  margin-bottom: .35em;
}

p + p {
  margin-top: .15em;
}

.bridgehead {
  font-style: italic;
  margin: 1.5em 0 .75em 0;
}

#editorial-note p {
  text-indent: 0;
  margin-top: .8em;
}

#editorial-note ul {
  margin: .7em 0 1em 1.4em;
  padding-left: 0;
}

#editorial-note li {
  margin: .35em 0;
}

code {
  font-family: monospace;
}

#toc ol {
  list-style-type: none;
  margin-left: 0;
  padding-left: 0;
}

#toc ol ol {
  margin: .35em 0 .8em 1.25em;
}

#toc li {
  margin: .25em 0;
}

#cover {
  text-align: center;
}

#cover h1 {
  display: none;
}

#cover img {
  max-height: 100%;
  max-width: 100%;
}
"""
    (css_dir / "core.css").write_text(core, encoding="utf-8")
    (css_dir / "local.css").write_text(local, encoding="utf-8")


def write_cover(images_dir: Path) -> None:
    cover = """<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="2560" viewBox="0 0 1600 2560" role="img" aria-labelledby="title desc">
  <title id="title">Polybius, The Histories</title>
  <desc id="desc">A restrained classical-style cover with a bronze field, a geometric border, and centered title text.</desc>
  <rect width="1600" height="2560" fill="#4d3527"/>
  <rect x="92" y="92" width="1416" height="2376" fill="#eadfca"/>
  <rect x="148" y="148" width="1304" height="2264" fill="#5b3b2b"/>
  <rect x="214" y="214" width="1172" height="2132" fill="none" stroke="#d7bd82" stroke-width="6"/>
  <g fill="#d7bd82">
    <rect x="292" y="428" width="1016" height="4"/>
    <rect x="292" y="2040" width="1016" height="4"/>
    <circle cx="800" cy="548" r="74" fill="none" stroke="#d7bd82" stroke-width="6"/>
    <path d="M732 548h136M800 480v136M752 500l96 96M848 500l-96 96" stroke="#d7bd82" stroke-width="5" fill="none"/>
  </g>
  <text x="800" y="910" fill="#f4e7c7" font-family="Georgia, serif" font-size="86" text-anchor="middle" letter-spacing="8">POLYBIUS</text>
  <text x="800" y="1135" fill="#f4e7c7" font-family="Georgia, serif" font-size="118" text-anchor="middle">The Histories</text>
  <text x="800" y="1305" fill="#d7bd82" font-family="Georgia, serif" font-size="44" text-anchor="middle">A Modern English Translation</text>
  <text x="800" y="1860" fill="#f4e7c7" font-family="Georgia, serif" font-size="40" text-anchor="middle">Books I-XXXIX</text>
</svg>
"""
    (images_dir / "cover.svg").write_text(cover, encoding="utf-8")


def write_container(root: Path) -> None:
    (root / "mimetype").write_text("application/epub+zip", encoding="ascii")
    meta_inf = root / "META-INF"
    meta_inf.mkdir(parents=True, exist_ok=True)
    container = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="EPUB/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    (meta_inf / "container.xml").write_text(container, encoding="utf-8")


def write_opf(epub_dir: Path, books: list[Book], identifier: str) -> None:
    modified = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest_items = [
        '<item id="nav" href="text/nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '<item id="cover" href="text/cover.xhtml" media-type="application/xhtml+xml"/>',
        '<item id="titlepage" href="text/titlepage.xhtml" media-type="application/xhtml+xml"/>',
        '<item id="editorial-note" href="text/editorial-note.xhtml" media-type="application/xhtml+xml"/>',
        '<item id="core-css" href="css/core.css" media-type="text/css"/>',
        '<item id="local-css" href="css/local.css" media-type="text/css"/>',
        '<item id="cover-image" href="images/cover.svg" media-type="image/svg+xml" properties="cover-image"/>',
    ]
    spine_items = [
        '<itemref idref="cover"/>',
        '<itemref idref="titlepage"/>',
        '<itemref idref="editorial-note"/>',
        '<itemref idref="nav"/>',
    ]
    for book in books:
        manifest_items.append(
            f'<item id="{book_id(book.number)}" href="text/{book.filename}" media-type="application/xhtml+xml"/>'
        )
        spine_items.append(f'<itemref idref="{book_id(book.number)}"/>')
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="en-US">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">urn:uuid:{identifier}</dc:identifier>
    <dc:title>Polybius: The Histories</dc:title>
    <dc:creator id="creator">Polybius</dc:creator>
    <dc:language>en-US</dc:language>
    <dc:subject>History, Ancient</dc:subject>
    <dc:description>A modern-English working translation of the extant local source corpus for Polybius, The Histories.</dc:description>
    <dc:publisher>Hermes local edition</dc:publisher>
    <meta property="dcterms:modified">{modified}</meta>
  </metadata>
  <manifest>
    {chr(10).join("    " + item for item in manifest_items)}
  </manifest>
  <spine toc="ncx">
    {chr(10).join("    " + item for item in spine_items)}
  </spine>
</package>
"""
    (epub_dir / "content.opf").write_text(opf, encoding="utf-8")


def write_ncx(epub_dir: Path, books: list[Book], identifier: str) -> None:
    navpoints = []
    order = 1
    for book in books:
        navpoints.append(
            f'''    <navPoint id="{book_id(book.number)}" playOrder="{order}">
      <navLabel><text>{html.escape(book.title)}</text></navLabel>
      <content src="text/{book.filename}"/>
    </navPoint>'''
        )
        order += 1
    ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:{identifier}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>Polybius: The Histories</text></docTitle>
  <navMap>
{chr(10).join(navpoints)}
  </navMap>
</ncx>
"""
    (epub_dir / "toc.ncx").write_text(ncx, encoding="utf-8")


def zip_epub(src: Path, out: Path) -> None:
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w") as zf:
        zf.write(src / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for path in sorted(src.rglob("*")):
            if path.is_dir() or path.name == "mimetype":
                continue
            zf.write(path, path.relative_to(src).as_posix(), compress_type=zipfile.ZIP_DEFLATED)


def validate_xml(root: Path) -> None:
    for path in root.rglob("*.xhtml"):
        ET.parse(path)
    ET.parse(root / "META-INF" / "container.xml")
    ET.parse(root / "EPUB" / "content.opf")
    ET.parse(root / "EPUB" / "toc.ncx")
    ET.parse(root / "EPUB" / "images" / "cover.svg")


def build() -> dict[str, object]:
    book_paths = sorted(BASE.glob("Polybius_Histories_Book_*_modern_English.md"))
    books = [parse_book(path) for path in book_paths]
    if len(books) != 39:
        raise RuntimeError(f"Expected 39 book files, found {len(books)}")

    if EPUB_SRC.exists():
        shutil.rmtree(EPUB_SRC)
    EPUB_SRC.mkdir(parents=True, exist_ok=True)
    epub_dir = EPUB_SRC / "EPUB"
    text_dir = epub_dir / "text"
    css_dir = epub_dir / "css"
    images_dir = epub_dir / "images"
    text_dir.mkdir(parents=True)
    css_dir.mkdir()
    images_dir.mkdir()

    identifier = str(uuid.uuid5(uuid.NAMESPACE_URL, "hermes-polybius-histories-modern-english"))
    write_container(EPUB_SRC)
    write_css(css_dir)
    write_cover(images_dir)
    write_frontmatter(text_dir, books)
    for book in books:
        write_book(book, text_dir)
    write_opf(epub_dir, books, identifier)
    write_ncx(epub_dir, books, identifier)
    validate_xml(EPUB_SRC)
    zip_epub(EPUB_SRC, EPUB_OUT)

    return {
        "source": str(EPUB_SRC),
        "epub": str(EPUB_OUT),
        "books": len(books),
        "chapters": sum(len(book.chapters) for book in books),
        "bytes": EPUB_OUT.stat().st_size,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(build(), indent=2))
