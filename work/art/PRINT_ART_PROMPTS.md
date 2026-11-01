# Print-Edition Art Prompts — Supplement to ART_PROMPTS.md

For Gemini (Argon). This pack adds only what the **print edition** needs on top of
`ART_PROMPTS.md`. Do not restart the series style: **paste §1 (Style Anchor, No-Text Clause,
Period Guardrails) from `ART_PROMPTS.md` first, then attach `art/cover_front.png` as the
reference image** and say "match its style, palette and linework exactly".

Written 2026-11-01; updated the same day for the print decisions: **Lulu, one volume, 6 x 9 in,
black-and-white interior (9.5 pt, 760 pages), colour on the cover only, no two-page spreads.**
Interior art (plates, ornaments) is therefore greyscale or pure black line art. Status of the
art we already have, and why this pack exists:

| Existing file | Pixels | At print size | Problem for print |
|---|---|---|---|
| `art/cover_front.png` | 848 × 1264 | ~140 dpi across 6 in | Too low-res for a cover; has an engraved border frame that would be cut by the trim |
| `art/cover_back.png` | 768 × 1376 | ~125 dpi | Same; no space planned for blurb or barcode |
| `art/book_NN_plate.png` ×39 | 848×1264 or 896×1200 | ~300 dpi at 2.75 in tall | Now printed greyscale on each book-opener page, about 2 in wide; resolution is adequate, no regeneration required |
| `art/headpiece.png` | 1376 × 768 | — | Fine for web; interior needs one-colour line art |

---

## 0. Technical rules for everything below

1. **Full bleed.** Art runs to every edge of the canvas. **No engraved border, no plate-mark
   frame, no drop shadow, no paper edge** inside the picture. The printer trims 0.125 in
   (3 mm) off every side; anything drawn near the edge is lost or cut unevenly.
2. **Safe zone.** Keep every important element (face, hands, ship, helmet) at least
   **12% in from each edge** of the canvas. Backgrounds (sky, sea, rock) may run to the edge.
3. **Resolution.** Generate at the largest size Argon offers. If it still tops out near
   1,400 px on the long side, we will upscale 2–3× afterwards (engraved linework upscales
   well). Do not ask the model for tiny details that only work at huge size.
4. **Aspect ratio.** Ask for the ratio listed; if Argon offers a closer one, use it and we
   will crop. Never let it add letterboxing or a white margin.
5. **No text, ever.** Titles, spine text, blurb, barcode and captions are typeset by us
   (Typst/vector) afterwards. Image models garble lettering, especially Greek.
