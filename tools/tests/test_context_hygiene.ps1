[CmdletBinding()]
param(
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

$checker = Join-Path $Root "tools/check_context_hygiene.ps1"
if (-not (Test-Path -LiteralPath $checker)) {
    throw "Missing context hygiene checker: $checker"
}

$fixture = Join-Path ([System.IO.Path]::GetTempPath()) ("ai-os-context-hygiene-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $fixture | Out-Null

try {
    foreach ($dir in @("01_Index", "10_Project", "tools", ".claude", ".local")) {
        New-Item -ItemType Directory -Force -Path (Join-Path $fixture $dir) | Out-Null
    }

    Set-Content -LiteralPath (Join-Path $fixture "01_Index/Index.md") -Encoding UTF8 -Value @"
---
type: index
status: active
updated: 2026-07-10
---
# Index

- [[10_Project/Linked]]
"@
    Set-Content -LiteralPath (Join-Path $fixture "10_Project/Linked.md") -Encoding UTF8 -Value @"
---
type: project
status: active
updated: 2026-07-10
---
# Linked
"@
    Set-Content -LiteralPath (Join-Path $fixture "10_Project/Unlinked.md") -Encoding UTF8 -Value @"
---
type: project
status: active
updated: 2026-07-10
---
# Unlinked
"@

    Set-Content -LiteralPath (Join-Path $fixture ".claude/settings.json") -Encoding UTF8 -Value '{"autoMemoryEnabled":false}'

    $fakeLog = Join-Path $fixture ".local/fake-memory.log"
    $fakeMemory = Join-Path $fixture "tools/fake-memory.ps1"
    Set-Content -LiteralPath $fakeMemory -Encoding UTF8 -Value @'
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
$log = Join-Path (Split-Path -Parent $PSScriptRoot) ".local/fake-memory.log"
Add-Content -LiteralPath $log -Encoding UTF8 -Value ($Arguments -join " ")
if ($Arguments[0] -eq "consolidate") {
    Write-Output "Consolidation DRY-RUN (no changes)."
    Write-Output "Scanned:              7"
    Write-Output "Exact duplicates:     2"
    Write-Output "Near-duplicates:      1"
    Write-Output "Cold (old + unused):  3"
    exit 0
}
if ($Arguments[0] -eq "export") {
    $outputIndex = [Array]::IndexOf($Arguments, "--output")
    $output = $Arguments[$outputIndex + 1]
    New-Item -ItemType Directory -Force -Path $output | Out-Null
    @(
        [pscustomobject]@{ id = "1"; source = "Linked.md"; content = "linked" },
        [pscustomobject]@{ id = "2"; source = "Deleted_Note.md"; content = "orphan" }
    ) | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output "fixture.json") -Encoding UTF8
    exit 0
}
exit 2
'@

    @{
        memoryToolPath = $fakeMemory
        memoryLibrary = "fixture"
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $fixture "tools/ai_os.config.json") -Encoding UTF8

    $powerShellExecutable = (Get-Process -Id $PID).Path
    $savedTemp = $env:TEMP
    $savedTmp = $env:TMP
    $savedTmpDir = $env:TMPDIR
    try {
        $env:TEMP = $null
        $env:TMP = $null
        $env:TMPDIR = $null
        $output = @(& $powerShellExecutable -NoProfile -File $checker -Root $fixture 2>&1)
        $exitCode = $LASTEXITCODE
    } finally {
        $env:TEMP = $savedTemp
        $env:TMP = $savedTmp
        $env:TMPDIR = $savedTmpDir
    }
    if ($exitCode -ne 0) {
        throw "Context hygiene checker failed with exit $exitCode`: $($output -join ' ')"
    }

    $reportPath = Join-Path $fixture ".local/context-hygiene.json"
    if (-not (Test-Path -LiteralPath $reportPath)) {
        throw "Context hygiene report was not written."
    }
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

    if ([int]$report.memory.exactDuplicates -ne 2 -or [int]$report.memory.nearDuplicates -ne 1) {
        throw "Duplicate counts were not parsed from the dry-run output."
    }
    if (@($report.memory.orphanSources).Count -ne 1 -or @($report.memory.orphanSources)[0] -ne "Deleted_Note.md") {
        throw "Deleted memory source was not reported as an orphan: $($report.memory | ConvertTo-Json -Compress)"
    }
    if (@($report.notes.unlinked | Where-Object { $_ -eq "10_Project/Unlinked.md" }).Count -ne 1) {
        throw "Unlinked canonical note did not use the expected workspace-relative path: $($report.notes.unlinked -join ', ')"
    }
    if ($report.claudeAutoMemory.status -ne "disabled") {
        throw "Project auto-memory setting was not recognized."
    }

    $memoryCalls = Get-Content -LiteralPath $fakeLog -Raw -Encoding UTF8
    if ($memoryCalls -match "--apply|--prune-cold|--archive-cold") {
        throw "Context hygiene checker attempted to mutate memory."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $fixture "10_Project/Unlinked.md"))) {
        throw "Context hygiene checker changed or deleted a canonical note."
    }

    Write-Host "PASS context hygiene is report-only and detects duplicates, orphans and unlinked notes"
    exit 0
} finally {
    if (Test-Path -LiteralPath $fixture) {
        Remove-Item -LiteralPath $fixture -Recurse -Force
    }
}
