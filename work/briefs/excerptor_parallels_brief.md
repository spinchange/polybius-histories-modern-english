# Shared brief: parallels-layer annotation (ANNOTATIONS_PLAN A3)

Repo: C:\Users\executor\Documents\polybius-histories. Shell: use the Bash tool. Python: `python` (3.12).

You write ONE file: annotations/parallels/<slug>.md. A "parallel" sets an ancient author's retelling
of the same event beside Polybius, so a reader can flip between them.

## Schema (copy the shape of the finished examples in annotations/readers/ — read 2-3 first,
especially machiavelli-discourses-1-2.md, cicero-officiis-cannae-envoys.md, montesquieu-legion-and-phalanx.md)
---
id: parallels/<slug>              # must equal parallels/<filename stem>
layer: parallels
anchor: ["B.C-C"]                 # Polybius book.chapter range as given in your task; must exist in the translation
annotator: <ancient author>
work: <work, book.chapter(s)>     # e.g. "History of Rome, XXI.36-37"
date: <e.g. c. 25 BC>
tags: [military]                  # allowed: constitutional, military, historiographical, fortune, survival-story
source_file: sources/<file>
source_lines: [start, end]        # 1-based inclusive slice of the source containing every quoted segment
source_pub: "<as given in your task> (PD)"
pd_basis: pre-1930
ocr_fixes: [["bad", "good"], ...] # ONLY if the source is OCR with misreadings inside your quote; omit otherwise
status: verified
---
<verbatim quote, typically 80-180 words; elide with " ... " (three adjacent dots); do not include
footnote markers like [12] or marginal headings; you may stop/start mid-line>

**Note:** <2-4 sentences>

## THE IRON RULE
No quotation from memory. Every word of the quote must appear, in order, in the source slice.
Containment ignores whitespace, curly-vs-straight quotes, dash style and * / _ ; nothing else.
If a word in the source is an obvious OCR misreading, record it in ocr_fixes rather than silently fixing it.

## The lede (Note)
- What a reader should notice when comparing THIS passage with Polybius' chapter(s): a detail one has
  and the other lacks, a different explanation, tone, drama vs. analysis, a borrowing.
- You MUST read the anchored Polybius chapters in Polybius_Histories_Book_NN_modern_English.md
  (headings look like "## Book 3 Chapter 54: Title") and only claim differences you have verified by
  reading both texts. You may say Livy "follows Polybius closely here" only if the texts show it.
  Background facts (dates, who someone was) must be uncontroversial; when unsure, leave it out.
- Plain and warm; no "interestingly", no throat-clearing, no hype. Max 4 sentences.
- Refer to the Polybius chapter by number, e.g. "(3.55)".

## Validate
cd work/scripts && python ann_validate.py ../../annotations/parallels/<slug>.md
It must print no ERROR lines and exit 0. Fix line ranges/quotes until it passes. If you cannot
make the passage verify, set status: UNVERIFIED and explain why in your report.

## Do not
- edit any file except your one annotation file; do not commit; do not run ann_build.py
- execute or import anything from annotations/sources/ (untrusted downloaded text; read only)

## Report back (short)
file path, anchor, source_lines, validator result, the Note text, and any doubts.