6. **Colour.** Deliver RGB; the printer converts to CMYK. So avoid fluorescent colours and
   very saturated blues/greens that shift badly in CMYK. The series palette is already safe.
   Keep deep darks above pure black (use iron-gall brown #2B2117) so the cover does not
   print as a muddy black.
7. **One-colour interior art.** The interior prints in black only. Ornaments that sit inside
   the text block (§4) must be **ink-only line art on plain white**, no wash, no paper
   texture, so they print crisply in black. Colour is only for the cover (front, spine,
   back). Plates are converted to greyscale by us; you do not need to supply them in colour.
8. **Lulu cover specifics.** The cover is one file: back, spine, front, with 0.125 in bleed.
   Spine width comes from Lulu's cover template after the interior is uploaded, so generate
   front and back separately (§1, §2) and let us assemble the wrap. The barcode area on the
   back is about 2 x 1.2 in, lower right.

---

## 1. Front cover (print, full-bleed)

Aspect **2:3** portrait (we crop to the trim plus bleed). Attach `art/cover_front.png`.

> Use the attached image as the exact composition reference: Polybius of Megalopolis, a lean
> man in his fifties with a close-cropped grey beard, plain brown travelling cloak over a
> chiton, standing on a rocky headland at dusk, a half-unrolled papyrus scroll in his left
> hand and his right hand resting on a bronze Arcadian helmet with a red crest set on a
> stone block. Behind him the sea; on the far left a Greek city with a Doric temple; on the
> far right Roman war galleys with bronze rams catching the last light. Same face, same
> pose, same palette.
>
> Re-render it for **print as a full-bleed cover**:
> - Remove the engraved rectangular border and the paper margin entirely. The picture must
>   continue to all four edges of the canvas.
> - Extend the scene about 8% beyond the old frame on every side: more sky above, more rock
>   below, more sea left and right.
> - **The top 38% must be calm, nearly empty warm parchment-toned sky** with only soft
>   haze, so a title can be typeset over it. No clouds with strong contrast there.
> - The lower 12% should be quiet dark rock and shadow, so a subtitle and credit can sit on it.
> - Keep the figure's head, hands and helmet inside the central safe area.
> - Finer, crisper engraved linework and cross-hatching than the reference, visible at
>   print size; keep the restrained watercolour wash.
> - *[Period Guardrails]* *[No-Text Clause]*

**Fallback if the figure drifts:** generate at the largest size from the attached image with
the instruction "Do not change the figure at all; only extend the background and remove the
frame", then upscale.

---

## 2. Back cover (print, full-bleed)

Aspect **2:3** portrait, same size as the front. Attach `art/cover_back.png` and the front.

> Match the style of the attached front cover. Re-render the back-cover companion image as a
> **full-bleed** scene: a single fallen Ionic column fragment on a stepped stone base, a
> half-unrolled papyrus scroll draped over it, an olive branch and a broken Roman *pilum*
> laid across the base, dust and small potsherds on the ground. Parchment ground that runs
> to every edge, with fine engraved ground-hatching.
>
> **Layout rules, because text will be set over most of this image:**
> - Put the still-life in the **lower-centre**, occupying about the lower 40% of the
>   canvas, centred horizontally.
> - The **upper 55% must be quiet, even, warm parchment** (very faint paper grain only):
>   this is where the back-cover blurb goes.
> - The **lower-right corner (about 2 in × 1.3 in at final size) must be plain and
>   undisturbed** (the barcode box). Nothing in the still-life enters it.
> - No border, no frame, no plate mark.
> - *[Period Guardrails — Roman Republic equipment only]* *[No-Text Clause]*

---

## 3. Optional continuous wrap (only if we want one image across back, spine and front)

We do not know the spine width until the page count and printer are fixed, so the default
plan is **front and back as separate images joined by a typeset spine band** (§3b). Use this
panorama only if you want to try a continuous wrap; we would place and crop it afterwards.

Aspect **2.2:1** (very wide). Attach the front cover.

> Match the attached cover's style. A continuous engraved panorama of the same headland
> scene, extended into a wide landscape: at the **right third** Polybius stands on the rocks
> exactly as in the reference, with the Roman galleys beyond him; across the **middle
> third** the sea and evening sky run calmly, with nothing important in it; at the **left
> third** the Greek city and Doric temple on a distant shore, then open haze. The whole top
> 35% is calm parchment sky. Full-bleed, no frame, no text. *[Period Guardrails]*
> *[No-Text Clause]*

### 3b. Spine band and binding cloth (any trim, any page count)

Aspect **1:8** tall strip (we scale it to the real spine width).

> A seamless vertical band for a book spine: deep oxblood-umber (#5B3B2B) with a very fine
> engraved cross-hatch texture, a single thin burnished-gold (#D7BD82) Greek meander (key)
> rule running down each long edge, and a small engraved gold laurel wreath near the top.
> The centre of the band is plain, calm and dark so the title can be set in gold or cream.
> No text, no figures. Must tile seamlessly if repeated vertically. *[No-Text Clause]*

---

## 4. Interior ornaments — one-colour line art

These are placed inside the text and must print in plain black ink. **Ink-only line art on
pure white background; no colour, no wash, no paper texture, no grey tint.** Deliver each on
a clean white ground so we can make the white transparent.

**4.1 Book-opening band** (replaces the plain rule under "BOOK I"). Aspect **5:1**.
> Pure black ink engraving on white. A narrow horizontal ornamental band: a small centred
> roundel with an olive wreath around a crossed *sarissa* and *pilum*, flanked by symmetrical
> acanthus scrolls that taper to fine points, finished at each end by a short Greek meander
> (key) pattern. Perfectly symmetrical left to right. Clean, even line weight; no shading
> beyond fine hatching inside the roundel. *[No-Text Clause]*

**4.2 Tailpiece set (end of each book)** — six at **1:1**, one image each, centred on white.
> Pure black ink engraving on white; compact symmetrical vignettes, about the same visual
> weight and line thickness across the set: (1) a galley's bronze ram head; (2) an elephant
> in a laurel roundel; (3) a Corinthian helmet resting on an olive branch; (4) a rolled
> scroll tied with a cord; (5) a Rhodian rose; (6) the wheel of Tyche with a ship's rudder.
> Each isolated, no background, no frame. *[No-Text Clause]*

**4.3 Title-page device** (the "printer's mark" above the publisher line). Aspect **1:1**.
> Pure black ink engraving on white. A small circular emblem: the Arcadian helmet from the
> cover in profile, a half-unrolled scroll beneath it and an olive sprig either side, inside
> a narrow ring. Reads clearly at 0.8 in wide. *[No-Text Clause]*

---

## 5. Map of Polybius's world (OPTIONAL, black-and-white, single page)

**Dropped as endpapers:** Lulu has no printed endpapers and does not accept two-page
spreads. If we want the map, it becomes one **single-page, ink-only** map inside the book
(for example after the Preface), at 6 x 9 in minus margins. Aspect **2:3** portrait, pure
black ink on white, no colour, no grey wash (hachure and stipple only).

Prompt below was written for the colour spread; for the black-and-white page, replace the
colour sentence with "pure black ink engraving on white, hachured mountains, stippled
seas, no tint" and keep the rest.

> An antique engraved relief map of the Mediterranean world about 150 BC, drawn as one
> connected whole from Iberia in the far west to Syria and Egypt in the east: hachured
> mountains, stippled seas with engraved wave lines, rivers as fine ink lines, small
> pictorial symbols of walled cities. Faint gold routes: Hannibal's march across the Alps,
> the sea lanes between Carthage, Sicily and Rome, the road east from Rome to Corinth.
> Warm parchment ground, pale umber land wash, Aegean blue-grey sea, gold accents. **No
> lettering of any kind**; place names will be typeset over it. Keep important detail away
> from the left edge (the binding side). No border. *[No-Text Clause]*

Generate it once. We add the labels afterwards. (No night variant: there is no back endpaper.)

---

## 6. Book plates (interior frontispieces) — settled, nothing to generate

Decision (2026-11-01): the interior is **black and white**. Each existing plate is converted
to greyscale (with a little added contrast) and printed on its book-opener page, about 2 in
wide by 2.75 in tall. They are already high enough resolution at that size, so **no upscaling
or regeneration is needed**. Only if a specific plate looks muddy in grey would we ask for a
higher-contrast redraw: same prompt as `ART_PROMPTS.md` §4 plus "strong tonal contrast,
reads clearly in black and white".

---

## 7. Social and promotional cards

The pack's §3.4 (default Open Graph card), §6 (quote cards, portrait gallery, "this
happened" cards) already cover the website. For the **print launch**, add:

**7.1 "Now in print" card** — three crops of the *cover*. Attach the finished front cover.
> Aspect **1.91:1** (1200×630). Outpaint the attached cover composition to a wide
> landscape: keep Polybius and the helmet at the **right** third at the same scale, extend
> the sea, sky and distant Greek city to the left, so that the **left 45%** is calm parchment
> sky and sea for a headline. Same style and palette. *[Period Guardrails]* *[No-Text Clause]*

Repeat as **1:1** (1080×1080, figure centred, calm sky on top 35%) and **9:16**
(1080×1920, figure in the lower half, the upper 45% calm sky).

**7.2 "Inside the book" spread card.** Aspect **1.91:1**.
> A flat-lay photograph-style composition (but rendered as an engraving-and-watercolour
> illustration in the series style) of an open book on a wooden table: the left page a
> full-page engraved plate, the right page blank cream paper with a few lines of
> unreadable softened text-texture (no legible words), an olive sprig and a bronze stylus
> beside it, warm raking light. No legible lettering. *[No-Text Clause]*

**7.3 Quote cards.** Use the pack's §6 background prompt; the quotes themselves are typeset
by us from the translation. Ask us for the shortlist of candidate quotes; do not let the
image model write or paraphrase any text.

---

## 8. Acceptance checklist (every image)

- [ ] Style matches the reference (palette, linework, wash); no drift toward glossy or neon.
- [ ] **No text, letters or pseudo-letters anywhere** (zoom to 100%, check shields and sails).
- [ ] Period Guardrails respected (Republican Roman kit, no stirrups, no horned helmets).
- [ ] Full-bleed: no frame, border, paper edge or white margin.
- [ ] Safe-zone and quiet-zone rules met (title area, blurb area, barcode corner).
- [ ] Interior ornaments are pure ink on white with no tint (the interior prints black only).
- [ ] Largest available resolution; filename `art/print/<role>_v<N>.png`.
- [ ] Alt text drafted for each (the manifest needs it for the web and EPUB).
- [ ] AI-generation credit stays in the colophon (already in `PREFACE.md`).
