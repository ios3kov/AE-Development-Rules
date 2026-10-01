param(
    [Parameter(Mandatory=$true)][string]$Target,
    [string]$Output = "windows-binary-audit.txt"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $Target)) {
    throw "Target not found: $Target"
}

$resolved = (Resolve-Path $Target).Path
if (Test-Path $Output) { throw "Evidence output exists" }
$lines = New-Object System.Collections.Generic.List[string]
$collectionStatus = "COMPLETE"

$lines.Add("# Windows binary compatibility evidence")
$lines.Add("target=$resolved")
$lines.Add("")

$lines.Add("## file")
$item = Get-Item $resolved
$lines.Add("length=$($item.Length)")
$lines.Add("last_write_utc=$($item.LastWriteTimeUtc.ToString('o'))")
$lines.Add("")

$lines.Add("## SHA-256")
$hash = Get-FileHash -Algorithm SHA256 $resolved
$lines.Add($hash.Hash)
$lines.Add("")

$lines.Add("## Authenticode")
$sig = Get-AuthenticodeSignature $resolved
$lines.Add("status=$($sig.Status)")
$lines.Add("status_message=$($sig.StatusMessage)")
if ($sig.SignerCertificate) {
    $lines.Add("subject=$($sig.SignerCertificate.Subject)")
    $lines.Add("thumbprint=$($sig.SignerCertificate.Thumbprint)")
}
if ($sig.TimeStamperCertificate) {
    $lines.Add("timestamp_subject=$($sig.TimeStamperCertificate.Subject)")
}
$lines.Add("")

$dumpbin = Get-Command dumpbin.exe -ErrorAction SilentlyContinue
if ($dumpbin) {
    $lines.Add("## PE headers")
    $headers = & $dumpbin.Source /headers $resolved 2>&1
    $headersExit = $LASTEXITCODE
    $lines.AddRange([string[]]$headers)
    $lines.Add("headers_exit=$headersExit")
    if ($headersExit -ne 0) { $collectionStatus = "PARTIAL" }
    $lines.Add("")
    $lines.Add("## dependencies")
    $deps = & $dumpbin.Source /dependents $resolved 2>&1
    $depsExit = $LASTEXITCODE
    $lines.AddRange([string[]]$deps)
    $lines.Add("dependencies_exit=$depsExit")
    if ($depsExit -ne 0) { $collectionStatus = "PARTIAL" }
} else {
    $lines.Add("## PE headers / dependencies")
    $lines.Add("BLOCKED: dumpbin.exe not found. Run from a Visual Studio Developer shell or provide equivalent PE/dependency evidence.")
    $collectionStatus = "PARTIAL"
}

$lines.Add("")
$lines.Add("## Collection status")
$lines.Add("collection_status=$collectionStatus")
$lines.Add("audit_verdict=NOT_ASSIGNED")

# CreateNew also rejects a destination created after the initial existence check.
$outputPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Output)
$stream = [System.IO.File]::Open($outputPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
$writer = [System.IO.StreamWriter]::new($stream, [System.Text.UTF8Encoding]::new($true))
try { foreach ($line in $lines) { $writer.WriteLine($line) } }
finally { $writer.Dispose() }
Write-Host "Evidence: $Output"
Write-Host "Evidence collection: $collectionStatus"
Write-Host "NOTE: exit code 0 means evidence collection completed; it does not mean Compatibility: PASS/VERIFIED."

if ($collectionStatus -ne "COMPLETE") { exit 2 }
