[CmdletBinding()]
param(
    [string]$Root = ""
)

# Builds an ANONYMIZED feedback report about the OS layer that the user can
# send to the template author. Includes: template version, check names and
# statuses (no details - details may contain local paths), check-history
# counters, and the System_Proposals note verbatim. Contains NO note content,
# NO project file paths and NO secrets. The user reviews the file before
# sending it - nothing is transmitted automatically.

$ErrorActionPreference = "Stop"
$powerShellExecutable = (Get-Process -Id $PID).Path

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent $PSScriptRoot
}

$localDir = Join-Path $Root ".local"
if (-not (Test-Path -LiteralPath $localDir)) {
    New-Item -ItemType Directory -Force -Path $localDir | Out-Null
}
$reportPath = Join-Path $localDir "feedback-report.md"

# Template version = first version heading in CHANGELOG.md.
$version = "unknown"
$changelogPath = Join-Path $Root "CHANGELOG.md"
if (Test-Path -LiteralPath $changelogPath) {
    $m = [regex]::Match((Get-Content -Raw -Encoding UTF8 -Path $changelogPath), '##\s*([0-9]+\.[0-9]+\.[0-9]+)')
    if ($m.Success) { $version = $m.Groups[1].Value }
}

# Fresh readiness run; keep only "name + status" columns from the tables.
$readinessScript = Join-Path $Root "tools/check_ai_os_readiness.ps1"
$raw = & $powerShellExecutable -NoProfile -File $readinessScript -Root $Root
$checkLines = @($raw | Where-Object { $_ -match '^\s*[a-z][\w.-]*\s+(OK|WARN|FAIL|SKIP)\b' } | ForEach-Object {
    $parts = ($_ -replace '\s+', ' ').Trim() -split ' '
    "{0}: {1}" -f $parts[0], $parts[1]
})

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# AI OS Template - Feedback Report")
$lines.Add("")
$lines.Add("Generated: " + (Get-Date).ToString("yyyy-MM-dd HH:mm"))
$lines.Add("Template version: $version")
$lines.Add("OS: " + [System.Environment]::OSVersion.VersionString)
$lines.Add("")
$lines.Add("## Check results (names and statuses only)")
$lines.Add("")
foreach ($l in $checkLines) { $lines.Add("- " + $l) }
$lines.Add("")
$lines.Add("## Check history (summary counters, last 10 runs each)")
$lines.Add("")
foreach ($log in @("readiness-check.log", "health-check.log")) {
    $p = Join-Path $localDir $log
    if (Test-Path -LiteralPath $p) {
        $lines.Add("### $log")
        foreach ($l in (Get-Content -Encoding UTF8 -Path $p | Select-Object -Last 10)) { $lines.Add($l) }
        $lines.Add("")
    }
}
$lines.Add("## System proposals")
$lines.Add("")
$proposalsPath = Join-Path $Root "60_Tasks/System_Proposals.md"
if (Test-Path -LiteralPath $proposalsPath) {
    foreach ($l in (Get-Content -Encoding UTF8 -Path $proposalsPath)) { $lines.Add($l) }
} else {
    $lines.Add("(System_Proposals.md not found)")
}
$lines.Add("")
$lines.Add("---")
$lines.Add("This report was generated locally by tools/make_feedback_report.ps1.")
$lines.Add("It contains no note content, no project file paths and no secrets - but REVIEW IT before sending.")

Set-Content -Encoding UTF8 -Path $reportPath -Value ($lines -join [Environment]::NewLine)
Write-Output "Feedback report written to: $reportPath"
Write-Output "Review it, then send the file to the person who provided this template."
exit 0
