[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RegistryPath,
    [ValidateRange(2, 300)][int]$PollSeconds = 10,
    [ValidateRange(5, 900)][int]$DebounceSeconds = 20,
    [string]$MutexName = "",
    [switch]$Once,
    [switch]$PlanOnly
)

$ErrorActionPreference = "Stop"
$runningOnWindows = $PSVersionTable.PSEdition -eq 'Desktop' -or $IsWindows
$powerShellExecutable = (Get-Process -Id $PID).Path
$controlCenterBinaryName = if ($runningOnWindows) { 'ai-os-control-center.exe' } else { 'ai-os-control-center' }
$taskName = "AI-OS Supervisor"
$MutexName = if ([string]::IsNullOrWhiteSpace($MutexName)) {
    if ($runningOnWindows) { 'Global\AI_OS_Shared_Supervisor' } else { 'AI_OS_Shared_Supervisor' }
} else {
    $MutexName
}
$importDirs = @("01_Index", "10_Project", "20_Domain", "30_Tech", "40_Decisions", "50_Meetings", "60_Tasks", "70_Resources")
$RegistryPath = [IO.Path]::GetFullPath($RegistryPath)
$stateDir = Split-Path -Parent $RegistryPath
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
$logPath = Join-Path $stateDir "supervisor.log"

if ((Test-Path -LiteralPath $logPath) -and (Get-Item -LiteralPath $logPath).Length -gt 2097152) {
    Move-Item -LiteralPath $logPath -Destination "$logPath.old" -Force
}

function Write-SupervisorLog {
    param([string]$Message)
    $stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -LiteralPath $logPath -Encoding UTF8 -Value "[$stamp] $Message"
}

function Read-Registry {
    for ($attempt = 0; $attempt -lt 3; $attempt++) {
        try {
            if (-not (Test-Path -LiteralPath $RegistryPath)) { return $null }
            return (Get-Content -LiteralPath $RegistryPath -Raw -Encoding UTF8 | ConvertFrom-Json)
        } catch {
            if ($attempt -eq 2) { throw }
            Start-Sleep -Milliseconds 200
        }
    }
}

function Get-EnabledWorkspaces {
    param($Registry)
    if ($null -eq $Registry -or $null -eq $Registry.workspaces) { return @() }
    return @($Registry.workspaces | Where-Object {
        $_.automationEnabled -ne $false -and
        -not [string]::IsNullOrWhiteSpace([string]$_.id) -and
        -not [string]::IsNullOrWhiteSpace([string]$_.root)
    })
}

function Get-ActiveWorkspace {
    param($Registry, [object[]]$Enabled)
    $active = @($Enabled | Where-Object { $_.id -eq $Registry.activeWorkspaceId } | Select-Object -First 1)
    if ($active.Count) { return $active[0] }
    return $null
}

function Get-WorkspaceSnapshot {
    param([string]$Root)
    $snapshot = @{}
    foreach ($dir in $importDirs) {
        $path = Join-Path $Root $dir
        if (-not (Test-Path -LiteralPath $path)) { continue }
        foreach ($file in @(Get-ChildItem -LiteralPath $path -Recurse -File -Filter "*.md" -ErrorAction SilentlyContinue | Where-Object {
            $_.FullName -notmatch "[\\/]\.git[\\/]" -and $_.FullName -notmatch "[\\/]90_Archive[\\/]Audio_Transcripts[\\/]"
        })) {
            $snapshot[$file.FullName] = [pscustomobject]@{ Ticks = $file.LastWriteTimeUtc.Ticks; Dir = $dir }
        }
    }
    return $snapshot
}

function Compare-WorkspaceSnapshot {
    param([hashtable]$Before, [hashtable]$After)
    $changed = New-Object System.Collections.Generic.HashSet[string]
    foreach ($path in $After.Keys) {
        if (-not $Before.ContainsKey($path) -or $Before[$path].Ticks -ne $After[$path].Ticks) {
            [void]$changed.Add([string]$After[$path].Dir)
        }
    }
    foreach ($path in $Before.Keys) {
        if (-not $After.ContainsKey($path)) {
            [void]$changed.Add([string]$Before[$path].Dir)
        }
    }
    return @($changed)
}

