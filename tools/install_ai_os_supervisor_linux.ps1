[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$SupervisorScript,
    [Parameter(Mandatory = $true)][string]$RegistryPath,
    [Parameter(Mandatory = $true)][string]$PowerShellPath,
    [switch]$Remove
)

$ErrorActionPreference = 'Stop'

foreach ($value in @($SupervisorScript, $RegistryPath, $PowerShellPath)) {
    if ([string]::IsNullOrWhiteSpace($value) -or $value -match '[\r\n]') {
        throw 'Supervisor paths must be non-empty single-line values.'
    }
}
if (-not (Test-Path -LiteralPath $PowerShellPath) -or -not (Test-Path -LiteralPath $SupervisorScript)) {
    throw 'The Linux supervisor runtime is incomplete.'
}

$configHome = if ($env:XDG_CONFIG_HOME) { $env:XDG_CONFIG_HOME } else { Join-Path $HOME '.config' }
$stateHome = if ($env:XDG_STATE_HOME) { $env:XDG_STATE_HOME } else { Join-Path $HOME '.local/state' }
$serviceDir = Join-Path $configHome 'systemd/user'
$servicePath = Join-Path $serviceDir 'ai-os-supervisor.service'
$autostartDir = Join-Path $configHome 'autostart'
$autostartPath = Join-Path $autostartDir 'ai-os-supervisor.desktop'
$stateDir = Join-Path $stateHome 'ai-os'
New-Item -ItemType Directory -Force -Path $serviceDir, $autostartDir, $stateDir | Out-Null

function Quote-UnitValue {
    param([string]$Value)
    return '"' + $Value.Replace('\', '\\').Replace('"', '\"') + '"'
}

function Stop-SystemdUnit {
    $systemctl = Get-Command systemctl -ErrorAction SilentlyContinue
    if ($systemctl) {
        & $systemctl.Source --user disable --now ai-os-supervisor.service 2>&1 | Out-Null
    }
}

if ($Remove) {
    Stop-SystemdUnit
    Remove-Item -LiteralPath $servicePath, $autostartPath -Force -ErrorAction SilentlyContinue
    $systemctl = Get-Command systemctl -ErrorAction SilentlyContinue
    if ($systemctl) {
        & $systemctl.Source --user daemon-reload 2>&1 | Out-Null
        & $systemctl.Source --user reset-failed ai-os-supervisor.service 2>&1 | Out-Null
    }
    Write-Output 'Linux supervisor disabled; workspace files were kept.'
    exit 0
}

$pwshArg = Quote-UnitValue $PowerShellPath
$scriptArg = Quote-UnitValue $SupervisorScript
$registryArg = Quote-UnitValue $RegistryPath
$unit = @"
[Unit]
Description=AI OS shared workspace supervisor
After=graphical-session.target network-online.target

[Service]
Type=simple
ExecStart=$pwshArg -NoProfile -File $scriptArg -RegistryPath $registryArg
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
"@
[IO.File]::WriteAllText($servicePath, $unit, [Text.UTF8Encoding]::new($false))

$desktop = @"
[Desktop Entry]
Type=Application
Name=AI OS Supervisor
Comment=Keeps AI OS memory, checks and the active Control Center running
Exec=$pwshArg -NoProfile -File $scriptArg -RegistryPath $registryArg
Terminal=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
"@
[IO.File]::WriteAllText($autostartPath, $desktop, [Text.UTF8Encoding]::new($false))

$systemctl = Get-Command systemctl -ErrorAction SilentlyContinue
if ($systemctl) {
    & $systemctl.Source --user daemon-reload 2>&1 | Out-Null
    & $systemctl.Source --user enable --now ai-os-supervisor.service 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Output 'Linux supervisor enabled with systemd --user.'
        exit 0
    }
}

# Minimal desktops and WSL sessions may not expose a user systemd bus. The XDG
# autostart entry covers the next login; start the same supervisor now as well.
Start-Process -FilePath $PowerShellPath `
    -ArgumentList @('-NoProfile', '-File', $SupervisorScript, '-RegistryPath', $RegistryPath) `
    -WorkingDirectory $stateDir | Out-Null
Write-Output 'Linux supervisor enabled with XDG Autostart fallback.'
exit 0
