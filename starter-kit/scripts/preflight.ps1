param([switch]$DocsOnly)

$ErrorActionPreference = "Stop"
$root = (git rev-parse --show-toplevel 2>$null)
if (-not $root) { throw "Run inside a Git repository" }
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
if ($DocsOnly) {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Error "BLOCKED: documentation scope check requires Node" -ErrorAction Continue
        exit 2
    }
    node (Join-Path $PSScriptRoot 'lib/preflight-docs.mjs')
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "[preflight] PASS: documentation scope and Git whitespace only; code/AE checks: NOT RUN"
    exit 0
}

$checksRun = 0
if (Test-Path "package.json") {
    if (-not (Get-Command node -ErrorAction SilentlyContinue) -or -not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Error "BLOCKED: package.json requires Node/npm to determine project checks" -ErrorAction Continue
        exit 2
    }
    $hasCheck = node -e "const p=JSON.parse(require('node:fs').readFileSync('package.json','utf8')); process.stdout.write(typeof p.scripts?.check === 'string' && p.scripts.check.trim() ? 'yes':'no')"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($hasCheck -eq "yes") {
        Write-Host "[preflight] npm run check"
        npm run check
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        $checksRun++
    } else {
        Write-Host "[preflight] project npm check: NOT RUN (no nonempty scripts.check)"
    }
}
if (Test-Path "scripts/project-preflight.ps1") {
    Write-Host "[preflight] scripts/project-preflight.ps1"
    $global:LASTEXITCODE = 0
    & "scripts/project-preflight.ps1"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $checksRun++
}
if ($checksRun -eq 0) {
    Write-Error "[preflight] BLOCKED: no project checks ran; configure scripts.check or a project-preflight hook" -ErrorAction Continue
    Write-Host "NOTE: use -DocsOnly only for a verified documentation-only change."
    exit 2
}
Write-Host "[preflight] PASS: $checksRun configured project check command(s) completed"
Write-Host "NOTE: command success does not establish acceptance coverage. Runtime AE, compatibility and release gates remain separate unless project-preflight runs them explicitly."
