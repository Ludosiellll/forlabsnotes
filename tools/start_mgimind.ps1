[CmdletBinding()]
param(
    [string]$Root = "",
    [string]$MgiMindPath = "",
    [ValidateRange(5, 180)]
    [int]$TimeoutSeconds = 45
)

$ErrorActionPreference = "Stop"
$runningOnWindows = $PSVersionTable.PSEdition -eq 'Desktop' -or $IsWindows
$script:qdrantGrpcPort = 6334
$script:qdrantHttpPort = 6333
$script:qdrantDataDir = ''

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent $PSScriptRoot
}

if ([string]::IsNullOrWhiteSpace($MgiMindPath)) {
    $configPath = Join-Path $Root "tools/ai_os.config.json"
    if (Test-Path -LiteralPath $configPath) {
        try {
            $config = Get-Content -Raw -Encoding UTF8 -LiteralPath $configPath | ConvertFrom-Json
            if ($config.memoryToolPath -and "$($config.memoryToolPath)" -notmatch '\{\{') {
                $MgiMindPath = $config.memoryToolPath
            }
        } catch {
            Write-Warning "Could not read $configPath`: $($_.Exception.Message)"
        }
    }

    if ([string]::IsNullOrWhiteSpace($MgiMindPath)) {
        if ($runningOnWindows) {
            $knownPath = Join-Path $env:LOCALAPPDATA "Programs\mgimind\mgimind.exe"
        } else {
            $dataHome = if ($env:XDG_DATA_HOME) { $env:XDG_DATA_HOME } else { Join-Path $HOME '.local/share' }
            $knownPath = Join-Path $dataHome 'ai-os/bin/mgimind'
        }
        if (Test-Path -LiteralPath $knownPath) {
            $MgiMindPath = $knownPath
        } else {
            $command = Get-Command mgimind -ErrorAction SilentlyContinue
            if ($command) { $MgiMindPath = $command.Source }
        }
    }
}

$memoryConfigCandidates = New-Object System.Collections.Generic.List[string]
if ($env:MGIMIND_HOME) {
    $memoryConfigCandidates.Add((Join-Path $env:MGIMIND_HOME 'config.json'))
}
if ($HOME) {
    $memoryConfigCandidates.Add((Join-Path $HOME 'mgimind/config.json'))
}
foreach ($candidate in @($memoryConfigCandidates | Select-Object -Unique)) {
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { continue }
    try {
        $memoryConfig = Get-Content -LiteralPath $candidate -Raw -Encoding UTF8 | ConvertFrom-Json
        $configuredPort = 0
        if ([int]::TryParse([string]$memoryConfig.qdrant_port, [ref]$configuredPort) -and $configuredPort -ge 2 -and $configuredPort -le 65535) {
            $script:qdrantGrpcPort = $configuredPort
            $script:qdrantHttpPort = $configuredPort - 1
            if ($memoryConfig.data_dir) {
                $script:qdrantDataDir = Join-Path ([string]$memoryConfig.data_dir) 'qdrant'
            }
            break
        }
    } catch {
        # Doctor will report malformed memory configuration with more context.
    }
}

$logDir = Join-Path $Root ".local"
$logPath = Join-Path $logDir "mgimind-autostart.log"
$stdoutPath = Join-Path $logDir "mgimind-serve.stdout.log"
$stderrPath = Join-Path $logDir "mgimind-serve.stderr.log"

if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}

if ((Test-Path -LiteralPath $logPath) -and (Get-Item -LiteralPath $logPath).Length -gt 524288) {
    Move-Item -LiteralPath $logPath -Destination "$logPath.old" -Force
}

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Encoding UTF8 -LiteralPath $logPath -Value "[$timestamp] $Message"
}

function Test-QdrantReady {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$script:qdrantHttpPort/readyz" -TimeoutSec 2
        return ($response.StatusCode -eq 200)
    } catch {
        return $false
    }
}

function Read-LogTail {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return "<no output>" }
    try {
        return ((Get-Content -LiteralPath $Path -Tail 12 -ErrorAction Stop) -join " | ")
    } catch {
        return "<unreadable: $($_.Exception.Message)>"
    }
}

if (-not $MgiMindPath -or -not (Test-Path -LiteralPath $MgiMindPath)) {
    Write-Log "ERROR executable not found: $MgiMindPath"
    exit 1
}

