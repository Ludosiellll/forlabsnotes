[CmdletBinding()]
param(
    [string]$Root = "",
    [string]$TaskName = "MGI-Mind Auto Start",
    [string]$WatcherTaskName = "AGENT Memory Watcher",
    [ValidateRange(15, 120)]
    [int]$TimeoutSeconds = 70,
    [ValidateRange(15, 600)]
    [int]$SyncLockTimeoutSeconds = 180
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

$startScript = Join-Path $Root "tools/start_mgimind.ps1"
$watcherWasRunning = $false
$syncMutex = $null
$syncLockAcquired = $false

function Test-QdrantReady {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:6333/readyz" -TimeoutSec 2
        return ($response.StatusCode -eq 200)
    } catch {
        return $false
    }
}

try {
    $watcher = Get-ScheduledTask -TaskName $WatcherTaskName -ErrorAction SilentlyContinue
    if ($watcher -and $watcher.State -eq "Running") {
        $watcherWasRunning = $true
        Stop-ScheduledTask -TaskName $WatcherTaskName
    }

    $mutexName = 'Global\AgentMgiSync_' + ($Root.ToLowerInvariant() -replace '[^a-z0-9]', '_')
    $syncMutex = New-Object System.Threading.Mutex($false, $mutexName)
    try {
        $syncLockAcquired = $syncMutex.WaitOne([TimeSpan]::FromSeconds($SyncLockTimeoutSeconds))
    } catch [System.Threading.AbandonedMutexException] {
        $syncLockAcquired = $true
    }
    if (-not $syncLockAcquired) {
        throw "Active memory sync did not finish within ${SyncLockTimeoutSeconds}s; refusing to stop Qdrant during an import."
    }

    $qdrantProcesses = @(Get-CimInstance Win32_Process | Where-Object {
        $_.Name -eq "qdrant.exe" -and $_.ExecutablePath -match "[\\/]mgimind[\\/]qdrant\.exe$"
    })
    foreach ($process in $qdrantProcesses) {
        Stop-Process -Id $process.ProcessId -Force
    }

    $stopTimer = [System.Diagnostics.Stopwatch]::StartNew()
    while ((Test-QdrantReady) -and $stopTimer.Elapsed.TotalSeconds -lt 15) {
        Start-Sleep -Milliseconds 500
    }
    if (Test-QdrantReady) {
        throw "Qdrant did not stop; cold-start test cannot proceed."
    }

    Start-ScheduledTask -TaskName $TaskName
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    while ($timer.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
        if (Test-QdrantReady) { break }
        Start-Sleep -Seconds 1
    }

    if (-not (Test-QdrantReady)) {
        throw "$TaskName did not restore Qdrant within ${TimeoutSeconds}s."
    }

    while ((Get-ScheduledTask -TaskName $TaskName).State -eq "Running" -and $timer.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
        Start-Sleep -Milliseconds 500
    }

    $info = Get-ScheduledTaskInfo -TaskName $TaskName
    if ($info.LastTaskResult -ne 0) {
        throw "$TaskName restored Qdrant but returned LastTaskResult=$($info.LastTaskResult)."
    }

    $logPath = Join-Path $Root ".local/mgimind-autostart.log"
    $tail = (Get-Content -LiteralPath $logPath -Tail 8 -ErrorAction Stop) -join "`n"
    if ($tail -notmatch "launch: mgimind serve pid=" -or $tail -notmatch "ready: Qdrant responded") {
        throw "Autostart log is missing launch/readiness diagnostics."
    }

    Write-Host "PASS $TaskName cold-started Qdrant and returned 0 in $([math]::Round($timer.Elapsed.TotalSeconds, 1))s"
    exit 0
} finally {
    if (-not (Test-QdrantReady)) {
        & powershell.exe -NoProfile -File $startScript -Root $Root | Out-Null
    }
    if ($syncLockAcquired) {
        try { $syncMutex.ReleaseMutex() } catch { }
    }
    if ($syncMutex) {
        $syncMutex.Dispose()
    }
    if ($watcherWasRunning) {
        Start-ScheduledTask -TaskName $WatcherTaskName
    }
}
