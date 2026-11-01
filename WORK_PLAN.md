# Polybius Edition — Remediation Work Plan (model-tiered)

Goal: take the translation from "good draft" to print/site-ready, spending the
minimum on model tokens. Findings below were verified in the 2026-10-31 review
(see REVIEW notes at bottom); agents should NOT re-discover them.

## Cost-shaping rules (read first, applies to every phase)

1. **Scripts before models.** Anything expressible as a rule runs as Python with
   a diff report. Models only see what scripts can't decide.
2. **Small work units.** One chapter = one task. Agents must NOT read whole book
   files: Grep for the `## Book N Chapter M` heading, then Read with
   offset/limit. Source Greek is already per-chapter in `source/book_NN/chapter_MM.md`.
3. **Escalation, not ambition.** Each tier outputs a verdict or an edit, plus an
   `UNSURE` flag. Unsure items batch up to the next tier. Never let Haiku guess
   at Greek; never let Sonnet silently skip a hard call.
4. **Batch dispatch from a cheap session.** Orchestrate phases from a Sonnet
   session (`claude --model sonnet` or `/model sonnet`), spawning Haiku/Sonnet
   subagents. Reserve Opus for Phase 3/4 units only. No Fable until Phase 8.
5. **Git discipline.** One branch per phase (`fix/p1-mechanical`, …), commit
   after each phase with `run_epubcheck.ps1` green after rebuild.
6. **Tracking.** Each phase appends to `work/status.csv`
   (`phase,book,chapter,action,verdict,notes`). Scripts create `work/` on first run.

## Model routing summary

| Phase | Work | Tier | Unit count |
|---|---|---|---|
| 1 | Mechanical cleanup scripts | script (authored by Sonnet) | ~6 scripts |
| 2 | Alignment screen, Books 20–39 | Sonnet screen → Opus confirm | ~330 chapters screened, few confirmed |
| 3 | Retranslate substituted chapters | Opus | 4+ chapters |
| 4 | Accuracy verification vs Greek | Opus (famous set), Sonnet (rest, escalating) | ~60 Opus, ~1200 Sonnet |
| 5 | Chapter titles regenerate/fill | Sonnet write → Haiku check | ~700 titles |
| 6 | Testimonia attributions + seam repairs | Sonnet | ~150 units |
| 7 | Preface, metadata, style sheet | Sonnet draft → user review | 3 docs |
| 8 | Final QA | Haiku checklist → Fable/Opus sample | full corpus + 25 chapters |

---

## Phase 1 — Deterministic cleanup (zero model cost at run time)

Have ONE Sonnet agent write these scripts into `work/scripts/`, each with
`--dry-run` producing a diff report in `work/reports/`. Human (or Haiku, Phase 8)
samples the reports; then run for real.

1. `merge_paragraphs.py` — join paragraph breaks that fall mid-sentence: merge
   para N+1 into N when N does not end in `. ! ? : " ” —` or N+1 starts with a
   lowercase letter or `, ) ”`. Skip headings/blank-only. (~2,000 sites corpus-wide.)
2. `normalize_punct.py` — straight→curly quotes (report unbalanced counts per
   file instead of guessing); em-dash spacing to one convention (unspaced);
   `B. C. 215`→`215 BC` (match site style — confirm with user); full-width
   parens `（）`→`()`; standalone `***`/`****`/`...` lacunae → single
   convention `[...]`.
3. `normalize_names.py` — word-boundary replacements from the style sheet
   (decided — see Phase 7): Massanissa→Masinissa, Genthius→Gentius,
   Achaia→Achaea, Poseidonius→Posidonius, Paullus→Paulus, Tarantines→Tarentines,
   Carthagena→New Carthage, Heronymus→Hieronymus, Mightly→Mighty,
   MoagĕTes→Moagetes. Rivers modernize deterministically: `\bIber\b`→Ebro,
   `\bPadus\b`→Po, `\bIster\b`→Danube (Rhone is already modern corpus-wide; do
   NOT touch Iberia/Iberians). Celts/Gauls/Galatians and Lacedaemonians/Spartans
   are context-dependent — handled by Sonnet in Phase 6 under the Phase 7 rules,
   never by script.
