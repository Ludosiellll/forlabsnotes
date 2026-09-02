[CmdletBinding()]
param(
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}

$payloadTemplate = Join-Path $Root "tools/ai-os-installer-app/resources/workspace-template"
$payloadControlCenter = Join-Path $payloadTemplate "tools/control-center-app/bin/ai-os-control-center.exe"
$templateRoot = if (Test-Path -LiteralPath $payloadControlCenter -PathType Leaf) {
    $payloadTemplate
} else {
    Join-Path $Root "distribution/workspace-template"
}
if (-not (Test-Path -LiteralPath $templateRoot -PathType Container)) {
    # Inside a standalone template kit, the repository root is the template.
    $templateRoot = $Root
}

$installer = Join-Path $Root "tools/install_ai_os_workspace.ps1"
if (-not (Test-Path -LiteralPath $installer -PathType Leaf)) {
    $installer = Join-Path $templateRoot "tools/install_ai_os_workspace.ps1"
}

$fixture = Join-Path $env:TEMP ("ai-os-template-release-" + [guid]::NewGuid().ToString("N"))
$destination = Join-Path $fixture "workspace"
$powerShellExecutable = (Get-Process -Id $PID).Path

try {
    $arguments = @("-NoProfile")
    if ($env:OS -eq "Windows_NT") {
        $arguments += @("-ExecutionPolicy", "RemoteSigned")
    }
    $arguments += @(
        "-File", $installer,
        "-SourceRoot", $templateRoot,
        "-DestinationRoot", $destination,
        "-ProjectName", "Release contract test",
        "-UserName", "Test user",
        "-ProjectSummary", "Isolated verification of the distributable workspace template.",
        "-MemoryLibraryName", "ai-os-template-release-test",
        "-SkipMemory",
        "-SkipCodeIntelligence",
        "-SkipScheduledTasks",
        "-SkipGit"
    )

    $output = @(& $powerShellExecutable @arguments 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "The distributable template could not complete a clean install: $($output -join ' ')"
    }

    $statePath = Join-Path $destination ".local/install-state.json"
    if (-not (Test-Path -LiteralPath $statePath -PathType Leaf)) {
        throw "The clean install did not create install-state.json."
    }
    $state = Get-Content -LiteralPath $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($state.status -notin @("ready", "ready-with-warnings") -or $state.components.readiness -ne "passed") {
        throw "The clean install did not finish in a usable state."
    }

    if (Test-Path -LiteralPath $payloadControlCenter -PathType Leaf) {
        $installedControlCenter = Join-Path $destination "tools/control-center-app/bin/ai-os-control-center.exe"
        if (-not (Test-Path -LiteralPath $installedControlCenter -PathType Leaf)) {
            throw "The release payload did not install AI OS Control Center."
        }
    }

    $readiness = Join-Path $destination "tools/check_ai_os_readiness.ps1"
    $readinessOutput = @(& $powerShellExecutable -NoProfile -File $readiness -Root $destination 2>&1)
    if ($LASTEXITCODE -ne 0) {
        throw "The installed distributable template failed its own readiness check: $($readinessOutput -join ' ')"
    }

    Write-Host "PASS distributable template completes a clean isolated install"
    exit 0
} finally {
    if (Test-Path -LiteralPath $fixture) {
        Remove-Item -LiteralPath $fixture -Recurse -Force
    }
}
