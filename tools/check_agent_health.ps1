[CmdletBinding()]
param(
    [string]$Root = "",
    [ValidateRange(1, 600)]
    [int]$MemoryLockTimeoutSeconds = 240,
    [Parameter(DontShow = $true)]
    [switch]$TestInjectFailure
)

# Workspace health check. Content checks always run; memory-layer checks are
# driven by tools/ai_os.config.json and report SKIP until it is configured
# (see TEMPLATE_SETUP.md step 4). Exit code 1 only on FAIL.

$ErrorActionPreference = "Stop"
$runningOnWindows = $PSVersionTable.PSEdition -eq 'Desktop' -or $IsWindows
$powerShellExecutable = (Get-Process -Id $PID).Path
if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent $PSScriptRoot
}
$results = New-Object System.Collections.Generic.List[object]

function Add-Check {
    param(
        [string]$Name,
        [ValidateSet("OK", "WARN", "FAIL", "SKIP")]
        [string]$Status,
        [string]$Detail = ""
    )
    $script:results.Add([pscustomobject]@{
        Name = $Name
        Status = $Status
        Detail = $Detail
    })
}

$memoryMutex = $null
$memoryLockAcquired = $false
function Get-SharedSupervisorBinding {
    if ($runningOnWindows) {
        $registryPath = Join-Path $env:LOCALAPPDATA "AI OS Setup/state.json"
    } else {
        $stateHome = if ($env:XDG_STATE_HOME) { $env:XDG_STATE_HOME } else { Join-Path $HOME '.local/state' }
        $registryPath = Join-Path $stateHome 'ai-os/state.json'
    }
    if (-not (Test-Path -LiteralPath $registryPath)) { return $null }
    try {
        $registry = Get-Content -LiteralPath $registryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $normalizedRoot = [IO.Path]::GetFullPath($Root).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
        $comparison = if ($runningOnWindows) { [StringComparison]::OrdinalIgnoreCase } else { [StringComparison]::Ordinal }
        $workspace = @($registry.workspaces | Where-Object {
            -not [string]::IsNullOrWhiteSpace([string]$_.root) -and
            [IO.Path]::GetFullPath([string]$_.root).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar).Equals($normalizedRoot, $comparison)
        } | Select-Object -First 1)
        if (-not $workspace.Count) { return $null }
        $task = if ($runningOnWindows) { Get-ScheduledTask -TaskName "AI-OS Supervisor" -ErrorAction SilentlyContinue } else { $null }
        $ready = $false
        $detail = ''
        if (-not $runningOnWindows) {
            $configHome = if ($env:XDG_CONFIG_HOME) { $env:XDG_CONFIG_HOME } else { Join-Path $HOME '.config' }
            $stateHome = if ($env:XDG_STATE_HOME) { $env:XDG_STATE_HOME } else { Join-Path $HOME '.local/state' }
            $pidPath = Join-Path $stateHome 'ai-os/supervisor.pid'
            $pidAlive = $false
            if (Test-Path -LiteralPath $pidPath) {
                $knownPid = 0
                if ([int]::TryParse((Get-Content -LiteralPath $pidPath -Raw).Trim(), [ref]$knownPid)) {
                    $pidAlive = $null -ne (Get-Process -Id $knownPid -ErrorAction SilentlyContinue)
                }
            }
            $systemdActive = $false
            $systemctl = Get-Command systemctl -ErrorAction SilentlyContinue
            if ($systemctl) {
                & $systemctl.Source --user is-active --quiet ai-os-supervisor.service 2>$null
                $systemdActive = $LASTEXITCODE -eq 0
            }
            $autostartPath = Join-Path $configHome 'autostart/ai-os-supervisor.desktop'
            $ready = $systemdActive -or $pidAlive
            $detail = if ($systemdActive) {
                'shared supervisor active via systemd --user'
            } elseif ($pidAlive) {
                'shared supervisor active via XDG fallback'
            } elseif (Test-Path -LiteralPath $autostartPath) {
                'XDG autostart is installed but the supervisor is not running in this session'
            } else {
                'Linux shared supervisor is not installed'
            }
        }
        return [pscustomobject]@{
            Workspace = $workspace[0]
            Task = $task
            Enabled = ($workspace[0].automationEnabled -ne $false)
            Active = ($registry.activeWorkspaceId -eq $workspace[0].id)
            Ready = $ready
            Detail = $detail
        }
    } catch {
        return $null
    }
}

