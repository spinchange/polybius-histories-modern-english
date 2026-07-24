#!/usr/bin/env bash
set -u

if [[ $# -lt 2 ]]; then
  echo "usage: bash run_polybius_translation_ranges.sh <book_number> <start-end> [<start-end> ...]"
  exit 2
fi

BOOK="$1"
shift

WORKDIR='/c/Users/executor/AppData/Local/hermes/cache/documents/the_histories_translation'
cd "$WORKDIR"
mkdir -p translations

failures=()

translate_range() {
  local start="$1"
  local end="$2"
  local out
  out=$(printf 'translations/book_%02d_chapters_%02d_%02d.translation.md' "$BOOK" "$start" "$end")
  if [[ -f "$out" ]]; then
    echo "SKIP $out"
    return 0
  fi
  local prompt
  prompt="In the current working directory, read source/book_$(printf '%02d' "$BOOK")/chapter_$(printf '%02d' "$start").md through source/book_$(printf '%02d' "$BOOK")/chapter_$(printf '%02d' "$end").md inclusive. Translate the Greek in full into clear modern English, using the old English only as a crib where it exists and not as final wording. If a chapter's English reference section says no matching English chapter is available in Perseus, translate directly from the Greek alone. Preserve markdown headings for each chapter and preserve bracketed section numbers like [2], [3]. Do not include the Greek text or the old English reference in the output. Write the finished translation to ${out} and then print a one-sentence confirmation with the output path."
  echo "START book=$BOOK chapters=$start-$end -> $out"
  if ! claude -p "$prompt" --allowedTools 'Read,Write,Edit' --max-turns 16; then
    echo "FAIL book=$BOOK chapters=$start-$end"
    failures+=("$start-$end")
  else
    echo "DONE book=$BOOK chapters=$start-$end"
  fi
}

for range in "$@"; do
  start="${range%-*}"
  end="${range#*-}"
  translate_range "$start" "$end"
done

if (( ${#failures[@]} > 0 )); then
  echo "TRANSLATION_FAILURES book=$BOOK ${failures[*]}"
  exit 1
fi

echo "TRANSLATION_DONE book=$BOOK"
