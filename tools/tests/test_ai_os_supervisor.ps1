[CmdletBinding()]
param(
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

$supervisor = Join-Path $Root "tools/ai_os_supervisor.ps1"
$taskInstaller = Join-Path $Root "tools/install_ai_os_supervisor_task.ps1"
if (-not (Test-Path -LiteralPath $supervisor)) {
    throw "Missing shared supervisor: $supervisor"
}
if (-not (Test-Path -LiteralPath $taskInstaller)) {
    throw "Missing shared supervisor task installer: $taskInstaller"
}

$fixture = Join-Path $env:TEMP ("ai os супервизор test " + [guid]::NewGuid().ToString("N"))
$registryPath = Join-Path $fixture "state.json"
New-Item -ItemType Directory -Path $fixture | Out-Null

try {
    $supervisorSource = Get-Content -LiteralPath $supervisor -Raw -Encoding UTF8
    if ($supervisorSource -match "CommandLine\s+-notmatch\s+'--start-hidden'") {
        throw 'Supervisor ignores an interactively opened project center and can spawn a hidden duplicate.'
    }
    if ($supervisorSource -notmatch 'Stopped duplicate Control Center') {
        throw 'Supervisor does not collapse duplicate project-center processes.'
    }

    $workspaces = @()
    for ($index = 0; $index -lt 10; $index++) {
        $workspaceRoot = Join-Path $fixture "рабочая среда $index"
        New-Item -ItemType Directory -Path $workspaceRoot | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $workspaceRoot "10_Project") | Out-Null
        Set-Content -LiteralPath (Join-Path $workspaceRoot "AGENTS.md") -Encoding UTF8 -Value "# fixture"
        $workspaces += [ordered]@{
            id = "ws-test-$index"
            root = $workspaceRoot
            projectName = "Одинаковое имя"
            automationEnabled = $true
            registeredUnix = 1
            updatedUnix = 1
        }
    }
    [ordered]@{
        schemaVersion = 2
        activeWorkspaceId = "ws-test-7"
        workspaces = $workspaces
    } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $registryPath -Encoding UTF8

    # Windows PowerShell switches native stdout to an OEM code page when its own
    # stdout is redirected. Force UTF-8 on both sides so non-ASCII workspace
    # paths survive the child-process JSON boundary used by release builds.
    $previousConsoleEncoding = [Console]::OutputEncoding
    try {
        [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
        $escapedSupervisor = $supervisor.Replace("'", "''")
        $escapedRegistryPath = $registryPath.Replace("'", "''")
        $planCommand = @"
[Console]::OutputEncoding = [Text.UTF8Encoding]::new(`$false)
& '$escapedSupervisor' -RegistryPath '$escapedRegistryPath' -Once -PlanOnly
exit `$LASTEXITCODE
"@
        $encodedPlanCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($planCommand))
        $output = @(& powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -EncodedCommand $encodedPlanCommand 2>&1)
    } finally {
        [Console]::OutputEncoding = $previousConsoleEncoding
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Supervisor plan failed: $($output -join ' ')"
    }
    $plan = ($output -join "`n") | ConvertFrom-Json
    if ($plan.workspaceCount -ne 10 -or $plan.enabledCount -ne 10) {
        throw "Supervisor did not preserve ten workspaces: $($output -join ' ')"
    }
    $expectedActiveId = "ws-test-7"
    $expectedActiveRoot = [IO.Path]::GetFullPath([string]$workspaces[7].root)
    $actualActiveRoot = if ([string]::IsNullOrWhiteSpace([string]$plan.activeRoot)) {
        "<empty>"
    } else {
        [IO.Path]::GetFullPath([string]$plan.activeRoot)
    }
    if (
        [string]$plan.activeWorkspaceId -ne $expectedActiveId -or
        $actualActiveRoot -ne $expectedActiveRoot
    ) {
        throw (
            "Supervisor selected the wrong active workspace. " +
            "expectedId=$expectedActiveId actualId=$($plan.activeWorkspaceId) " +
            "expectedRoot=$expectedActiveRoot actualRoot=$actualActiveRoot plan=$($output -join ' ')"
        )
    }
    if ($plan.taskName -ne "AI-OS Supervisor") {
        throw "Supervisor task is not global: $($plan.taskName)"
    }

    $taskSource = Get-Content -LiteralPath $taskInstaller -Raw -Encoding UTF8
    if ($taskSource -notmatch 'AI-OS Supervisor' -or $taskSource -notmatch 'MultipleInstances IgnoreNew') {
        throw "Supervisor task contract is missing the global name or single-instance setting."
    }
    if ($taskSource -match 'TaskName.*ProjectName') {
        throw "Supervisor task name still depends on a project name."
    }

    $watchedRoot = $workspaces[3].root
    $tools = Join-Path $watchedRoot "tools"
    $syncMarker = Join-Path $watchedRoot ".sync-called"
    New-Item -ItemType Directory -Path $tools | Out-Null
    Set-Content -LiteralPath (Join-Path $tools "sync_mgimind.ps1") -Encoding UTF8 -Value @'
param([string]$Root,[string[]]$Dirs)
Add-Content -LiteralPath (Join-Path $Root '.sync-called') -Encoding UTF8 -Value ($Dirs -join ',')
exit 0
'@
    $stdoutPath = Join-Path $fixture "supervisor.stdout.log"
    $stderrPath = Join-Path $fixture "supervisor.stderr.log"
    $testMutexName = "Local\AI_OS_Shared_Supervisor_Test_$([guid]::NewGuid().ToString('N'))"
    $arguments = "-NoProfile -ExecutionPolicy RemoteSigned -File `"$supervisor`" -RegistryPath `"$registryPath`" -PollSeconds 2 -DebounceSeconds 5 -MutexName `"$testMutexName`""
    $process = Start-Process -FilePath "powershell.exe" `
        -ArgumentList $arguments `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath `
        -PassThru
    try {
        $supervisorLog = Join-Path $fixture "supervisor.log"
        $readyDeadline = (Get-Date).AddSeconds(30)
        $readyPattern = 'Watch ready id=ws-test-3'
        while ((Get-Date) -lt $readyDeadline) {
            if ($process.HasExited) {
                $stderrText = if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Raw -Encoding UTF8 } else { "" }
                throw "Supervisor exited before watch initialization. exit=$($process.ExitCode) $stderrText"
            }
            if ((Test-Path -LiteralPath $supervisorLog) -and (Get-Content -LiteralPath $supervisorLog -Raw -Encoding UTF8) -match $readyPattern) {
                break
            }
            Start-Sleep -Milliseconds 250
        }
        if (-not (Test-Path -LiteralPath $supervisorLog) -or (Get-Content -LiteralPath $supervisorLog -Raw -Encoding UTF8) -notmatch $readyPattern) {
            throw "Supervisor did not initialize the watched workspace within 30 seconds."
        }
        Set-Content -LiteralPath (Join-Path $watchedRoot "10_Project/Changed.md") -Encoding UTF8 -Value "# changed"
        $deadline = (Get-Date).AddSeconds(20)
        while (-not (Test-Path -LiteralPath $syncMarker) -and (Get-Date) -lt $deadline) {
            Start-Sleep -Milliseconds 500
        }
        if (-not (Test-Path -LiteralPath $syncMarker)) {
            $logText = if (Test-Path -LiteralPath $supervisorLog) {
                Get-Content -LiteralPath $supervisorLog -Raw -Encoding UTF8
            } else {
                "<missing supervisor.log>"
            }
            throw "One shared supervisor did not sync the changed workspace within the debounce window.`n$logText"
        }
        $syncedDirs = Get-Content -LiteralPath $syncMarker -Raw -Encoding UTF8
        if ($syncedDirs -notmatch '10_Project') {
            throw "Supervisor synced the wrong directories: $syncedDirs"
        }
    } finally {
        if (-not $process.HasExited) { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue }
    }

    Write-Host "PASS one supervisor plans and watches ten independent workspaces through one global task"
    exit 0
} finally {
    if (Test-Path -LiteralPath $fixture) {
        Remove-Item -LiteralPath $fixture -Recurse -Force
    }
}
