[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Agent,
    [Parameter(Mandatory = $true)][string]$Task,
    [string[]]$Actions = @(),
    [string]$Checks = "",
    [string[]]$Risks = @(),
    [string]$Value = "",
    [string]$Root = ""
)

# Appends ONE JSON line describing a finished agent task to the unified event
# journal (.local/agent-events.ndjson). Any agent (Claude, Codex, Cursor, ...)
# calls this at end-of-task per the workflow protocol; the Control Center
# dashboard renders the journal. Never put secrets or private data here.

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent $PSScriptRoot
}

$localDir = Join-Path $Root ".local"
if (-not (Test-Path -LiteralPath $localDir)) {
    New-Item -ItemType Directory -Force -Path $localDir | Out-Null
}
$journal = Join-Path $localDir "agent-events.ndjson"

# Rotate at ~2 MB so a long-lived journal never bloats.
if ((Test-Path -LiteralPath $journal) -and ((Get-Item -LiteralPath $journal).Length -gt 2097152)) {
    Move-Item -LiteralPath $journal -Destination "$journal.old" -Force
}

$checksMap = @{}
foreach ($pair in ($Checks -split ',')) {
    $kv = $pair -split '=', 2
    if ($kv.Count -eq 2 -and $kv[0].Trim()) { $checksMap[$kv[0].Trim()] = $kv[1].Trim() }
}

$event = [ordered]@{
    time    = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    agent   = $Agent
    task    = $Task
    actions = @($Actions)
    checks  = $checksMap
    risks   = @($Risks)
    value   = $Value
}

Add-Content -Encoding UTF8 -Path $journal -Value (($event | ConvertTo-Json -Compress -Depth 4))
Write-Output "Event logged to .local/agent-events.ndjson"
exit 0