if (Test-QdrantReady) {
    Write-Log "ready: Qdrant already responds on 127.0.0.1:$script:qdrantHttpPort (gRPC $script:qdrantGrpcPort)."
    exit 0
}

foreach ($path in @($stdoutPath, $stderrPath)) {
    try { Set-Content -Encoding UTF8 -LiteralPath $path -Value "" } catch { }
}

try {
    $customPort = $script:qdrantGrpcPort -ne 6334
    $startArgs = @{
        RedirectStandardOutput = $stdoutPath
        RedirectStandardError = $stderrPath
        PassThru = $true
    }
    if ($customPort) {
        $qdrantName = if ($runningOnWindows) { 'qdrant.exe' } else { 'qdrant' }
        $qdrantPath = Join-Path (Split-Path -Parent $MgiMindPath) $qdrantName
        if (-not (Test-Path -LiteralPath $qdrantPath -PathType Leaf)) {
            throw "Custom Qdrant port requires the verified binary next to mgimind: $qdrantPath"
        }
        if ([string]::IsNullOrWhiteSpace($script:qdrantDataDir)) {
            throw 'Custom Qdrant port requires data_dir in the MGI-Mind config.'
        }
        New-Item -ItemType Directory -Path $script:qdrantDataDir -Force | Out-Null
        $oldHost = $env:QDRANT__SERVICE__HOST
        $oldHttp = $env:QDRANT__SERVICE__HTTP_PORT
        $oldGrpc = $env:QDRANT__SERVICE__GRPC_PORT
        $oldStorage = $env:QDRANT__STORAGE__STORAGE_PATH
        $env:QDRANT__SERVICE__HOST = '127.0.0.1'
        $env:QDRANT__SERVICE__HTTP_PORT = [string]$script:qdrantHttpPort
        $env:QDRANT__SERVICE__GRPC_PORT = [string]$script:qdrantGrpcPort
        $env:QDRANT__STORAGE__STORAGE_PATH = $script:qdrantDataDir
        $startArgs.FilePath = $qdrantPath
        $startArgs.WorkingDirectory = (Split-Path -Parent $qdrantPath)
    } else {
        $startArgs.FilePath = $MgiMindPath
        $startArgs.ArgumentList = 'serve'
        $startArgs.WorkingDirectory = (Split-Path -Parent $MgiMindPath)
    }
    if ($runningOnWindows) { $startArgs.WindowStyle = 'Hidden' }
    try {
        $process = Start-Process @startArgs
    } finally {
        if ($customPort) {
            $env:QDRANT__SERVICE__HOST = $oldHost
            $env:QDRANT__SERVICE__HTTP_PORT = $oldHttp
            $env:QDRANT__SERVICE__GRPC_PORT = $oldGrpc
            $env:QDRANT__STORAGE__STORAGE_PATH = $oldStorage
        }
    }
    $launchLabel = if ($customPort) { "qdrant $script:qdrantHttpPort/$script:qdrantGrpcPort" } else { 'mgimind serve' }
    Write-Log "launch: $launchLabel pid=$($process.Id), timeout=${TimeoutSeconds}s."
} catch {
    Write-Log "ERROR launch failed: $($_.Exception.Message)"
    exit 1
}

$timer = [System.Diagnostics.Stopwatch]::StartNew()
$parentExitLogged = $false

while ($timer.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
    if (Test-QdrantReady) {
        $elapsed = [math]::Round($timer.Elapsed.TotalSeconds, 1)
        $statsLine = ""
        try {
            $statsLine = @(& $MgiMindPath stats 2>&1) | Where-Object { $_ -match "memories" } | Select-Object -First 1
        } catch { }
        Write-Log "ready: Qdrant responded after ${elapsed}s; $statsLine"
        exit 0
    }

    if (-not $parentExitLogged -and $process.HasExited) {
        Write-Log "launch parent exited code=$($process.ExitCode); waiting for detached Qdrant child."
        $parentExitLogged = $true
    }

    Start-Sleep -Seconds 1
}

$processState = if ($process.HasExited) { "exited code=$($process.ExitCode)" } else { "still running pid=$($process.Id)" }
Write-Log "ERROR readiness timeout after ${TimeoutSeconds}s; launcher=$processState."
Write-Log "stderr: $(Read-LogTail $stderrPath)"
Write-Log "stdout: $(Read-LogTail $stdoutPath)"
exit 1