4. `seam_report.py` — list for Phase 6: paragraphs matching `^\[[A-Z]` bracket-
   repeats; paragraphs ending without terminal punctuation followed by a
   heading; stray markers like `[7;8]`; headings missing a preceding blank line.
5. `heading_report.py` — all 1,310 headings with: has-title?, title-case
   violations, duplicates, Olympiad-rubric presence in source vs translation.
6. `rebuild_all.ps1` — regenerate book files if needed → `build_master_edition.ps1`
   → `build_epub.py` → `build_html.py` → `run_epubcheck.ps1`. Run at the end of
   every phase.

Known one-off fixes to fold into the seam list: `Book_03` lines ~395/445/479/
1043/1579, `Book_04:1435`, `Book_06:449` ("VI. On the Roman Military" leftover),
`Book_16:207` (footnote fused into heading), `Book_22:111` full-width parens,
`Book_35:121` stray ellipsis.

**Phase 1 outcome (done 2026-10-31, merged to main):**
- 1,527 merges, 118 name replacements, 37 files repunctuated; EPUBCheck green.
  Pre-cleanup seam baseline kept as `seam_report.baseline_precleanup.csv`
  (line numbers there match the one-off list above).
- **Book files are now canonical.** The per-book markdown files carry the
  Phase 1 edits; the Hermes-cache assemble/extract scripts are historical.
  Never regenerate book files from the cache — it would destroy all fixes.
- The verification dry-run overwrote the real diff reports before commit; the
  authoritative Phase 1 diff is `git diff 97e72d5..a1af861`. Before any rerun
  of the mutating scripts, scriptwright should make reports timestamped (or
  refuse to overwrite a non-empty report).
- Only standalone `***`/`****`/`...`/`…` became `[...]`; attached ellipses
  (`[snow]...`) were left for Phase 6 judgment.
- The unparseable heading `## II. Fragment of Uncertain Place in Book 20`
  goes to the Phase 6 seam queue.

## Phase 2 — Alignment screen, Books 20–39 (+ Books 7–19 cheaply)

Root cause on record: `source/` pairs Büttner-Wobst Greek with a Shuckburgh-
numbered 1889 crib; titles and occasionally whole translations followed the crib.

**Sonnet, one chapter per task**, prompt template:

> Read `source/book_NN/chapter_MM.md` (Greek + 1889 crib) and the translation of
> Book NN Chapter MM in `Polybius_Histories_Book_NN_modern_English.md` (Grep the
> heading, Read ~80 lines). Answer in JSON:
> `{"content_matches_greek": true|false|UNSURE, "title_matches_content": true|false,
> "evidence": "<names/anchors compared>", "proposed_title": "<3–8 words, only if title wrong>"}`
> The Greek is authoritative; the crib may describe a DIFFERENT chapter. Match on
> proper names and events, not style. If you cannot read the Greek well enough
> to be sure, answer UNSURE — do not guess.

- `content_matches_greek: false` or `UNSURE` → Opus confirms (same prompt).
  Confirmed false → Phase 3 queue.
- `title_matches_content: false` → Phase 5 queue with the proposed title.
- Known-bad, skip straight to Phase 3: **37.1, 38.2, 39.2, 39.3**.
- Known-bad titles (Phase 5 queue, whole ranges): Book 31 ch. 2–28, Book 30
  ch. 14–32, Book 25, Book 38, Book 39, 9.44; duplicates 7.2/7.3, 9.22/9.24,
  31.17/31.26.

## Phase 3 — Retranslation of substituted chapters (Opus)

One chapter per task. Input: the Greek from `source/`, the surrounding translated
chapters for voice (one before, one after), and the project register note:
"modern, plain, dignified English; Fortune for τύχη; no archaism, no slang."
Opus translates from the Greek only — the crib in the file is known to be the
WRONG content for these chapters; it must be ignored. Also remove the duplicate
crib-derived text where it shadows a real translation elsewhere (38.2 duplicates
38.8; 37.1 duplicates 36.9–10; 39.2 duplicates 38.6).

## Phase 4 — Accuracy verification pass vs Greek

Error class on record: sense inversions (negations, particles), misread
correlatives, wrong historical identities.

