[CmdletBinding()]
param(
    [string]$Root = "",
    [switch]$SkipHealth,
    [Parameter(DontShow = $true)]
    [switch]$TestInjectFailure
)

$ErrorActionPreference = "Stop"
$runningOnWindows = $PSVersionTable.PSEdition -eq 'Desktop' -or $IsWindows
$powerShellExecutable = (Get-Process -Id $PID).Path

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent $PSScriptRoot
}

$results = New-Object System.Collections.Generic.List[object]

function Add-ReadinessCheck {
    param(
        [string]$Name,
        [ValidateSet("OK", "WARN", "FAIL")]
        [string]$Status,
        [string]$Detail = ""
    )
    $script:results.Add([pscustomobject]@{
        Name = $Name
        Status = $Status
        Detail = $Detail
    })
}

function Read-Text {
    param([string]$Path)
    $fullPath = Join-Path $Root $Path
    if (-not (Test-Path -LiteralPath $fullPath)) {
        throw "Missing file: $Path"
    }
    return Get-Content -Raw -Encoding UTF8 -Path $fullPath
}

function Test-ContainsAll {
    param(
        [string]$Text,
        [string[]]$Needles
    )
    $missing = @($Needles | Where-Object { $Text -notmatch [regex]::Escape($_) })
    return $missing
}

function Test-PowerShellSyntax {
    param([string]$Path)

    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$tokens, [ref]$errors) | Out-Null
    return @($errors)
}

try {
    $requiredFiles = @(
        "README.md",
        "START_HERE.md",
        "TEMPLATE_SETUP.md",
        "AGENTS.md",
        "CLAUDE.md",
        ".cursor/rules/context-map.mdc",
        ".mcp.json",
        ".gitignore",
        "01_Index/AI_Context.md",
        "01_Index/Project_Map.md",
        "01_Index/User_Working_Profile.md",
        "10_Project/Current_Focus.md",
        "10_Project/Project_Brief.md",
        "30_Tech/Tech_Map.md",
        "30_Tech/Codebase_Map.md",
        "40_Decisions/Decision_Log.md",
        "60_Tasks/Task_Log.md",
        "60_Tasks/System_Proposals.md",
        "70_Resources/Agent_Workflow_Protocol.md",
        "70_Resources/AI_Operating_System.md",
        "70_Resources/AI_Context_Quality_Guide.md",
        "70_Resources/Agent_Context_Automation.md",
        "70_Resources/Skill_Router_Matrix.md",
        "70_Resources/AI_OS_Eval_Prompt_Suite.md",
        "70_Resources/AI_OS_Eval_Run_Log.md",
        "70_Resources/Agent_Skills_Roadmap.md",
        "70_Resources/MGI_Mind_Local_Setup_Template.md",
        "template-skills/SKILLS_MANIFEST.md",
        "tools/check_agent_health.ps1",
        "tools/check_context_hygiene.ps1",
        "tools/check_ai_os_readiness.ps1",
        "tools/install_ai_os_workspace.ps1",
        "tools/ai_os_package_cache.psm1",
        "tools/ai_os_supervisor.ps1",
        "tools/install_ai_os_supervisor_task.ps1",
        "tools/install_ai_os_supervisor_linux.ps1",
        "tools/build_template_kit.ps1",
        "tools/build_ai_os_installer.ps1",
        "tools/build_ai_os_linux.sh",
        "tools/ai-os-installer-app/Cargo.toml",
        "tools/ai-os-installer-app/src/main.rs",
        "tools/install_ai_os_scheduled_tasks.ps1",
        "tools/start_mgimind.ps1",
        "tools/sync_mgimind.ps1",
        "tools/watch_agent_reimport.ps1",
        "tools/run_scheduled_readiness.ps1",
        "tools/sync_agent_skills.ps1",
        "tools/log_agent_event.ps1",
        "tools/make_dashboard.ps1",
        "tools/tests/test_ai_os_exit_codes.ps1",
        "tools/tests/test_context_hygiene.ps1",
        "tools/tests/test_ai_os_workspace_installer.ps1",
        "tools/tests/test_ai_os_package_cache.ps1",
        "tools/tests/test_ai_os_supervisor.ps1",
        "tools/tests/test_dashboard_project_isolation.ps1",
        "tools/tests/test_app_icons.ps1",
        "tools/tests/test_embedded_windows_icons.ps1",
        "tools/tests/test_template_release_contract.ps1",
        "tools/tests/test_scheduled_task_contract.ps1",
        "tools/tests/test_mgimind_cold_start.ps1",
        "tools/tests/test_mgimind_sync_lock.ps1"
    )
    $missing = @($requiredFiles | Where-Object { -not (Test-Path -LiteralPath (Join-Path $Root $_)) })
    if ($missing.Count) {
        Add-ReadinessCheck "required-files" "FAIL" ($missing -join "; ")
    } else {
        Add-ReadinessCheck "required-files" "OK" "all required AI OS files found"
    }
} catch {
    Add-ReadinessCheck "required-files" "FAIL" $_.Exception.Message
}

