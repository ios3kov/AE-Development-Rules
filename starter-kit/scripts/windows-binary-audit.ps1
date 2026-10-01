param(
    [Parameter(Mandatory=$true)][string]$Target,
    [string]$Output = "windows-binary-audit.txt"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $Target)) {
    throw "Target not found: $Target"
}

$resolved = (Resolve-Path $Target).Path
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
    $lines.AddRange([string[]]$headers)
    $lines.Add("")
    $lines.Add("## dependencies")
    $deps = & $dumpbin.Source /dependents $resolved 2>&1
    $lines.AddRange([string[]]$deps)
} else {
    $lines.Add("## PE headers / dependencies")
    $lines.Add("BLOCKED: dumpbin.exe not found. Run from a Visual Studio Developer shell or provide equivalent PE/dependency evidence.")
    $collectionStatus = "PARTIAL"
}

$lines.Add("")
$lines.Add("## Collection status")
$lines.Add("collection_status=$collectionStatus")
$lines.Add("audit_verdict=NOT_ASSIGNED")

$lines | Set-Content -Encoding UTF8 $Output
Write-Host "Evidence: $Output"
Write-Host "Evidence collection: $collectionStatus"
Write-Host "NOTE: exit code 0 means evidence collection completed; it does not mean Compatibility: PASS/VERIFIED."
