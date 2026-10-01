param(
    [string]$OutputDir = ".artifacts/dependencies"
)

$ErrorActionPreference = "Stop"

$root = (git rev-parse --show-toplevel 2>$null)
if (-not $root) { throw "Run inside a Git repository" }

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$runId = [guid]::NewGuid().ToString()
$report = Join-Path $OutputDir "dependency-evidence-$stamp-$runId.txt"

$names = @(
    "package.json","package-lock.json","npm-shrinkwrap.json","pnpm-lock.yaml","yarn.lock",
    "Cargo.toml","Cargo.lock","requirements.txt","requirements-dev.txt","poetry.lock",
    "Pipfile","Pipfile.lock","pyproject.toml","vcpkg.json","vcpkg-lock.json",
    "conanfile.txt","conanfile.py","conan.lock"
)

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# Dependency evidence")
$lines.Add("utc=$stamp")
$lines.Add("run_id=$runId")
$lines.Add("repo=$root")
$lines.Add("commit=$(git -C $root rev-parse HEAD)")
$lines.Add("")
$lines.Add("## Manifest / lockfile hashes")

$files = Get-ChildItem -Path $root -Recurse -File |
    Where-Object { $names -contains $_.Name -and $_.FullName -notmatch '\\(node_modules|target|\.git)\\' } |
    Sort-Object FullName

if ($files.Count -eq 0) {
    $lines.Add("No known dependency manifest/lockfile found.")
} else {
    foreach ($file in $files) {
        $hash = Get-FileHash -Algorithm SHA256 $file.FullName
        $lines.Add("$($hash.Hash)  $($file.FullName)")
    }
}

$lines.Add("")
$lines.Add("## Tool availability")
foreach ($tool in @("npm","cargo","python","pip","pip-audit","osv-scanner","syft")) {
    $cmd = Get-Command $tool -ErrorAction SilentlyContinue
    if ($cmd) { $lines.Add("$tool=$($cmd.Source)") } else { $lines.Add("$tool=NOT_FOUND") }
}

$lines.Add("")
$lines.Add("## Notes")
$lines.Add("This inventories local dependency sources only.")
$lines.Add("Run an ecosystem-appropriate vulnerability scanner separately and record PASS/FAIL/BLOCKED/NOT RUN/N/A.")
$lines.Add("For public dependency-heavy products, generate an SPDX or CycloneDX SBOM where practical.")

$outputPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($report)
$stream = [System.IO.File]::Open($outputPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
$writer = [System.IO.StreamWriter]::new($stream, [System.Text.UTF8Encoding]::new($true))
try { foreach ($line in $lines) { $writer.WriteLine($line) } }
finally { $writer.Dispose() }
Get-Content $report
Write-Host "Evidence: $report"