function Add-SharedSupervisorCheck {
    param(
        [string]$Name,
        $Binding,
        [string]$Purpose
    )
    if ($null -eq $Binding) { return $false }
    if (-not $Binding.Enabled) {
        Add-Check $Name "SKIP" "$Purpose is disabled for this workspace in AI OS Setup"
        return $true
    }
    if (-not $runningOnWindows) {
        $status = if ($Binding.Ready) { 'OK' } else { 'WARN' }
        Add-Check $Name $status "${Purpose}: $($Binding.Detail)"
        return $true
    }
    if ($null -eq $Binding.Task) {
        Add-Check $Name "WARN" "workspace expects the shared supervisor, but task 'AI-OS Supervisor' is missing"
        return $true
    }
    $problems = @(Get-ScheduledTaskContractProblems $Binding.Task)
    if ($problems.Count) {
        Add-Check $Name "FAIL" ($problems -join "; ")
    } elseif ($Binding.Task.State -eq 'Running') {
        $activeDetail = if ($Binding.Active) { "; this is the active workspace" } else { "; starts on demand when this workspace becomes active" }
        Add-Check $Name "OK" "shared supervisor running; $Purpose managed$activeDetail"
    } else {
        Add-Check $Name "WARN" "shared supervisor state=$($Binding.Task.State); $Purpose is not currently managed"
    }
    return $true
}

$sharedSupervisor = Get-SharedSupervisorBinding

try {
    $memoryMutexPrefix = if ($runningOnWindows) { 'Global\' } else { '' }
    $memoryMutexName = $memoryMutexPrefix + 'AgentMgiSync_' + ($Root.ToLowerInvariant() -replace '[^a-z0-9]', '_')
    $memoryMutex = New-Object System.Threading.Mutex($false, $memoryMutexName)
    try {
        $memoryLockAcquired = $memoryMutex.WaitOne(0)
    } catch [System.Threading.AbandonedMutexException] {
        $memoryLockAcquired = $true
    }
    if (-not $memoryLockAcquired) {
        Write-Verbose "Memory sync is active; waiting up to $MemoryLockTimeoutSeconds seconds before health reads."
        try {
            $memoryLockAcquired = $memoryMutex.WaitOne([TimeSpan]::FromSeconds($MemoryLockTimeoutSeconds))
        } catch [System.Threading.AbandonedMutexException] {
            $memoryLockAcquired = $true
        }
    }
    if (-not $memoryLockAcquired) {
        Add-Check "memory-read-lock" "FAIL" "timed out waiting for an active memory sync to finish"
    }
} catch {
    Add-Check "memory-read-lock" "FAIL" $_.Exception.Message
}

function Get-ScheduledTaskContractProblems {
    param([object]$Task)

    $problems = New-Object System.Collections.Generic.List[string]
    if ($Task.Settings.DisallowStartIfOnBatteries) { $problems.Add("cannot start on battery") }
    if ($Task.Settings.StopIfGoingOnBatteries) { $problems.Add("stops on battery") }
    if (-not $Task.Settings.StartWhenAvailable) { $problems.Add("missed runs are not recovered") }
    if ([int]$Task.Settings.RestartCount -lt 3) { $problems.Add("restart count is below 3") }
    if (@($Task.Triggers).Count -lt 2) { $problems.Add("fewer than two triggers") }
    return @($problems)
}

function Get-AiOsConfig {
    param([string]$BaseRoot)

    $configPath = Join-Path $BaseRoot "tools/ai_os.config.json"
    if (-not (Test-Path -LiteralPath $configPath)) {
        return $null
    }
    try {
        $cfg = Get-Content -Raw -Encoding UTF8 -Path $configPath | ConvertFrom-Json
    } catch {
        return $null
    }
    if (-not $cfg.memoryToolPath -or -not $cfg.memoryLibrary) { return $null }
    if ("$($cfg.memoryToolPath)$($cfg.memoryLibrary)" -match '\{\{') { return $null }
    if (-not (Test-Path -LiteralPath $cfg.memoryToolPath)) {
        $cmd = Get-Command $cfg.memoryToolPath -ErrorAction SilentlyContinue
        if (-not $cmd) { return $null }
        $cfg.memoryToolPath = $cmd.Source
    }
    return $cfg
}

function Resolve-WikilinkTarget {
    param([string]$Target)

    $clean = (($Target -split "\|")[0] -split "#")[0].Trim()
    if ([string]::IsNullOrWhiteSpace($clean)) {
        return $true
    }

    $direct = Join-Path $Root ($clean + ".md")
    if (Test-Path -LiteralPath $direct) {
        return $true
    }

    $leaf = [System.IO.Path]::GetFileName($clean)
    if ([string]::IsNullOrWhiteSpace($leaf)) {
        $leaf = $clean
    }

    $match = Get-ChildItem -LiteralPath $Root -Recurse -File -Filter ($leaf + ".md") -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "[\\/]\.git[\\/]" } |
        Select-Object -First 1

    return ($null -ne $match)
}