function Remove-LegacyWorkspaceTasks {
    param([object[]]$Workspaces)
    if (-not $runningOnWindows) { return }
    foreach ($task in @(Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object { $_.TaskName -like 'AI-OS*' -and $_.TaskName -ne $taskName })) {
        $actionText = (($task.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments) $($_.WorkingDirectory)" }) -join ' ')
        $belongsToWorkspace = $false
        foreach ($workspace in $Workspaces) {
            if ($actionText -match [regex]::Escape([string]$workspace.root)) {
                $belongsToWorkspace = $true
                break
            }
        }
        if ($belongsToWorkspace) {
            Stop-ScheduledTask -TaskName $task.TaskName -ErrorAction SilentlyContinue
            Unregister-ScheduledTask -TaskName $task.TaskName -Confirm:$false -ErrorAction SilentlyContinue
            Write-SupervisorLog "Removed legacy task $($task.TaskName)"
        }
    }
}

function Ensure-MemoryService {
    param($Workspace)
    if ($null -eq $Workspace) { return }
    $script = Join-Path ([string]$Workspace.root) "tools/start_mgimind.ps1"
    if (Test-Path -LiteralPath $script) {
        $args = @('-NoProfile')
        if ($runningOnWindows) { $args += @('-ExecutionPolicy', 'RemoteSigned') }
        $args += @('-File', $script, '-Root', [string]$Workspace.root)
        & $powerShellExecutable @args 2>&1 | ForEach-Object { Write-SupervisorLog ([string]$_) }
        Write-SupervisorLog "Memory service checked for $($Workspace.id) exit=$LASTEXITCODE"
    }
}

function Ensure-ActiveControlCenter {
    param($Active, [object[]]$Workspaces)
    $desired = $null
    if ($null -ne $Active) {
        $candidate = Join-Path ([string]$Active.root) "tools/control-center-app/bin/$controlCenterBinaryName"
        if (Test-Path -LiteralPath $candidate) {
            $desired = [IO.Path]::GetFullPath($candidate)
        } else {
            Write-SupervisorLog "Control Center missing for $($Active.id): $candidate"
        }
    }

    if (-not $runningOnWindows) {
        $pidPath = Join-Path $stateDir 'control-center.pid'
        $workspacePath = Join-Path $stateDir 'control-center-workspace.txt'
        $runningProcess = $null
        if (Test-Path -LiteralPath $pidPath) {
            $knownPid = 0
            if ([int]::TryParse((Get-Content -LiteralPath $pidPath -Raw).Trim(), [ref]$knownPid)) {
                $runningProcess = Get-Process -Id $knownPid -ErrorAction SilentlyContinue
            }
        }
        $runningWorkspace = if (Test-Path -LiteralPath $workspacePath) { (Get-Content -LiteralPath $workspacePath -Raw).Trim() } else { '' }
        $desiredWorkspace = if ($null -ne $Active) { [string]$Active.id } else { '' }
        if ($runningProcess -and ($null -eq $desired -or $runningWorkspace -ne $desiredWorkspace)) {
            Stop-Process -Id $runningProcess.Id -Force -ErrorAction SilentlyContinue
            Write-SupervisorLog "Stopped inactive Control Center pid=$($runningProcess.Id)"
            $runningProcess = $null
        }
        if ($null -ne $desired -and -not $runningProcess) {
            & chmod 755 -- $desired
            if ($LASTEXITCODE -ne 0) {
                Write-SupervisorLog "Could not mark Control Center executable: $desired"
                return
            }
            $previousRoot = $env:AI_OS_ROOT
            try {
                $env:AI_OS_ROOT = [string]$Active.root
                $process = Start-Process -FilePath $desired -ArgumentList '--start-hidden' -WorkingDirectory ([string]$Active.root) -PassThru
                [IO.File]::WriteAllText($pidPath, [string]$process.Id)
                [IO.File]::WriteAllText($workspacePath, $desiredWorkspace)
                Write-SupervisorLog "Started active Control Center for $desiredWorkspace pid=$($process.Id)"
            } finally {
                $env:AI_OS_ROOT = $previousRoot
            }
        }
        return
    }

    $managed = @{}
    foreach ($workspace in $Workspaces) {
        $candidate = Join-Path ([string]$workspace.root) "tools/control-center-app/bin/$controlCenterBinaryName"
        $managed[[IO.Path]::GetFullPath($candidate).ToLowerInvariant()] = $true
    }
    $desiredRunning = $false
    foreach ($process in @(Get-CimInstance Win32_Process -Filter "Name='ai-os-control-center.exe'" -ErrorAction SilentlyContinue)) {
        $exe = [string]$process.ExecutablePath
        if ([string]::IsNullOrWhiteSpace($exe)) { continue }
        $key = [IO.Path]::GetFullPath($exe).ToLowerInvariant()
        if (-not $managed.ContainsKey($key)) { continue }
        if ($null -ne $desired -and $key -eq $desired.ToLowerInvariant()) {
            if (-not $desiredRunning) {
                $desiredRunning = $true
            } else {
                Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
                Write-SupervisorLog "Stopped duplicate Control Center pid=$($process.ProcessId)"
            }
        } else {
            Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
            Write-SupervisorLog "Stopped inactive Control Center pid=$($process.ProcessId)"
        }
    }
    if ($null -ne $desired -and -not $desiredRunning) {
        $previousRoot = $env:AI_OS_ROOT
        try {
            $env:AI_OS_ROOT = [string]$Active.root
            Start-Process -FilePath $desired -ArgumentList '--start-hidden' -WorkingDirectory ([string]$Active.root) -WindowStyle Hidden | Out-Null
            Write-SupervisorLog "Started active Control Center for $($Active.id)"
        } finally {
            $env:AI_OS_ROOT = $previousRoot
        }
    }
}

function Invoke-ReadinessWhenDue {
    param($Workspace)
    $root = [string]$Workspace.root
    $script = Join-Path $root "tools/run_scheduled_readiness.ps1"
    if (-not (Test-Path -LiteralPath $script)) { return }
    $log = Join-Path $root ".local/readiness-scheduled.log"
    if ((Test-Path -LiteralPath $log) -and (Get-Item -LiteralPath $log).LastWriteTimeUtc -gt (Get-Date).ToUniversalTime().AddHours(-24)) { return }
    $args = @('-NoProfile')
    if ($runningOnWindows) { $args += @('-ExecutionPolicy', 'RemoteSigned') }
    $args += @('-File', $script, '-Root', $root)
    & $powerShellExecutable @args 2>&1 | Out-Null
    Write-SupervisorLog "Readiness finished for $($Workspace.id) exit=$LASTEXITCODE"
}

$initialRegistry = Read-Registry
$initialEnabled = @(Get-EnabledWorkspaces -Registry $initialRegistry)
$initialActive = if ($initialEnabled.Count) { Get-ActiveWorkspace -Registry $initialRegistry -Enabled $initialEnabled } else { $null }

if ($PlanOnly) {
    [ordered]@{
        taskName = $taskName
        workspaceCount = @($initialRegistry.workspaces).Count
        enabledCount = $initialEnabled.Count
        activeWorkspaceId = if ($null -ne $initialActive) { [string]$initialActive.id } else { $null }
        activeRoot = if ($null -ne $initialActive) { [string]$initialActive.root } else { $null }
    } | ConvertTo-Json -Compress
    exit 0
}

$mutex = New-Object System.Threading.Mutex($false, $MutexName)
$lockAcquired = $false
try {
    try { $lockAcquired = $mutex.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $lockAcquired = $true }
    if (-not $lockAcquired) { exit 0 }

    Write-SupervisorLog "Supervisor started"
    [IO.File]::WriteAllText((Join-Path $stateDir 'supervisor.pid'), [string]$PID)
    $snapshots = @{}
    $pending = @{}
    $lastChange = @{}
    $lastMemoryCheck = [datetime]::MinValue
    $legacyCleanupDone = $false

    do {
        $registry = Read-Registry
        $enabled = @(Get-EnabledWorkspaces -Registry $registry)
        if (-not $enabled.Count) {
            Write-SupervisorLog "No enabled workspaces; supervisor exiting"
            break
        }
        $active = Get-ActiveWorkspace -Registry $registry -Enabled $enabled
        $memoryWorkspace = if ($null -ne $active) { $active } else { @($enabled | Select-Object -First 1)[0] }

        if (-not $legacyCleanupDone) {
            Remove-LegacyWorkspaceTasks -Workspaces @($registry.workspaces)
            $legacyCleanupDone = $true
        }
        if ((Get-Date) - $lastMemoryCheck -gt [TimeSpan]::FromMinutes(15)) {
            Ensure-MemoryService -Workspace $memoryWorkspace
            $lastMemoryCheck = Get-Date
        }
        Ensure-ActiveControlCenter -Active $active -Workspaces @($registry.workspaces)

        $knownIds = @($enabled | ForEach-Object { [string]$_.id })
        foreach ($id in @($snapshots.Keys)) {
            if ($knownIds -notcontains $id) {
                $snapshots.Remove($id)
                $pending.Remove($id)
                $lastChange.Remove($id)
            }
        }

        foreach ($workspace in $enabled) {
            $id = [string]$workspace.id
            $root = [string]$workspace.root
            if (-not (Test-Path -LiteralPath (Join-Path $root 'AGENTS.md'))) { continue }
            $next = Get-WorkspaceSnapshot -Root $root
            if (-not $snapshots.ContainsKey($id)) {
                $snapshots[$id] = $next
                Write-SupervisorLog "Watch ready id=$id files=$($next.Count)"
                if (-not $Once) { Invoke-ReadinessWhenDue -Workspace $workspace }
                continue
            }
            $changedDirs = @(Compare-WorkspaceSnapshot -Before $snapshots[$id] -After $next)
            $snapshots[$id] = $next
            if ($changedDirs.Count) {
                if (-not $pending.ContainsKey($id)) { $pending[$id] = New-Object System.Collections.Generic.HashSet[string] }
                foreach ($dir in $changedDirs) { [void]$pending[$id].Add($dir) }
                $lastChange[$id] = Get-Date
            }
            if ($pending.ContainsKey($id) -and $pending[$id].Count -and (Get-Date) - $lastChange[$id] -ge [TimeSpan]::FromSeconds($DebounceSeconds)) {
                $dirs = @($pending[$id] | Sort-Object)
                $sync = Join-Path $root "tools/sync_mgimind.ps1"
                if (Test-Path -LiteralPath $sync) {
                    $args = @('-NoProfile')
                    if ($runningOnWindows) { $args += @('-ExecutionPolicy', 'RemoteSigned') }
                    $args += @('-File', $sync, '-Root', $root, '-Dirs', ($dirs -join ','))
                    & $powerShellExecutable @args 2>&1 | ForEach-Object { Write-SupervisorLog ([string]$_) }
                    if ($LASTEXITCODE -eq 0) {
                        $pending[$id].Clear()
                        Write-SupervisorLog "Sync complete id=$id dirs=$($dirs -join ',')"
                    } else {
                        $lastChange[$id] = Get-Date
                        Write-SupervisorLog "Sync failed id=$id exit=$LASTEXITCODE"
                    }
                }
            }
        }

        if ($Once) { break }
        Start-Sleep -Seconds $PollSeconds
    } while ($true)
} catch {
    Write-SupervisorLog "Supervisor failed: $($_.Exception.Message)"
    throw
} finally {
    Remove-Item -LiteralPath (Join-Path $stateDir 'supervisor.pid') -Force -ErrorAction SilentlyContinue
    if ($lockAcquired) { try { $mutex.ReleaseMutex() } catch { } }
    $mutex.Dispose()
}

exit 0