try {
    $agentSkills = Join-Path $Root ".agents/skills"
    $claudeSkills = Join-Path $Root ".claude/skills"
    $mismatches = New-Object System.Collections.Generic.List[string]
    $canonicalSkills = @(Get-ChildItem -LiteralPath $agentSkills -Directory -ErrorAction Stop | Where-Object {
        Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md")
    })
    foreach ($skill in $canonicalSkills) {
        $target = Join-Path $claudeSkills "$($skill.Name)/SKILL.md"
        $canonicalRelative = ".agents/skills/$($skill.Name)/SKILL.md"
        if (-not (Test-Path -LiteralPath $target)) {
            $mismatches.Add("missing bridge: $($skill.Name)")
        } elseif ((Get-Content -LiteralPath $target -Raw -Encoding UTF8) -notmatch [regex]::Escape($canonicalRelative)) {
            $mismatches.Add("wrong bridge target: $($skill.Name)")
        }
    }
    if ($mismatches.Count) {
        Add-ReadinessCheck "claude-skill-sync" "FAIL" (($mismatches | Select-Object -First 8) -join "; ")
    } else {
        Add-ReadinessCheck "claude-skill-sync" "OK" "$($canonicalSkills.Count) Claude bridges point to canonical .agents/skills"
    }
} catch {
    Add-ReadinessCheck "claude-skill-sync" "FAIL" $_.Exception.Message
}

try {
    $agents = Read-Text "AGENTS.md"
    $missing = Test-ContainsAll $agents @(
        "01_Index/AI_Context.md",
        "70_Resources/Agent_Workflow_Protocol.md",
        "navigation aid",
        "Autonomous Context Capture",
        "Non-conformism"
    )
    if ($missing.Count) {
        Add-ReadinessCheck "agents-entrypoint" "FAIL" ($missing -join "; ")
    } else {
        Add-ReadinessCheck "agents-entrypoint" "OK" "AGENTS.md points to context, protocol, memory and capture rules"
    }
} catch {
    Add-ReadinessCheck "agents-entrypoint" "FAIL" $_.Exception.Message
}

try {
    $claude = Read-Text "CLAUDE.md"
    $missing = Test-ContainsAll $claude @(
        "AGENTS.md",
        "Agent_Workflow_Protocol.md",
        "semantic recall only",
        "mandatory preflight",
        "self-audit",
        "non-yes-man"
    )
    if ($missing.Count) {
        Add-ReadinessCheck "claude-entrypoint" "FAIL" ($missing -join "; ")
    } else {
        Add-ReadinessCheck "claude-entrypoint" "OK" "Claude entrypoint includes recall limits, preflight and self-audit"
    }
} catch {
    Add-ReadinessCheck "claude-entrypoint" "FAIL" $_.Exception.Message
}

try {
    $claudeSettings = Get-Content -LiteralPath (Join-Path $Root ".claude/settings.json") -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($claudeSettings.PSObject.Properties['autoMemoryEnabled'] -and $claudeSettings.autoMemoryEnabled -eq $false) {
        Add-ReadinessCheck "claude-single-truth" "OK" "project auto-memory disabled; canonical notes remain the truth store"
    } else {
        Add-ReadinessCheck "claude-single-truth" "WARN" "Claude auto-memory is enabled/default and can drift from canonical notes"
    }
} catch {
    Add-ReadinessCheck "claude-single-truth" "WARN" $_.Exception.Message
}

try {
    $cursor = Read-Text ".cursor/rules/context-map.mdc"
    $missing = Test-ContainsAll $cursor @(
        "alwaysApply: true",
        "AGENTS.md",
        "Agent_Workflow_Protocol.md",
        "navigation aids, not the source of truth",
        "protocol preflight"
    )
    if ($missing.Count) {
        Add-ReadinessCheck "cursor-entrypoint" "FAIL" ($missing -join "; ")
    } else {
        Add-ReadinessCheck "cursor-entrypoint" "OK" "Cursor rule is always-on and points to shared protocol"
    }
} catch {
    Add-ReadinessCheck "cursor-entrypoint" "FAIL" $_.Exception.Message
}

