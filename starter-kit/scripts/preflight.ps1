param()

$ErrorActionPreference = "Stop"

$root = (git rev-parse --show-toplevel 2>$null)
if (-not $root) {
    throw "Run inside a Git repository"
}

Set-Location $root

Write-Host "[preflight] git diff"
git diff --check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
git diff --cached --check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if ($env:AE_PREFLIGHT_BASE_REF) {
    git rev-parse --verify "$($env:AE_PREFLIGHT_BASE_REF)^{commit}" | Out-Null
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    git diff --check "$($env:AE_PREFLIGHT_BASE_REF)...HEAD"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if (Test-Path "package.json") {
    if (-not (Get-Command node -ErrorAction SilentlyContinue) -or -not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "BLOCKED: package.json requires Node/npm to determine project checks"
    }
    $hasCheck = node -e "const p=require('./package.json'); process.stdout.write(p.scripts&&p.scripts.check?'yes':'no')"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($hasCheck -eq "yes") {
        Write-Host "[preflight] npm run check"
        npm run check
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } else {
        Write-Host "[preflight] package.json has no check script; skipping npm project check"
    }
}

if (Test-Path "scripts/project-preflight.ps1") {
    Write-Host "[preflight] scripts/project-preflight.ps1"
    $global:LASTEXITCODE = 0
    & "scripts/project-preflight.ps1"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "[preflight] PASS"
Write-Host "NOTE: runtime AE, compatibility and release gates remain separate unless project-preflight runs them explicitly."
