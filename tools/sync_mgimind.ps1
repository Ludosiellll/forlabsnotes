[CmdletBinding()]
param(
    [string]$Root = "",
    [string[]]$Dirs = @("01_Index", "10_Project", "20_Domain", "30_Tech", "40_Decisions", "50_Meetings", "60_Tasks", "70_Resources"),
    [switch]$DryRun,
    [switch]$SkipStart,
    [ValidateRange(1, 3600)]
    [int]$LockTimeoutSeconds = 600
)

$ErrorActionPreference = "Stop"
$runningOnWindows = $PSVersionTable.PSEdition -eq 'Desktop' -or $IsWindows
$powerShellExecutable = (Get-Process -Id $PID).Path
$script:memoryLibrary = 'agent'

$packageModule = Join-Path $PSScriptRoot 'ai_os_package_cache.psm1'
if (Test-Path -LiteralPath $packageModule -PathType Leaf) {
    Import-Module $packageModule -Force
}

function Invoke-MemoryNativeCommand {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$Arguments = @()
    )

    $sharedRunner = Get-Command Invoke-AiOsNativeCommand -ErrorAction SilentlyContinue
    if ($sharedRunner) {
        return Invoke-AiOsNativeCommand -FilePath $FilePath -Arguments $Arguments
    }

    $previousErrorActionPreference = $ErrorActionPreference
    $lastExitVariable = Get-Variable -Name LASTEXITCODE -Scope Global -ErrorAction SilentlyContinue
    $previousLastExitCode = if ($lastExitVariable) { $lastExitVariable.Value } else { $null }
    try {
        $ErrorActionPreference = 'Continue'
        $global:LASTEXITCODE = $null
        try {
            $output = @(& $FilePath @Arguments 2>&1)
            $exitCode = if ($null -eq $global:LASTEXITCODE) { -1 } else { $global:LASTEXITCODE }
        } catch {
            $output = @($_)
            $exitCode = -1
        }
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
        if ($lastExitVariable) {
            $global:LASTEXITCODE = $previousLastExitCode
        } else {
            Remove-Variable -Name LASTEXITCODE -Scope Global -ErrorAction SilentlyContinue
        }
    }

    [pscustomobject]@{
        ExitCode = [int]$exitCode
        Output = @($output | ForEach-Object { [string]$_ })
    }
}

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent $PSScriptRoot
}
$Root = (Resolve-Path -LiteralPath $Root).Path.TrimEnd("\", "/")

$localDir = Join-Path $Root ".local"
if (-not (Test-Path -LiteralPath $localDir)) {
    New-Item -ItemType Directory -Force -Path $localDir | Out-Null
}
$logPath = Join-Path $localDir "mgimind-sync.log"

function Write-SyncLog {
    param([string]$Message)
    $stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -Encoding UTF8 -Path $logPath -Value "[$stamp] $Message"
}

function Get-MgiMindExecutable {
    $configPath = Join-Path $Root 'tools/ai_os.config.json'
    if (Test-Path -LiteralPath $configPath) {
        try {
            $config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($config.memoryLibrary -and "$($config.memoryLibrary)" -notmatch '\{\{') {
                $script:memoryLibrary = [string]$config.memoryLibrary
            }
            if ($config.memoryToolPath -and (Test-Path -LiteralPath ([string]$config.memoryToolPath))) {
                return [string]$config.memoryToolPath
            }
        } catch {
            Write-SyncLog "Could not read workspace memory config: $($_.Exception.Message)"
        }
    }

    $cmd = Get-Command mgimind -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    if ($runningOnWindows) {
        $knownPath = Join-Path $env:LOCALAPPDATA 'Programs/mgimind/mgimind.exe'
    } else {
        $dataHome = if ($env:XDG_DATA_HOME) { $env:XDG_DATA_HOME } else { Join-Path $HOME '.local/share' }
        $knownPath = Join-Path $dataHome 'ai-os/bin/mgimind'
    }
    if (Test-Path -LiteralPath $knownPath) {
        return $knownPath
    }

    $startupScript = Join-Path $Root "tools/start_mgimind.ps1"
    if (Test-Path -LiteralPath $startupScript) {
        $scriptText = Get-Content -Raw -Encoding UTF8 -Path $startupScript
        $match = [regex]::Match($scriptText, '\$mgimindPath\s*=\s*"([^"]+)"')
        if ($match.Success -and (Test-Path -LiteralPath $match.Groups[1].Value)) {
            return $match.Groups[1].Value
        }
    }

    return $null
}

$allowedDirs = @("01_Index", "10_Project", "20_Domain", "30_Tech", "40_Decisions", "50_Meetings", "60_Tasks", "70_Resources")
$selectedDirs = @(
    $Dirs |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        ForEach-Object { $_ -split "," } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        ForEach-Object { $_.Trim().TrimEnd("\", "/") } |
        Sort-Object -Unique
)

foreach ($dir in $selectedDirs) {
    if ($allowedDirs -notcontains $dir) {
        throw "Directory '$dir' is not in the approved AGENT import scope."
    }
}

$mutexPrefix = if ($runningOnWindows) { 'Global\' } else { '' }
$mutexName = $mutexPrefix + 'AgentMgiSync_' + ($Root.ToLowerInvariant() -replace '[^a-z0-9]', '_')
$syncMutex = New-Object System.Threading.Mutex($false, $mutexName)
$lockAcquired = $false
$processExit = 1

try {
    try {
        $lockAcquired = $syncMutex.WaitOne(0)
    } catch [System.Threading.AbandonedMutexException] {
        $lockAcquired = $true
    }

    if (-not $lockAcquired) {
        Write-SyncLog "Another sync is active; waiting up to $LockTimeoutSeconds seconds"
        try {
            $lockAcquired = $syncMutex.WaitOne([TimeSpan]::FromSeconds($LockTimeoutSeconds))
        } catch [System.Threading.AbandonedMutexException] {
            $lockAcquired = $true
        }
        if (-not $lockAcquired) {
            throw "Timed out after $LockTimeoutSeconds seconds waiting for another mgi-mind sync to finish."
        }
        Write-SyncLog "Previous sync finished; continuing"
    }

    if (-not $SkipStart) {
        $startupScript = Join-Path $Root "tools/start_mgimind.ps1"
        if (Test-Path -LiteralPath $startupScript) {
            Write-SyncLog "Ensuring mgi-mind service is running"
            $startArgs = @('-NoProfile')
            if ($runningOnWindows) { $startArgs += @('-ExecutionPolicy', 'RemoteSigned') }
            $startArgs += @('-File', $startupScript, '-Root', $Root)
            & $powerShellExecutable @startArgs | Out-Null
        }
    }

    $mgimind = Get-MgiMindExecutable
    if (-not $mgimind) {
        throw "mgimind executable was not found."
    }

    $modeLabel = if ($DryRun) { "dry-run" } else { "apply" }
    $results = New-Object System.Collections.Generic.List[object]

    foreach ($dir in $selectedDirs) {
        $path = Join-Path $Root $dir
        if (-not (Test-Path -LiteralPath $path)) {
            $results.Add([pscustomobject]@{ Dir = $dir; Status = "SKIP"; Detail = "missing" })
            continue
        }

        Write-SyncLog "Importing $dir with $modeLabel"
        $args = @("import", "markdown", $path, "--library", $script:memoryLibrary)
        if (-not $DryRun) {
            $args += "--apply"
        }
        $commandResult = Invoke-MemoryNativeCommand -FilePath $mgimind -Arguments $args
        $output = @($commandResult.Output)
        $exitCode = $commandResult.ExitCode
        if ($exitCode -eq 0) {
            $summary = (($output | Select-String -Pattern "Applied:|Run with --apply|files scanned" | Select-Object -Last 2) -join " ")
            $results.Add([pscustomobject]@{ Dir = $dir; Status = "OK"; Detail = $summary })
            Write-SyncLog "OK $dir"
        } else {
            $detail = (($output | Select-Object -First 5) -join " ")
            $results.Add([pscustomobject]@{ Dir = $dir; Status = "FAIL"; Detail = $detail })
            Write-SyncLog "FAIL $dir exit=$exitCode $detail"
        }
    }

    $statsResult = Invoke-MemoryNativeCommand -FilePath $mgimind -Arguments @('stats')
    $stats = @($statsResult.Output)
    if ($statsResult.ExitCode -eq 0) {
        $statsText = ($stats -join " ")
        Write-SyncLog "Stats: $statsText"
    } else {
        Write-SyncLog "Stats failed: $($stats -join ' ')"
    }

    $results | Format-Table -AutoSize
    $processExit = if (@($results | Where-Object { $_.Status -eq "FAIL" }).Count -gt 0) { 1 } else { 0 }
} finally {
    if ($lockAcquired) {
        try { $syncMutex.ReleaseMutex() } catch { }
    }
    $syncMutex.Dispose()
}

exit $processExit
