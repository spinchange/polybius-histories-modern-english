#!/usr/bin/env bash
set -euo pipefail

WORKDIR='/c/Users/executor/AppData/Local/hermes/cache/documents/the_histories_translation'
cd "$WORKDIR"
mkdir -p translations

translate_range() {
  local book="$1"
  local start="$2"
  local end="$3"
  local out
  out=$(printf 'translations/book_%02d_chapters_%02d_%02d.translation.md' "$book" "$start" "$end")
  if [[ -f "$out" ]]; then
    echo "SKIP $out"
    return 0
  fi
  local source_dir
  source_dir=$(printf 'source/book_%02d' "$book")
  local prompt
  prompt="In the current working directory, read ${source_dir}/chapter_$(printf '%02d' "$start").md through ${source_dir}/chapter_$(printf '%02d' "$end").md inclusive. Translate the Greek in full into clear modern English, using the old English only as a crib and not as final wording. Preserve markdown headings for each chapter and preserve bracketed section numbers like [2], [3]. Do not include the Greek text or the old English reference in the output. Write the finished translation to ${out} and then print a one-sentence confirmation with the output path."
  echo "START book=$book chapters=$start-$end -> $out"
  claude -p "$prompt" --allowedTools 'Read,Write,Edit' --max-turns 12
  echo "DONE  book=$book chapters=$start-$end"
}

# Remaining Book 1 ranges
translate_range 1 19 21
translate_range 1 36 42
translate_range 1 43 49
translate_range 1 50 56
translate_range 1 57 63
translate_range 1 64 70
translate_range 1 71 77
translate_range 1 78 84
translate_range 1 85 88

# All Book 2 ranges
translate_range 2 1 7
translate_range 2 8 14
translate_range 2 15 21
translate_range 2 22 28
translate_range 2 29 35
translate_range 2 36 42
translate_range 2 43 49
translate_range 2 50 56
translate_range 2 57 63
translate_range 2 64 71

echo 'ALL_TRANSLATIONS_DONE'