**Apply the already-verified fixes first (Sonnet, from this spec — no discovery):**
- **38.22**: Greek `οὐ φυλαξάμενον ὀνομάσαι τὴν πατρίδα σαφῶς` = Scipio *without
  holding back named his own fatherland plainly*. Current text says the opposite.
  Also `ὅ τι βούλοιτο ὁ λόγος` is the content of Polybius' QUESTION ("what he
  meant by the words"), not "whatever he intended by the remark".
- **6.56**: `καθ᾽ ὅσον … κατὰ τοσοῦτο` clause is about the Romans alone (they
  honor honest profit exactly as much as they revile illicit gain), not a
  Rome-vs-Carthage contrast.
- **Book 6 ch. 1 fragment**: `τὸ γὰρ ἀδύνατον ἐν τῷ ψεύδει μόνον οὐδ᾽ ἀπολογίαν
  ἐπιδέχεται` ≈ "only in a falsehood does impossibility not even admit of
  excuse" — current rendering is inverted nonsense.
- **35.13**: logic inverted — the point is that even nightfall barely ended the
  fighting.
- **35.89**: the volunteer for Spain in 151 BC is Scipio **Aemilianus**, not
  Africanus.
- **39.109 (CORRECTED in Phase 4b)**: the Greek reads Πτολεμαῖος ὁ τῆς Συρίας βασιλεύς. Do NOT drop "of Syria": in 145 BC Philometor took the Syrian crown at Antioch. Rendered "Ptolemy, king of Egypt, who had just become king of Syria as well" (39.7).
- **6.11 lacuna**: Greek has `****` after "the crossing of Xerxes"; mark the
  lacuna instead of smoothing the sentence.
- Minor Book 6 polish (from review): 6.319 "as they choose" (προθῶνται);
  6.441 "swells up" contradiction → "tends to gain more power than it should";
  νὴ Δία ×4 → "indeed".

**Then the discovery pass**, one chapter per task:
- **Opus tier (~60 chapters):** the famous set — Book 1.1–4, 62–64; Book 3.6–12,
  Alps 47–56, Cannae 107–118; Book 6 complete; 9.22–26; 10.2–20 (Scipio at New
  Carthage); 12.25a–28a; 15.6–19 (Zama); 18.28–32 (legion vs phalanx); 31.23–30
  (Scipio & Polybius); 36.9–17; 38–39 complete.
- **Sonnet tier (everything else):** prompt limits the job to the error class:
  "Compare against the Greek ONLY for: negation/inversion of sense, misread
  correlatives/particles, wrong proper-name identity, numbers. Output a list of
  `{quote, problem, proposed_fix}` or `CLEAN`. Flag `UNSURE` rather than guess."
  UNSURE and any proposed fix touching syntax batches up to Opus.
- A script applies accepted fixes from the JSON; nothing edits prose freehand.

## Phase 5 — Chapter titles (Sonnet write, Haiku check)

- Sonnet, batched 10 chapters per task: write a 3–8 word title from the
  *translated content* (never from the crib). Covers the ~105 bare headings
  (all of Book 34, tails of 30/31/36/38, fragment letters where a title helps)
  and every title flagged in Phase 2.
- Haiku, whole-corpus pass: title-case conformance to the style sheet, no
  duplicates within a book, heading format `## Book N Chapter M: Title` exact.
  Haiku reports; a script or Sonnet applies.

## Phase 6 — Testimonia apparatus + seam repairs (Sonnet)

- **Testimonia:** for each fragment chapter in Books 7–39 whose text is a later
  author quoting Polybius ("Polybius says/writes…"; Strabo's polemic in 34;
  Plutarch in 29.233ff), add an attribution line under the heading in the
  existing convention: `*Quoted by Athenaeus, Deipnosophistae.*` The source
  file's crib usually names the quoting author; Sonnet may use it for the
  attribution ONLY (not for content). Book 34 first — every chapter needs one,
  plus a one-paragraph headnote that the book survives only in quotations.
  Voice-switch sentences ("Polybius says: I have already…") get the quote set
  off or the frame italicized — pick one convention and keep it.
