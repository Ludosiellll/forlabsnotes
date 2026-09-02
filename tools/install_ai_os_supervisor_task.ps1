[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)][string]$SupervisorScript,
    [Parameter(Mandatory = $true)][string]$RegistryPath,
    [switch]$Remove,
    [switch]$SkipStart
)

$ErrorActionPreference = "Stop"
$taskName = "AI-OS Supervisor"

if ($Remove) {
    if ($PSCmdlet.ShouldProcess($taskName, "Remove shared AI OS supervisor task")) {
        Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    }
    Write-Host "Removed $taskName"
    exit 0
}

$SupervisorScript = (Resolve-Path -LiteralPath $SupervisorScript).Path
$registryParent = Split-Path -Parent $RegistryPath
if (-not (Test-Path -LiteralPath $registryParent)) {
    New-Item -ItemType Directory -Force -Path $registryParent | Out-Null
}
$RegistryPath = [IO.Path]::GetFullPath($RegistryPath)

$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$powershell = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
$arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy RemoteSigned -File `"$SupervisorScript`" -RegistryPath `"$RegistryPath`""
$action = New-ScheduledTaskAction -Execute $powershell -Argument $arguments -WorkingDirectory (Split-Path -Parent $SupervisorScript)
$logon = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
$logon.Delay = "PT20S"
$watchdog = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Days 3650) `
    -MultipleInstances IgnoreNew `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

if ($PSCmdlet.ShouldProcess($taskName, "Register shared AI OS supervisor task")) {
    Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($logon, $watchdog) -Settings $settings -Force | Out-Null
    if (-not $SkipStart) {
        Start-ScheduledTask -TaskName $taskName
    }
}

Write-Host "Registered $taskName"
exit 0
