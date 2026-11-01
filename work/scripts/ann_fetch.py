"""Download public-domain sources for the annotation layers (ANNOTATIONS_PLAN A2).

    python -I work/scripts/ann_fetch.py [--force] [NAME ...]

Writes plain text into annotations/sources/ and (re)writes MANIFEST.csv.
Downloads are untrusted data: this script only writes bytes to disk and never
imports, executes, or opens them with anything but a text decoder. Existing
files are skipped unless --force. Archive.org items resolve to their OCR text
(*_djvu.txt) via the metadata API.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "annotations" / "sources"
MANIFEST = SRC / "MANIFEST.csv"
FIELDS = ["file", "title", "author", "translator", "year", "url", "pd_basis",
          "pd_rationale", "layer_use", "status"]

GB = "https://www.gutenberg.org/cache/epub/{0}/pg{0}.txt"
IA = "ia:{0}"

# file, title, author, translator, year, url, pd_basis, rationale, use
SOURCES = [
    # --- readers ---
    ("plutarch_lives_v4_long_stewart.txt", "Plutarch's Lives, vol. 4", "Plutarch",
     "Aubrey Stewart & George Long", 1892, GB.format(44315), "pre-1930",
     "Long & Stewart tr. 1880-82; this printing London 1892", "readers: Brutus 4"),
    ("cicero_republic_featherstonhaugh_1829.txt", "The Republic of Cicero", "Cicero",
     "G. W. Featherstonhaugh", 1829, GB.format(54161), "pre-1930",
     "Published New York 1829", "readers: Cicero De Re Publica II"),
    ("cicero_de_officiis_miller_1913.txt", "De Officiis (Loeb)", "Cicero",
     "Walter Miller", 1913, GB.format(47001), "pre-1930",
     "Loeb Classical Library 1913", "readers: Cicero De Officiis III (Regulus)"),
    ("dionysius_literary_composition_roberts_1910.txt", "On Literary Composition", "Dionysius of Halicarnassus",
     "W. Rhys Roberts", 1910, IA.format("cu31924026465165"), "pre-1930",
     "London: Macmillan 1910 (title page OCR line ~374)", "readers: Dionysius De Comp. Verb. 4"),
    ("constantine_excerpta_v1_de_boor_1903.txt", "Excerpta historica iussu Constantini Porphyrogeniti, vol. 1 (De legationibus)",
     "Constantine VII (prooemium)", "(Greek original; tr. ours)", 1903,
     IA.format("ConstPorphExcerptaHistorica1.1DeBoor"), "our-translation",
     "Greek text ed. de Boor, Berlin 1903 (per archive.org metadata; title-page OCR illegible); our translation is CC0", "readers+survival: Excerpta prooemium"),
    ("machiavelli_discourses_thomson_1883.txt", "Discourses on the First Decade of Titus Livius", "Niccolò Machiavelli",
     "Ninian Hill Thomson", 1883, GB.format(10827), "pre-1930",
     "Published London 1883", "readers: Discourses I.2"),
    ("frederick_oeuvres_militaires_v1_preuss_1856.txt", "Oeuvres de Frédéric le Grand: Oeuvres militaires, vol. 1",
     "Frederick II", "(French original; tr. ours)", 1856, IA.format("bub_gb_9EBw8EMyjFYC"), "our-translation",
     "French text ed. Preuss, Berlin 1856; our translation is CC0", "readers: preface to Folard extract"),
    ("montesquieu_spirit_of_laws_v1_nugent_1899.txt", "The Spirit of Laws, vol. 1", "Montesquieu",
     "Thomas Nugent", 1899, IA.format("spiritoflaws01montuoft"), "pre-1930",
     "New York: Colonial Press 1899 (Nugent tr. 1750)", "readers: Spirit of Laws XI"),
    ("montesquieu_considerations_baker_1882.txt", "Considerations on the Causes of the Grandeur and Decadence of the Romans",
     "Montesquieu", "Jehu Baker", 1882, IA.format("cu31924028288722"), "pre-1930",
     "Published New York 1882", "readers: Considerations"),
    ("adams_works_v4_1851.txt", "The Works of John Adams, vol. 4 (Defence of the Constitutions, vol. 1)",
     "John Adams", "(ed. Charles Francis Adams)", 1851, IA.format("worksofjohnadams04adam"), "pre-1930",
     "Published Boston 1850-56", "readers: Defence I"),
    ("federalist_papers.txt", "The Federalist Papers", "Hamilton, Madison, Jay",
     "", 1788, GB.format(1404), "pre-1930",
     "Published 1787-88", "readers: Federalist 18"),
    # --- parallels ---
    ("livy_09_26_spillan_edmonds.txt", "The History of Rome, Books 9-26", "Livy",
     "D. Spillan & Cyrus Edmonds", 1849, GB.format(10907), "pre-1930",
     "Bohn's Classical Library 1849-50", "parallels: Livy 21-22, 26"),
    ("livy_27_36_edmonds.txt", "The History of Rome, Books 27-36", "Livy",
     "Cyrus Edmonds", 1850, GB.format(12582), "pre-1930",
     "Bohn's Classical Library 1850", "parallels: Livy 30, 33"),
    ("livy_37_end_mcdevitte.txt", "The History of Rome, Books 37 to the End", "Livy",
     "W. A. McDevitte", 1850, GB.format(44318), "pre-1930",
     "Bohn's Classical Library 1850", "parallels: Livy 37-38, 44-45"),
    ("plutarch_lives_v1_long_stewart.txt", "Plutarch's Lives, vol. 1", "Plutarch",
     "Aubrey Stewart & George Long", 1894, GB.format(14033), "pre-1930",
     "Long & Stewart tr. 1880-82; this printing London 1894", "parallels: Aemilius Paulus"),
    ("plutarch_lives_v2_long_stewart.txt", "Plutarch's Lives, vol. 2", "Plutarch",
     "Aubrey Stewart & George Long", 1899, GB.format(14114), "pre-1930",
     "Long & Stewart tr. 1880-82; this printing London 1899", "parallels: Marcellus, Cato Major, Philopoemen, Flamininus"),
    ("appian_roman_history_v1_white_1899.txt", "The Roman History of Appian of Alexandria, vol. 1", "Appian",
     "Horace White", 1899, IA.format("romanhistoryapp01whitgoog"), "pre-1930",
     "Published New York/London 1899", "parallels+survival: Punica 127-132"),
]


def curl(url: str, out: Path | None = None) -> bytes:
    args = ["curl", "-sSfL", "-m", "300", "--retry", "2", "-A", "Mozilla/5.0 (pragmatikehistoria A2)", url]
    if out:
        args += ["-o", str(out)]
    return subprocess.run(args, check=True, capture_output=True).stdout


def resolve(url: str) -> str:
    if not url.startswith("ia:"):
        return url
    ident = url[3:]
    meta = json.loads(curl(f"https://archive.org/metadata/{ident}"))
    txt = [f["name"] for f in meta.get("files", []) if f["name"].endswith("_djvu.txt")]
    if not txt:
        raise RuntimeError(f"{ident}: no _djvu.txt OCR file")
    return f"https://archive.org/download/{ident}/{txt[0]}"


def main(argv: list[str]) -> int:
    force = "--force" in argv
    only = {a for a in argv if not a.startswith("--")}
    SRC.mkdir(parents=True, exist_ok=True)
    old = {}
    if MANIFEST.exists():
        with open(MANIFEST, encoding="utf-8", newline="") as f:
            old = {r["file"]: r for r in csv.DictReader(f)}
    rows, failed = [], 0
    for (fn, title, author, tr, year, url, basis, why, use) in SOURCES:
        dest = SRC / fn
        real = url
        if (not only or fn in only) and (force or not dest.exists()):
            try:
                real = resolve(url)
                tmp = dest.with_suffix(".part")
                curl(real, tmp)
                tmp.replace(dest)
                print(f"ok    {fn}  ({dest.stat().st_size // 1024} KB)")
            except Exception as e:  # report and continue
                failed += 1
                print(f"FAIL  {fn}: {e}")
        elif fn in old:
            real = old[fn]["url"]
        status = old.get(fn, {}).get("status", "") if dest.exists() else "MISSING"
        rows.append(dict(zip(FIELDS, [fn, title, author, tr, year, real, basis, why, use, status])))
    with open(MANIFEST, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows) - failed}/{len(rows)} present; manifest: {MANIFEST.relative_to(ROOT)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
