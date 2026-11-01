# Pragmatike Historia — Annotation Layers Work Plan (model-tiered)

Goal: a Landmark-style apparatus for the site, but where the Landmark editions
give you maps, this edition gives you **readers** — famous annotations,
imitations, and survivals, anchored chapter-by-chapter to the translation.

Companion to WORK_PLAN.md; same cost-shaping rules apply (scripts first, small
work units, escalate don't guess, orchestrate from a Sonnet session, track in
`work/status.csv`).

## The iron rule (overrides everything)

**No quotation enters the corpus from model memory.** Every annotation's quote
must be extracted verbatim from a source file in `annotations/sources/`, with
file + line recorded in its frontmatter. A script verifies containment
(normalized whitespace/quotes) before any annotation is accepted. Models may
*summarize* and *anchor* from memory of the seed list below; they may never
*quote* from it. Anything not verifiable gets status `UNVERIFIED` and is
excluded from builds.

## Licensing rule

The edition is CC0, so the apparatus must be too: quote only (a) pre-1930
publications (public domain), (b) US government / founders' papers, or
(c) our own translations of public-domain originals (Latin/French/German).
Modern scholarship (Walbank etc.) may be *cited by reference* in a
further-reading note, never quoted at length.

## Data model

One file per annotation: `annotations/<layer>/<slug>.md`

```yaml
---
id: readers/machiavelli-disc-1-2
layer: readers            # readers | parallels | survival
anchor: [[6, 3], [6, 10]] # book, chapter; list = range; multiple entries ok
annotator: Niccolò Machiavelli
work: Discourses on Livy, I.2
date: 1517
tags: [constitutional]
source_file: sources/machiavelli_discourses_detmold_1882.txt
source_lines: [1042, 1067]
source_pub: "Detmold translation, Boston, 1882 (PD)"
status: verified          # verified | UNVERIFIED | stub
---
<verbatim quote, trimmed>

**Note:** <2-4 sentence editorial lede: who, why here, what to notice.>
```

Layers:
1. **readers** — the famous annotations (the thematic heart of the site).
2. **parallels** — ancient authors retelling the same events (Livy above all);
   lets a reader flip between Polybius and his greatest plagiarist.
