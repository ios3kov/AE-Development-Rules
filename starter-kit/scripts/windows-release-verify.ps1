[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)][string]$Target,
    [Parameter(Mandatory=$true, Position=1)][string]$EvidenceDirectory
)

$ErrorActionPreference = "Stop"

# Record before verification; never reuse a destination or alter the payload.
& node (Join-Path $PSScriptRoot "record-artifact.mjs") $Target $EvidenceDirectory
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& node (Join-Path $PSScriptRoot "verify-artifact.mjs") $Target (Join-Path $EvidenceDirectory "artifact-record.json")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "PASS: recorded artifact integrity only."
Write-Host "host_load=NOT_RUN"
Write-Host "installation=NOT_RUN"
Write-Host "NOTE: selected-channel download, documented installation and actual host load require separate evidence."