$notConfiguredHint = "memory layer not configured yet; copy tools/ai_os.config.template.json to tools/ai_os.config.json and fill it (TEMPLATE_SETUP.md step 4)"

try {
    $canvasFiles = @(Get-ChildItem -LiteralPath $Root -Recurse -File -Filter "*.canvas" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "[\\/]\.git[\\/]" })
    if (-not $canvasFiles.Count) {
        Add-Check "canvas" "SKIP" "no .canvas files in this workspace (optional)"
    } else {
        foreach ($canvasFile in $canvasFiles) {
            $canvas = Get-Content -Raw -Encoding UTF8 -Path $canvasFile.FullName | ConvertFrom-Json
            $nodeIds = @($canvas.nodes | ForEach-Object { $_.id })
            $edgeIds = @($canvas.edges | ForEach-Object { $_.id })
            $allIds = @($nodeIds + $edgeIds)
            $dupes = @($allIds | Group-Object | Where-Object { $_.Count -gt 1 } | ForEach-Object { $_.Name })
            $badEdges = @($canvas.edges | Where-Object { ($nodeIds -notcontains $_.fromNode) -or ($nodeIds -notcontains $_.toNode) } | ForEach-Object { $_.id })
            if ($dupes.Count -or $badEdges.Count) {
                Add-Check "canvas" "FAIL" "$($canvasFile.Name): duplicate IDs: $($dupes -join ', '); bad edges: $($badEdges -join ', ')"
            } else {
                Add-Check "canvas" "OK" "$($canvasFile.Name): nodes=$($canvas.nodes.Count), edges=$($canvas.edges.Count)"
            }
        }
    }
} catch {
    Add-Check "canvas" "FAIL" $_.Exception.Message
}

try {
    $mcpPath = Join-Path $Root ".mcp.json"
    $mcpTemplatePath = Join-Path $Root ".mcp.json.template"
    if (Test-Path -LiteralPath $mcpPath) {
        Get-Content -Raw -Encoding UTF8 -Path $mcpPath | ConvertFrom-Json | Out-Null
        Add-Check ".mcp.json" "OK" "valid JSON"
    } elseif (Test-Path -LiteralPath $mcpTemplatePath) {
        Add-Check ".mcp.json" "SKIP" "not activated; copy .mcp.json.template to .mcp.json when using a memory MCP server"
    } else {
        Add-Check ".mcp.json" "WARN" "neither .mcp.json nor .mcp.json.template found"
    }
} catch {
    Add-Check ".mcp.json" "FAIL" $_.Exception.Message
}

try {
    $missing = New-Object System.Collections.Generic.List[string]
    $mdFiles = Get-ChildItem -LiteralPath $Root -Recurse -File -Filter "*.md" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FullName -notmatch "[\\/]\.git[\\/]" -and
            $_.FullName -notmatch "[\\/]\.local[\\/]" -and
            $_.FullName -notmatch "[\\/]\.venv[^\\/]*[\\/]" -and
            $_.FullName -notmatch "[\\/]template-skills[\\/]" -and
            $_.FullName -notmatch "[\\/]_delivery[\\/]" -and
            $_.FullName -notmatch "[\\/]_to_delete[\\/]"
        }

    foreach ($file in $mdFiles) {
        $text = Get-Content -Raw -Encoding UTF8 -Path $file.FullName
        foreach ($match in [regex]::Matches($text, "\[\[([^\]|#]+)")) {
            if (-not (Resolve-WikilinkTarget $match.Groups[1].Value)) {
                $missing.Add($match.Groups[1].Value)
            }
        }
    }

    $uniqueMissing = @($missing | Sort-Object -Unique)
    if ($uniqueMissing.Count) {
        Add-Check "wikilinks" "WARN" ($uniqueMissing -join "; ")
    } else {
        Add-Check "wikilinks" "OK" "all file targets resolved"
    }
} catch {
    Add-Check "wikilinks" "WARN" $_.Exception.Message
}

