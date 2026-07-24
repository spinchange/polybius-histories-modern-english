"""
Cleanup script for Polybius translation files:
1. Remove [N] section markers from all .md files
2. Strip HTML <a> tags from headings in chunk files
3. Split Polybius_Histories_Books_I_II_modern_English.md into Book I and Book II
"""

import re
from pathlib import Path

BASE_DIR = Path(r"C:\Users\executor\AppData\Local\hermes\cache\documents\the_histories_translation")


def clean_section_markers_and_html(text: str) -> str:
    lines = text.split('\n')
    result = []
    prev_blank = False

    for line in lines:
        stripped = line.strip()

        # Remove HTML <a> tags from heading lines while keeping link text
        if stripped.startswith('#'):
            line = re.sub(r'<a\b[^>]*>(.*?)</a>', r'\1', line)
            stripped = line.strip()

        # Skip lines that are only a section marker like [2] or [12]
        if re.match(r'^\[\d+\]$', stripped):
            continue

        is_blank = stripped == ''

        # Collapse consecutive blank lines
        if is_blank and prev_blank:
            continue

        result.append(line.rstrip())
        prev_blank = is_blank

    return '\n'.join(result)


def process_file(path: Path) -> bool:
    original = path.read_text(encoding='utf-8')
    cleaned = clean_section_markers_and_html(original)
    if cleaned != original:
        path.write_text(cleaned, encoding='utf-8')
        return True
    return False


def split_books_i_ii() -> None:
    combined = BASE_DIR / 'Polybius_Histories_Books_I_II_modern_English.md'
    if not combined.exists():
        print("  Combined I-II file not found, skipping split.")
        return

    content = combined.read_text(encoding='utf-8')

    # Locate the Book 2 divider
    match = re.search(r'\n## Book 2\n', content)
    if not match:
        print("  ERROR: Could not find '## Book 2' boundary.")
        return

    book1_raw = content[:match.start()].rstrip()
    book2_raw = content[match.start() + 1:]  # keep leading '\n## Book 2\n...'

    # Fix title for Book I
    book1_content = book1_raw.replace(
        '# Polybius — The Histories (Books I–II)',
        '# Polybius — The Histories, Book I'
    ).replace(
        'Modern English translation of the Greek text corresponding to the supplied Loeb volume.',
        'Modern English translation of the Greek text.'
    )

    # Build Book II content with a proper title
    book2_content = (
        '# Polybius — The Histories, Book II\n\n'
        'Modern English translation of the Greek text.\n\n'
        + book2_raw
    )

    book1_path = BASE_DIR / 'Polybius_Histories_Book_I_modern_English.md'
    book2_path = BASE_DIR / 'Polybius_Histories_Book_II_modern_English.md'

    book1_path.write_text(book1_content, encoding='utf-8')
    book2_path.write_text(book2_content, encoding='utf-8')
    combined.unlink()

    print(f"  Created:  {book1_path.name}")
    print(f"  Created:  {book2_path.name}")
    print(f"  Deleted:  {combined.name}")


def main() -> None:
    # Step 1: Split combined Books I-II file
    print("=== Splitting Books I-II ===")
    split_books_i_ii()

    # Step 2: Clean all .md files (section markers + HTML tags)
    print("\n=== Cleaning section markers and HTML tags ===")
    changed_count = 0
    for path in sorted(BASE_DIR.rglob('*.md')):
        changed = process_file(path)
        if changed:
            print(f"  Cleaned: {path.relative_to(BASE_DIR)}")
            changed_count += 1

    print(f"\nDone. {changed_count} file(s) modified.")


if __name__ == '__main__':
    main()
