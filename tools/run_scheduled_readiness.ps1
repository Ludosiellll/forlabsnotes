[CmdletBinding()]
param(
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"
$powerShellExecutable = (Get-Process -Id $PID).Path

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent $PSScriptRoot
}

$localDir = Join-Path $Root ".local"
if (-not (Test-Path -LiteralPath $localDir)) {
    New-Item -ItemType Directory -Force -Path $localDir | Out-Null
}
$logPath = Join-Path $localDir "readiness-scheduled.log"

# Rotate the transcript log if it grows beyond ~512 KB so it never bloats.
if ((Test-Path -LiteralPath $logPath) -and ((Get-Item -LiteralPath $logPath).Length -gt 524288)) {
    Move-Item -LiteralPath $logPath -Destination "$logPath.old" -Force
}

$stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
Add-Content -Encoding UTF8 -Path $logPath -Value "[$stamp] scheduled readiness run: start"

$readinessScript = Join-Path $Root "tools/check_ai_os_readiness.ps1"
# No -ExecutionPolicy override: CurrentUser policy (RemoteSigned) already allows
# local scripts, and a scheduled task should not weaken the policy it runs under.
$output = & $powerShellExecutable -NoProfile -File $readinessScript -Root $Root
$exitCode = $LASTEXITCODE

foreach ($line in @($output)) {
    Add-Content -Encoding UTF8 -Path $logPath -Value ("  " + $line)
}

$stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
Add-Content -Encoding UTF8 -Path $logPath -Value "[$stamp] scheduled readiness run: end exit=$exitCode"

exit $exitCode