try {
    $pattern = '(api[_-]?key|secret[_-]?key|password|token)\s*[:=]\s*["'']?[A-Za-z0-9_./+=-]{20,}|\b(sk-[A-Za-z0-9]{20,}|hf_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[abp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16})\b'
    $textExtensions = @(".md", ".mdc", ".txt", ".json", ".ps1", ".py", ".env", ".yml", ".yaml", ".toml", ".ini", ".template")
    $secretFiles = New-Object System.Collections.Generic.List[string]
    $files = Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FullName -notmatch "[\\/]\.git[\\/]" -and
            $_.FullName -notmatch "[\\/]\.venv[^\\/]*[\\/]" -and
            $_.FullName -notmatch "[\\/]\.local[\\/]" -and
            $_.FullName -notmatch "[\\/]\.obsidian[\\/]" -and
            $_.FullName -notmatch "[\\/]90_Archive[\\/]" -and
            $_.FullName -notmatch "[\\/]_transcripts[\\/]" -and
            $_.FullName -notmatch "[\\/]_to_delete[\\/]" -and
            ($textExtensions -contains $_.Extension)
        }

    foreach ($file in $files) {
        try {
            $text = Get-Content -Raw -Encoding UTF8 -Path $file.FullName
            if ([regex]::IsMatch($text, $pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
                $secretFiles.Add($file.FullName)
            }
        } catch {
            # Ignore unreadable/binary-looking files in this lightweight local scan.
        }
    }

    $uniqueSecretFiles = @($secretFiles | Sort-Object -Unique)
    if ($uniqueSecretFiles.Count) {
        Add-Check "secret-scan" "FAIL" ("possible secrets in: " + ($uniqueSecretFiles -join "; "))
    } else {
        Add-Check "secret-scan" "OK" "no high-confidence patterns"
    }
} catch {
    Add-Check "secret-scan" "WARN" $_.Exception.Message
}

try {
    # Deep secret scan: gitleaks (~170 curated detectors) with the same dir
    # exclusions as the built-in scan (tools/gitleaks.toml). Optional layer -
    # SKIP when the single-binary tool is not installed.
    if ($runningOnWindows) {
        $gitleaks = Join-Path $env:LOCALAPPDATA 'Programs\gitleaks\gitleaks.exe'
    } else {
        $dataHome = if ($env:XDG_DATA_HOME) { $env:XDG_DATA_HOME } else { Join-Path $HOME '.local/share' }
        $gitleaks = Join-Path $dataHome 'ai-os/bin/gitleaks'
    }
    if (-not (Test-Path -LiteralPath $gitleaks)) {
        $glCmd = Get-Command gitleaks -ErrorAction SilentlyContinue
        if ($glCmd) { $gitleaks = $glCmd.Source } else { $gitleaks = $null }
    }
    if (-not $gitleaks) {
        Add-Check "gitleaks-scan" "SKIP" "optional: install the single-binary gitleaks (github.com/gitleaks/gitleaks releases) for a deep secret scan; this check activates automatically"
    } else {
        $glConfig = Join-Path $Root "tools/gitleaks.toml"
        $prevEap = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
        & $gitleaks dir $Root --config $glConfig --no-banner --exit-code 1 2>$null | Out-Null
        $glExit = $LASTEXITCODE
        $ErrorActionPreference = $prevEap
        if ($glExit -eq 0) {
            Add-Check "gitleaks-scan" "OK" "no leaks (curated detector set)"
        } else {
            Add-Check "gitleaks-scan" "FAIL" "gitleaks found potential secrets; inspect: gitleaks dir <workspace> --config tools/gitleaks.toml"
        }
    }
} catch {
    Add-Check "gitleaks-scan" "SKIP" $_.Exception.Message
}

$aiOsConfig = Get-AiOsConfig -BaseRoot $Root

try {
    if ($null -eq $aiOsConfig) {
        Add-Check "memory-doctor" "SKIP" $notConfiguredHint
        Add-Check "memory-stats" "SKIP" $notConfiguredHint
    } else {
        $doctor = & $aiOsConfig.memoryToolPath doctor 2>&1
        if ($LASTEXITCODE -eq 0) {
            Add-Check "memory-doctor" "OK" "doctor OK"
        } else {
            Add-Check "memory-doctor" "FAIL" (($doctor | Select-Object -First 3) -join " ")
        }

        $stats = & $aiOsConfig.memoryToolPath stats 2>&1
        $statsMatch = [regex]::Match(($stats -join "`n"), ([regex]::Escape($aiOsConfig.memoryLibrary) + ':\s*(\d+)\s+memories'))
        if ($LASTEXITCODE -eq 0 -and $statsMatch.Success -and [int]$statsMatch.Groups[1].Value -gt 0) {
            Add-Check "memory-stats" "OK" ("library " + $aiOsConfig.memoryLibrary + ": " + $statsMatch.Groups[1].Value + " memories")
        } elseif ($LASTEXITCODE -eq 0 -and $statsMatch.Success) {
            Add-Check "memory-stats" "WARN" ("library " + $aiOsConfig.memoryLibrary + " has 0 memories; run tools/sync_mgimind.ps1")
        } else {
            Add-Check "memory-stats" "WARN" (($stats | Select-Object -First 3) -join " ")
        }
    }
} catch {
    Add-Check "memory-layer" "WARN" $_.Exception.Message
}

