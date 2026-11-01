# Phase 6 rules (STYLE_SHEET.md does not exist yet — these ARE the decided rules)

You own the whole book file(s) named in your prompt and nothing else. Work from
`work/phase6/book_NN.md` (script-generated). Never rewrite translation prose beyond
the minimal edits below. Never compose bridging or explanatory text of your own,
except the two headnote/attribution forms specified here. Locate text with Grep on
quoted context — line numbers shift as you edit. Do not use git.

## A. Seams (sections A, B, C of your work file)
- Bracket-repeat (`[Having made these preparations,] …` at a paragraph start, repeating the
  previous chapter's closing words): read the previous chapter's tail and this head; if it
  is a duplicate, delete the bracketed repeat. If it is NOT a duplicate, remove only the
  brackets. Unsure → ESCALATE.
- Paragraph that ends without terminal punctuation before a heading (truncated sentence):
  append ` [...]` (the lacuna convention). Never finish the sentence yourself. If it only
  looks truncated because it ends in a quotation/closing bracket/footnote, leave it.
- Stray markers (`[7;8]`, `IV. On` etc.): delete the marker. Leading crib rubric such as
  `III. On the Other Errors of Timaeus` or `VI. Gaul`: delete the Roman numeral AND the rubric
  phrase, but only if what remains is a grammatical sentence of Polybius/the quoting author;
  otherwise ESCALATE.
- Headings missing a preceding blank line: add the blank line.
- Attached ellipses (`[snow]...`, `word...`, `…`): convert to the single convention `[...]`
  when it marks a gap in the text; if it is rhetorical (trailing off in speech), leave it.
- Unbalanced curly quotes (section B): most are legitimate multi-paragraph speeches or
  treaty texts (an opening quote with no close at paragraph end is correct typography in
  that case). Fix only a clear typo (a missing or doubled mark in a single-paragraph
  quote). Do not touch the rest.

## B. Testimonia attributions (section D, Books 7–39 only)
- Format: directly under the heading, one blank line, then
  `*Quoted by <Author>, <Work>.*`, one blank line, then the text. Italic, one line, final
  period. Authors/works: Athenaeus, *Deipnosophistae*; Strabo, *Geography*; Plutarch,
  *<title if evident>*; Stephanus of Byzantium, *Ethnica*; Suidas, *Lexicon*;
  Pliny, *Natural History*; Diodorus, *Library*; Josephus, *<work if evident>*.
  Write the work title without asterisks inside the italic line (the whole line is italic).
  e.g. `*Quoted by Athenaeus, Deipnosophistae.*`
- Attribute ONLY when the evidence shows that author actually quoting/citing Polybius
  for this passage (e.g. the Greek says `Ἀθήναιος…`, or a Strabo passage introduced as
  `Polybius says…`). A scholar's cross-reference in the 1889 crib ("cf. Plutarch,
  Is. et Osir. 23") is NOT attribution. English-says-pattern alone is NOT evidence.
- Mixed chapters (paragraphs from different witnesses; decided 2026-11-01): put the line
  before each quoted paragraph instead of under the heading. Such a line governs that one
  paragraph unless it states a longer scope: `*Quoted by Suidas, Lexicon (this and the next
  paragraph).*` Unmarked paragraphs there are Constantinian excerpts. Byzantine excerpt
  collections (and Wescher's siege codex) never get a line. Further forms in use: Livy,
  *History of Rome*; Hero of Byzantium, *Poliorcetica*; Harpocration, *Lexicon of the Ten Orators*.
- No evidence → do NOT guess. Append an ESCALATE row (see logging) and move on.
- Voice-switch sentences inside a quoting author's text ("Polybius says: I have already…"):
  italicize the frame words only (`*Polybius says:*`), keep the quotation roman.
- The 1889 crib may be used for the attribution ONLY, never for content.

## C. Ethnonyms (section E)
- Gauls/Galatians: peoples in Italy and Europe are "Gauls" ("Gallic"); peoples in Asia
  Minor (the Galatians of Phrygia, Gallograeci, Tolistobogii, etc.) are "Galatians".
  "Celts"/"Celtic" disappears from narrative (→ Gauls) EXCEPT where Polybius is making an
  explicitly ethnographic point (Book 2's excursus on the peoples of Gaul may keep ONE
  framing mention: e.g. "the Gauls, called Celts by the Greeks"). Do not touch
  "Celtiberians", "Celtica" as a place name when it is a region and not a people, or any
  proper name. If a replacement would produce "Gauls and Gauls" or "Gauls, also called
  Gauls", repair minimally or ESCALATE.
- Spartans/Lacedaemonians: "Spartans" in narrative; keep "Lacedaemonians" only in
  formal/diplomatic contexts (treaties, embassies, decrees, official self-description,
  "the Senate of the Lacedaemonians" in a letter). Adjective: "Lacedaemonian" → "Spartan"
  when narrative. Leave Laconia/Laconian alone. In ambiguous cases leave it and note
  `UNSURE` in the log.
- Edit by minimal word replacement only. Keep capitalization and article ("a Celtic army"
  → "a Gallic army").

## D. Logging (mandatory)
Append one line per touched chapter (or per ESCALATE/UNSURE item) to `work/status.csv`:
`6,BOOK,CHAPTER,ACTION,VERDICT,"NOTES"` where BOOK is a plain integer (no zero pad),
ACTION ∈ {seam, quotes, ellipsis, rubric, attribution, ethnonym, headnote, note},
VERDICT ∈ {done, ESCALATE, UNSURE}, and NOTES is double-quoted (double any inner quote).
Append with shell `>>`; never rewrite the file. Final reply: a compact summary + every
ESCALATE/UNSURE with chapter and reason. No more than ~25 lines.

## E. Whole-book extras (only if your prompt assigns them)
- Headnote form: one italic paragraph placed between the line `Modern English translation of
  the Greek text.` and the first `## Book` heading, blank lines around it.
