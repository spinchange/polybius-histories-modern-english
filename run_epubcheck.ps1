$ErrorActionPreference = 'Stop'

$Base = Split-Path -Parent $MyInvocation.MyCommand.Path
$Java = Join-Path $Base 'dist/tools/jdk-21.0.11+10-jre/bin/java.exe'
$Jar = Join-Path $Base 'dist/tools/epubcheck-5.3.0/epubcheck.jar'
$Epub = Join-Path $Base 'dist/polybius-the-histories-modern-english.epub'

if (-not (Test-Path -LiteralPath $Java)) {
    throw "Java runtime not found: $Java"
}

if (-not (Test-Path -LiteralPath $Jar)) {
    throw "EPUBCheck jar not found: $Jar"
}

if (-not (Test-Path -LiteralPath $Epub)) {
    throw "EPUB not found: $Epub"
}

& $Java -jar $Jar $Epub
