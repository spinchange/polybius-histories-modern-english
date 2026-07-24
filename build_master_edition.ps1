$ErrorActionPreference = 'Stop'

$Base = Split-Path -Parent $MyInvocation.MyCommand.Path
$OutPath = Join-Path $Base 'Polybius_Histories_Extant_Works_modern_English.md'
$EditorialPath = Join-Path $Base 'EDITORIAL_NOTE.md'

$bookFiles = Get-ChildItem -Path $Base -Filter 'Polybius_Histories_Book_*_modern_English.md' |
    Sort-Object Name

if ($bookFiles.Count -ne 39) {
    throw "Expected 39 assembled book files, found $($bookFiles.Count)."
}

$parts = New-Object System.Collections.Generic.List[string]
$parts.Add('# Polybius - The Histories')
$parts.Add('')
$parts.Add('Modern English translation of the extant local source corpus.')
$parts.Add('')

if (Test-Path -LiteralPath $EditorialPath) {
    $editorial = [System.IO.File]::ReadAllText($EditorialPath, [System.Text.Encoding]::UTF8)
    $parts.Add($editorial.Trim())
    $parts.Add('')
}

foreach ($file in $bookFiles) {
    $parts.Add('')
    $parts.Add('---')
    $parts.Add('')
    $parts.Add(([System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)).Trim())
    $parts.Add('')
}

[System.IO.File]::WriteAllText($OutPath, ($parts -join [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false))

Get-Item -LiteralPath $OutPath | Select-Object FullName, Length, LastWriteTime