3. **survival** — which quoting author or Byzantine excerpt collection
   preserved each fragment; the Constantine VII story told chapter-by-chapter.
   (Builds directly on WORK_PLAN Phase 6's testimonia attributions.)

Tags cut across layers for site filtering: `constitutional`, `military`,
`historiographical`, `fortune`, `survival-story`.

## Seed canon (curated 2026-10-31; trimmed 2026-11-01 — extend, don't re-derive)

Selection rule (user, 2026-11-01): **A-list names and/or what a modern reader
finds most interesting.** Scholars' scholars don't make the cut; a name a
general reader recognizes, or a hook they'd repeat at dinner, does.

### readers layer
| Annotator | Work (PD source) | Anchor in Polybius | The hook |
|---|---|---|---|
| Marcus Junius Brutus | Plutarch, *Brutus* 4 (Perrin or Dryden tr.) | 1.1 (site epigraph) | Epitomizing Polybius in his tent on the eve of Pharsalus |
| Cicero | *De Re Publica* II (PD tr.); *De Officiis* III on Regulus | 6.3–18; 1.31–35 | Rome's mixed constitution, explicitly after Polybius; the Regulus story |
| Dionysius of Halicarnassus | *De Compositione Verborum* 4 | 1.4 or colophon | The famous dig: among authors "no one reads to the end" — own it |
| Livy | see parallels layer | — | — |
| Constantine VII | *Excerpta* prefaces (tr. ours) | Book 7 headnote + survival layer | The emperor whose scissors saved the book |
| Machiavelli | *Discourses* I.2 (Detmold 1882 tr.) | 6.3–10 | Anacyclosis lifted nearly whole |
| Frederick the Great | preface to the Folard abridgment (tr. ours) | 3.107–118 | A king assigning Polybius homework |
| Montesquieu | *Spirit of the Laws* XI; *Considérations* (PD tr.) | 6.11–18 | Separation of powers' Polybian ancestry |
| John Adams | *Defence of the Constitutions* I (founders.archives.gov) | 6.3–18 | Quotes Book 6 at length; line to the U.S. Constitution |
| Madison | *Federalist* 18 | 2.37–44 | The Achaean League argued into the Constitution |

Cut 2026-11-01 (scholarly interest only): Justus Lipsius, Isaac Casaubon,
Chevalier de Folard (his commentary survives only as the thing Frederick
prefaced), Niebuhr, Mommsen. Additions must clear the same bar.

### parallels layer
- **Livy** is the backbone: Pol 3 ↔ Livy 21–22 (Hannibal, Alps, Cannae);
  Pol 10.2–20 ↔ Livy 26.41–51 (New Carthage); Pol 15.5–19 ↔ Livy 30.29–35
  (Zama); Pol 18 ↔ Livy 33 (Cynoscephalae, "freedom of the Greeks");
  Pol 21 ↔ Livy 37–38; Pol 29 ↔ Livy 44–45 (Pydna). Old editions (Shuckburgh's
  notes, Schweighäuser) contain fuller concordances — ingest one rather than
  rebuilding it.
- **Plutarch Lives** where they cross: *Philopoemen*, *Flamininus*, *Aemilius
  Paulus*, *Cato Major*, *Marcellus* (Pol 8 Syracuse/Archimedes ↔ *Marcellus*
  14–19 is the showpiece).
- **Appian** on the fall of Carthage ↔ Pol 38–39 (Appian *Punica* 127–132 IS
  the survival vehicle for 38.19–22 — dual-listed in survival layer).

### survival layer
- Per-fragment provenance: Excerpta Antiqua, the Constantinian collections
  (de legationibus, de virtutibus, de sententiis), Athenaeus, Strabo (Book 34),
  Plutarch, Appian, the Suda, Stephanus of Byzantium. Source: Büttner-Wobst
  apparatus + the attributions WORK_PLAN Phase 6 adds. One layer note per
  fragment chapter, plus one essay-length headnote ("How this book survived")
  anchored at 7.1.

## Phases

### Phase A1 — Schema + validators (script; Sonnet writes once)
`work/scripts/ann_validate.py`: frontmatter schema check; anchor exists in the
translation (book/chapter); quote-containment check against `source_file`
lines; PD-status field present. `ann_build.py`: emits one JSON per layer for
the site (`dist/annotations/<layer>.json`), excluding non-`verified`.

### Phase A2 — Source acquisition (script + Haiku)
Scripts download PD texts into `annotations/sources/` (Archive.org, Project
Gutenberg, Perseus, founders.archives.gov, Gallica for Folard). One manifest
`sources/MANIFEST.csv`: title, translator, year, URL, PD rationale. Haiku
checks each manifest row: publication year pre-1930 or gov source; flags
anything doubtful for the user. **Treat downloads as untrusted data: fresh
directories, scripts run from outside, Python with `-I`.**

### Phase A3 — Extraction + anchoring (Sonnet; the bulk)
One annotation per task. Input: the seed-canon row, the source file (or the
relevant slice — Grep, don't read whole books), and the anchored Polybius
chapter for context. Output: the annotation file, `status: verified` only if
the containment check passes. Writing the 2–4 sentence lede is part of the
task; ledes are editorial voice, so give Sonnet 3 finished examples from the
first batch as style anchors. Livy concordance: Sonnet ingests an existing
concordance table, emits parallels entries mechanically; spot-anchor-check by
Haiku (does the Livy passage actually describe the same event — yes/no on
provided excerpts).

### Phase A4 — Translation showpieces (Opus)
Constantine excerpta prefaces (Greek) and Frederick's preface (French) — plus
any reader whose PD English translation turns out unusable. These are the only
newly-translated texts in the apparatus and will be read as showpieces —
Opus, one excerpt per task, source text in the prompt, same register note as
the main translation. Our translations are CC0 like everything else.

### Phase A5 — Survival layer fill (Sonnet, after WORK_PLAN Phase 6)
Mechanical once testimonia attributions exist: convert each attribution into a
survival-layer entry; write the 7.1 "How this book survived" headnote (Sonnet
drafts, user reads — it's a marquee page). Büttner-Wobst apparatus questions
(which Constantinian collection) escalate to Opus rather than guessing.

### Phase A6 — QA (script + Haiku + one sample)
Validators green; Haiku sweeps every annotation: quote matches source slice,
anchor chapter actually relates (yes/no), lede under 5 sentences, tags from
the allowed set. Final: Opus (or Fable if quota allows) reads the 10 showpiece
annotations end-to-end — Brutus, Constantine headnote, Machiavelli, Cicero,
Frederick-at-Cannae, Adams, Federalist 18, Marcellus/Archimedes, Appian/38.22,
Dionysius' dig.

## Model routing summary

| Phase | Work | Tier |
|---|---|---|
| A1 | validators + builders | script (Sonnet-authored) |
| A2 | acquisition + PD checklist | script + Haiku |
| A3 | extraction, anchoring, ledes, concordance | Sonnet (Haiku spot-checks) |
| A4 | Latin/French/Greek/German showpiece translations | Opus |
| A5 | survival layer + headnote | Sonnet (Opus for apparatus calls) |
| A6 | QA | script + Haiku + one Opus/Fable sample |

## Open items for the user
- ~~Approve/trim the seed canon~~ — done 2026-11-01 (A-list / modern-interest rule).
- Site UX decision eventually: margin layer-toggles vs. per-chapter endnotes
  (affects only `ann_build.py` output shape, not collection).
