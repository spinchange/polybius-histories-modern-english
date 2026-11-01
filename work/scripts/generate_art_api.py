#!/usr/bin/env python3
"""
generate_art_api.py — Production Batch Art Generator for Polybius The Histories (Modern English Edition)

Uses GEMINI_API_KEY with Google Generative Language API (Gemini Flash Image models)
to generate all remaining book plates and flagship art assets defined in ART_PROMPTS.md.

Features:
- Multimodal reference image anchor (art/book_01_plate.png) attached inline (§0 Step 2)
- Complete Style Anchor (§1.1), Period Guardrails (§1.3), and No-Text Clause (§1.2)
- Exact scene prompts parsed directly from work/art/ART_PROMPTS.md
- Aspect ratio targeting (3:4 for 2:3 plates, 9:16 for cover_back, 16:9 for headpiece)
- Output is verified and converted in-place to true PNG format (valid \\x89PNG header)
- CLI support: --dry-run, --book <num>, --single <key>, --force, --verify, --list, --workers, --model
"""

import os
import sys
import io
import re
import time
import json
import base64
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ART_DIR = PROJECT_ROOT / "art"
WORK_ART_DIR = PROJECT_ROOT / "work" / "art"
PROMPTS_FILE = WORK_ART_DIR / "ART_PROMPTS.md"
MANIFEST_FILE = WORK_ART_DIR / "manifest.json"
REF_IMAGE_PATH = ART_DIR / "book_01_plate.png"

CANDIDATE_MODELS = [
    "gemini-3.1-flash-image-preview",
    "gemini-3.1-flash-image",
    "gemini-2.5-flash-image",
    "gemini-3.1-flash-lite-image",
    "gemini-4-argon",
]

# §1.1 Series Style Anchor
STYLE_ANCHOR = """You are illustrating a scholarly but handsome new English edition of Polybius's Histories (Greek historian, c. 200–118 BC, covering Rome's rise from 264 to 146 BC). All images belong to one coherent series.

Medium: a hybrid of fine copperplate engraving / etching linework and restrained watercolour washes, like a 19th-century archaeological folio plate made with modern composition. Confident cross-hatching in the shadows, crisp contour lines, paper texture visible.

Palette (strict): warm parchment ground #FAF6EC, iron-gall ink brown #2B2117, deep oxblood/umber accent #5B3B2B, burnished gold #D7BD82, muted earth #7A6A55. Allowed extras, used sparingly: Tyrian purple, Aegean blue-grey, terracotta red. No neon, no saturated modern colour, no glossy digital rendering.

Light: low, raking Mediterranean light. Long shadows, dust or sea haze in the air, quiet drama. Think Jacques-Louis David's restraint with Piranesi's depth.

Mood: serious, humane, observant. Polybius was an eyewitness and a statesman. Show causes, consequences and human faces rather than glorified gore. Violence is implied, not graphic.

Composition: clear focal hierarchy, strong silhouette that reads at thumbnail size, generous negative space at the top for later typography."""

# §1.2 No-Text Clause
NO_TEXT_CLAUSE = """No text, letters, inscriptions, captions, signatures, watermarks or logos anywhere in the image. Any shields or banners carry only abstract devices."""

# §1.3 Period Guardrails
PERIOD_GUARDRAILS = """Historical accuracy, 3rd–2nd century BC:
- Romans (Republic): bronze Montefortino helmets with horsehair or feather crests, mail shirts or square bronze pectoral plates, tall oval curved scutum, pilum, short Spanish sword. No segmented plate armour (lorica segmentata), no rectangular Imperial shields, no eagles on poles.
- Hellenistic Greeks/Macedonians: linen or bronze cuirasses, Thracian or Phrygian helmets, round bronze-faced shields, the sarissa pike (5–6 m) in phalanx.
- Carthaginians: mixed army of Libyan infantry, Numidian light cavalry (no saddle, no bridle, javelins), Iberians in white tunics edged with purple, Balearic slingers, Gauls.
- Gauls: long swords, tall flat shields, torcs, trousers, some fighting bare-chested. No horned helmets.
- Cavalry: no stirrups, saddle-cloths only.
- Ships: oared war galleys (triremes, quinqueremes) with bronze rams, painted eyes on the bow, square sails stowed for battle.
- Architecture: Doric/Ionic temples, ashlar city walls with towers, Punic harbour architecture at Carthage. No medieval or Imperial-Roman monumental buildings (no Colosseum, no domes)."""

# Reference instruction (§0 Step 2)
REF_INSTRUCTION = "Match the copperplate engraving linework, cross-hatching, restrained watercolour wash, warm parchment border, and historical 3rd–2nd century BC aesthetic of the attached reference image."


