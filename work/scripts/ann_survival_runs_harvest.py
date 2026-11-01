"""Harvest CANDIDATE source-note lines for survival-run entries (ANNOTATIONS_PLAN A5, option b).

Reads an OCR file of a critical edition (untrusted data; never executed) between two
1-based line numbers and prints every line that looks like an excerpt source note,
tolerating the OCR spellings Exc./Exe./Exo./Exoc./Exc./Ewerpt./Exterpt., Cod. Urb.,
Suidas, Athenaeus, Steph. Byz., cod. Wescheri, and the 'FRAGMENTA LIBRI' / 'RES ...'
section headers. Output is candidates only: a human (and Opus) assigns each note to
chapters. Run with `python -I`.

    python -I ann_survival_runs_harvest.py OCR_FILE FIRST_LINE LAST_LINE [> out.txt]
"""
import re
import sys

NOTE_RE = re.compile(
    r"(?:\[|\|)?\s*(?:E[xXeEoOΕχ]+[cCoOο]*\.?|Ewerpt|Exterpt|Excerpt)[\w. ]{0,6}"
    r"(?:Peir|Vat|Val|De legat|antiq|ant\.)"
    r"|[Cc]od\.? ?[Uu]rb|Urb\. fol|\(?exc\.? ?ant|[Cc]od\. Wescher|Suidas v\.|Athenaeus [IVX]+|Athen\. [IVX]+"
    r"|Steph\. Byz|Strab\.? [IVX\d]|Ecloga|desinunt Exc|post unius foli|FRAGMENTA LIBRI|^\s*[IVX]+\.\s+(?:RES|EX )"
)


def main(argv):
    path, a, b = argv[0], int(argv[1]), int(argv[2])
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    sys.stdout.reconfigure(encoding="utf-8")
    for i in range(a - 1, min(b, len(lines))):
        if NOTE_RE.search(lines[i]):
            print(f"{i + 1}\t{lines[i].strip()[:150]}")


if __name__ == "__main__":
    main(sys.argv[1:])
