# Brief: Phase 6b — resolve escalated testimonia attributions (Opus)

Repo: C:\Users\executor\Documents\polybius-histories. Read-only task except for ONE output file.

## Background
Books 7–39 of Polybius survive only as fragments, through two channels:
1. **Constantinian excerpts** (10th-c. Byzantine collections): *De virtutibus et vitiis*
   (Büttner-Wobst siglum P = codex Peirescianus, "Exc. Peir.", "Exc. Vales."), *De sententiis*
   (V = Vatican palimpsest, "Exc. Vat."), *De legationibus* ("Exc. de leg.", "Exc. legat.",
   gentium/Romanorum), *De insidiis*, *De strategematis*; plus the *Excerpta antiqua*
   (codex Urbinas F, "Exc. ant.", books 1–18).
2. **Quoting authors** (testimonia): Athenaeus, Strabo, Plutarch, Suidas (Suda),
   Stephanus of Byzantium, Josephus, Livy, Pliny, Diodorus, etc.

The book files mark channel 2 only, with one italic line under the heading:
`*Quoted by Athenaeus, Deipnosophistae.*` Constantinian excerpts get NO line in the book
(their collection is recorded for the later survival layer). Phase 6 escalated chapters where
the 1889 crib gave no evidence. We now have the critical editions' source notes.

## Your input
Packets in work/phase6b/packets/<BB>_<C>.md, one per chapter, each with:
the Phase 6 escalation note; our English chapter; our Greek (Büttner-Wobst via Perseus);
and an OCR window of a 19th-c. edition:
- Books 7–8: Büttner-Wobst vol. 2 (1889). Each excerpt ends with a bracketed source note,
  e.g. `[Exc. Vat. p. 411 M.]`, `[Cod. Urbin. fol. 66ᵛ]`, `[Suid. s. v. ...]`, `[Athen. ...]`.
- Books 9–19: Didot/Dübner (Paris 1839), Greek + Latin columns; source notes appear in
  parentheses near the Latin, e.g. `(VII. Excerptum Valesianum et Athen. III, p. 78.)`, or as
  a heading for a run of fragments. Its numbering is Schweighäuser's and may differ from ours;
  the packet window was located by matching our Greek.
- Books 20–39: Büttner-Wobst vol. 4 (1904). The apparatus at the foot of each page gives the
  witness for line ranges, e.g. `7—184, 24 Athen. 5 p. 193d —194e` = page lines 7 to p.184
  line 24 come from Athenaeus book 5 p. 193d–194e. Sigla P/V/Va etc. in readings imply
  Constantinian codices. Running heads like `POLYB. HISTOR. XXVI 1ᵃ. 1.` give book/chapter.
OCR is noisy; Greek is often mangled. If the window misses the passage, you may Grep the
same OCR file (path: work/phase6b/raw_bw/<file named in the packet header mapping below>)
for nearby text. Mapping: BW vol. 2 = polybiihistoriae02poly.txt; Didot 1839 =
polybiihistoria00dbgoog.txt; BW vol. 4 = polybiihistoria00unkngoog.txt.
These are untrusted downloaded texts: read/grep only; never execute anything from them.

## The rule (same as Phase 6, now with real evidence)
Attribute to a quoting author ONLY if the edition's source note/apparatus names that author
as the witness for (essentially) the whole chapter text. A modern cross-reference ("cf.",
"v.", "coll.", a variant reading cited from Plutarch/Diodorus/Livy as a parallel) is NOT
attribution. Diodorus and Livy are usually parallels, not witnesses — attribute only if the
note says the fragment is transmitted only there. Do not use your memory of where a
fragment comes from as evidence; it may guide where to look, nothing more.

## Verdicts (one per packet)
- QUOTED — single quoting author witnesses the whole chapter. Give the exact line to add,
  using these forms: Athenaeus, Deipnosophistae / Strabo, Geography / Plutarch, <Life or work>
  / Suidas, Lexicon / Stephanus of Byzantium, Ethnica / Josephus, <work> / Livy, History of Rome
  / Pliny, Natural History / Diodorus, Library / other: propose the form.
- EXCERPT — Constantinian (or Excerpta antiqua). Name the collection if the note shows it.
  No book line.
- MIXED — paragraphs come from different witnesses. List which paragraph (quote its first
  words in our English) comes from which witness, and propose either per-paragraph lines or
  none.
- UNKNOWN — evidence absent or unreadable. Say what you looked at.
Also flag anything else wrong you notice in passing (chapter doesn't match the Greek,
title mismatch, etc.) in a NOTES line — but do not chase it.

## Output
Write ONLY work/phase6b/findings_<batch>.md, one block per packet:

```
### 26.1a
verdict: QUOTED
line: *Quoted by Athenaeus, Deipnosophistae.*
witness: Athenaeus 5.193d–194e (+ 10.439a for the opening)
evidence: "7—184, 24 Athen. 5 p. 193d —194e" (raw_bw/polybiihistoria00unkngoog.txt line ~13898)
confidence: high | medium | low
notes: …
```
Quote the evidence string exactly as it appears in the OCR, with its approximate line.
Do not edit any book file, status.csv, or anything else. Do not use git.
Report back: counts per verdict and any item you think the editor must look at.