try {
    $protocol = Read-Text "70_Resources/Agent_Workflow_Protocol.md"
    $missing = Test-ContainsAll $protocol @(
        "Source Of Truth",
        "Mandatory Preflight",
        "Non-Yes-Man Rule",
        "Agent Loop",
        "End-Of-Task Self-Audit",
        "semantic memory"
    )
    if ($missing.Count) {
        Add-ReadinessCheck "workflow-protocol" "FAIL" ($missing -join "; ")
    } else {
        Add-ReadinessCheck "workflow-protocol" "OK" "authority, preflight, challenge, loop and self-audit present"
    }
} catch {
    Add-ReadinessCheck "workflow-protocol" "FAIL" $_.Exception.Message
}

try {
    $router = Read-Text "70_Resources/Skill_Router_Matrix.md"
    $routerNeedles = @(
        "Project restriction / freeze / no-edit mode",
        "UI/UX",
        "diagnosing-bugs",
        "Deploy",
        "External data sync / integrations",
        "domain-modeling",
        "Secrets",
        "New skill discovery/install",
        "never replace the workspace markdown"
    )
    $missing = Test-ContainsAll $router $routerNeedles
    if ($missing.Count) {
        Add-ReadinessCheck "skill-router" "FAIL" ($missing -join "; ")
    } else {
        Add-ReadinessCheck "skill-router" "OK" "critical task classes are routed"
    }
} catch {
    Add-ReadinessCheck "skill-router" "FAIL" $_.Exception.Message
}

try {
    $suite = Read-Text "70_Resources/AI_OS_Eval_Prompt_Suite.md"
    $requiredEvalIds = @(
        "E01-context-recall",
        "E02-ui-review-only",
        "E03-bug-loop",
        "E04-restriction-respect",
        "E05-secret-capture",
        "E06-domain-model",
        "E07-role-boundary",
        "E08-canvas-edit",
        "E09-handoff",
        "E10-skill-install",
        "E11-health-check",
        "E12-review",
        "E13-memory-source-trap",
        "E14-tool-hoarding-trap",
        "E15-stale-memory-conflict",
        "E16-sync-discipline",
        "E17-person-projection-trap",
        "E18-advice-mode-capture",
        "E19-stale-world-fact"
    )
    $missing = Test-ContainsAll $suite $requiredEvalIds
    if ($missing.Count) {
        Add-ReadinessCheck "eval-suite" "FAIL" ($missing -join "; ")
    } else {
        Add-ReadinessCheck "eval-suite" "OK" "E01-E19 prompts present"
    }
} catch {
    Add-ReadinessCheck "eval-suite" "FAIL" $_.Exception.Message
}

try {
    $evalRun = Read-Text "70_Resources/AI_OS_Eval_Run_Log.md"
    if ($evalRun -match '\|\s*(19|20)\d{2}-\d{2}-\d{2}\s*\|\s*E\d{2}[^|]*\|[^|]*\|\s*Pass\s*\|') {
        Add-ReadinessCheck "eval-run-recorded" "OK" "at least one dated eval pass recorded"
    } else {
        Add-ReadinessCheck "eval-run-recorded" "WARN" "no recorded eval passes yet; run the baseline pack in fresh sessions and log results"
    }
} catch {
    Add-ReadinessCheck "eval-run-recorded" "WARN" $_.Exception.Message
}

try {
    $mgiSetup = Read-Text "70_Resources/MGI_Mind_Local_Setup_Template.md"
    $missing = Test-ContainsAll $mgiSetup @(
        "source of truth",
        "rerank",
        "sync_mgimind.ps1",
        "watch_agent_reimport.ps1",
        "raw transcripts"
    )
    if ($missing.Count) {
        Add-ReadinessCheck "mgi-runbook" "FAIL" ($missing -join "; ")
    } else {
        Add-ReadinessCheck "mgi-runbook" "OK" "memory role, import scope, sync and watcher documented"
    }
} catch {
    Add-ReadinessCheck "mgi-runbook" "FAIL" $_.Exception.Message
}

