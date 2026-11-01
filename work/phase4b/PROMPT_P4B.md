# Phase 4b follow-up tasks (read the section for YOUR task id only)

General: the Greek (source/book_NN/chapter_MM.md, section "## Greek" only — the "English Reference"
crib is an 1889 translation and may describe a different chapter) is the only authority.
Register: modern, plain, dignified English; "Fortune" for τύχη; lacunae marked `[...]` only;
curly quotes ’ “ ”. No stylistic changes. Do not use git. Do not touch files other than those named.

## Task S1 / S2 / S3 — small corrections (you EDIT the named book files with the Edit tool)
Locate each passage by Grep on distinctive English words; read ~40 lines; check the Greek; make the
SMALLEST edit that fixes the stated problem. If the current English no longer has the problem, or the
Greek does not support the proposed correction, do NOT edit — report "NO CHANGE" with the reason.
Write a log of every edit (file, chapter, old text, new text) or NO CHANGE to
work/phase4b/edits_<your id>.md.

S1 (Polybius_Histories_Book_01, 03, 08, 10 _modern_English.md):
- 1.22: the closing bracketed sentence "[the Romans watched for the right moment to fight at sea.]" is
  invented text over a break; the Greek stops at "πα". Replace it with `[...]` after "Having made use
  of such a preparation,".
- 1.37: τύχη is rendered with lowercase "fortune"; make that instance "Fortune".
- 3.53/3.54: καὶ συνάψαι πρὸς τὴν παρεμβολήν ("rejoined the camp") is rendered at the end of 3.53 AND
  at the start of 3.54. Check which chapter the Greek puts it in; remove the duplicate.
- 10.15/10.16: Greek ch. 15 ends mid-sentence; the English completes the sentence at the end of 15 and
  repeats it at the start of 16. Remove the duplication (keep it where the Greek has it).
- 8.24: the chapter heading ("The Gallic King, Cauarus") does not fit the chapter's content (Tarentum
  material). Retitle from the translated content: `## Book 8 Chapter 24: <3–8 words>`, title case,
  no terminal punctuation, unique among Book 8 headings.

S2 (Polybius_Histories_Book_14, 26 _modern_English.md):
- 14.6/14.7: after the 14.6 fix the English of 14.7 opens "[...] and link up with him" — the "and" no
  longer fits. Make it grammatical with the end of 14.6 (e.g. "would link up with him"), adding no
  content the Greek lacks.
- 26.1: "knucklebones made from gazelle horn" — ἀστραγάλους δορκαδείους means gazelle knucklebones, no
  horn. Fix.

S3 (Polybius_Histories_Book_36, 39 _modern_English.md):
- 36.5: "but had spoken only when they were surrendering themselves" seems to misread ἀλλὰ καθ᾽ ὃν
  καιρὸν ἐδίδοσαν τὴν ἐπιτροπήν (they should have deliberated back when they surrendered). Check; fix.
- 36.14: the Malleolus clause — the Greek says he seemed the dullest of all Romans, not that all
  Romans thought him the dullest. Fix.
- 36.15: the Bithynians clause — the Bithynians are the ones who least want this in their kings. Fix.
- 39.6: "although he had for a long time held great authority" mistranslates μέγαν καιρὸν; render
  roughly "although he had great opportunity and great power among the Greeks" (verify against the
  Greek; give the faithful rendering).
- 39.7: the Greek reads Πτολεμαῖος ὁ τῆς Συρίας βασιλεύς. Render so readers are not confused, e.g.
  "Ptolemy, king of Egypt, who had just become king of Syria as well" (Philometor took the Syrian crown
  in 145 BC). Check that the chapter's context supports this; if it does not, make NO CHANGE and say why.
  Also keep 39.7 consistent with any other mention in Book 39.

