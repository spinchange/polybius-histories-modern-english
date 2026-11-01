# Phase 4 confirm/finalize task

Your batch file is work/phase4/confirm/<id>.md. For each chapter it gives the Greek, the CURRENT English,
and candidate findings (from an earlier pass, which may be wrong — the Greek is the only authority).
For EACH finding decide, from the Greek, whether the English really has the error; then write the
exact final replacement text.

Verdicts: ACCEPT (the candidate fix is right as written, after convention normalization),
REVISE (error is real but the proposed fix is wrong/incomplete — give your own), REJECT (English is
acceptable or the candidate misreads the Greek), HUMAN (corrupt/ambiguous Greek, or a genuine
editorial choice the translator must make — give your best fix anyway).

Rules for the replacement (`fix`):
- It replaces EXACTLY the candidate's `quote` (a contiguous substring). Keep the replacement as
  close to the original wording as the correction allows. Fix sense only; no stylistic changes.
- Lacunae: the Greek's `*`/`**`/`***` marks missing text. Mark it with the project convention `[...]`
  (never "[gap]", "[text missing]", "[Text breaks.]"). Never invent words to fill a gap; if the
  English supplied words over a gap, remove them and put `[...]` — unless the words are clearly
  recoverable from the surrounding Greek.
- Register: modern, plain, dignified English; "Fortune" for τύχη. Curly quotes ’ “ ” only.
  Names: Gauls (Italy/Europe) / Galatians (Asia Minor); Spartans in narrative; modern river names
  (Ebro, Po, Danube, Rhone). Keep existing name spellings unless the Greek proves them wrong.
- If two findings in one chapter overlap, make their fixes consistent and non-overlapping
  (the later one must not quote text the earlier one changes).

Output: write ONE JSON file work/phase4/confirm_out/<id>.json (Write tool):
[{"id":"F0001","verdict":"ACCEPT|REVISE|REJECT|HUMAN","fix":"<final replacement or empty if REJECT>","reason":"<≤25 words>"}, ...]
Every finding id in the batch must appear. Valid JSON only. Do not edit book files; do not use git.
Final reply: ≤4 lines — counts per verdict and the single most important HUMAN item.
