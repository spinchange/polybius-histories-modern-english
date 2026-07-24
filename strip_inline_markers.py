"""
Second-pass cleanup: remove inline [N] section markers that the first pass
(which only removed markers alone on their own line) left behind.

Handles:
  - leading markers:           "[2] To their kings..."   -> "To their kings..."
  - indented leading + stray .: " [11]. ἔτι δ᾽..."        -> "ἔτι δ᾽..."
  - mid-line concatenated:      "...traitors. [2] I..."   -> "...traitors. I..."
Preserves:
  - ellipsis lacunae:          " [7]... Ἀννίβας"          -> "... Ἀννίβας"
  - non-numeric brackets:      "the truth [in what...]"   -> unchanged
"""

import re
import sys
from pathlib import Path

BASE_DIR = Path(r"C:\Users\executor\AppData\Local\hermes\cache\documents\the_histories_translation")

MARKER = re.compile(r'\[\d+\]')
# A leading marker (optionally indented). A single stray punctuation mark glued
# to it (a period, comma, Greek semicolon/ano-teleia) is an extraction artifact
# and is dropped too -- but the first dot of an ellipsis "..." (a lacuna marker)
# is preserved.
LEAD_STRIP = re.compile(r'^\s*\[\d+\](?:\.(?!\.\.)|[,;·:])?[ \t]*')
# A mid-line marker: collapse the marker and the spaces around it to one space.
# Punctuation that may belong to the surrounding prose is left untouched.
MID_STRIP = re.compile(r'[ \t]*\[\d+\][ \t]*')
LEADING_MARKER = re.compile(r'^\s*\[\d+\]')
MULTISPACE = re.compile(r'[ \t]{2,}')


def clean_line(line: str):
    if not MARKER.search(line):
        return line, False
    new = line
    if LEADING_MARKER.match(new):
        new = LEAD_STRIP.sub('', new, count=1).lstrip()
    new = MID_STRIP.sub(' ', new)
    new = MULTISPACE.sub(' ', new).rstrip()
    return new, (new != line)


def clean_text(text: str):
    out_lines = []
    changed = False
    for line in text.split('\n'):
        new, ch = clean_line(line)
        changed = changed or ch
        out_lines.append(new)
    result = '\n'.join(out_lines)
    # collapse any 3+ consecutive newlines that could result from emptied lines
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result, changed


def main(apply: bool):
    md_files = sorted(BASE_DIR.rglob('*.md'))
    changed_files = []
    preview_budget = 25
    for path in md_files:
        original = path.read_text(encoding='utf-8')
        cleaned, changed = clean_text(original)
        if not changed:
            continue
        changed_files.append(path)
        if not apply and preview_budget > 0:
            # show a few representative before/after line diffs
            orig_lines = original.split('\n')
            new_lines = cleaned.split('\n')
            shown = 0
            print(f"\n--- {path.relative_to(BASE_DIR)} ---")
            for o, n in zip(orig_lines, new_lines):
                if o != n and shown < 2:
                    print(f"  - {o[:140]}")
                    print(f"  + {n[:140]}")
                    shown += 1
                    preview_budget -= 1
                if preview_budget <= 0:
                    break
        if apply:
            path.write_text(cleaned, encoding='utf-8')

    # verify no numeric markers remain (only when applying)
    print(f"\n{'APPLIED' if apply else 'DRY-RUN'}: {len(changed_files)} file(s) "
          f"{'modified' if apply else 'would change'}.")
    if apply:
        remaining = 0
        for path in md_files:
            remaining += len(MARKER.findall(path.read_text(encoding='utf-8')))
        print(f"Remaining [N] markers across all .md files: {remaining}")


if __name__ == '__main__':
    main(apply='--apply' in sys.argv)
