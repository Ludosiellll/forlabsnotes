[CmdletBinding()]
param(
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

$fixture = Join-Path $env:TEMP ("ai-os-dashboard-isolation-" + [guid]::NewGuid().ToString("N"))
$template = Join-Path $Root "distribution/workspace-template"

try {
    New-Item -ItemType Directory -Force -Path $fixture | Out-Null
    & robocopy.exe $template $fixture /E /R:1 /W:1 /XD ".git" ".local" "target" "gen" "resources" /XF "ai_os.config.json" ".mcp.json" /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -gt 7) {
        throw "Fixture copy failed with robocopy exit $LASTEXITCODE"
    }

    $fakeMind = Join-Path $fixture "fake-mgimind.cmd"
    @'
@echo off
if "%2"=="--json" (
  echo {"libraries":{"current-project":7,"another-project":99},"total_memories":106}
) else (
  echo Total memories: 106
)
'@ | Set-Content -LiteralPath $fakeMind -Encoding ASCII

    [ordered]@{
        memoryToolPath = $fakeMind
        memoryLibrary = "current-project"
        powershellPath = (Get-Process -Id $PID).Path
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $fixture "tools/ai_os.config.json") -Encoding UTF8

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $fixture "tools/make_dashboard.ps1") -Root $fixture | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Dashboard build failed with exit $LASTEXITCODE"
    }

    $dashboard = Get-Content -LiteralPath (Join-Path $fixture ".local/dashboard.html") -Raw -Encoding UTF8
    if ($dashboard -notmatch '<b>7</b><span>') {
        throw "Dashboard did not use the selected project's memory-library count."
    }
    if ($dashboard -match '<b>106</b><span>') {
        throw "Dashboard exposed the all-project memory total."
    }

    Write-Output "PASS dashboard memory count is isolated to the active project"
} finally {
    if (Test-Path -LiteralPath $fixture) {
        Remove-Item -LiteralPath $fixture -Recurse -Force
    }
}
