[CmdletBinding()]
param(
    [string]$TemplateRoot = "",
    [string]$OutputDirectory = "",
    [string]$ControlCenterBinary = "",
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$KitVersion = "0.4.5",
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$MemoryVersion = "2.4.0"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($TemplateRoot)) {
    $TemplateRoot = Join-Path (Split-Path -Parent $PSScriptRoot) "distribution/workspace-template"
}
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = [Environment]::GetFolderPath("Desktop")
}

$TemplateRoot = (Resolve-Path -LiteralPath $TemplateRoot).Path
$OutputDirectory = (Resolve-Path -LiteralPath $OutputDirectory).Path
$controlCenterSource = Join-Path $TemplateRoot "tools/control-center-app/src/main.rs"
$controlCenterSetupVersion = ([regex]::Match(
    (Get-Content -LiteralPath $controlCenterSource -Raw -Encoding UTF8),
    '(?m)^const\s+SETUP_VERSION:\s*&str\s*=\s*"([^"]+)";'
)).Groups[1].Value
if ($controlCenterSetupVersion -ne $KitVersion) {
    throw "KitVersion $KitVersion does not match Control Center SETUP_VERSION $controlCenterSetupVersion"
}
$stage = [IO.Path]::GetFullPath((Join-Path $OutputDirectory "AI_OS_TEMPLATE_KIT"))
$expectedParent = [IO.Path]::GetFullPath($OutputDirectory).TrimEnd('\')
if ((Split-Path -Parent $stage).TrimEnd('\') -ne $expectedParent -or (Split-Path -Leaf $stage) -ne "AI_OS_TEMPLATE_KIT") {
    throw "Unsafe stage path: $stage"
}

$zipPath = [IO.Path]::GetFullPath((Join-Path $OutputDirectory "AI_OS_TEMPLATE_KIT_v$KitVersion.zip"))
if ((Split-Path -Parent $zipPath).TrimEnd('\') -ne $expectedParent) {
    throw "Unsafe zip path: $zipPath"
}
$zipHashPath = "$zipPath.sha256"
if ((Split-Path -Parent $zipHashPath).TrimEnd('\') -ne $expectedParent) {
    throw "Unsafe ZIP checksum path: $zipHashPath"
}

$readmeSource = Join-Path $TemplateRoot "70_Resources/Template_Kit_READ_ME_FIRST.md"
$memoryNoteSource = Join-Path $TemplateRoot "70_Resources/Template_Memory_Tool_Install_Note.md"
if ([string]::IsNullOrWhiteSpace($ControlCenterBinary)) {
    $ControlCenterBinary = @(
        'D:\RustBuilds\ai-os-installer\control-center\release\ai-os-control-center.exe',
        (Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'AI_OS_TEMPLATE_v0_1/tools/control-center-app/bin/ai-os-control-center.exe')
    ) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if ([string]::IsNullOrWhiteSpace($ControlCenterBinary)) {
    throw 'Control Center binary is missing. Build the Windows Control Center or pass -ControlCenterBinary explicitly.'
}
foreach ($required in @($readmeSource, $memoryNoteSource, $ControlCenterBinary)) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Required kit input is missing: $required" }
}

$tmp = Join-Path $env:TEMP ("ai-os-kit-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
    $tag = "v$MemoryVersion"
    $archiveName = "mgimind-x86_64-pc-windows-msvc.zip"
    $baseUrl = "https://github.com/madgodinc/mgi-mind/releases/download/$tag"
    $archive = Join-Path $tmp $archiveName
    $publisherHashFile = "$archive.sha256"
    Invoke-WebRequest -Uri "$baseUrl/$archiveName" -OutFile $archive -UseBasicParsing
    Invoke-WebRequest -Uri "$baseUrl/$archiveName.sha256" -OutFile $publisherHashFile -UseBasicParsing

    $expectedArchiveHash = ((Get-Content -LiteralPath $publisherHashFile -Raw) -split '\s+')[0].ToLowerInvariant()
    $actualArchiveHash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualArchiveHash -ne $expectedArchiveHash) {
        throw "MGI-Mind publisher checksum mismatch. Expected $expectedArchiveHash, got $actualArchiveHash"
    }

    $expanded = Join-Path $tmp "expanded"
    Expand-Archive -LiteralPath $archive -DestinationPath $expanded -Force
    $memoryExe = Get-ChildItem -LiteralPath $expanded -Recurse -File -Filter "mgimind.exe" | Select-Object -First 1
    if (-not $memoryExe) { throw "Official archive does not contain mgimind.exe" }
    $reportedVersion = (& $memoryExe.FullName --version 2>&1) -join " "
    if ($LASTEXITCODE -ne 0 -or $reportedVersion -notmatch [regex]::Escape($MemoryVersion)) {
        throw "Downloaded memory tool reports an unexpected version: $reportedVersion"
    }

    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
    New-Item -ItemType Directory -Path $stage | Out-Null
    $templateDestination = Join-Path $stage "AI_OS_TEMPLATE_v0_1"
    $robocopyExit = 0
    & robocopy.exe $TemplateRoot $templateDestination /E /R:1 /W:1 /XD ".local" "target" "gen" "resources" /XF "ai_os.config.json" ".mcp.json" /NFL /NDL /NJH /NJS /NP | Out-Null
    $robocopyExit = $LASTEXITCODE
    if ($robocopyExit -gt 7) { throw "Template copy failed with robocopy exit $robocopyExit" }
    $controlBin = Join-Path $templateDestination 'tools/control-center-app/bin'
    New-Item -ItemType Directory -Force -Path $controlBin | Out-Null
    Copy-Item -LiteralPath $ControlCenterBinary -Destination (Join-Path $controlBin 'ai-os-control-center.exe') -Force

    $readmeText = (Get-Content -LiteralPath $readmeSource -Raw -Encoding UTF8).Replace("{{KIT_VERSION}}", $KitVersion)
    Set-Content -LiteralPath (Join-Path $stage "READ_ME_FIRST.md") -Value $readmeText -Encoding UTF8
    $memoryDestination = Join-Path $stage "memory-tool"
    New-Item -ItemType Directory -Path $memoryDestination | Out-Null
    Copy-Item -LiteralPath $memoryExe.FullName -Destination (Join-Path $memoryDestination "mgimind.exe")
    $installText = (Get-Content -LiteralPath $memoryNoteSource -Raw -Encoding UTF8).Replace("{{MEMORY_VERSION}}", $MemoryVersion)
    Set-Content -LiteralPath (Join-Path $memoryDestination "INSTALL_NOTE.md") -Value $installText -Encoding UTF8

    $licenseUrl = "https://raw.githubusercontent.com/madgodinc/mgi-mind/$tag/LICENSE"
    Invoke-WebRequest -Uri $licenseUrl -OutFile (Join-Path $memoryDestination "LICENSE-MGI-MIND.txt") -UseBasicParsing
    $notice = @"
# Third-party notice

MGI-Mind $MemoryVersion
- Source: https://github.com/madgodinc/mgi-mind/tree/$tag
- License: Apache-2.0 (see LICENSE-MGI-MIND.txt)
- Official Windows archive SHA-256: $actualArchiveHash

The archive was verified against the publisher-provided .sha256 file before mgimind.exe was extracted. Qdrant, ONNX Runtime and model files are not redistributed in this kit; `mgimind doctor --fix` downloads and verifies the versions pinned by MGI-Mind.
"@
    Set-Content -LiteralPath (Join-Path $memoryDestination "THIRD_PARTY_NOTICE.md") -Value $notice -Encoding UTF8

    $binaryFiles = @(
        [pscustomobject]@{ Path = (Join-Path $templateDestination "tools/control-center-app/bin/ai-os-control-center.exe"); Relative = "AI_OS_TEMPLATE_v0_1/tools/control-center-app/bin/ai-os-control-center.exe" },
        [pscustomobject]@{ Path = (Join-Path $memoryDestination "mgimind.exe"); Relative = "memory-tool/mgimind.exe" }
    )
    $hashLines = foreach ($binary in $binaryFiles) {
        $hash = (Get-FileHash -LiteralPath $binary.Path -Algorithm SHA256).Hash.ToLowerInvariant()
        "$hash  $($binary.Relative)"
    }
    Set-Content -LiteralPath (Join-Path $stage "SHA256SUMS.txt") -Value $hashLines -Encoding ASCII
    Set-Content -LiteralPath (Join-Path $memoryDestination "SHA256SUMS.txt") -Value (($hashLines | Where-Object { $_ -match 'memory-tool/mgimind.exe$' }) -replace 'memory-tool/', '') -Encoding ASCII

    $cargoToml = Get-Content -LiteralPath (Join-Path $TemplateRoot "tools/control-center-app/Cargo.toml") -Raw -Encoding UTF8
    $appVersion = [regex]::Match($cargoToml, '(?m)^version\s*=\s*"([^"]+)"').Groups[1].Value
    $manifest = [ordered]@{
        kitVersion = $KitVersion
        createdUtc = (Get-Date).ToUniversalTime().ToString("o")
        templateFolder = "AI_OS_TEMPLATE_v0_1"
        controlCenterVersion = $appVersion
        memoryTool = [ordered]@{
            name = "MGI-Mind"
            version = $MemoryVersion
            source = "https://github.com/madgodinc/mgi-mind/releases/tag/$tag"
            publisherArchiveSha256 = $actualArchiveHash
        }
        author = "Denis Labyntsev (@Ludosiel)"
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $stage "KIT_MANIFEST.json") -Encoding UTF8

    if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
    if (Test-Path -LiteralPath $zipHashPath) { Remove-Item -LiteralPath $zipHashPath -Force }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::CreateFromDirectory($stage, $zipPath, [IO.Compression.CompressionLevel]::Optimal, $false)

    $zip = [IO.Compression.ZipFile]::OpenRead($zipPath)
    try {
        $entries = @($zip.Entries | ForEach-Object { $_.FullName.Replace('\', '/') })
        $requiredEntries = @(
            "READ_ME_FIRST.md",
            "KIT_MANIFEST.json",
            "SHA256SUMS.txt",
            "AI_OS_TEMPLATE_v0_1/AGENTS.md",
            "AI_OS_TEMPLATE_v0_1/TEMPLATE_SETUP.md",
            "AI_OS_TEMPLATE_v0_1/tools/check_context_hygiene.ps1",
            "AI_OS_TEMPLATE_v0_1/tools/install_ai_os_workspace.ps1",
            "AI_OS_TEMPLATE_v0_1/tools/tests/test_context_hygiene.ps1",
            "AI_OS_TEMPLATE_v0_1/tools/tests/test_ai_os_workspace_installer.ps1",
            "AI_OS_TEMPLATE_v0_1/tools/control-center-app/bin/ai-os-control-center.exe",
            "memory-tool/mgimind.exe",
            "memory-tool/LICENSE-MGI-MIND.txt",
            "memory-tool/THIRD_PARTY_NOTICE.md"
        )
        $missing = @($requiredEntries | Where-Object { $entries -notcontains $_ })
        if ($missing.Count) { throw "ZIP is missing required entries: $($missing -join ', ')" }
        $forbidden = @($entries | Where-Object {
            $_ -match '(^|/)(\.local|target|gen)/' -or
            $_ -cmatch '(^|/)resources/' -or
            $_ -match '(^|/)(ai_os\.config\.json|\.mcp\.json)$'
        })
        if ($forbidden.Count) { throw "ZIP contains local/runtime files: $($forbidden -join ', ')" }
    } finally {
        $zip.Dispose()
    }

    $zipHash = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()
    Set-Content -LiteralPath $zipHashPath -Value "$zipHash  $([IO.Path]::GetFileName($zipPath))" -Encoding ASCII
    $recordedZipHash = ((Get-Content -LiteralPath $zipHashPath -Raw -Encoding ASCII) -split '\s+')[0].ToLowerInvariant()
    if ($recordedZipHash -ne $zipHash) {
        throw "ZIP checksum sidecar does not match the built archive."
    }

    Write-Host "Kit built and verified: $zipPath"
    Write-Host "SHA-256: $zipHash"
    Write-Host "Stage folder: $stage"
    Write-Host "MGI-Mind $MemoryVersion publisher archive SHA-256: $actualArchiveHash"
    exit 0
} finally {
    if (Test-Path -LiteralPath $tmp) {
        $resolvedTmp = [IO.Path]::GetFullPath($tmp)
        $tempRoot = [IO.Path]::GetFullPath($env:TEMP).TrimEnd('\')
        if ($resolvedTmp.StartsWith($tempRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
            Remove-Item -LiteralPath $resolvedTmp -Recurse -Force
        }
    }
}
