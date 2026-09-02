[CmdletBinding()]
param(
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

$installer = Join-Path $Root "tools/install_ai_os_workspace.ps1"
if (-not (Test-Path -LiteralPath $installer)) {
    throw "Missing workspace installer: $installer"
}

$fixture = Join-Path $env:TEMP ("ai os установщик test " + [guid]::NewGuid().ToString("N"))
$source = Join-Path $fixture "чистый шаблон"
$destination = Join-Path $fixture "Установленный проект с пробелами"
$memoryDestination = Join-Path $fixture "Проект с чистой памятью"
$fakeMemoryState = Join-Path $fixture "fake-memory-library.txt"
$oldLocalAppData = $env:LOCALAPPDATA
$oldFakeMemoryState = $env:AI_OS_TEST_MEMORY_STATE
New-Item -ItemType Directory -Path $source | Out-Null

try {
    foreach ($dir in @(
        "01_Index",
        "10_Project",
        "30_Tech",
        "tools/tests",
        "tools/control-center-app/bin",
        "template-skills/sample",
        ".claude"
    )) {
        New-Item -ItemType Directory -Force -Path (Join-Path $source $dir) | Out-Null
    }

    Set-Content -LiteralPath (Join-Path $source "AGENTS.md") -Encoding UTF8 -Value "# {{PROJECT_NAME}} for {{USER_NAME}}"
    Set-Content -LiteralPath (Join-Path $source "TEMPLATE_SETUP.md") -Encoding UTF8 -Value "Setup {{PROJECT_NAME}} at {{PROJECT_ROOT}}"
    Set-Content -LiteralPath (Join-Path $source "CHANGELOG.md") -Encoding UTF8 -Value "# Changelog`n`n## 9.8.7 - Fixture"
    Set-Content -LiteralPath (Join-Path $source "01_Index/People.md") -Encoding UTF8 -Value "{{USER_NAME}} | {{CLIENT_NAME}} | {{COMPANY_NAME}}"
    Set-Content -LiteralPath (Join-Path $source "10_Project/Project_Brief.md") -Encoding UTF8 -Value @"
---
type: project
status: draft
updated: YYYY-MM-DD
---
# Project Brief
## Summary
One paragraph: what {{PROJECT_NAME}} is, for whom ({{CLIENT_NAME}} / {{COMPANY_NAME}}), and what the current working focus is.
Code: {{CODE_REPO_PATH}}
"@
    Set-Content -LiteralPath (Join-Path $source "10_Project/Current_Focus.md") -Encoding UTF8 -Value @"
---
type: project
status: active
updated: YYYY-MM-DD
---
# Current Focus
## Now
- Example: project in progress.
"@
    Set-Content -LiteralPath (Join-Path $source "30_Tech/Tech_Map.md") -Encoding UTF8 -Value "# {{PROJECT_NAME}}`nRepo {{CODE_REPO_PATH}}"
    Set-Content -LiteralPath (Join-Path $source "template-skills/sample/SKILL.md") -Encoding UTF8 -Value "# Sample"
    Set-Content -LiteralPath (Join-Path $source ".claude/settings.json") -Encoding UTF8 -Value '{"autoMemoryEnabled":false}'
    Set-Content -LiteralPath (Join-Path $source "tools/control-center-app/bin/ai-os-control-center.exe") -Encoding ASCII -Value "fixture"
    Set-Content -LiteralPath (Join-Path $source "tools/install_ai_os_scheduled_tasks.ps1") -Encoding UTF8 -Value "exit 0"
    Set-Content -LiteralPath (Join-Path $source "tools/install_ai_os_workspace.ps1") -Encoding UTF8 -Value @'
$fixtureTokens = @{
    '{{CLIENT_NAME}}' = 'client'
    '{{COMPANY_NAME}}' = 'company'
}
'@
    Set-Content -LiteralPath (Join-Path $source "tools/check_ai_os_readiness.ps1") -Encoding UTF8 -Value "Write-Host 'fixture readiness'; exit 0"
    Set-Content -LiteralPath (Join-Path $source "tools/start_mgimind.ps1") -Encoding UTF8 -Value "param([string]`$Root); exit 0"
    Set-Content -LiteralPath (Join-Path $source "tools/sync_mgimind.ps1") -Encoding UTF8 -Value @'
param([string]$Root)
$config = Get-Content -LiteralPath (Join-Path $Root 'tools/ai_os.config.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not (Test-Path -LiteralPath $env:AI_OS_TEST_MEMORY_STATE)) { exit 41 }
$libraries = @(Get-Content -LiteralPath $env:AI_OS_TEST_MEMORY_STATE -Encoding UTF8)
if ($libraries -notcontains [string]$config.memoryLibrary) { exit 42 }
exit 0
'@
    Set-Content -LiteralPath (Join-Path $source "tools/sync_agent_skills.ps1") -Encoding UTF8 -Value @'
param([string]$Root)
New-Item -ItemType Directory -Force -Path (Join-Path $Root ".claude/skills/sample") | Out-Null
Set-Content -LiteralPath (Join-Path $Root ".claude/skills/sample/SKILL.md") -Encoding UTF8 -Value "bridge"
exit 0
'@

    $args = @(
        "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $installer,
        "-SourceRoot", $source,
        "-DestinationRoot", $destination,
        "-ProjectName", "Atlas Test",
        "-UserName", "Alex Example",
        "-ClientName", "n/a",
        "-CompanyName", "n/a",
        "-CodeRepoPath", "none yet",
        "-MemoryLibraryName", "atlas-test",
        "-ProjectSummary", "A private planning workspace used to verify the installer.",
        "-SkipMemory",
        "-SkipCodeIntelligence",
        "-SharedSupervisor",
        "-SkipGit"
    )
    $output = @(& powershell.exe @args 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "Fresh install failed: $($output -join ' ')"
    }

    $brief = Get-Content -LiteralPath (Join-Path $destination "10_Project/Project_Brief.md") -Raw -Encoding UTF8
    $agents = Get-Content -LiteralPath (Join-Path $destination "AGENTS.md") -Raw -Encoding UTF8
    if ($agents -notmatch "Atlas Test" -or $brief -notmatch "private planning workspace" -or $brief -match '\{\{PROJECT_NAME\}\}') {
        throw "Project answers were not applied to the installed workspace: $brief"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $destination ".agents/skills/sample/SKILL.md"))) {
        throw "Bundled skills were not activated."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $destination ".claude/skills/sample/SKILL.md"))) {
        throw "Claude skill bridge was not created."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $destination "tools/control-center-app/bin/ai-os-control-center.exe"))) {
        throw "Bundled Control Center was not copied into the installed workspace."
    }
    $installedTool = Join-Path $destination "tools/install_ai_os_workspace.ps1"
    $toolTokens = $null
    $toolErrors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($installedTool, [ref]$toolTokens, [ref]$toolErrors) | Out-Null
    if ($toolErrors.Count -or (Get-Content -LiteralPath $installedTool -Raw -Encoding UTF8) -notmatch '\{\{CLIENT_NAME\}\}') {
        throw "Project token replacement modified protected AI OS implementation files."
    }
    $statePath = Join-Path $destination ".local/install-state.json"
    $state = Get-Content -LiteralPath $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($state.status -ne "ready" -or $state.templateVersion -ne "9.8.7" -or $state.components.automation -ne "shared-supervisor") {
        throw "Install state is missing or incorrect."
    }

    $previousEap = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $second = @(& powershell.exe @args 2>&1)
    $secondExit = $LASTEXITCODE
    $ErrorActionPreference = $previousEap
    if ($secondExit -eq 0) {
        throw "Installer overwrote a configured workspace without -Repair."
    }

    $marker = "USER NOTE MUST SURVIVE REPAIR"
    Add-Content -LiteralPath (Join-Path $destination "10_Project/Project_Brief.md") -Encoding UTF8 -Value $marker
    $managedMarker = Join-Path $source 'tools/managed-runtime-version.txt'
    $installedManagedMarker = Join-Path $destination 'tools/managed-runtime-version.txt'
    Set-Content -LiteralPath $managedMarker -Encoding UTF8 -Value 'managed runtime v2'
    Set-Content -LiteralPath $installedManagedMarker -Encoding UTF8 -Value 'managed runtime v1'
    Set-Content -LiteralPath (Join-Path $source 'tools/ai_os.config.json') -Encoding UTF8 -Value '{"sourceTemplate":true}'
    $installedConfig = Join-Path $destination 'tools/ai_os.config.json'
    $repairArgs = $args + @("-Repair")
    $repair = @(& powershell.exe @repairArgs 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "Repair failed: $($repair -join ' ')"
    }
    $briefAfterRepair = Get-Content -LiteralPath (Join-Path $destination "10_Project/Project_Brief.md") -Raw -Encoding UTF8
    if ($briefAfterRepair -notmatch [regex]::Escape($marker)) {
        throw "Repair overwrote user-owned project notes."
    }
    if ((Get-Content -LiteralPath $installedManagedMarker -Raw -Encoding UTF8).Trim() -ne 'managed runtime v2') {
        throw 'Repair did not refresh managed runtime files.'
    }
    $configAfterRepair = Get-Content -LiteralPath $installedConfig -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($configAfterRepair.sourceTemplate -or $configAfterRepair.memoryLibrary -ne 'atlas-test') {
        throw 'Repair replaced the workspace configuration with template data or changed its project identity.'
    }

    $sourceText = Get-Content -LiteralPath (Join-Path $source "AGENTS.md") -Raw -Encoding UTF8
    if ($sourceText -notmatch '\{\{PROJECT_NAME\}\}') {
        throw "Installer modified its clean source template."
    }

    $fakeMemoryExe = Join-Path $fixture 'mgimind.exe'
    $fakeMemorySource = @'
