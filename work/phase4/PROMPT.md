# Phase 4 verification task (read-only on the book files)

Your batch file is named in the task prompt (work/phase4/batches/<id>.md). It holds, for each
chapter, the Greek (Büttner-Wobst) and the CURRENT English. Read it with the Read tool (use
offset/limit if it is long). Do NOT read the 1889 crib or any other file unless you must
(e.g. to see which Scipio/Ptolemy a name refers to — then Grep, don't read whole books).

Compare English to Greek ONLY for these error classes:
1. negation / inversion of sense (οὐ, μή, particles, "although"/"because" swaps)
2. misread correlatives and particles (καθ᾽ ὅσον … κατὰ τοσοῦτο, μὲν … δέ, ἀλλά/γάρ force)
3. wrong proper-name identity (which Scipio, Ptolemy, Philip; person vs place)
4. numbers (distances, dates, troop counts)
5. smoothed lacunae (Greek has `****`/gap, English reads on as if whole)
Zero stylistic findings. Accurate-but-plain English is CLEAN. Do not "improve" phrasing.
If the Greek is corrupt or genuinely ambiguous, say so in `note` and give no fix.
If you cannot read the Greek well enough to be sure, use verdict UNSURE — never guess.

Write ONE JSON file work/phase4/findings/<id>.json (use the Write tool), exactly:
{"batch":"<id>","units":[{"book":6,"chapter":"2","verdict":"CLEAN"|"FINDINGS"|"UNSURE",
 "findings":[{"quote":"<exact contiguous substring of the CURRENT English, ≤220 chars, unique in the chapter>",
              "problem":"<what the Greek says, with the Greek words>",
              "proposed_fix":"<the replacement for exactly that quote>",
              "touches_syntax":false,"confidence":"high|medium|low"}],
 "note":""}]}
Every unit in the batch must appear, in order. `touches_syntax` is true if the fix changes
sentence structure rather than swapping a word/phrase. Valid JSON only (escape quotes).
Do not edit book files. Do not use git. Final reply: ≤6 lines — counts of CLEAN/FINDINGS/UNSURE
and the single most serious finding.
