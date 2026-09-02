[CmdletBinding()]
param(
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

function Test-ScriptRejectsSingleFailure {
    param(
        [string]$Name,
        [string]$ScriptPath,
        [string[]]$ExtraArgs = @()
    )

    $args = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", $ScriptPath,
        "-Root", $Root
    ) + $ExtraArgs + @("-TestInjectFailure")

    $output = @(& powershell.exe @args 2>&1)
    $exitCode = $LASTEXITCODE
    $text = $output -join "`n"

    if ($text -notmatch "test-injected") {
        throw "$Name did not execute the injected single-FAIL check. Exit=$exitCode"
    }
    if ($exitCode -ne 1) {
        throw "$Name returned exit $exitCode for exactly one injected FAIL; expected 1."
    }

    Write-Host "PASS $Name rejects one FAIL with exit 1"
}

Test-ScriptRejectsSingleFailure `
    -Name "check_agent_health.ps1" `
    -ScriptPath (Join-Path $Root "tools/check_agent_health.ps1")

Test-ScriptRejectsSingleFailure `
    -Name "check_ai_os_readiness.ps1" `
    -ScriptPath (Join-Path $Root "tools/check_ai_os_readiness.ps1") `
    -ExtraArgs @("-SkipHealth")

Write-Host "All AI OS exit-code regression tests passed."
exit 0
