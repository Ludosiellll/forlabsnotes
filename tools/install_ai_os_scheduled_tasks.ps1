[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$Root = "",
    [string]$ProjectName = "",
    [switch]$IncludeMemory,
    [switch]$IncludeControlCenter,
    [switch]$LegacyNames,
    [switch]$SkipStart
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent $PSScriptRoot
}
$Root = (Resolve-Path -LiteralPath $Root).Path

if ([string]::IsNullOrWhiteSpace($ProjectName)) {
    $ProjectName = Split-Path -Leaf $Root
}

if ($LegacyNames) {
    $readinessName = "AI-OS Readiness Check"
    $watcherName = "AGENT Memory Watcher"
    $memoryName = "MGI-Mind Auto Start"
    $controlCenterName = "AI-OS Control Center"
} else {
    $readinessName = "AI-OS Readiness Check ($ProjectName)"
    $watcherName = "AI-OS Memory Watcher ($ProjectName)"
    $memoryName = "AI-OS Memory Service ($ProjectName)"
    $controlCenterName = "AI-OS Control Center ($ProjectName)"
}

$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$powershell = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"

function New-ScriptAction {
    param([string]$ScriptName)
    $scriptPath = Join-Path $Root "tools/$ScriptName"
    if (-not (Test-Path -LiteralPath $scriptPath)) {
        throw "Missing scheduled-task script: $scriptPath"
    }
    $arguments = "-NoProfile -WindowStyle Hidden -File `"$scriptPath`" -Root `"$Root`""
    return New-ScheduledTaskAction -Execute $powershell -Argument $arguments -WorkingDirectory $Root
}

function New-ResilientSettings {
    param([TimeSpan]$ExecutionTimeLimit)
    return New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -ExecutionTimeLimit $ExecutionTimeLimit `
        -MultipleInstances IgnoreNew `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 1)
}

function Register-AiOsTask {
    param(
        [string]$Name,
        [object]$Action,
        [object[]]$Triggers,
        [object]$Settings
    )

    if ($PSCmdlet.ShouldProcess($Name, "Register resilient AI OS scheduled task")) {
        Stop-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue
        Register-ScheduledTask -TaskName $Name -Action $Action -Trigger $Triggers -Settings $Settings -Force | Out-Null
        Write-Host "Registered $Name"
    }
}

$readinessLogon = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
$readinessLogon.Delay = "PT2M"
$readinessDaily = New-ScheduledTaskTrigger -Daily -At 11:00
Register-AiOsTask `
    -Name $readinessName `
    -Action (New-ScriptAction "run_scheduled_readiness.ps1") `
    -Triggers @($readinessLogon, $readinessDaily) `
    -Settings (New-ResilientSettings (New-TimeSpan -Minutes 30))

if ($IncludeMemory) {
    $memoryLogon = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
    $memoryLogon.Delay = "PT15S"
    $memoryWatchdog = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15)
    Register-AiOsTask `
        -Name $memoryName `
        -Action (New-ScriptAction "start_mgimind.ps1") `
        -Triggers @($memoryLogon, $memoryWatchdog) `
        -Settings (New-ResilientSettings (New-TimeSpan -Minutes 5))

    $watcherLogon = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
    $watcherDaily = New-ScheduledTaskTrigger -Daily -At 11:05
    Register-AiOsTask `
        -Name $watcherName `
        -Action (New-ScriptAction "watch_agent_reimport.ps1") `
        -Triggers @($watcherLogon, $watcherDaily) `
        -Settings (New-ResilientSettings (New-TimeSpan -Days 3650))
}

if ($IncludeControlCenter) {
    $controlCenterPath = Join-Path $Root "tools/control-center-app/bin/ai-os-control-center.exe"
    if (-not (Test-Path -LiteralPath $controlCenterPath)) {
        throw "Control Center binary not found: $controlCenterPath"
    }
    $controlCenterAction = New-ScheduledTaskAction `
        -Execute $controlCenterPath `
        -Argument "--start-hidden" `
        -WorkingDirectory $Root
    $controlCenterLogon = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
    $controlCenterLogon.Delay = "PT30S"
    $controlCenterDaily = New-ScheduledTaskTrigger -Daily -At 11:10
    Register-AiOsTask `
        -Name $controlCenterName `
        -Action $controlCenterAction `
        -Triggers @($controlCenterLogon, $controlCenterDaily) `
        -Settings (New-ResilientSettings (New-TimeSpan -Days 3650))
}

if (-not $SkipStart -and -not $WhatIfPreference) {
    Start-ScheduledTask -TaskName $readinessName
    if ($IncludeMemory) {
        Start-ScheduledTask -TaskName $memoryName
        Start-ScheduledTask -TaskName $watcherName
    }
    if ($IncludeControlCenter) {
        Start-ScheduledTask -TaskName $controlCenterName
    }
}

Write-Host "AI OS scheduled tasks are installed for $Root"
exit 0
