[CmdletBinding()]
param(
    [string]$ProjectName = "",
    [switch]$TemplateNames,
    [switch]$IncludeControlCenter
)

$ErrorActionPreference = "Stop"

if ($TemplateNames) {
    if ([string]::IsNullOrWhiteSpace($ProjectName)) {
        throw "-ProjectName is required with -TemplateNames."
    }
    $memoryName = "AI-OS Memory Service ($ProjectName)"
    $watcherName = "AI-OS Memory Watcher ($ProjectName)"
    $readinessName = "AI-OS Readiness Check ($ProjectName)"
    $controlCenterName = "AI-OS Control Center ($ProjectName)"
} else {
    $memoryName = "MGI-Mind Auto Start"
    $watcherName = "AGENT Memory Watcher"
    $readinessName = "AI-OS Readiness Check"
    $controlCenterName = "AI-OS Control Center"
}

$expected = @(
    [pscustomobject]@{ Name = $memoryName; Script = "start_mgimind.ps1"; MinimumTriggers = 2; RequiredArgument = "-WindowStyle Hidden" },
    [pscustomobject]@{ Name = $watcherName; Script = "watch_agent_reimport.ps1"; MinimumTriggers = 2; RequiredArgument = "-WindowStyle Hidden" },
    [pscustomobject]@{ Name = $readinessName; Script = "run_scheduled_readiness.ps1"; MinimumTriggers = 2; RequiredArgument = "-WindowStyle Hidden" }
)
if ($IncludeControlCenter) {
    $expected += [pscustomobject]@{ Name = $controlCenterName; Script = "ai-os-control-center.exe"; MinimumTriggers = 2; RequiredArgument = "--start-hidden" }
}

foreach ($contract in $expected) {
    $task = Get-ScheduledTask -TaskName $contract.Name -ErrorAction Stop
    $settings = $task.Settings
    $actionText = (($task.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -join " ")

    if ($task.State -eq "Disabled") {
        throw "$($contract.Name) is disabled."
    }
    if ($settings.DisallowStartIfOnBatteries) {
        throw "$($contract.Name) cannot start on battery."
    }
    if ($settings.StopIfGoingOnBatteries) {
        throw "$($contract.Name) stops when switching to battery."
    }
    if (-not $settings.StartWhenAvailable) {
        throw "$($contract.Name) does not use StartWhenAvailable."
    }
    if ([int]$settings.RestartCount -lt 3) {
        throw "$($contract.Name) has RestartCount=$($settings.RestartCount); expected at least 3."
    }
    if (@($task.Triggers).Count -lt $contract.MinimumTriggers) {
        throw "$($contract.Name) has too few triggers."
    }
    if ($actionText -notmatch [regex]::Escape($contract.Script)) {
        throw "$($contract.Name) does not execute $($contract.Script)."
    }
    if ($actionText -notmatch [regex]::Escape($contract.RequiredArgument)) {
        throw "$($contract.Name) is missing required hidden-start argument '$($contract.RequiredArgument)'."
    }

    Write-Host "PASS $($contract.Name) battery/restart/trigger contract"
}

Write-Host "All scheduled-task contract tests passed."
exit 0
