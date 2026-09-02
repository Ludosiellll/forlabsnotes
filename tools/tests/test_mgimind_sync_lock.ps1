[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$syncScript = Join-Path $repoRoot "tools/sync_mgimind.ps1"
$fixtureRoot = Join-Path $env:TEMP ("ai-os-sync-lock-test-" + [guid]::NewGuid().ToString("N"))
$fakeBin = Join-Path $fixtureRoot "bin"
$stateDir = Join-Path $fixtureRoot "state"
$outputDir = Join-Path $fixtureRoot "output"

New-Item -ItemType Directory -Force -Path $fakeBin, $stateDir, $outputDir, (Join-Path $fixtureRoot "01_Index"), (Join-Path $fixtureRoot "tools") | Out-Null
Set-Content -LiteralPath (Join-Path $fixtureRoot "01_Index/Test.md") -Encoding UTF8 -Value "# Sync lock fixture"

$fakeMgiMind = @'
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$CommandArgs)

$stateDir = $env:AI_OS_SYNC_LOCK_TEST_STATE
if ($CommandArgs.Count -gt 0 -and $CommandArgs[0] -eq "stats") {
    Write-Output "agent: 1 memories"
    exit 0
}

if ($env:AI_OS_SYNC_LOCK_TEST_FORCE_FAIL -eq "1") {
    Write-Error "forced import failure"
    exit 42
}

Write-Error "harmless native-style diagnostic" -ErrorAction Continue

$guardPath = Join-Path $stateDir "active-import.lock"
try {
    $guard = [System.IO.File]::Open(
        $guardPath,
        [System.IO.FileMode]::OpenOrCreate,
        [System.IO.FileAccess]::ReadWrite,
        [System.IO.FileShare]::None
    )
} catch {
    Add-Content -LiteralPath (Join-Path $stateDir "overlap.txt") -Value "overlap"
    Write-Error "concurrent import detected"
    exit 43
}

try {
    Start-Sleep -Milliseconds 1500
    Write-Output "Applied: 1 new file(s), 0 replacement(s)"
} finally {
    $guard.Dispose()
}

exit 0
'@
$fakeMgiMindPath = Join-Path $fakeBin "mgimind.ps1"
Set-Content -LiteralPath $fakeMgiMindPath -Encoding UTF8 -Value $fakeMgiMind
$warningMgiMindPath = Join-Path $fakeBin "mgimind-warning.cmd"
Set-Content -LiteralPath $warningMgiMindPath -Encoding ASCII -Value @'
@echo off
echo harmless native diagnostic 1>&2
if "%1"=="stats" goto stats
echo Applied: 1 new file, 0 replacements
exit /b 0
:stats
echo agent: 1 memories
exit /b 0
'@
@{
    memoryToolPath = $fakeMgiMindPath
    memoryLibrary = "sync-lock-test"
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $fixtureRoot "tools/ai_os.config.json") -Encoding UTF8

$supportsSkipStart = (Get-Content -LiteralPath $syncScript -Raw -Encoding UTF8) -match '\[switch\]\$SkipStart'

$oldPath = $env:PATH
$oldState = $env:AI_OS_SYNC_LOCK_TEST_STATE
$oldForceFail = $env:AI_OS_SYNC_LOCK_TEST_FORCE_FAIL

function Start-SyncProcess {
    param(
        [string]$Name
    )

    $stdout = Join-Path $outputDir "$Name.stdout.txt"
    $stderr = Join-Path $outputDir "$Name.stderr.txt"
    $skipStartArgument = if ($supportsSkipStart) { " -SkipStart" } else { "" }
    $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$syncScript`" -Root `"$fixtureRoot`" -Dirs 01_Index$skipStartArgument"
    return Start-Process -FilePath "powershell.exe" -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
}

try {
    $env:PATH = "$fakeBin;$oldPath"
    $env:AI_OS_SYNC_LOCK_TEST_STATE = $stateDir
    Remove-Item Env:AI_OS_SYNC_LOCK_TEST_FORCE_FAIL -ErrorAction SilentlyContinue

    $first = Start-SyncProcess -Name "first"
    Start-Sleep -Milliseconds 200
    $second = Start-SyncProcess -Name "second"
    $first.WaitForExit()
    $second.WaitForExit()

    $overlapDetected = Test-Path -LiteralPath (Join-Path $stateDir "overlap.txt")
    $firstOutput = Get-Content -LiteralPath (Join-Path $outputDir "first.stdout.txt") -Raw -ErrorAction SilentlyContinue
    $secondOutput = Get-Content -LiteralPath (Join-Path $outputDir "second.stdout.txt") -Raw -ErrorAction SilentlyContinue
    if ($overlapDetected -or $firstOutput -notmatch "OK" -or $secondOutput -notmatch "OK") {
        Write-Error "Concurrent sync serialization failed: overlap=$overlapDetected, firstOK=$($firstOutput -match 'OK'), secondOK=$($secondOutput -match 'OK')"
    }

    $env:AI_OS_SYNC_LOCK_TEST_FORCE_FAIL = "1"
    $previousErrorPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $forcedArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $syncScript, "-Root", $fixtureRoot, "-Dirs", "01_Index")
    if ($supportsSkipStart) { $forcedArgs += "-SkipStart" }
    & powershell.exe @forcedArgs *> (Join-Path $outputDir "forced-failure.txt")
    $forcedFailureExit = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorPreference
    if ($forcedFailureExit -eq 0) {
        Write-Error "A single failed import incorrectly returned exit 0."
    }

    Remove-Item Env:AI_OS_SYNC_LOCK_TEST_FORCE_FAIL -ErrorAction SilentlyContinue
    @{
        memoryToolPath = $warningMgiMindPath
        memoryLibrary = "sync-warning-test"
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $fixtureRoot "tools/ai_os.config.json") -Encoding UTF8
    $warningArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $syncScript, "-Root", $fixtureRoot, "-Dirs", "01_Index")
    if ($supportsSkipStart) { $warningArgs += "-SkipStart" }
    $previousErrorPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & powershell.exe @warningArgs *> (Join-Path $outputDir "warning-success.txt")
    $warningExit = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorPreference
    if ($warningExit -ne 0) {
        Write-Error "Native stderr with exit 0 incorrectly failed sync. exit=$warningExit"
    }

    Write-Output "PASS: concurrent syncs were serialized, stderr with exit 0 stayed successful, and a failed import returned non-zero."
} finally {
    $env:PATH = $oldPath
    if ($null -eq $oldState) {
        Remove-Item Env:AI_OS_SYNC_LOCK_TEST_STATE -ErrorAction SilentlyContinue
    } else {
        $env:AI_OS_SYNC_LOCK_TEST_STATE = $oldState
    }
    if ($null -eq $oldForceFail) {
        Remove-Item Env:AI_OS_SYNC_LOCK_TEST_FORCE_FAIL -ErrorAction SilentlyContinue
    } else {
        $env:AI_OS_SYNC_LOCK_TEST_FORCE_FAIL = $oldForceFail
    }
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force -ErrorAction SilentlyContinue
}