- **Seams:** work through `work/reports/seam_report` + the known list in
  Phase 1, plus `work/reports/quote_balance.txt` (39 paragraphs with unbalanced
  curly quotes — some are legitimate multi-paragraph speeches; judge, don't
  script) and attached-ellipsis lacunae left by Phase 1. Each task gets both
  chapters' tails/heads inline. Bracket-repeats are
  deleted or merged; truncated sentences get a marked lacuna, never invented text.
- **26.1a**: add a note that it repeats 26.1 via a second quoting author.
- **Book 33**: note the missing ch. 2 (absent in source) in the book headnote.
- **Ethnonym pass (decided rules, Phase 7):** Sonnet applies the region rule
  for Gauls/Galatians (hotspots: Book 2 ch. 14–35; Books 21, 25, 30) and the
  Spartans-in-narrative rule (hotspots: Book 4 ch. 22–27, Book 20). Work from
  a script-generated occurrence list, chapter by chapter; Haiku verifies no
  stragglers afterward.

## Phase 7 — Reader-facing front matter (Sonnet draft → USER decisions)

Sonnet drafts; the user signs off (this is the one phase that is mostly human):

1. **Translator's preface** replacing EDITORIAL_NOTE.md in reader-facing builds:
   Greek basis (Büttner-Wobst via Perseus), role of the 1889 crib, Book 17
   note / Book 19 testimonia / Book 40 index-fragments not included (39.8
   epilogue is), units policy (feet in Book 6 camp chapters, stades elsewhere),
   lacuna convention. No pipeline language ("local source corpus", script names).
