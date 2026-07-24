#!/usr/bin/env bash
set -u

WORKDIR='/c/Users/executor/AppData/Local/hermes/cache/documents/the_histories_translation'
cd "$WORKDIR"
mkdir -p translations

failures=()

translate_range() {
  local start="$1"
  local end="$2"
  local out
  out=$(printf 'translations/book_04_chapters_%02d_%02d.translation.md' "$start" "$end")
  if [[ -f "$out" ]]; then
    echo "SKIP $out"
    return 0
  fi
  local prompt
  prompt="In the current working directory, read source/book_04/chapter_$(printf '%02d' "$start").md through source/book_04/chapter_$(printf '%02d' "$end").md inclusive. Translate the Greek in full into clear modern English, using the old English only as a crib where it exists and not as final wording. If a chapter's English reference section says no matching English chapter is available in Perseus, translate directly from the Greek alone. Preserve markdown headings for each chapter and preserve bracketed section numbers like [2], [3]. Do not include the Greek text or the old English reference in the output. Write the finished translation to ${out} and then print a one-sentence confirmation with the output path."
  echo "START book=4 chapters=$start-$end -> $out"
  if ! claude -p "$prompt" --allowedTools 'Read,Write,Edit' --max-turns 16; then
    echo "FAIL book=4 chapters=$start-$end"
    failures+=("$start-$end")
    return 0
  fi
  echo "DONE book=4 chapters=$start-$end"
}

translate_range 5 8
translate_range 17 20
translate_range 29 32
translate_range 41 44
translate_range 53 56
translate_range 65 68
translate_range 77 80

if (( ${#failures[@]} > 0 )); then
  echo "BOOK4_WORKER2_FAILURES ${failures[*]}"
  exit 1
fi

echo 'BOOK4_WORKER2_DONE'
