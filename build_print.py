"""Build the print edition (interior PDF) with Typst, laid out for Lulu.

Reuses the book parser from build_epub.py, so the print edition always reflects
the same book files as the EPUB and HTML.  Default output, one volume:

    dist/polybius-the-histories-print-6x9.pdf

Layout profile (decided 2026-11-01): Lulu "US Trade" 6 x 9 in, black and white
interior (Premium B&W recommended for the plates), 9.5 pt Libertinus Serif,
tight margins.  Lulu limits: 800 pages (paperback perfect bound and casewrap),
>= 0.5 in margins on every side, 0.2-0.3 in gutter, fonts embedded, no
two-page spreads, odd pages on the right, page count a multiple of 4.

The book also carries two back-matter parts built from the annotation layers:
"Companion Notes" (readers + parallels) and "How the Text Survived" (the essay
and a source-by-book table drawn from the survival layer).

    python build_print.py                  one volume (default)
    python build_print.py --volumes 2      two volumes (split after Book 9)
    python build_print.py --split 8        two volumes, split after Book 8
    python build_print.py --typ-only       write the .typ sources, do not compile

Interior only: the cover needs the spine width Lulu computes from the uploaded
interior (download the cover template after upload).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

import build_epub as eb

BASE = eb.BASE
DIST = eb.DIST
WORK = BASE / "work" / "print"
IMG = WORK / "img"
ANN = DIST / "annotations"

DEFAULT_SPLIT = 9
PLATE_MAX_PX = 1500
PLATE_HEIGHT = "2.75in"
PAGE_W, PAGE_H = 432, 648  # points (6 x 9 in)

TYPST_FALLBACK = (
    Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    / "Typst.Typst_Microsoft.Winget.Source_8wekyb3d8bbwe"
    / "typst-x86_64-pc-windows-msvc" / "typst.exe"
)

RUBRIC_RE = re.compile(r"^(?:Olympiad\s+\d+,\s*year\s+\d+\.?.{0,60}|[IVXLCDM]+\.\s.{0,60})$")
ITALIC_ONLY_RE = re.compile(r"^\*[^*]+\*$")

# --------------------------------------------------------------------------
# Typst helpers
# --------------------------------------------------------------------------


def q(text: str) -> str:
    """Typst string literal."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


INLINE_RE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")


def inline(text: str) -> str:
    """Markdown-ish inline text -> Typst markup made only of string literals."""
    out = []
    for part in INLINE_RE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            out.append(f"#strong({q(part[2:-2])})")
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            out.append(f"#emph({q(part[1:-1])})")
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            out.append(f"#{q(part[1:-1])}")
        else:
            out.append(f"#{q(part)}")
    return "".join(out) or "#\"\""


def body_paragraph(text: str) -> str:
    stripped = text.strip()
    if eb.BRIDGEHEAD_RE.match(stripped) or RUBRIC_RE.match(stripped):
        return f"#rubric[{inline(stripped)}]"
    if ITALIC_ONLY_RE.match(stripped) and len(stripped) < 140:
        return f"#attribution[{inline(stripped)}]"
    return inline(stripped)


# --------------------------------------------------------------------------
# Art (greyscale for a black-and-white interior)
# --------------------------------------------------------------------------


def prepare_plate(number: int) -> str | None:
    src = BASE / "art" / f"book_{number:02d}_plate.png"
    if not src.exists():
        return None
    IMG.mkdir(parents=True, exist_ok=True)
    dst = IMG / f"book_{number:02d}_plate_bw.jpg"
    if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
        im = Image.open(src).convert("L")
        if max(im.size) > PLATE_MAX_PX:
            im.thumbnail((PLATE_MAX_PX, PLATE_MAX_PX), Image.LANCZOS)
        im = ImageOps.autocontrast(im, cutoff=1)
        im.save(dst, "JPEG", quality=90, optimize=True)
    return f"img/{dst.name}"


# --------------------------------------------------------------------------
# Annotation layers (from the clean, verified build in dist/annotations)
# --------------------------------------------------------------------------


def load_layer(name: str) -> list[dict]:
    path = ANN / f"{name}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("annotations", [])