using System;
using System.IO;

public static class FakeMgiMind
{
    public static int Main(string[] args)
    {
        var state = Environment.GetEnvironmentVariable("AI_OS_TEST_MEMORY_STATE");
        if (string.IsNullOrWhiteSpace(state)) return 90;
        var command = args.Length == 0 ? "" : args[0];
        if (command == "init" || command == "doctor") return 0;
        if (command == "list")
        {
            if (!File.Exists(state))
            {
                Console.WriteLine("No libraries. Create one with `mgimind create <name>`");
                return 0;
            }
            Console.WriteLine("Libraries:");
            foreach (var library in File.ReadAllLines(state)) Console.WriteLine("  - " + library);
            return 0;
        }
        if (command == "create" && args.Length == 2)
        {
            File.AppendAllLines(state, new[] { args[1] });
            Console.WriteLine("Library '" + args[1] + "' created.");
            return 0;
        }
        return 91;
    }
}
'@
    Add-Type -TypeDefinition $fakeMemorySource -Language CSharp -OutputAssembly $fakeMemoryExe -OutputType ConsoleApplication
    $fakeQdrant = Join-Path $fixture 'qdrant.exe'
    $fakeOnnx = Join-Path $fixture 'onnxruntime.dll'
    Set-Content -LiteralPath $fakeQdrant -Encoding ASCII -Value 'fixture qdrant'
    Set-Content -LiteralPath $fakeOnnx -Encoding ASCII -Value 'fixture onnx runtime'
    $env:LOCALAPPDATA = Join-Path $fixture 'localappdata'
    $env:AI_OS_TEST_MEMORY_STATE = $fakeMemoryState

    $memoryArgs = @(
        "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $installer,
        "-SourceRoot", $source,
        "-DestinationRoot", $memoryDestination,
        "-ProjectName", "Memory Test",
        "-UserName", "Alex Example",
        "-MemoryLibraryName", "memory-test",
        "-ProjectSummary", "Verifies clean memory provisioning.",
        "-MemoryToolSource", $fakeMemoryExe,
        "-MemoryToolSha256", (Get-FileHash -LiteralPath $fakeMemoryExe -Algorithm SHA256).Hash,
        "-MemoryToolVersion", "test-1",
        "-MemoryQdrantSource", $fakeQdrant,
        "-MemoryQdrantSha256", (Get-FileHash -LiteralPath $fakeQdrant -Algorithm SHA256).Hash,
        "-MemoryQdrantVersion", "test-1",
        "-MemoryOnnxSource", $fakeOnnx,
        "-MemoryOnnxSha256", (Get-FileHash -LiteralPath $fakeOnnx -Algorithm SHA256).Hash,
        "-MemoryOnnxVersion", "test-1",
        "-SkipCodeIntelligence",
        "-SharedSupervisor",
        "-SkipGit"
    )
    $memoryOutput = @(& powershell.exe @memoryArgs 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "Clean memory install failed: $($memoryOutput -join ' ')"
    }
    $memoryState = Get-Content -LiteralPath (Join-Path $memoryDestination '.local/install-state.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($memoryState.status -ne 'ready' -or $memoryState.components.memory -ne 'installed') {
        throw "Installer did not provision memory before the initial import: $($memoryOutput -join ' ')"
    }

    Write-Host "PASS workspace installer is safe, repeatable, provisions clean memory and preserves user notes during repair"
    exit 0
} finally {
    $env:LOCALAPPDATA = $oldLocalAppData
    $env:AI_OS_TEST_MEMORY_STATE = $oldFakeMemoryState
    if (Test-Path -LiteralPath $fixture) {
        Remove-Item -LiteralPath $fixture -Recurse -Force
    }
}
