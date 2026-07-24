#!/usr/bin/env bash
set -euo pipefail

WORKDIR='/c/Users/executor/AppData/Local/hermes/cache/documents/the_histories_translation'
cd "$WORKDIR"
mkdir -p translations

translate_range() {
  local start="$1"
  local end="$2"
  local out
  out=$(printf 'translations/book_03_chapters_%02d_%02d.translation.md' "$start" "$end")
  if [[ -f "$out" ]]; then
    echo "SKIP $out"
    return 0
  fi
  local prompt
  prompt="In the current working directory, read source/book_03/chapter_$(printf '%02d' "$start").md through source/book_03/chapter_$(printf '%02d' "$end").md inclusive. Translate the Greek in full into clear modern English, using the old English only as a crib and not as final wording. Preserve markdown headings for each chapter and preserve bracketed section numbers like [2], [3]. Do not include the Greek text or the old English reference in the output. Write the finished translation to ${out} and then print a one-sentence confirmation with the output path."
  echo "START book=3 chapters=$start-$end -> $out"
  claude -p "$prompt" --allowedTools 'Read,Write,Edit' --max-turns 12
  echo "DONE book=3 chapters=$start-$end"
}

translate_range 1 7
translate_range 8 14
translate_range 15 21
translate_range 22 28
translate_range 29 35
translate_range 36 42
translate_range 43 49
translate_range 50 56
translate_range 57 63
translate_range 64 70
translate_range 71 77
translate_range 78 84
translate_range 85 87

echo 'BOOK3_TRANSLATIONS_DONE'
