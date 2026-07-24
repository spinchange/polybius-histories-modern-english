# Polybius — Extant Works Modern Translation Plan

**Goal:** Produce a readable modern-English translation of the full extant Greek corpus of Polybius available from stable digital sources, starting from the already completed Books I–II and extending through the remaining surviving books and fragment collections.

**Current Status:**
- Completed and assembled: `Polybius_Histories_Books_I_II_modern_English.md`
- Verified chapter coverage:
  - Book 1: chapters 1–88
  - Book 2: chapters 1–71
- Machine-readable Greek source already confirmed available at least through book 39 from Perseus.

---

## Scope Definition

This project should distinguish between:

1. **Entire original work** — impossible, because much of Polybius is lost.
2. **Entire extant works / extant Histories corpus** — possible in principle, using surviving complete books and surviving fragmentary material.

Working default scope:
- Books 1–5 where text is substantially extant
- Surviving later books and excerpted/fragmentary material available in digital Greek sources
- Any explicitly labeled fragment sections if a machine-readable Greek witness is available

---

## Phase 1: Source Audit

### Task 1.1: Enumerate digital Greek witnesses
- Confirm available books from Perseus
- Confirm whether fragment sections are available in machine-readable Greek
- Record any gaps, broken chapters, or malformed pages

### Task 1.2: Define canonical project scope
- Mark books/sections as:
  - `complete`
  - `fragmentary`
  - `unavailable digitally`
- Create a manifest listing every book/section to be translated

### Task 1.3: Identify fallback sources
- If Perseus lacks fragment sections or specific chapters, check alternate public-domain digital witnesses
- Use fallback only where it preserves Greek source access

Deliverable:
- `extant_corpus_manifest.json`
- `SOURCE_AUDIT.md`

---

## Phase 2: Corpus Extraction

### Task 2.1: Generalize the extraction pipeline
- Extend the current extraction script beyond Books I–II
- Save per-book and per-chapter source files under `source/`

### Task 2.2: Normalize structure
- Use consistent markdown structure:
  - heading
  - Greek source
  - old English reference crib
- Flag chapters with obvious truncation or source corruption

### Task 2.3: Chunking strategy
- Split large books into translation-safe ranges
- Keep chunk sizes small enough for reliable automated translation

Deliverables:
- `source/book_XX/chapter_YY.md`
- `chunks/` or `chunks_small/` for all remaining books
- updated summary manifest

---

## Phase 3: Translation Production

### Translation rules
- Translate from Greek into clear modern English
- Use older English only as a crib, not as final phrasing
- Preserve chapter headings and bracketed section numbers
- Do not paraphrase away fragmentary or difficult passages
- Keep fragment labels explicit where source tradition is fragmentary

### Production order
1. Book 3
2. Book 4
3. Book 5
4. Books 6 onward in surviving order
5. Fragment collections

### Quality control
For each chunk:
- verify file exists
- verify headings preserved
- verify no Greek/reference text leaked into output
- spot-check for obvious crib-copying or unmodernized diction

Deliverables:
- `translations/book_XX_*.translation.md`

---

## Phase 4: Assembly

### Task 4.1: Per-book assembly
- Merge ranges into one file per book
- Verify chapter continuity

### Task 4.2: Corpus assembly
- Build one combined file for the extant Histories corpus
- Optionally also build a split multi-file edition

### Task 4.3: Edition metadata
- Add preface explaining:
  - source basis
  - what “extant” means here
  - which books are complete vs fragmentary
  - which parts remain reconstructed from surviving witnesses only

Deliverables:
- `Polybius_Histories_Book_III_modern_English.md`, etc.
- `Polybius_Histories_Extant_Works_modern_English.md`
- `EDITORIAL_NOTE.md`

---

## Phase 5: Packaging

Optional output formats:
- Markdown master edition
- DOCX
- PDF
- ZIP bundle with per-book files and manifest

---

## Recommended Immediate Next Step

Proceed with **Books III–V next**, because they are the most valuable continuation and likely the most straightforward before tackling later fragmentary material.

Suggested next concrete deliverable:
- `Polybius_Histories_Books_III_V_modern_English.md`

---

## Success Criteria

The project is complete when:
- all digitally available extant Greek sections in scope have been translated
- every translated section is assembled into ordered book files
- one master file exists for the extant corpus
- the edition clearly labels complete vs fragmentary materials
