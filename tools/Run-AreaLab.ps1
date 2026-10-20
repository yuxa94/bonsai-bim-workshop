param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$labPublic = Split-Path -Parent $PSScriptRoot
$labVenv = Join-Path $PSScriptRoot '.area-venv'
$labPython = Join-Path $labVenv 'Scripts/python.exe'
if (-not (Test-Path -LiteralPath $labPython)) {
    & $Python -m venv $labVenv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.10+ is required. Ask Codex to install Python, then run again.' }
}
& $labPython -c "import importlib.util,sys; sys.exit(0 if all(importlib.util.find_spec(x) for x in ('ifcopenshell','numpy','shapely')) else 1)"
if ($LASTEXITCODE -ne 0) {
    & $labPython -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Keep the error and ask Codex to diagnose it.' }
}
$labOutput = Join-Path $labPublic ('area-results-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0,4))
& $labPython (Join-Path $PSScriptRoot 'area_extract.py') (Join-Path $labPublic 'area-lab/inputs/25B.ifc') (Join-Path $labPublic 'area-lab/inputs/A32-05.ifc') --out $labOutput
if ($LASTEXITCODE -ne 0) { throw 'Extraction stopped. Read the specific error above.' }
Write-Host ('Open report: ' + (Join-Path $labOutput 'review.html'))
Write-Host ('Import into Excel: ' + (Join-Path $labOutput 'objects.csv'))
