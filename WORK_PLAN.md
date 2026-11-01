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
- **39.109**: Ptolemy Philometor is king of **Egypt**; drop "of Syria".
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
  Phase 1. Each task gets both chapters' tails/heads inline. Bracket-repeats are
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
   `compare_structure.py` clean.
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
