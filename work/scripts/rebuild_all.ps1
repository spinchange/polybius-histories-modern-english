# Rebuild chain: master edition -> EPUB -> HTML -> 6x9 print PDFs (Typst) -> EPUBCheck.  Run at the end of every phase.
# Book files (Polybius_Histories_Book_NN_*.md) are the source of truth and are NOT regenerated here
# (the assemble_/extract_ scripts point at an external Hermes cache path).
$ErrorActionPreference = 'Stop'
$Root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
Push-Location $Root
try {
    & (Join-Path $Root 'build_master_edition.ps1')
    python (Join-Path $Root 'build_epub.py');  if ($LASTEXITCODE) { throw 'build_epub.py failed' }
    python (Join-Path $Root 'build_html.py');  if ($LASTEXITCODE) { throw 'build_html.py failed' }
    python (Join-Path $Root 'build_print.py'); if ($LASTEXITCODE) { throw 'build_print.py failed' }
    & (Join-Path $Root 'run_epubcheck.ps1') 2>&1 | Tee-Object -Variable check
    $check | Out-File (Join-Path $Root 'work\reports\epubcheck_last.txt') -Encoding utf8
    if ($LASTEXITCODE) { throw "epubcheck exit code $LASTEXITCODE" }
} finally { Pop-Location }