2. **STYLE_SHEET.md** — DECIDED by the user 2026-10-31 (agents follow these;
   remaining small calls like Senate/senate, strategus/general, title case are
   Sonnet's to propose in the style sheet draft):
   - **Celts/Gauls/Galatians: region rule.** Peoples in Italy and Europe =
     "Gauls" ("Gallic"); peoples in Asia Minor = "Galatians". "Celts" drops out
     of narrative except where Polybius is making an explicitly ethnographic
     point (Book 2's excursus may keep one framing mention). State the rule in
     the preface.
   - **Lacedaemonians/Spartans:** "Spartans" in narrative; "Lacedaemonians"
     only in formal/diplomatic contexts (treaties, embassies, official
     self-description). State in preface.
   - **Rivers: modern names** — Ebro, Po, Danube, Rhone (matches the corpus's
     existing Rhone/Danube usage and modern-translation convention). Cities and
     regions stay ancient (New Carthage, Iberia). Deterministic — done in
     Phase 1.
   - **Dates — DECIDED by the user 2026-10-31:** `215 BC` (no periods, BC
     after), en-dash ranges `210–206 BC`, headings included. Applied in
     Phase 1; state in the style sheet.
   - **License: CC0 1.0 public-domain dedication** with a courtesy-attribution
     request naming the edition. Rationale: AI-generated text is of doubtful
     copyrightability, and the edition is in the free-classics spirit.
3. **Metadata — DECIDED:** credit the model family as translator and the user
   as editor.
   - Preface/title page line: "Translated from the Greek by Claude, Anthropic's
     family of AI models. Directed and edited by spinchange." (The editor name
     can be swapped for a personal name before print.)
   - OPF: `<dc:contributor id="trl">Claude (Anthropic)</dc:contributor>` with
     `role=trl`; a second contributor entry for the editor (`role=edt`);
     `<dc:rights>CC0 1.0 Universal — public domain dedication</dc:rights>` plus
     a `link rel=cc:license` in the HTML head; replace publisher placeholder
     with the edition/site name once chosen; fix `dc:description` wording
     (no "local source corpus").

## Phase 8 — QA pyramid

1. **Scripts:** heading_report + seam_report rerun clean; epubcheck green;
   a **coverage check** replacing the retired `compare_structure.py` (its 1:1
   English-paragraph-to-Greek-block test is broken by design after Phase 1's
   merges, and it points at the Hermes cache): new script reads `source/`
   in-repo and verifies every Greek chapter is represented in the right book
   and order — no paragraph-count parity.
2. **Haiku, per book:** checklist — every heading titled and formatted; no
   paragraph starts lowercase; no `[` bracket-repeat pattern; quotes balanced;
   one lacuna convention; attribution line present in testimonia chapters.
3. **Opus or Fable, once:** read 25 chapters (the famous set sample + 10
   random) end-to-end for flow; verify the Phase 3/4 fixes against the Greek.

## Dispatch notes

- Project personas live in `.claude/agents/` with model tiers baked in —
  spawn by type instead of writing per-task role prompts:
  **scriptwright** (P1/A1, Sonnet), **collator** (P2, Sonnet),
  **philologist** (P3–4, Opus), **titler** (P5, Sonnet),
  **apparatus-clerk** (P6/A5, Sonnet), **excerptor** (A3, Sonnet),
  **archivist** (A2, Haiku), **proofreader** (P8/A6, Haiku).
  The task prompt then only needs the work unit (book/chapter or canon row).
- From a Sonnet session, parallelize per-chapter tasks ~5–10 at a time; each
  task appends to `work/status.csv`.
- Phases 1→2→3 are sequential; 4, 5, 6 can run in parallel after 2; 7 anytime;
  8 last.

## Review findings inventory (2026-10-31, verified — do not re-derive)

- Crib-substituted chapters: 37.1, 38.2 (Greek = Xerxes/Athens), 39.2, 39.3.
- Duplicated content from substitution: 38.2↔38.8, 37.1↔36.9–10, 39.2↔38.6.
- 38.8 "Popilius laughed" — Greek ὁ Πόπλιος = Publius (Scipio); fix with 38.2.
- Title misalignment ranges and known accuracy errors: listed in Phases 2 and 4.
- EPUB validates clean (epubcheck 5.3.0); identifier is stable uuid5; HTML/PDF
  build fine. dist epub currently modified/uncommitted.

## Phase 2/3 outcome (2026-10-31)

- Phase 2: Books 20–39 screened (360 chapters, Sonnet collators 5/agent; Opus
  confirm step never triggered — zero false/UNSURE; control on known-bad 37.1
  correctly flagged). 135 crib-derived titles queued in
  `work/reports/phase2_title_queue.csv` for Phase 5.
- **Books 7–19 alignment screening consciously skipped.** Phase 4 puts every
  chapter there in front of an agent against the Greek anyway, which would
  catch wholesale mismatches.
- Phase 3: 37.1, 38.2, 39.2, 39.3 retranslated from the Greek; crib bodies
  removed; titles already fixed (not in the Phase 5 queue). 38.8
  "Popilius laughed" → "Publius laughed" applied (ὁ Πόπλιος = Scipio).
- **Phase 6 queue additions:** 37.1 now a Stephanus-type gazetteer fragment —
  add its attribution line AND drop/rework the leftover rubric
  "Olympiad 158, year 1. Macedonian War.", which doesn't fit it. 39.2 is a
  quotation by Strabo (attribution). 39.3 uncertain readings: καταμόνους,
  ἀπὸ τῆς χώρας, χάριν — flag for Phase 4 Opus.

## Phase 5 outcome (2026-10-31)

- 244 headings retitled (105 bare, the Phase 2 queue, duplicates, 9.44, long/case fixes) by titler
  agents in 31 batches, one book per agent at a time. Titles written from the translated
  content; Phase 2 hints were advisory. 15.8 and 10.43 left alone / case-only. Known-bad
  ranges not in the Phase 2 queue (e.g. most of Book 25, 31.6) were NOT retitled — the
  collator screen judged those titles correct.
- Scripted check (`heading_report.py`) now shows 0 bare headings, 0 duplicates per book,
  0 format issues. Straight apostrophes in 7 headings normalized to ’. `work/status.csv`
  re-quoted (all rows 6 fields). EPUBCheck green.
- Leftovers for Phase 6: stray crib rubrics at the top of 12.4a ("III. On the Other Errors
  of Timaeus") and 34.5 ("III. Polybius argues against…"); 16.10's Livy footnote was dropped
  with the fused heading — restore as a real footnote; `## II. Fragment of Uncertain Place`
  in Book 20 (unparsed).
- Soft calls to eyeball: 1.25, 24.4, 32.4, 38.21, 39.6, 39.7; 33.8 uses "Massalia" (style
  sheet to decide Marseilles/Massalia).
- Haiku title-case pass was replaced by the script check (no model needed).

## Phase 6 outcome (2026-10-31)

- 11 apparatus-clerk agents, one book-set each, driven by `work/scripts/phase6_prep.py` →
  `work/phase6/book_NN.md` and the shared conventions in `work/phase6/RULES.md`
  (STYLE_SHEET.md does not exist yet; RULES.md carries the decided rules).
- Done: leftover crib rubrics deleted; bracket-repeats deleted; truncated paragraphs and
  gap ellipses normalized to `[...]`; Celts→Gauls, Lacedaemonians→Spartans (formal uses kept),
  Gauls→Galatians for Asia Minor (incl. 4 Book 21 headings); Book 33/34 headnotes; 26.1a note;
  16.10 Livy note restored; 37.1 rubric dropped; 4.13/14 split word "Phi-/-lip" rejoined.
- **Attributions: only 13 added**, where the source explicitly shows the quoting author
  (Strabo in 24.4, 25.1, 34.5/6/11/12; Suidas 8.38, 7.10, 7.14b; Stephanus 7.14c/d; Athenaeus 7.1;
  Plutarch 19.1 — work title not known). The plan's premise that the crib "usually names the
  quoting author" did not hold (≈40 of 774 chapters). Remaining candidates are listed, not
  guessed, in `work/reports/phase6_escalations.md` — resolving them needs an outside source
  (e.g. the Büttner-Wobst apparatus), a Phase 4/7 decision, or acceptance without attribution.
- Open decisions: (a) chapter breaks that cut a sentence (2.13/14, 4.x, 18.31/32, 18.50/51 …)
  now end with ` [...]` — the sentence really continues in the next chapter; consider rejoining or
  dropping the marker; (b) translator markers `[text missing]` / `[Text breaks.]` (31–32) vs the
  `[...]` convention; (c) 8.24 heading doesn't fit its content (Books 7–19 were not screened);
  (d) Book 20 `## II. Fragment of Uncertain Place` still has no chapter number.
- Log note: one clerk's status.csv rewrite clobbered ~16 concurrent rows; book-file edits are
  intact (the diff is the record). Lesson: parallel agents append only.

## Phase 4 outcome (2026-10-31)

- **Step 1 (verified fixes):** applied from the spec by a Sonnet philologist; deviations where the
  Greek disagreed with the spec are logged in `work/status.csv` (e.g. 35.1: νὺξ διέλυε really does say
  night ended the fighting; 6.12 is optative προθεῖντο; the Book 6 fragment is in ch. 2). **Open:** 39.7
  "Ptolemy king of Syria" — the Greek really reads Συρίας; not emended (Phase 4 spec said drop it).
- **Discovery sweep:** `phase4_prep.py` → 191 batches (42 Opus / 209 chapters incl. Book 6, 38, 39 whole;
  149 Sonnet / 1,101 chapters). 436 findings (90 Opus-tier, 346 Sonnet-tier); every quote matched the text.
  Dominant error classes: lacunae the English read straight over (≈ half), then sense inversions,
  wrong numbers, wrong names.
- **Confirm/finalize:** 385 findings (all Opus high/medium + Sonnet high/medium/structural) went to
  48 Opus confirm batches: 201 ACCEPT, 131 REVISE, 23 REJECT, 30 HUMAN. Opus normalized every lacuna
  marker to `[...]` and rejected Sonnet false positives (e.g. 1.44 Atarbas=Adherbal, 2.52 πρόβλημα,
  5.95 instrumental dative). Low-confidence Sonnet findings (≈63) were NOT confirmed or applied.
- **Applied:** 332 fixes by `phase4_apply.py` (exact-match, per-chapter, CRLF-preserving); 0 conflicts.
  Log: `work/reports/phase4_applied.csv`. Plus: Ortiagon (22.21 heading), Aristophantus (5.6 heading).
- **HUMAN (30, not applied):** `work/reports/phase4_human.md`. Need a translator's call — mostly corrupt
  Greek (9.17, 12.28, 16.3, 22.16 papyrus, 24.12), disputed readings (10.3 negation, 14.8 subject,
  36.17 "Demetrius" vs Philip), or unmarked-gap judgments (9.24, 38.21).
- **Found but not filed by the sweep (do these next):** 39.6 μέγαν καιρὸν; 1.22 invented closing bracket
  → `[...]`; 1.37 "fortune"→"Fortune"; 14.7 "and link up" → "would link up" (after the 14.6 fix);
  26.1 "gazelle horn" knucklebones; 36.5 ἀλλὰ καθ᾽ ὃν καιρὸν; 36.14 Malleolus, 36.15 Bithynians,
  36.17 leftover "[fragmentary text continues]" labels; 32.11 "[Text missing.]" marker; 10.15/16 and
  3.53/54 duplicated clauses at chapter joins; 8.24 heading doesn't fit its content (Books 7–19 were
  never alignment-screened); 6.19–6.18 etc. fine.
- **Chapter-break policy (open):** many chapter divisions cut a sentence mid-clause or mid-word
  (3.116 `προσ|πεπτωκότας`, 4.13/14 `Phi|lip`, 38.3, 38.6 …). Phase 4 corrected the worst English
  inventions but the policy (rejoin / `[...]` / unmarked) is still your call.
- **Build note:** another process was editing `build_epub.py` (book plates), `EDITORIAL_NOTE.md`,
  `art/`, `work/art/` during this phase; dist/ was NOT regenerated in this commit. EPUBCheck was run in a
  clean worktree with only Phase 4's book edits: 0 fatals / 0 errors / 0 warnings. Rebuild dist after
  the art work lands.

## Phase 4b outcome (2026-11-01) — branch fix/p4b-followups

- **39.7:** keeps "of Syria": "Ptolemy, king of Egypt, who had just become king of Syria as well"
  (Greek ὁ τῆς Συρίας βασιλεύς; Philometor took the Syrian crown in 145 BC). The 39.109 entry above is corrected.
- **Chapter breaks that cut a sentence:** `p4b_seams.py` found 108; Sonnet checkers verified each against
  the Greek (no `*` gap at 107 of them) → 74 clean joins + 33 repaired joins (doubled words/dashes,
  missing verbs, English that had repeated one Greek clause across the break); 1 true lacuna left
  alone (18.33/34). In each case the unfinished sentence moved under the next heading; NO `[...]`
  used. Log of every move: `work/reports/p4b_seam_moves.csv`. 22 chapters still open with `[...]`
  after a properly ended sentence — those are real gaps in the Greek.
- **Non-standard gap markers** (`[text missing]`, `[Text breaks.]`, `[the text breaks off]`,
  `[fragmentary text …]`) normalized to `[...]` (Books 12, 31, 32, 36).
- **Held items:** all 30 in `work/reports/phase4_human.md` now carry an Opus RECOMMENDED rendering
  and one-line reason. NOT applied — awaiting the translator's approval/override.
- **Small errors applied** (logs in `work/phase4b/edits_S1..S3.md`): 1.22, 1.37, 3.53/54, 10.15/16,
  8.24 (retitled "Tarentine Conspirators Approach Hannibal"), 14.7, 26.1, 36.5, 36.14, 36.15, 39.6, 39.7.
- **Attribution sort (the 68 escalations):** 2 real quotations (21.38 and 29.15, both Plutarch) → lines
  added; 27 Constantinian-type excerpts; 39 unknown (mixed sources or no named author). 7.1's line now
  reads "Quoted by Athenaeus, Deipnosophistae; the last sentence by Suidas, Lexicon." Far fewer than
  hoped: the files rarely name the quoting author.
- **Spotted, not done:** 3.38 "places demonstrating these points" (τοὺς τόπους τοὺς συνεπιδεικνυμένους
  = "places pointed out along with the account"); 3.62 πάντες ἐμακάριζον ("all called the dead man
  fortunate"); 4.43 ἀπολιπών ("leaving behind", not "falls short of"); 24.12 "if not, and if not
  even Philopoemen" (εἰ δὲ μηδ᾽ = "but if not even"); 29.13 probably Athenaeus but unnamed in the file.
- **Build:** dist/ NOT regenerated (another session's art/build changes are in the tree). EPUBCheck run
  in an isolated worktree with only these book edits: 0 fatals / 0 errors / 0 warnings.