try {
    $scripts = @(
        "tools/check_agent_health.ps1",
        "tools/check_context_hygiene.ps1",
        "tools/check_ai_os_readiness.ps1",
        "tools/install_ai_os_workspace.ps1",
        "tools/ai_os_package_cache.psm1",
        "tools/ai_os_supervisor.ps1",
        "tools/install_ai_os_supervisor_task.ps1",
        "tools/install_ai_os_supervisor_linux.ps1",
        "tools/build_template_kit.ps1",
        "tools/build_ai_os_installer.ps1",
        "tools/install_ai_os_scheduled_tasks.ps1",
        "tools/start_mgimind.ps1",
        "tools/sync_mgimind.ps1",
        "tools/watch_agent_reimport.ps1",
        "tools/run_scheduled_readiness.ps1",
        "tools/sync_agent_skills.ps1",
        "tools/log_agent_event.ps1",
        "tools/make_dashboard.ps1",
        "tools/tests/test_ai_os_exit_codes.ps1",
        "tools/tests/test_context_hygiene.ps1",
        "tools/tests/test_ai_os_workspace_installer.ps1",
        "tools/tests/test_ai_os_package_cache.ps1",
        "tools/tests/test_ai_os_supervisor.ps1",
        "tools/tests/test_dashboard_project_isolation.ps1",
        "tools/tests/test_app_icons.ps1",
        "tools/tests/test_embedded_windows_icons.ps1",
        "tools/tests/test_template_release_contract.ps1",
        "tools/tests/test_scheduled_task_contract.ps1",
        "tools/tests/test_mgimind_cold_start.ps1",
        "tools/tests/test_mgimind_sync_lock.ps1"
    )
    $syntaxErrors = New-Object System.Collections.Generic.List[string]
    foreach ($scriptPath in $scripts) {
        $fullPath = Join-Path $Root $scriptPath
        $errors = Test-PowerShellSyntax $fullPath
        foreach ($parseError in $errors) {
            $syntaxErrors.Add("${scriptPath}: $($parseError.Message)")
        }
    }
    if ($syntaxErrors.Count) {
        Add-ReadinessCheck "powershell-syntax" "FAIL" ($syntaxErrors -join "; ")
    } else {
        Add-ReadinessCheck "powershell-syntax" "OK" "health/sync/watch scripts parse"
    }
} catch {
    Add-ReadinessCheck "powershell-syntax" "FAIL" $_.Exception.Message
}

try {
    $gitignore = Read-Text ".gitignore"
    $missing = Test-ContainsAll $gitignore @(
        ".local/",
        "_transcripts",
        "ai_os.config.json",
        ".mcp.json"
    )
    if ($missing.Count) {
        Add-ReadinessCheck "local-state-ignore" "WARN" ($missing -join "; ")
    } else {
        Add-ReadinessCheck "local-state-ignore" "OK" "local logs, raw transcripts and machine-specific config are ignored"
    }
} catch {
    Add-ReadinessCheck "local-state-ignore" "WARN" $_.Exception.Message
}

if (-not $SkipHealth) {
    try {
        $healthScript = Join-Path $Root "tools/check_agent_health.ps1"
        $healthArgs = @('-NoProfile')
        if ($runningOnWindows) { $healthArgs += @('-ExecutionPolicy', 'RemoteSigned') }
        $healthArgs += @('-File', $healthScript, '-Root', $Root)
        $healthOutput = & $powerShellExecutable @healthArgs 2>&1
        if ($LASTEXITCODE -eq 0) {
            Add-ReadinessCheck "health-check" "OK" "check_agent_health.ps1 passed"
        } else {
            $failureLines = @($healthOutput | Where-Object { ([string]$_) -match '\bFAIL\b' })
            $detailLines = if ($failureLines.Count) { $failureLines | Select-Object -First 5 } else { $healthOutput | Select-Object -Last 12 }
            Add-ReadinessCheck "health-check" "FAIL" (($detailLines | ForEach-Object { [string]$_ }) -join " ")
        }
    } catch {
        Add-ReadinessCheck "health-check" "FAIL" $_.Exception.Message
    }
}

if ($TestInjectFailure) {
    Add-ReadinessCheck "test-injected" "FAIL" "single failure injected by regression test"
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
    $stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -Encoding UTF8 -Path (Join-Path $localDir "readiness-check.log") -Value "[$stamp] OK=$okCount WARN=$warnCount FAIL=$failCount"
} catch {
    Write-Warning "Could not write readiness-check.log: $($_.Exception.Message)"
}

if (@($results | Where-Object { $_.Status -eq "FAIL" }).Count -gt 0) {
    exit 1
}

exit 0
