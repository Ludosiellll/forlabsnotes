[CmdletBinding()]
param(
    [string]$Root = "",
    [string[]]$Dirs = @("01_Index", "10_Project", "20_Domain", "30_Tech", "40_Decisions", "50_Meetings", "60_Tasks", "70_Resources"),
    [int]$PollSeconds = 10,
    [int]$DebounceSeconds = 45,
    [switch]$Once
)

$ErrorActionPreference = "Stop"
$runningOnWindows = $PSVersionTable.PSEdition -eq 'Desktop' -or $IsWindows
$powerShellExecutable = (Get-Process -Id $PID).Path

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent $PSScriptRoot
}

$syncScript = Join-Path $Root "tools/sync_mgimind.ps1"
if (-not (Test-Path -LiteralPath $syncScript)) {
    throw "Missing sync script: $syncScript"
}

$localDir = Join-Path $Root ".local"
if (-not (Test-Path -LiteralPath $localDir)) {
    New-Item -ItemType Directory -Force -Path $localDir | Out-Null
}
$logPath = Join-Path $localDir "mgimind-watch.log"

# Single-instance guard: a second watcher for the same workspace would double-sync.
$mutexPrefix = if ($runningOnWindows) { 'Global\' } else { '' }
$mutexName = $mutexPrefix + 'AgentWatcher_' + ($Root -replace '[^A-Za-z0-9]', '_')
$script:watcherMutex = New-Object System.Threading.Mutex($false, $mutexName)
if (-not $script:watcherMutex.WaitOne(0)) {
    Write-Output "Another watcher instance is already running for this workspace. Exiting."
    exit 0
}

# Rotate the watch log at ~1 MB so a long-lived autostarted watcher never bloats it.
if ((Test-Path -LiteralPath $logPath) -and ((Get-Item -LiteralPath $logPath).Length -gt 1048576)) {
    Move-Item -LiteralPath $logPath -Destination "$logPath.old" -Force
}

function Write-WatchLog {
    param([string]$Message)
    $stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -Encoding UTF8 -Path $logPath -Value "[$stamp] $Message"
}

function Get-AgentMarkdownSnapshot {
    param(
        [string]$BaseRoot,
        [string[]]$ImportDirs
    )

    $snapshot = @{}
    foreach ($dir in $ImportDirs) {
        $path = Join-Path $BaseRoot $dir
        if (-not (Test-Path -LiteralPath $path)) {
            continue
        }

        Get-ChildItem -LiteralPath $path -Recurse -File -Filter "*.md" -ErrorAction SilentlyContinue |
            Where-Object {
                $_.FullName -notmatch "[\\/]\.git[\\/]" -and
                $_.FullName -notmatch "[\\/]90_Archive[\\/]Audio_Transcripts[\\/]"
            } |
            ForEach-Object {
                $snapshot[$_.FullName] = [pscustomobject]@{
                    Ticks = $_.LastWriteTimeUtc.Ticks
                    Dir = $dir
                }
            }
    }

    return $snapshot
}

if ($PollSeconds -lt 2) {
    throw "PollSeconds must be at least 2."
}
if ($DebounceSeconds -lt $PollSeconds) {
    throw "DebounceSeconds must be greater than or equal to PollSeconds."
}

$state = Get-AgentMarkdownSnapshot -BaseRoot $Root -ImportDirs $Dirs
Write-WatchLog "Watcher initialized. files=$($state.Count), dirs=$($Dirs -join ',')"

if ($Once) {
    "Watcher initialized. files=$($state.Count). Use without -Once to keep watching."
    exit 0
}

$pending = New-Object System.Collections.Generic.HashSet[string]
$lastChange = $null

while ($true) {
    Start-Sleep -Seconds $PollSeconds

    $next = Get-AgentMarkdownSnapshot -BaseRoot $Root -ImportDirs $Dirs
    $allPaths = @($state.Keys + $next.Keys | Sort-Object -Unique)
    $changed = $false

    foreach ($path in $allPaths) {
        $old = $state[$path]
        $new = $next[$path]

        if ($null -eq $old -and $null -ne $new) {
            [void]$pending.Add($new.Dir)
            $changed = $true
            continue
        }

        if ($null -ne $old -and $null -eq $new) {
            [void]$pending.Add($old.Dir)
            $changed = $true
            continue
        }

        if ($null -ne $old -and $null -ne $new -and $old.Ticks -ne $new.Ticks) {
            [void]$pending.Add($new.Dir)
            $changed = $true
        }
    }

    if ($changed) {
        $lastChange = Get-Date
        $state = $next
        Write-WatchLog "Detected markdown change. pending=$(@($pending) -join ',')"
    }

    if ($pending.Count -gt 0 -and $lastChange -ne $null) {
        $age = ((Get-Date) - $lastChange).TotalSeconds
        if ($age -ge $DebounceSeconds) {
            $dirsToSync = @($pending | Sort-Object)
            $pending.Clear() | Out-Null
            Write-WatchLog "Debounce elapsed. Syncing $($dirsToSync -join ',')"
            # Pass dirs as ONE comma-joined string: an array flattens into separate
            # argv entries across the powershell.exe -File boundary, and the second
            # dir then fails positional binding ("A positional parameter cannot be
            # found..."). sync_mgimind.ps1 splits on commas itself.
            $syncArgs = @('-NoProfile')
            if ($runningOnWindows) { $syncArgs += @('-ExecutionPolicy', 'RemoteSigned') }
            $syncArgs += @('-File', $syncScript, '-Root', $Root, '-Dirs', ($dirsToSync -join ','))
            & $powerShellExecutable @syncArgs
            $syncExit = $LASTEXITCODE
            if ($syncExit -eq 0) {
                Write-WatchLog "Sync complete. exit=0 dirs=$($dirsToSync -join ',')"
            } else {
                # Re-queue failed dirs and restart the debounce window so the retry
                # happens after DebounceSeconds instead of hammering every poll.
                foreach ($dir in $dirsToSync) { [void]$pending.Add($dir) }
                $lastChange = Get-Date
                Write-WatchLog "Sync FAILED. exit=$syncExit dirs=$($dirsToSync -join ','); will retry after debounce"
            }
            # Intentionally NO full re-snapshot here: $state stays at the last poll
            # snapshot, so markdown edited while the sync was running is still
            # detected as changed on the next poll instead of being silently lost.
        }
    }
}
