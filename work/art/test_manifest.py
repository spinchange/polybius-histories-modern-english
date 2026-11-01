import json
import sys
from pathlib import Path

def validate():
    manifest_path = Path("work/art/manifest.json")
    if not manifest_path.exists():
        print(f"FAIL: {manifest_path} does not exist")
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "flagships" in data, "Missing flagships"
    assert "books" in data, "Missing books"

    flagships = data["flagships"]
    expected_flags = ["cover_front", "cover_back", "hero_day", "hero_night", "og_default", "headpiece"]
    for ef in expected_flags:
        assert ef in flagships, f"Missing {ef}"
        item = flagships[ef]
        for key in ["filename", "title", "aspect", "ref", "alt_text"]:
            assert key in item, f"{ef} missing {key}"
        wc = len(item["alt_text"].split())
        assert 25 <= wc <= 45, f"{ef} alt_text has {wc} words"
        assert "image of" not in item["alt_text"].lower(), f"{ef} has 'image of'"
        assert "picture of" not in item["alt_text"].lower(), f"{ef} has 'picture of'"

    books = data["books"]
    assert len(books) == 39, f"Expected 39 books, got {len(books)}"
    for i, b in enumerate(books, start=1):
        assert b["book"] == i, f"Expected book {i}, got {b.get('book')}"
        expected_fn = f"art/book_{i:02d}_plate.png"
        assert b["filename"] == expected_fn, f"Expected filename {expected_fn}, got {b.get('filename')}"
        assert b["scene"], f"Book {i} missing scene"
        assert b["ref"], f"Book {i} missing ref"
        assert b["caption"], f"Book {i} missing caption"
        wc = len(b["alt_text"].split())
        assert 25 <= wc <= 45, f"Book {i} alt_text has {wc} words: '{b['alt_text']}'"
        assert "image of" not in b["alt_text"].lower(), f"Book {i} has 'image of'"
        assert "picture of" not in b["alt_text"].lower(), f"Book {i} has 'picture of'"

    print(f"SUCCESS: {manifest_path} is valid JSON with 6 flagships and 39 books conforming to all requirements.")

if __name__ == "__main__":
    validate()