def ensure_valid_png(filepath: Path) -> bool:
    """Check magic bytes; convert from JPEG if needed; return True if valid PNG."""
    if not filepath.exists() or filepath.stat().st_size == 0:
        return False
    with open(filepath, "rb") as f:
        header = f.read(8)
    if header == b"\x89PNG\r\n\x1a\n":
        return True
    try:
        img = Image.open(filepath)
        img.save(filepath, "PNG")
        with open(filepath, "rb") as f:
            return f.read(8) == b"\x89PNG\r\n\x1a\n"
    except Exception as e:
        print(f"Warning: Failed to convert {filepath.name} to PNG: {e}")
        return False


def sanitize_existing_art():
    """Convert any existing JPEG files in art/ directory with .png extension into true PNGs."""
    converted = 0
    if not ART_DIR.exists():
        ART_DIR.mkdir(parents=True, exist_ok=True)
    for p in ART_DIR.glob("*.png"):
        with open(p, "rb") as f:
            hdr = f.read(8)
        if hdr != b"\x89PNG\r\n\x1a\n":
            try:
                img = Image.open(p)
                img.save(p, "PNG")
                converted += 1
                print(f"Converted {p.name} in-place to true PNG format.")
            except Exception as e:
                print(f"Error converting {p.name}: {e}")
    if converted:
        print(f"Sanitized {converted} existing files to valid PNG.")


def load_book_prompts() -> dict[int, dict]:
    """Parse book prompts from ART_PROMPTS.md."""
    text = PROMPTS_FILE.read_text(encoding="utf-8")
    book_prompts = {}
    pattern = r"\*\*Book (\d+) — ([^\n]+)\*\*\s*\n((?:> [^\n]*\n?)+)"
    for match in re.finditer(pattern, text):
        num = int(match.group(1))
        title = match.group(2).strip()
        lines = [l[2:].strip() if l.startswith("> ") else l.strip() for l in match.group(3).splitlines()]
        clean_prompt = " ".join([l for l in lines if l and not l.startswith("*Alt") and not l.startswith("*Inset") and not l.startswith("*(Shares")])
        book_prompts[num] = {"title": title, "prompt": clean_prompt}
    return book_prompts


def get_all_target_specs() -> list[dict]:
    """Compile full target list: 39 books + 6 flagships."""
    book_prompts = load_book_prompts()
    targets = []

    # Flagships
    targets.append({
        "key": "cover_front",
        "book": None,
        "filename": "cover_front.png",
        "aspect": "3:4",
        "title": "Front Cover: The Historian Between Two Worlds",
        "scene": "A Greek historian in his fifties, Polybius of Megalopolis: lean, weathered, close-cropped grey beard, plain travelling cloak over a chiton. He stands on a rocky headland at dusk, seen from slightly below, one hand holding a half-unrolled papyrus scroll and the other resting on a bronze Arcadian cavalry helmet set on a rock. Behind him the Mediterranean opens out. On the left horizon is the faint silhouette of a Greek city with a Doric temple; on the right, Roman galleys with bronze rams catch the last light. His gaze is steady and searching, looking out of the frame. The top third is open sky in warm parchment haze, kept clear for a title.",
        "include_period": True
    })

    targets.append({
        "key": "cover_back",
        "book": None,
        "filename": "cover_back.png",
        "aspect": "9:16",
        "title": "Back Cover / Spine Companion",
        "scene": "A single Ionic column fragment wrapped by a half-unrolled scroll, olive branch and broken Roman pilum laid across its base, parchment ground, engraving style, centred with vast negative space above and below.",
        "include_period": True
    })

    targets.append({
        "key": "hero_day",
        "book": None,
        "filename": "hero_day.png",
        "aspect": "16:9",
        "title": "Website Hero: The Fifty-Three Years",
        "scene": "One continuous engraved frieze that moves left to right through Rome's rise: Roman boarding bridges crashing onto Carthaginian galleys; elephants crossing snowbound Alpine passes; a Macedonian phalanx bristling with sarissas in hill fog; a Roman senator in a toga receiving foreign envoys; and finally a burning harbour city at the far right, with a lone Roman general and a Greek companion watching from a rise. The scenes run together seamlessly like a Parthenon-style frieze, with watercolour wash fading to parchment at both ends.",
        "include_period": True
    })

    targets.append({
        "key": "hero_night",
        "book": None,
        "filename": "hero_night.png",
        "aspect": "16:9",
        "title": "Website Hero Night Variant",
        "scene": "Night variant: one continuous engraved frieze through Rome's rise rendered as a gold-and-cream line engraving on a deep umber-black ground (#1D1813), lines in #D7BD82 and #E8DDC8: Roman boarding bridges crashing onto Carthaginian galleys; elephants crossing Alpine passes; Macedonian phalanx; Roman senators; and burning Carthage.",
        "include_period": True
    })

    targets.append({
        "key": "og_default",
        "book": None,
        "filename": "og_default.png",
        "aspect": "16:9",
        "title": "Social Card: Polybius at His Desk",
        "scene": "Right half: a close three-quarter engraved portrait of a Greek historian (Polybius) lit from the right, quill in hand, scroll spread on a stone table with a small bronze astrolabe-like instrument and a clay lamp. Left 45%: empty warm parchment with faint engraved wave-hatching texture, reserved for a title overlay. High contrast.",
        "include_period": True
    })

    targets.append({
        "key": "headpiece",
        "book": None,
        "filename": "headpiece.png",
        "aspect": "16:9",
        "title": "Chapter Headpiece Band",
        "scene": "A horizontal ornamental band in engraving style: a Greek meander (key) pattern border, a central small roundel with an olive wreath around a crossed sarissa and pilum, and acanthus scrolls tapering to each end. Ink-brown on parchment, gold accents. Must tile or centre cleanly.",
        "include_period": False
    })

    # Books 1-39
    for b in range(1, 40):
        bp = book_prompts.get(b, {})
        fname = f"book_{b:02d}_plate.png"
        targets.append({
            "key": f"book_{b:02d}",
            "book": b,
            "filename": fname,
            "aspect": "3:4",
            "title": f"Book {b}: {bp.get('title', '')}",
            "scene": bp.get("prompt", ""),
            "include_period": True
        })

    return targets