if ($runningOnWindows) {
try {
    # Identify the scheduled task by its action path (this workspace's wrapper
    # script), not by a fixed task name — several workspaces on one machine can
    # each have their own readiness task without name collisions.
    $wrapperPath = Join-Path $Root "tools/run_scheduled_readiness.ps1"
    $wrapperPattern = [regex]::Escape($wrapperPath)
    $matchingTasks = @(Get-ScheduledTask -ErrorAction Stop | Where-Object {
        @($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -match $wrapperPattern
    })
    if (Add-SharedSupervisorCheck -Name "readiness-autorun" -Binding $sharedSupervisor -Purpose "scheduled readiness") {
        # Shared task owns this responsibility.
    } elseif (-not $matchingTasks.Count) {
        Add-Check "readiness-autorun" "SKIP" "no scheduled task runs this workspace's readiness wrapper (optional in minimal install; TEMPLATE_SETUP.md step 6)"
    } else {
        $task = $matchingTasks[0]
        $info = Get-ScheduledTaskInfo -TaskName $task.TaskName -TaskPath $task.TaskPath -ErrorAction Stop
        $contractProblems = @(Get-ScheduledTaskContractProblems $task)
        if ($contractProblems.Count) {
            Add-Check "readiness-autorun" "FAIL" ($contractProblems -join "; ")
        } elseif ($info.LastTaskResult -eq 0) {
            Add-Check "readiness-autorun" "OK" "task '$($task.TaskName)' present; battery/restart/trigger contract OK"
        } else {
            # 267011 = registered but has not run yet; 267009 = currently running.
            Add-Check "readiness-autorun" "WARN" "task '$($task.TaskName)' LastTaskResult=$($info.LastTaskResult)"
        }
    }
} catch {
    Add-Check "readiness-autorun" "SKIP" "cannot query scheduled tasks: $($_.Exception.Message)"
}

try {
    # The watcher task is identified by its script path (name-independent).
    $watcherPath = Join-Path $Root "tools/watch_agent_reimport.ps1"
    $watcherPattern = [regex]::Escape($watcherPath)
    $watcherTasks = @(Get-ScheduledTask -ErrorAction Stop | Where-Object {
        @($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -match $watcherPattern
    })
    if (Add-SharedSupervisorCheck -Name "watcher-autorun" -Binding $sharedSupervisor -Purpose "memory freshness watcher") {
        # Shared task owns this responsibility.
    } elseif (-not $watcherTasks.Count) {
        if ($null -eq $aiOsConfig) {
            Add-Check "watcher-autorun" "SKIP" "memory is not configured, so no watcher task is needed"
        } else {
            Add-Check "watcher-autorun" "WARN" "memory is configured but no scheduled task runs the watcher (TEMPLATE_SETUP.md step 6)"
        }
    } else {
        $contractProblems = @(Get-ScheduledTaskContractProblems $watcherTasks[0])
        if ($contractProblems.Count) {
            Add-Check "watcher-autorun" "FAIL" ($contractProblems -join "; ")
        } elseif ($watcherTasks[0].State -eq 'Running') {
            Add-Check "watcher-autorun" "OK" "task '$($watcherTasks[0].TaskName)' running; battery/restart/trigger contract OK"
        } else {
            Add-Check "watcher-autorun" "WARN" "task '$($watcherTasks[0].TaskName)' state=$($watcherTasks[0].State) (watcher not running)"
        }
    }
} catch {
    Add-Check "watcher-autorun" "SKIP" "cannot query scheduled tasks: $($_.Exception.Message)"
}

try {
    if ($null -eq $aiOsConfig) {
        Add-Check "memory-service-autorun" "SKIP" "memory is not configured"
    } else {
        $memoryStartPath = Join-Path $Root "tools/start_mgimind.ps1"
        $memoryStartPattern = [regex]::Escape($memoryStartPath)
        $memoryTasks = @(Get-ScheduledTask -ErrorAction Stop | Where-Object {
            @($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -match $memoryStartPattern
        })
        if (Add-SharedSupervisorCheck -Name "memory-service-autorun" -Binding $sharedSupervisor -Purpose "memory service") {
            # Shared task owns this responsibility.
        } elseif (-not $memoryTasks.Count) {
            Add-Check "memory-service-autorun" "WARN" "memory is configured but no scheduled task starts its local service"
        } else {
            $memoryTask = $memoryTasks[0]
            $memoryInfo = Get-ScheduledTaskInfo -TaskName $memoryTask.TaskName -TaskPath $memoryTask.TaskPath -ErrorAction Stop
            $contractProblems = @(Get-ScheduledTaskContractProblems $memoryTask)
            if ($contractProblems.Count) {
                Add-Check "memory-service-autorun" "FAIL" ($contractProblems -join "; ")
            } elseif ($memoryInfo.LastTaskResult -eq 0 -or $memoryTask.State -eq 'Running') {
                Add-Check "memory-service-autorun" "OK" "task '$($memoryTask.TaskName)' passed; battery/restart/trigger contract OK"
            } else {
                Add-Check "memory-service-autorun" "WARN" "task '$($memoryTask.TaskName)' LastTaskResult=$($memoryInfo.LastTaskResult)"
            }
        }
    }
} catch {
    Add-Check "memory-service-autorun" "SKIP" "cannot query scheduled tasks: $($_.Exception.Message)"
}

try {
    $controlCenterPath = Join-Path $Root "tools/control-center-app/bin/ai-os-control-center.exe"
    if (-not (Test-Path -LiteralPath $controlCenterPath)) {
        Add-Check "control-center-autorun" "SKIP" "Control Center binary is not bundled"
    } else {
        $controlCenterPattern = [regex]::Escape($controlCenterPath)
        $controlCenterTasks = @(Get-ScheduledTask -ErrorAction Stop | Where-Object {
            @($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -match $controlCenterPattern
        })
        if (Add-SharedSupervisorCheck -Name "control-center-autorun" -Binding $sharedSupervisor -Purpose "Control Center") {
            # Shared task owns this responsibility.
        } elseif (-not $controlCenterTasks.Count) {
            Add-Check "control-center-autorun" "SKIP" "Control Center autostart was not requested"
        } else {
            $controlCenterTask = $controlCenterTasks[0]
            $contractProblems = @(Get-ScheduledTaskContractProblems $controlCenterTask)
            if ($contractProblems.Count) {
                Add-Check "control-center-autorun" "FAIL" ($contractProblems -join "; ")
            } elseif ($controlCenterTask.State -eq 'Running') {
                Add-Check "control-center-autorun" "OK" "task '$($controlCenterTask.TaskName)' running hidden; battery/restart/trigger contract OK"
            } else {
                Add-Check "control-center-autorun" "WARN" "task '$($controlCenterTask.TaskName)' state=$($controlCenterTask.State)"
            }
        }
    }
} catch {
    Add-Check "control-center-autorun" "SKIP" "cannot query scheduled tasks: $($_.Exception.Message)"
}
} else {
    if (-not (Add-SharedSupervisorCheck -Name "readiness-autorun" -Binding $sharedSupervisor -Purpose "scheduled readiness")) {
        Add-Check "readiness-autorun" "SKIP" "workspace is not registered with AI OS Setup"
    }

    if ($null -eq $aiOsConfig) {
        Add-Check "watcher-autorun" "SKIP" "memory is not configured, so no watcher is needed"
        Add-Check "memory-service-autorun" "SKIP" "memory is not configured"
    } else {
        if (-not (Add-SharedSupervisorCheck -Name "watcher-autorun" -Binding $sharedSupervisor -Purpose "memory freshness watcher")) {
            Add-Check "watcher-autorun" "WARN" "memory is configured, but the workspace is not registered with AI OS Setup"
        }
        if (-not (Add-SharedSupervisorCheck -Name "memory-service-autorun" -Binding $sharedSupervisor -Purpose "memory service")) {
            Add-Check "memory-service-autorun" "WARN" "memory is configured, but the workspace is not registered with AI OS Setup"
        }
    }

    $controlCenterPath = Join-Path $Root "tools/control-center-app/bin/ai-os-control-center"
    if (-not (Test-Path -LiteralPath $controlCenterPath)) {
        Add-Check "control-center-autorun" "SKIP" "Control Center Linux binary is not bundled"
    } elseif (-not (Add-SharedSupervisorCheck -Name "control-center-autorun" -Binding $sharedSupervisor -Purpose "Control Center")) {
        Add-Check "control-center-autorun" "SKIP" "Control Center autostart was not requested through AI OS Setup"
    }
}

try {
    $rawTranscripts = @()
    $transcriptsDir = Join-Path $Root "50_Meetings/_transcripts"
    if (Test-Path -LiteralPath $transcriptsDir) {
        $rawTranscripts = @(Get-ChildItem -LiteralPath $transcriptsDir -Recurse -File -Filter "*.md" -ErrorAction SilentlyContinue)
    }
    if ($rawTranscripts.Count) {
        Add-Check "transcripts-in-import-scope" "FAIL" ("raw markdown under 50_Meetings/_transcripts would be imported into the memory layer (markdown import has no exclude flag); move raw transcripts to an archive folder outside the import scope: " + (($rawTranscripts | ForEach-Object { $_.Name }) -join "; "))
    } else {
        Add-Check "transcripts-in-import-scope" "OK" "no markdown under 50_Meetings/_transcripts"
    }
} catch {
    Add-Check "transcripts-in-import-scope" "WARN" $_.Exception.Message
}

try {
    $importDirs = @("01_Index", "10_Project", "20_Domain", "30_Tech", "40_Decisions", "50_Meetings", "60_Tasks", "70_Resources")
    $syncLogPath = Join-Path $Root ".local/mgimind-sync.log"
    if ($null -eq $aiOsConfig) {
        Add-Check "memory-freshness" "SKIP" $notConfiguredHint
    } elseif (-not (Test-Path -LiteralPath $syncLogPath)) {
        Add-Check "memory-freshness" "WARN" "no .local/mgimind-sync.log yet; run tools/sync_mgimind.ps1 after note changes"
    } else {
        $lastApply = @{}
        $currentApplyDir = $null
        foreach ($line in (Get-Content -Encoding UTF8 -Path $syncLogPath)) {
            $mImport = [regex]::Match($line, '^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] Importing (\S+) with (\S+)')
            if ($mImport.Success) {
                if ($mImport.Groups[3].Value -eq "apply") {
                    $currentApplyDir = $mImport.Groups[2].Value
                } else {
                    $currentApplyDir = $null
                }
                continue
            }
            $mOk = [regex]::Match($line, '^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] OK (\S+)$')
            if ($mOk.Success -and $null -ne $currentApplyDir -and $mOk.Groups[2].Value -eq $currentApplyDir) {
                $lastApply[$currentApplyDir] = [datetime]::ParseExact($mOk.Groups[1].Value, "yyyy-MM-dd HH:mm:ss", [System.Globalization.CultureInfo]::InvariantCulture)
                $currentApplyDir = $null
            }
        }

        $staleDirs = New-Object System.Collections.Generic.List[string]
        foreach ($dir in $importDirs) {
            $dirPath = Join-Path $Root $dir
            if (-not (Test-Path -LiteralPath $dirPath)) { continue }
            $newest = Get-ChildItem -LiteralPath $dirPath -Recurse -File -Filter "*.md" -ErrorAction SilentlyContinue |
                Where-Object { $_.FullName -notmatch "[\\/]\.git[\\/]" } |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 1
            if ($null -eq $newest) { continue }
            if (-not $lastApply.ContainsKey($dir)) {
                $staleDirs.Add($dir)
            } elseif ($newest.LastWriteTime -gt $lastApply[$dir].AddSeconds(5)) {
                $staleDirs.Add($dir)
            }
        }

        if ($staleDirs.Count) {
            Add-Check "memory-freshness" "WARN" ("markdown newer than last apply-sync (stale memory index): " + ($staleDirs -join ", ") + "; run tools/sync_mgimind.ps1 -Dirs " + ($staleDirs -join ","))
        } else {
            Add-Check "memory-freshness" "OK" "no markdown newer than last apply-sync"
        }
    }
} catch {
    Add-Check "memory-freshness" "WARN" $_.Exception.Message
}

try {
    $hygieneScript = Join-Path $Root "tools/check_context_hygiene.ps1"
    if (-not (Test-Path -LiteralPath $hygieneScript)) {
        Add-Check "context-hygiene" "WARN" "checker missing"
    } else {
        $hygieneOutput = @(& $powerShellExecutable -NoProfile -File $hygieneScript -Root $Root -Quiet 2>&1)
        if ($LASTEXITCODE -ne 0) {
            Add-Check "context-hygiene" "FAIL" (($hygieneOutput | Select-Object -First 4) -join " ")
        } else {
            $hygieneReport = Get-Content -LiteralPath (Join-Path $Root ".local/context-hygiene.json") -Raw -Encoding UTF8 | ConvertFrom-Json
            $issueParts = New-Object System.Collections.Generic.List[string]
            if (@($hygieneReport.notes.unlinked).Count) { $issueParts.Add("unlinked=$(@($hygieneReport.notes.unlinked).Count)") }
            if (@($hygieneReport.notes.staleActive).Count) { $issueParts.Add("stale=$(@($hygieneReport.notes.staleActive).Count)") }
            if (@($hygieneReport.notes.missingFrontmatter).Count) { $issueParts.Add("frontmatter=$(@($hygieneReport.notes.missingFrontmatter).Count)") }
            if ([int]$hygieneReport.memory.exactDuplicates) { $issueParts.Add("exact-duplicates=$($hygieneReport.memory.exactDuplicates)") }
            if ([int]$hygieneReport.memory.nearDuplicates) { $issueParts.Add("near-duplicates=$($hygieneReport.memory.nearDuplicates)") }
            if (@($hygieneReport.memory.orphanSources).Count) { $issueParts.Add("memory-orphans=$(@($hygieneReport.memory.orphanSources).Count)") }
            if ($hygieneReport.claudeAutoMemory.status -eq "enabled-or-default") { $issueParts.Add("Claude auto-memory enabled") }

            if ($issueParts.Count) {
                Add-Check "context-hygiene" "WARN" (($issueParts.ToArray()) -join "; ")
            } else {
                Add-Check "context-hygiene" "OK" "report-only lint clean; memory was not mutated"
            }
        }
    }
} catch {
    Add-Check "context-hygiene" "FAIL" $_.Exception.Message
}


try {
    $currentFocus = Join-Path $Root "10_Project/Current_Focus.md"
    $lineCount = (Get-Content -Encoding UTF8 -Path $currentFocus).Count
    if ($lineCount -le 180) {
        Add-Check "current-focus-size" "OK" "lines=$lineCount"
    } else {
        Add-Check "current-focus-size" "WARN" "lines=$lineCount; consider compacting"
    }
} catch {
    Add-Check "current-focus-size" "WARN" $_.Exception.Message
}

try {
    $taskLog = Get-Content -Raw -Encoding UTF8 -Path (Join-Path $Root "60_Tasks/Task_Log.md")
    if ($taskLog -notmatch "## Active" -or $taskLog -notmatch "## Waiting") {
        Add-Check "task-log-active" "WARN" "missing '## Active' or '## Waiting' section; cannot count active tasks reliably"
    } else {
        $activeBlock = (($taskLog -split "## Active", 2)[1] -split "## Waiting", 2)[0]
        $activeCount = ([regex]::Matches($activeBlock, "- \[ \]")).Count
        if ($activeCount -le 30) {
            Add-Check "task-log-active" "OK" "active=$activeCount"
        } else {
            Add-Check "task-log-active" "WARN" "active=$activeCount; consider pruning"
        }
    }
} catch {
    Add-Check "task-log-active" "WARN" $_.Exception.Message
}

if ($TestInjectFailure) {
    Add-Check "test-injected" "FAIL" "single failure injected by regression test"
}

if ($memoryLockAcquired) {
    try { $memoryMutex.ReleaseMutex() } catch { }
}
if ($memoryMutex) {
    $memoryMutex.Dispose()
}

$results | Format-Table -AutoSize

try {
    $localDir = Join-Path $Root ".local"
    if (-not (Test-Path -LiteralPath $localDir)) {
        New-Item -ItemType Directory -Force -Path $localDir | Out-Null
    }
    $okCount = @($results | Where-Object { $_.Status -eq "OK" }).Count
    $warnCount = @($results | Where-Object { $_.Status -eq "WARN" }).Count
    $failCount = @($results | Where-Object { $_.Status -eq "FAIL" }).Count
    $skipCount = @($results | Where-Object { $_.Status -eq "SKIP" }).Count
    $stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -Encoding UTF8 -Path (Join-Path $localDir "health-check.log") -Value "[$stamp] OK=$okCount WARN=$warnCount FAIL=$failCount SKIP=$skipCount"
} catch {
    Write-Warning "Could not write health-check.log: $($_.Exception.Message)"
}

if (@($results | Where-Object { $_.Status -eq "FAIL" }).Count -gt 0) {
    exit 1
}

exit 0