def chap_key(label: str) -> tuple[int, str]:
    m = re.match(r"(\d+)([a-z]*)$", label)
    return (int(m.group(1)), m.group(2)) if m else (9999, label)


def anchor_ref(anchors: list[dict]) -> str:
    refs = []
    for a in anchors:
        if a["from"] == a["to"]:
            refs.append(f"{a['book']}.{a['from']}")
        else:
            refs.append(f"{a['book']}.{a['from']}–{a['to']}")
    return "; ".join(refs)


def anchor_sort_key(entry: dict):
    a = entry["anchors"][0]
    return (a["book"], chap_key(a["from"]), entry["id"])


def dagger_set(entries: list[dict]) -> set[tuple[int, str]]:
    """Chapters that carry a dagger: the first chapter of each note's anchor."""
    return {(e["anchors"][0]["book"], e["anchors"][0]["from"]) for e in entries}


def one_line(text: str) -> str:
    return " ".join(line.strip() for line in text.strip().splitlines())


def quote_markup(text: str) -> str:
    paras = [one_line(p) for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    return "\n\n".join(inline(p) for p in paras)


def note_entry(e: dict) -> str:
    who = e["annotator"]
    work = e.get("work") or ""
    date = e.get("date") or ""
    byline = who + (f": {work}" if work else "") + (f" ({date})" if date else "")
    src = e.get("source_pub") or ""
    src = re.sub(r"\s*\(PD\)\s*$", "", src)
    source = f"Source: {src}." if src else ""
    parts = [
        f"#cnentry({q(anchor_ref(e['anchors']))}, [{inline(byline)}],",
        f"  [{quote_markup(e['quote'])}],",
        f"  [{inline(one_line(e['note']))}],",
        f"  [{inline(source) if source else ''}])",
    ]
    return "\n".join(parts)


def companion_notes_source(readers: list[dict], parallels: list[dict]) -> str:
    out = ["\n= Companion Notes\n"]
    out.append(
        "#cnintro[Some of the most interesting things ever said about Polybius were said by "
        "people who read him, and some of his best stories were told again by other ancient "
        "writers. These notes gather both, keyed to the chapters they touch. A dagger "
        "(†) after a chapter number in the text marks a chapter with a note here. Every "
        "quotation is from a public-domain translation or is translated for this edition; "
        "the source is named under each note.]\n"
    )
    out.append("#cnsub[Readers of Polybius]\n")
    for e in sorted(readers, key=anchor_sort_key):
        out.append(note_entry(e) + "\n")
    out.append("#cnsub[Parallel accounts]\n")
    for e in sorted(parallels, key=anchor_sort_key):
        out.append(note_entry(e) + "\n")
    return "\n".join(out)


ESSAY_EDITS = [
    ("This chapter is an example.", "Chapter 7.1 is an example."),
    ("Their provenance is recorded in this layer instead.", "Their provenance is recorded in the table that follows."),
    (", and Polybius stands fifth on his list of the chronicles used (his own preface, quoted in the note beside this one, is translated for this edition)",
     ", and Polybius stands fifth on his list of the chronicles used"),
    ("its note in this layer says so rather than guess.", "the table lists both sources rather than guess."),
]


def compress_chapters(tokens: list[tuple[int, str]]) -> str:
    tokens = sorted(set(tokens))
    out, i = [], 0
    while i < len(tokens):
        n, suf = tokens[i]
        if suf:
            out.append(f"{n}{suf}")
            i += 1
            continue
        j = i
        while j + 1 < len(tokens) and not tokens[j + 1][1] and tokens[j + 1][0] == tokens[j][0] + 1:
            j += 1
        out.append(f"{n}" if j == i else f"{n}–{tokens[j][0]}")
        i = j + 1
    return ", ".join(out)


def survival_source(survival: list[dict], readers: list[dict]) -> str:
    essay = next((e for e in survival if e["id"].endswith("how-this-book-survived")), None)
    rest = [e for e in survival if e is not essay]
    out = ["\n= How the Text Survived\n"]
    if essay:
        note = essay["note"]
        has_cvii = any("Constantine" in r.get("annotator", "") for r in readers)
        for old, new in ESSAY_EDITS:
            if old not in note:
                continue
            if "preface, quoted in the note" in old and has_cvii:
                new = ", and Polybius stands fifth on his list of the chronicles used (his own preface is quoted in the Companion Notes)"
            note = note.replace(old, new)
        for para in [p for p in re.split(r"\n\s*\n", note.strip()) if p.strip()]:
            out.append(inline(one_line(para)) + "\n")
    out.append("#cnsub[Where each fragment comes from]\n")
    out.append(
        "#cnintro[Chapters of Books 7 to 39 that survive through a single quoting author carry "
        "an italic line under the heading in the text. This table lists every chapter by "
        "the work that preserved it.]\n"
    )
    by_book: dict[int, dict[str, list[tuple[int, str]]]] = {}
    for e in rest:
        for a in e["anchors"]:
            lo, hi = chap_key(a["from"]), chap_key(a["to"])
            toks = []
            if a["from"] == a["to"] or lo[0] == hi[0]:
                toks = [lo] if a["from"] == a["to"] else [lo, hi]
            else:
                toks = [(n, "") for n in range(lo[0], hi[0] + 1)]
            by_book.setdefault(a["book"], {}).setdefault(e["annotator"], []).extend(toks)
    rows = []
    for book in sorted(by_book):
        lines = []
        for src in sorted(by_book[book], key=lambda s: min(by_book[book][s])):
            lines.append(f"#emph({q(src)}) #h(0.3em) #{q(compress_chapters(by_book[book][src]))}")
        rows.append(f"[#strong({q(eb.roman(book))})], [" + " #linebreak() ".join(lines) + "]")
    out.append("#survival-table(" + ",\n  ".join(rows) + ")\n")
    return "\n".join(out)


# --------------------------------------------------------------------------
# Front matter
# --------------------------------------------------------------------------

CREDIT_1 = "Translated from the Greek by Claude, Anthropic’s family of AI models."
CREDIT_2 = "Directed and edited by Christopher Duffy, Sr."


def roman_range(first: int, last: int) -> str:
    return f"Books {eb.roman(first)}–{eb.roman(last)}" if first != last else f"Book {eb.roman(first)}"


def preface_blocks() -> str:
    md = (BASE / "PREFACE.md").read_text(encoding="utf-8")
    out = []
    bullets: list[str] = []

    def flush():
        nonlocal bullets
        if bullets:
            items = ",\n".join(f"[{b}]" for b in bullets)
            out.append(f"#list(tight: true, {items})")
            bullets = []

    for raw in md.splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            flush()
            out.append(f"#prefhead({q(line[3:].strip())})")
            continue
        if line.startswith("- "):
            bullets.append(inline(line[2:].strip()))
            continue
        flush()
        if ITALIC_ONLY_RE.match(line):
            out.append(f"#align(center)[#v(1em)#text(size: 0.92em)[{inline(line)}]]")
        else:
            out.append(inline(line))
    flush()
    return "\n\n".join(out)


def front_matter(vol_label: str | None, span: str) -> str:
    vol_line = f'#text(size: 11pt, tracking: 0.12em)[{vol_label.upper()}]' if vol_label else ""
    vol_title = f"{vol_label}: {span}" if vol_label else span
    return f"""
// ---------------------------------------------------------------- half title
#noheader[
  #v(1fr)
  #align(center)[
    #text(size: 22pt, tracking: 0.28em)[#smallcaps[Polybius]]
    #v(0.6em)
    #text(size: 15pt, style: "italic")[The Histories]
    #v(1.4em)
    {vol_line}
  ]
  #v(2fr)
]
#blankpage()

// ---------------------------------------------------------------- title page
#noheader[
  #v(1.6fr)
  #align(center)[
    #text(size: 30pt, tracking: 0.3em)[#smallcaps[Polybius]]
    #v(0.7em)
    #line(length: 2.2cm, stroke: 0.5pt)
    #v(0.7em)
    #text(size: 21pt, style: "italic")[The Histories]
    #v(1.2em)
    #text(size: 11.5pt)[A Modern English Translation]
    #v(0.3em)
    #text(size: 10.5pt)[{vol_title}]
    #v(2.2em)
    #text(size: 9.5pt)[{CREDIT_1}#linebreak(){CREDIT_2}]
  ]
  #v(2fr)
  #align(center)[#text(size: 9.5pt, tracking: 0.08em)[#smallcaps[Pragmatike Historia] #sym.dot.c pragmatikehistoria.org]]
  #v(0.8cm)
]

// ---------------------------------------------------------------- copyright
#to-even()
#noheader[
  #v(1fr)
  #set text(size: 8.8pt)
  #set par(first-line-indent: 0pt, justify: false, spacing: 0.7em)
  *Polybius, The Histories: a modern English translation*

  {CREDIT_1} {CREDIT_2}

  The text, the illustrations and the apparatus of this edition are dedicated to
  the public domain under the Creative Commons CC0 1.0 Universal dedication
  (creativecommons.org/publicdomain/zero/1.0/). Anyone may copy, adapt,
  print or distribute them, with no permission needed. As a courtesy, reuse is
  asked to name the edition: _Pragmatike Historia_, pragmatikehistoria.org.

  The translation is made from the Greek text of Büttner-Wobst (Teubner,
  1889–1905). The illustrations were generated with Google’s Gemini models.
  Read the Translator’s Preface for what this edition is and is not.

  Set in Libertinus Serif. Interior prepared at 6 × 9 inches.
]
"""


# --------------------------------------------------------------------------
# Preamble (page geometry, styles, running heads)
# --------------------------------------------------------------------------

PREAMBLE = r"""
#let ink = luma(0)
#set document(title: "__DOC_TITLE__", author: "Polybius (translated by Claude; edited by Christopher Duffy, Sr.)")
#set text(font: ("Libertinus Serif", "Georgia"), size: 9.5pt, lang: "en", hyphenate: true, fill: ink,
          number-type: "old-style", costs: (widow: 200%, orphan: 200%, runt: 120%))
#set smartquote(enabled: false)
#set par(justify: true, leading: 0.52em, spacing: 0.52em, first-line-indent: (amount: 1.1em, all: false))
#set page(
  width: 6in, height: 9in,
  margin: (inside: 0.75in, outside: 0.5in, top: 0.85in, bottom: 0.75in),
  binding: left,
  numbering: "i",
  header-ascent: 0.3in,
  footer-descent: 0.25in,
)

#let in-body = state("in-body", false)

// pages that must carry neither header nor folio (title pages, blanks)
#let noheader(body) = [#metadata("noheader") <noheader>#body]

#let blankpage() = [#pagebreak() #metadata("noheader") <noheader> #pagebreak()]

// start the next page on a recto (odd) or verso (even); filler pages carry no header or folio
#let to-odd() = { set page(header: none, footer: none); pagebreak(to: "odd", weak: true) }
#let to-even() = { set page(header: none, footer: none); pagebreak(to: "even", weak: true) }

#let on-marked-page() = {
  let pg = here().page()
  query(<noheader>).any(m => m.location().page() == pg)
}
#let on-opener-page() = {
  let pg = here().page()
  query(heading.where(level: 1)).any(h => h.location().page() == pg)
}

#let folio() = context counter(page).display(here().page-numbering())

#set page(
  header: context {
    if on-marked-page() or on-opener-page() { return }
    let pg = here().page()
    let heads = query(heading.where(level: 1).before(here()))
    let current = if heads.len() > 0 { heads.last().body } else { [] }
    set text(size: 8.4pt)
    if calc.odd(pg) {
      align(right)[#smallcaps(current) #h(1.4em) #folio()]
    } else {
      align(left)[#folio() #h(1.4em) #smallcaps[Polybius, The Histories]]
    }
  },
  footer: context {
    if on-marked-page() { return }
    if on-opener-page() { align(center, text(size: 8.4pt, folio())) }
  },
)

#let rubric(body) = block(above: 0.9em, below: 0.5em, width: 100%, sticky: true,
  align(center, text(size: 9pt, style: "italic", tracking: 0.02em, body)))
#let attribution(body) = block(above: 0.15em, below: 0.4em, width: 100%, sticky: true,
  align(left, text(size: 8.8pt, body)))
#let chead(num, title, dagger: false) = block(above: 0.75em, below: 0.3em, width: 100%, sticky: true, breakable: false)[
  #set par(first-line-indent: 0pt, justify: false, leading: 0.45em)
  #text(size: 8.6pt, tracking: 0.1em)[#smallcaps[Chapter #num#if dagger [#super[†]]]] #h(0.5em) #text(size: 10pt, weight: "bold")[#title]
]
#let prefhead(title) = block(above: 1.1em, below: 0.5em, sticky: true)[
  #text(size: 10.5pt, weight: "bold")[#title]
]

#let bookplate(path, cap) = align(center)[
  #image(path, height: __PLATE_H__, fit: "contain")
  #v(0.35em)
  #block(width: 85%)[#set par(justify: false, first-line-indent: 0pt, leading: 0.45em)
    #text(size: 7.8pt, style: "italic")[#cap]]
  #v(0.5em)
]

// companion notes
#let cnintro(body) = block(above: 0.4em, below: 0.6em)[#set par(first-line-indent: 0pt); #body]
#let cnsub(body) = block(above: 1.4em, below: 0.6em, sticky: true)[
  #align(center, text(size: 10.5pt, style: "italic")[#body])
]
#let cnentry(ref, byline, quote, note, source) = block(above: 0.95em, below: 0.2em, breakable: true)[
  #set par(first-line-indent: 0pt, justify: true, leading: 0.48em, spacing: 0.48em)
  #text(size: 9pt, weight: "bold")[#ref] #h(0.4em) #text(size: 9pt)[#byline]
  #v(0.2em)
  #block(inset: (left: 0.9em, right: 0.3em))[#set text(size: 8.5pt); #quote]
  #v(0.1em)
  #text(size: 9pt)[#note]
  #if source != [] [#v(0.1em)#text(size: 7.6pt, style: "italic")[#source]]
]
#let survival-table(..cells) = {
  set text(size: 8.4pt)
  set par(first-line-indent: 0pt, justify: false, leading: 0.4em)
  grid(columns: (2.4em, 1fr), row-gutter: 0.55em, column-gutter: 0.6em, ..cells)
}

#show heading.where(level: 1): it => context {
  if in-body.at(it.location()) {
    pagebreak(weak: true)
    v(6%)
    align(center)[
      #text(size: 14pt, tracking: 0.3em)[#smallcaps[#it.body]]
      #v(0.7em)
      #line(length: 1.6cm, stroke: 0.5pt)
    ]
    v(1.4em)
  } else {
    to-odd()
    v(10%)
    align(center, text(size: 15pt, style: "italic")[#it.body])
    v(1.6em)
  }
}

#show outline.entry: it => {
  set text(size: 9.2pt)
  block(above: 0.5em, link(it.element.location(), it.indented(none, it.inner())))
}
"""


# --------------------------------------------------------------------------
# Volume assembly
# --------------------------------------------------------------------------


def book_source(book: eb.Book, manifest_books: dict[int, dict], daggers: set[tuple[int, str]]) -> str:
    parts = [f"= Book {eb.roman(book.number)}\n"]
    plate = prepare_plate(book.number)
    if plate:
        cap = manifest_books.get(book.number, {}).get("caption", f"Book {eb.roman(book.number)}")
        parts.append(f"#bookplate({q(plate)}, {q(cap)})\n")
    if book.note is not None:
        parts.append(f"#attribution[{inline(book.note)}]\n")
        return "\n".join(parts)
    for chapter in book.chapters:
        title = chapter.title if chapter.title != f"Chapter {chapter.label}" else ""
        dag = "true" if (book.number, chapter.label) in daggers else "false"
        parts.append(f"#chead({q(chapter.label)}, {q(title)}, dagger: {dag})\n")
        for para in chapter.paragraphs:
            parts.append(body_paragraph(para) + "\n")
    return "\n".join(parts)


def volume_source(books: list[eb.Book], vol_label: str | None, manifest_books: dict[int, dict],
                  back_matter: bool, readers, parallels, survival) -> str:
    span = roman_range(books[0].number, books[-1].number)
    doc_title = "Polybius, The Histories" + (f" ({vol_label})" if vol_label else "")
    pre = PREAMBLE.replace("__DOC_TITLE__", doc_title).replace("__PLATE_H__", PLATE_HEIGHT)
    daggers = dagger_set(readers + parallels) if back_matter else set()
    src = [pre, front_matter(vol_label, span)]
    src.append('\n#to-odd()\n#noheader[]\n')
    src.append('#v(8%)\n#align(center, text(size: 15pt, style: "italic")[Contents])\n#v(1.2em)\n')
    src.append("#columns(2, gutter: 1.4em)[#outline(title: none, depth: 1, indent: 0pt)]\n")
    src.append("\n= Translator’s Preface\n")
    src.append(preface_blocks() + "\n")
    if back_matter:
        src.append(
            '\n#align(center)[#v(0.8em)#text(size: 0.92em, style: "italic")'
            '[A dagger (†) after a chapter number marks a chapter with a note in the Companion Notes at the back of the book.]]\n'
        )
    # body: arabic numbering restarts at 1, first book opens on a recto
    src.append('\n#to-odd()\n#set page(numbering: "1")\n#counter(page).update(1)\n#in-body.update(true)\n')
    for book in books:
        src.append(book_source(book, manifest_books, daggers))
    if back_matter:
        src.append(companion_notes_source(readers, parallels))
        src.append(survival_source(survival, readers))
    return "\n".join(src)


def find_typst() -> str:
    exe = shutil.which("typst")
    if exe:
        return exe
    if TYPST_FALLBACK.exists():
        return str(TYPST_FALLBACK)
    raise RuntimeError("typst not found (winget install Typst.Typst)")


def compile_typ(typ: Path, pdf: Path) -> None:
    cmd = [find_typst(), "compile", "--root", str(WORK), str(typ), str(pdf)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode:
        sys.stderr.write(res.stderr)
        raise RuntimeError(f"typst failed for {typ.name}")
    if res.stderr.strip():
        sys.stderr.write(res.stderr)


def finalize_pdf(pdf: Path) -> int:
    """Pad with blank pages to a multiple of 4 (Lulu recommendation); return the page count."""
    import pymupdf

    doc = pymupdf.open(pdf)
    while len(doc) % 4:
        doc.new_page(width=PAGE_W, height=PAGE_H)
    n = len(doc)
    tmp = pdf.with_suffix(".tmp.pdf")
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, pdf)
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--volumes", type=int, choices=(1, 2), default=1)
    ap.add_argument("--split", type=int, default=DEFAULT_SPLIT, help="last book of volume 1 (two volumes)")
    ap.add_argument("--typ-only", action="store_true")
    args = ap.parse_args()
    two = args.volumes == 2

    paths = sorted(BASE.glob("Polybius_Histories_Book_*_modern_English.md"))
    books = [eb.parse_book(p) for p in paths]
    if len(books) != 39:
        raise RuntimeError(f"Expected 39 book files, found {len(books)}")
    manifest = eb.load_manifest()
    manifest_books = {b["book"]: b for b in manifest.get("books", []) if "book" in b}
    readers, parallels, survival = load_layer("readers"), load_layer("parallels"), load_layer("survival")

    WORK.mkdir(parents=True, exist_ok=True)
    if not two:
        plan = [("single", None, books, DIST / "polybius-the-histories-print-6x9.pdf", True)]
    else:
        v1 = [b for b in books if b.number <= args.split]
        v2 = [b for b in books if b.number > args.split]
        plan = [
            ("vol1", "Volume I", v1, DIST / "polybius-the-histories-print-vol1-6x9.pdf", False),
            ("vol2", "Volume II", v2, DIST / "polybius-the-histories-print-vol2-6x9.pdf", True),
        ]

    report = {}
    for key, label, vbooks, pdf, back in plan:
        typ = WORK / f"{key}.typ"
        typ.write_text(volume_source(vbooks, label, manifest_books, back, readers, parallels, survival),
                       encoding="utf-8")
        entry = {"typ": str(typ), "books": f"{vbooks[0].number}-{vbooks[-1].number}"}
        if not args.typ_only:
            compile_typ(typ, pdf)
            entry["pages"] = finalize_pdf(pdf)
            entry["pdf"] = str(pdf)
            entry["bytes"] = pdf.stat().st_size
        report[key] = entry
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
