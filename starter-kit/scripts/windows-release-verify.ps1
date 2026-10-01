param(
    [Parameter(Mandatory=$true)][string]$Target,
    [string]$Output = "windows-release-verify.txt",
    [switch]$LocalCheck
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $Target)) {
    throw "Target not found: $Target"
}

$resolved = (Resolve-Path $Target).Path
if (Test-Path $Output) { throw "Evidence output exists" }
$lines = New-Object System.Collections.Generic.List[string]
$fail = $false

$lines.Add("# Windows release verification evidence")
$lines.Add("target=$resolved")
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
    if ($sig.Status -eq "Valid") { $lines.Add("timestamp=PASS") }
    else { $lines.Add("timestamp=BLOCKED (signature validation failed)"); $fail = $true }
} else {
    $lines.Add("timestamp_subject=missing_or_unavailable")
    if ($LocalCheck) { $lines.Add("timestamp=NOT RUN (local mode)") }
    else { $lines.Add("timestamp=BLOCKED"); $fail = $true }
}
if ($sig.Status -ne "Valid") {
    $fail = $true
}

$lines.Add("")
$lines.Add("## Internet zone metadata")
try {
    $zone = Get-Content -Path $resolved -Stream Zone.Identifier -ErrorAction Stop
    $lines.AddRange([string[]]$zone)
} catch {
    $lines.Add("Zone.Identifier not present or not readable.")
    $lines.Add("NOTE: a public distribution check should use the actual downloaded file when validating delivery behavior.")
}

$lines.Add("")
$lines.Add("## SmartScreen")
$lines.Add("NOT AUTOMATICALLY VERIFIED: SmartScreen reputation is external/reputation-dependent and requires a real target-environment distribution test.")

# CreateNew also rejects a destination created after the initial existence check.
$outputPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Output)
$stream = [System.IO.File]::Open($outputPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
$writer = [System.IO.StreamWriter]::new($stream, [System.Text.UTF8Encoding]::new($true))
try { foreach ($line in $lines) { $writer.WriteLine($line) } }
finally { $writer.Dispose() }
Get-Content $Output

if ($fail) {
    throw "Windows release verification failed: signature or required timestamp is not verified."
}

Write-Host "PASS: selected signature/hash/timestamp checks passed."
Write-Host "NOTE: still requires clean install -> After Effects load -> smoke test on target Windows."