def build_prompt_payload(target: dict, ref_b64: str | None) -> dict:
    """Build the generateContent request payload adhering to all guidelines."""
    prompt_parts = []
    
    if ref_b64:
        prompt_parts.append(REF_INSTRUCTION)
    
    prompt_parts.append(STYLE_ANCHOR)
    prompt_parts.append(f"Scene: {target['scene']}")
    
    if target.get("include_period", True):
        prompt_parts.append(PERIOD_GUARDRAILS)
        
    prompt_parts.append(NO_TEXT_CLAUSE)
    
    full_text = "\n\n".join(prompt_parts)

    parts = []
    if ref_b64:
        parts.append({
            "inlineData": {
                "mimeType": "image/png",
                "data": ref_b64
            }
        })
    parts.append({"text": full_text})

    return {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": target.get("aspect", "3:4")
            }
        }
    }


def call_gemini_image_api(payload: dict, api_key: str, model_name: str, timeout: int = 45) -> bytes:
    """Call Google Generative Language API and return raw image bytes."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        candidates = res_data.get("candidates", [])
        if not candidates:
            raise RuntimeError("API returned empty candidates list")
        parts = candidates[0].get("content", {}).get("parts", [])
        for p in parts:
            if "inlineData" in p:
                b64_str = p["inlineData"].get("data", "")
                return base64.b64decode(b64_str)
        finish_reason = candidates[0].get("finishReason")
        raise RuntimeError(f"No image in candidate response (finishReason: {finish_reason})")


def generate_single_item(target: dict, api_key: str, ref_b64: str | None, model_override: str | None = None, dry_run: bool = False) -> tuple[bool, str]:
    """Generate and save one item with model fallback and format conversion."""
    dest_path = ART_DIR / target["filename"]
    payload = build_prompt_payload(target, ref_b64)

    if dry_run:
        prompt_preview = payload["contents"][0]["parts"][-1]["text"][:160].replace("\n", " ")
        print(f"[DRY-RUN] Would generate {target['filename']} (aspect: {target['aspect']})")
        print(f"          Prompt excerpt: {prompt_preview}...")
        return True, "dry-run"

    models_to_try = [model_override] if model_override else CANDIDATE_MODELS
    last_err = ""

    for model in models_to_try:
        try:
            print(f"[{target['key']}] Generating with {model}...")
            img_bytes = call_gemini_image_api(payload, api_key, model)
            
            # Convert to PNG using PIL and write
            img = Image.open(io.BytesIO(img_bytes))
            img.save(dest_path, "PNG")
            
            if ensure_valid_png(dest_path):
                print(f"[{target['key']}] Successfully saved and verified {target['filename']} ({os.path.getsize(dest_path):,} bytes)")
                return True, model
            else:
                raise ValueError("Saved file failed PNG verification")

        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            last_err = f"HTTP {e.code} on {model}: {err_body[:200]}"
            if e.code == 429:
                print(f"[{target['key']}] Quota / Rate limit (429) on {model}")
            else:
                print(f"[{target['key']}] Error: {last_err}")
        except Exception as e:
            last_err = f"Error on {model}: {str(e)}"
            print(f"[{target['key']}] {last_err}")

    return False, last_err


def verify_all_art() -> dict:
    """Check existence and validity of all 45 art files."""
    targets = get_all_target_specs()
    results = {"total": len(targets), "valid": 0, "missing": [], "invalid": [], "files": {}}

    for t in targets:
        fname = t["filename"]
        fpath = ART_DIR / fname
        if not fpath.exists():
            results["missing"].append(fname)
            results["files"][fname] = "MISSING"
        else:
            is_valid = ensure_valid_png(fpath)
            size = fpath.stat().st_size
            if is_valid and size > 0:
                results["valid"] += 1
                results["files"][fname] = f"VALID ({size:,} B)"
            else:
                results["invalid"].append(fname)
                results["files"][fname] = f"INVALID ({size:,} B)"

    return results


def main():
    parser = argparse.ArgumentParser(description="Generate art for Polybius Modern English Edition")
    parser.add_argument("--book", type=int, help="Generate plate for a specific book number (1-39)")
    parser.add_argument("--single", type=str, help="Generate single key or filename (e.g. book_38, cover_back, headpiece)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate generation and display prompt payloads without API calls")
    parser.add_argument("--force", action="store_true", help="Regenerate already existing valid files")
    parser.add_argument("--verify", action="store_true", help="Verify all 45 art files and exit")
    parser.add_argument("--list", action="store_true", help="List all targets and current status")
    parser.add_argument("--model", type=str, help="Force specific model")
    parser.add_argument("--workers", type=int, default=2, help="Number of concurrent workers (default: 2)")
    args = parser.parse_args()

    # Always ensure existing files are true PNGs
    sanitize_existing_art()

    if args.verify:
        v = verify_all_art()
        print(f"\n--- Art Verification Summary ---")
        print(f"Total expected: {v['total']}")
        print(f"Valid PNGs:     {v['valid']}/{v['total']}")
        print(f"Missing:        {len(v['missing'])}")
        print(f"Invalid:        {len(v['invalid'])}")
        if v["missing"]:
            print(f"Missing files:  {', '.join(v['missing'])}")
        return 0 if v["valid"] == v["total"] else 1

    targets = get_all_target_specs()

    if args.list:
        print(f"\n{'Key':<12} {'Filename':<22} {'Aspect':<8} {'Status'}")
        print("-" * 65)
        for t in targets:
            fpath = ART_DIR / t["filename"]
            status = "EXISTS" if (fpath.exists() and fpath.stat().st_size > 0) else "PENDING"
            print(f"{t['key']:<12} {t['filename']:<22} {t['aspect']:<8} {status}")
        return 0

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key and not args.dry_run:
        print("ERROR: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        return 1

    # Load reference image if available
    ref_b64 = None
    if REF_IMAGE_PATH.exists():
        with open(REF_IMAGE_PATH, "rb") as f:
            ref_b64 = base64.b64encode(f.read()).decode("utf-8")
        print(f"Loaded reference image: {REF_IMAGE_PATH.name} ({len(ref_b64):,} b64 chars)")
    else:
        print("Warning: Reference image art/book_01_plate.png not found. Continuing without reference.")

    # Filter targets
    if args.book:
        queue = [t for t in targets if t.get("book") == args.book]
        if not queue:
            print(f"Error: Book {args.book} not found.")
            return 1
    elif args.single:
        filtered = [t for t in targets if t["key"] == args.single or t["filename"] == args.single or t["filename"] == f"{args.single}.png"]
        if not filtered:
            print(f"Error: Target '{args.single}' not found in manifest/prompts.")
            return 1
        queue = filtered
    else:
        queue = []
        for t in targets:
            fpath = ART_DIR / t["filename"]
            if args.force or not fpath.exists() or not ensure_valid_png(fpath):
                queue.append(t)
            else:
                print(f"Skipping {t['filename']} (already exists & verified). Use --force to regenerate.")

    print(f"\nItems in generation queue: {len(queue)} of {len(targets)}")
    if not queue:
        print("All art assets are present and verified!")
        return 0

    # Execute generation
    success_count = 0
    failure_count = 0

    if args.workers <= 1 or len(queue) == 1 or args.dry_run:
        for t in queue:
            ok, msg = generate_single_item(t, api_key, ref_b64, args.model, args.dry_run)
            if ok:
                success_count += 1
            else:
                failure_count += 1
                print(f"Failed to generate {t['filename']}: {msg}")
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(generate_single_item, t, api_key, ref_b64, args.model, args.dry_run): t
                for t in queue
            }
            for fut in as_completed(futures):
                t = futures[fut]
                try:
                    ok, msg = fut.result()
                    if ok:
                        success_count += 1
                    else:
                        failure_count += 1
                        print(f"Failed to generate {t['filename']}: {msg}")
                except Exception as exc:
                    failure_count += 1
                    print(f"Exception during {t['filename']}: {exc}")

    print(f"\n--- Batch Complete ---")
    print(f"Generated successfully: {success_count}")
    print(f"Failures:               {failure_count}")

    # Final verification
    v = verify_all_art()
    print(f"Total valid PNGs:       {v['valid']}/{v['total']}")
    return 0 if v["valid"] == v["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