## Task H — held items (NO book edits)
Your input is work/phase4b/human_in/h_NN.md: for each item, the held entry (current English quote,
problem, an earlier proposed fix), the whole Greek chapter and the whole current English chapter.
For each item write ONE recommended rendering for exactly the "current" quote text (the span that
would be replaced), faithful to the Greek, marking real gaps/corruption with `[...]` and inventing
nothing; and a one-line reason (≤30 words) that tells the translator what choice you made if the
Greek is ambiguous. Output ONE JSON file work/phase4b/human_out/h_NN.json:
[{"id":"F0133","recommended":"<replacement for the current quote>","reason":"<one line>"}, ...]
Every item id in your batch must appear. Valid JSON only.

## Task A — attribution sort (NO book edits)
Your input is work/phase4b/attr_in/a_NN.md: chapters (Books 7–39) that a clerk could not attribute.
Most Polybius fragments in these books come from Byzantine excerpt collections (the Constantinian
excerpts: de Legationibus, de Virtutibus et Vitiis, de Sententiis, de Insidiis...), which copy Polybius
verbatim and are NOT testimonia. A chapter is a real QUOTATION only when a named later author is the
source of that text: e.g. Athenaeus (Deipnosophistae), Strabo (Geography), Plutarch, Stephanus of
Byzantium (Ethnica), Suidas (Lexicon), Josephus, Pliny, Livy/Diodorus where they are cited as the
immediate source of THIS passage. Evidence must be in the Greek text or the source file itself
(read source/book_NN/chapter_MM.md including the crib, which may NAME the source — but a scholar's
"cf." cross-reference is not evidence). Classify each chapter as:
  QUOTATION (give author, work, and the exact words of evidence),
  EXCERPT   (Constantinian/anonymous excerpt; no line to be added),
  UNKNOWN   (cannot tell; no line to be added).
When a chapter mixes sources, classify UNKNOWN. Do not guess an author. Output ONE JSON file
work/phase4b/attr_out/a_NN.json:
[{"book":8,"chapter":"38","class":"QUOTATION|EXCERPT|UNKNOWN","author":"Suidas","work":"Lexicon","evidence":"<exact words>"}, ...]
Every chapter in your batch must appear. Valid JSON only.

Final reply for every task: ≤5 lines.

## Task SEAM — sanity-check proposed chapter-break moves (NO book edits)
Your input is work/phase4b/seam_in/s_NN.md. Background: chapter numbers were added by later editors, so
a chapter break may cut a sentence while NOTHING is missing from the Greek. For each SEAM we propose to
move the unfinished sentence from the end of chapter N to the start of chapter N+1 (so the break falls
on a sentence boundary), joining it to the continuation and deleting the `[...]` marks at the seam.
For each seam check, from the BEFORE/MOVED/AFTER text and (briefly) the Greek at the break
(source/book_BB/chapter_CC.md, "## Greek" section, end of ch N and start of ch N+1):
 1. The Greek really runs on across the break (no `*`/`**` gap marker there). If the Greek has a real
    lacuna at the break, verdict SKIP (note "true lacuna").
 2. The MOVED text is exactly ONE unfinished sentence (no complete sentence inside it). If it contains
    a complete earlier sentence, verdict SKIP (note "moved text spans several sentences").
 3. The AFTER start of ch N+1 reads as one grammatical sentence with no repeated or lost words. If the
    English of ch N already completed the sentence and ch N+1 repeats it, or the join is ungrammatical,
    verdict FIX and give `new_head_para`: the full corrected text of ch N+1's first paragraph
    (only the BEFORE start text is available to you truncated; read the first paragraph in full from the
    book file with Grep/Read: Polybius_Histories_Book_BB_modern_English.md). Change as little as possible.
 4. Otherwise verdict OK.
Output ONE JSON file work/phase4b/seam_out/s_NN.json:
[{"key":"3:115>116","verdict":"OK|FIX|SKIP","new_head_para":"<only for FIX>","note":"<≤20 words>"}, ...]
Every SEAM key in the batch must appear. Valid JSON only. Do not edit book files. Reply in ≤3 lines.
