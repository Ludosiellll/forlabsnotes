[CmdletBinding()]
param(
    [string]$TemplateRoot = "",
    [string]$OutputDirectory = "",
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$ProductVersion = "0.4.5",
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$MemoryVersion = "2.4.0",
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$QdrantVersion = "1.18.1",
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$OnnxRuntimeVersion = "1.24.2",
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$CodeIntelVersion = "0.9.0",
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$TauriCliVersion = "2.11.4",
    [ValidateSet('Online', 'Offline')]
    [string]$DistributionMode = 'Online',
    [string]$CargoTargetDirectory = "D:\RustBuilds\ai-os-installer"
)

$ErrorActionPreference = "Stop"
$buildMutex = New-Object System.Threading.Mutex($false, "Local\AI_OS_Installer_Build")
$hasBuildLock = $buildMutex.WaitOne(0)
if (-not $hasBuildLock) {
    $buildMutex.Dispose()
    throw "Another AI OS installer build is already running."
}

$vaultRoot = Split-Path -Parent $PSScriptRoot
$appRoot = Join-Path $PSScriptRoot "ai-os-installer-app"
if ([string]::IsNullOrWhiteSpace($TemplateRoot)) {
    $versionedTemplate = Join-Path $vaultRoot "distribution/workspace-template"
    if (Test-Path -LiteralPath (Join-Path $versionedTemplate "AGENTS.md")) {
        $TemplateRoot = $versionedTemplate
    } elseif (Test-Path -LiteralPath (Join-Path $vaultRoot "AGENTS.md")) {
        # In a distributed kit the workspace template is already the repository root.
        $TemplateRoot = $vaultRoot
    } else {
        throw "Workspace template was not found next to the build script."
    }
}
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = [Environment]::GetFolderPath("Desktop")
}

$TemplateRoot = (Resolve-Path -LiteralPath $TemplateRoot).Path
$OutputDirectory = (Resolve-Path -LiteralPath $OutputDirectory).Path
$appRoot = (Resolve-Path -LiteralPath $appRoot).Path
$templateVersion = ([regex]::Match((Get-Content -LiteralPath (Join-Path $TemplateRoot "CHANGELOG.md") -Raw -Encoding UTF8), '(?m)^##\s+(\d+\.\d+\.\d+)\b')).Groups[1].Value
if ($templateVersion -ne $ProductVersion) {
    throw "ProductVersion $ProductVersion does not match template version $templateVersion"
}
$controlCenterSource = Join-Path $TemplateRoot "tools/control-center-app/src/main.rs"
$controlCenterSetupVersion = ([regex]::Match(
    (Get-Content -LiteralPath $controlCenterSource -Raw -Encoding UTF8),
    '(?m)^const\s+SETUP_VERSION:\s*&str\s*=\s*"([^"]+)";'
)).Groups[1].Value
if ($controlCenterSetupVersion -ne $ProductVersion) {
    throw "ProductVersion $ProductVersion does not match Control Center SETUP_VERSION $controlCenterSetupVersion"
}
$resources = [IO.Path]::GetFullPath((Join-Path $appRoot "resources"))
if ((Split-Path -Parent $resources).TrimEnd('\') -ne $appRoot.TrimEnd('\') -or (Split-Path -Leaf $resources) -ne "resources") {
    throw "Unsafe generated resources path: $resources"
}

$cargoToml = Get-Content -LiteralPath (Join-Path $appRoot "Cargo.toml") -Raw -Encoding UTF8
$configuredVersion = [regex]::Match($cargoToml, '(?m)^version\s*=\s*"([^"]+)"').Groups[1].Value
if ($configuredVersion -ne $ProductVersion) {
    throw "ProductVersion $ProductVersion does not match installer Cargo.toml version $configuredVersion"
}
$tauriConfig = Get-Content -LiteralPath (Join-Path $appRoot "tauri.conf.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ([string]$tauriConfig.version -ne $ProductVersion) {
    throw "ProductVersion $ProductVersion does not match tauri.conf.json version $($tauriConfig.version)"
}
if ([string]$tauriConfig.bundle.windows.webviewInstallMode.type -ne 'downloadBootstrapper' -or
    [string]$tauriConfig.bundle.windows.nsis.compression -ne 'none') {
    throw 'The online Setup must use the WebView bootstrapper and uncompressed NSIS startup path.'
}
$offlineConfig = Get-Content -LiteralPath (Join-Path $appRoot 'tauri.offline.conf.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ([string]$offlineConfig.bundle.windows.webviewInstallMode.type -ne 'offlineInstaller' -or
    @($offlineConfig.bundle.resources) -notcontains 'resources/memory-tool' -or
    @($offlineConfig.bundle.resources) -notcontains 'resources/memory-runtime' -or
    @($offlineConfig.bundle.resources) -notcontains 'resources/code-intel-tool') {
    throw 'The Offline Kit configuration must include WebView and all local package directories.'
}

foreach ($required in @(
    (Join-Path $TemplateRoot "AGENTS.md"),
    (Join-Path $vaultRoot "tools/control-center-app/Cargo.toml"),
    (Join-Path $vaultRoot "tools/install_ai_os_workspace.ps1"),
    (Join-Path $vaultRoot "tools/ai_os_package_cache.psm1"),
    (Join-Path $vaultRoot "tools/ai_os_supervisor.ps1"),
    (Join-Path $vaultRoot "tools/install_ai_os_supervisor_task.ps1"),
    (Join-Path $appRoot "icons/icon.ico"),
    (Join-Path $appRoot "tauri.offline.conf.json")
)) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Required installer input is missing: $required" }
}

$tmp = Join-Path $env:TEMP ("ai-os-installer-build-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tmp | Out-Null

function Get-VerifiedReleaseAsset {
    param(
        [string]$Repository,
        [string]$Tag,
        [string]$AssetName,
        [string]$ChecksumsName,
        [string]$DestinationDirectory
    )

    $release = Invoke-RestMethod `
        -Uri "https://api.github.com/repos/$Repository/releases/tags/$Tag" `
        -Headers @{ "User-Agent" = "ai-os-installer-builder" }
    $asset = @($release.assets | Where-Object { $_.name -eq $AssetName }) | Select-Object -First 1
    $checksums = @($release.assets | Where-Object { $_.name -eq $ChecksumsName }) | Select-Object -First 1
    if (-not $asset -or -not $checksums) {
        throw "Release $Repository $Tag is missing $AssetName or $ChecksumsName"
    }

    New-Item -ItemType Directory -Force -Path $DestinationDirectory | Out-Null
    $archive = Join-Path $DestinationDirectory $AssetName
    $sums = Join-Path $DestinationDirectory $ChecksumsName
    if (-not (Test-Path -LiteralPath $archive)) {
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $archive -UseBasicParsing
    }
    if (-not (Test-Path -LiteralPath $sums)) {
        Invoke-WebRequest -Uri $checksums.browser_download_url -OutFile $sums -UseBasicParsing
    }
    $line = Get-Content -LiteralPath $sums -Encoding UTF8 | Where-Object {
        $_ -match [regex]::Escape($AssetName) -and $_ -notmatch [regex]::Escape($AssetName + '.bundle')
    } | Select-Object -First 1
    if (-not $line) { throw "Publisher checksum for $AssetName was not found." }
    $expected = (($line.Trim() -split '\s+')[0]).ToLowerInvariant()
    $actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($expected -ne $actual) {
        throw "Publisher checksum mismatch for $AssetName. Expected $expected, got $actual"
    }
    return [pscustomobject]@{
        Archive = $archive
        ArchiveName = $AssetName
        DownloadUrl = [string]$asset.browser_download_url
        SizeBytes = [long](Get-Item -LiteralPath $archive).Length
        Sha256 = $actual
        Release = $release
    }
}

function Get-VerifiedDigestReleaseAsset {
    param(
        [string]$Repository,
        [string]$Tag,
        [string]$AssetName,
        [string]$DestinationDirectory
    )

    $release = Invoke-RestMethod `
        -Uri "https://api.github.com/repos/$Repository/releases/tags/$Tag" `
        -Headers @{ "User-Agent" = "ai-os-installer-builder" }
    $asset = @($release.assets | Where-Object { $_.name -eq $AssetName }) | Select-Object -First 1
    if (-not $asset) {
        throw "Release $Repository $Tag is missing $AssetName"
    }
    $digestMatch = [regex]::Match([string]$asset.digest, '^sha256:([0-9a-fA-F]{64})$')
    if (-not $digestMatch.Success) {
        throw "GitHub did not publish a SHA-256 digest for $Repository $Tag $AssetName"
    }
    $expected = $digestMatch.Groups[1].Value.ToLowerInvariant()
    New-Item -ItemType Directory -Force -Path $DestinationDirectory | Out-Null
    $archive = Join-Path $DestinationDirectory $AssetName
    if (-not (Test-Path -LiteralPath $archive)) {
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $archive -UseBasicParsing
    }
    $actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($expected -ne $actual) {
        throw "Publisher digest mismatch for $AssetName. Expected $expected, got $actual"
    }
    [pscustomobject]@{
        Archive = $archive
        ArchiveName = $AssetName
        DownloadUrl = [string]$asset.browser_download_url
        SizeBytes = [long](Get-Item -LiteralPath $archive).Length
        Sha256 = $actual
        Release = $release
    }
}

function Initialize-MsvcEnvironment {
    if (Get-Command link.exe -ErrorAction SilentlyContinue) { return }

    $candidates = New-Object System.Collections.Generic.List[string]
    $vswhereCandidates = @(
        (Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'),
        (Join-Path $env:ProgramFiles 'Microsoft Visual Studio/Installer/vswhere.exe')
    )
    foreach ($vswhere in $vswhereCandidates) {
        if (-not (Test-Path -LiteralPath $vswhere)) { continue }
        $installation = (& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2>$null | Select-Object -First 1)
        if ($installation) { $candidates.Add((Join-Path $installation 'VC/Auxiliary/Build/vcvars64.bat')) }
    }
    foreach ($drive in @(Get-PSDrive -PSProvider FileSystem)) {
        $candidates.Add((Join-Path $drive.Root 'Visual Studio/VC/Auxiliary/Build/vcvars64.bat'))
    }
    foreach ($base in @(
        (Join-Path $env:ProgramFiles 'Microsoft Visual Studio/2022'),
        (Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/2022')
    )) {
        if (Test-Path -LiteralPath $base) {
            Get-ChildItem -LiteralPath $base -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                $candidates.Add((Join-Path $_.FullName 'VC/Auxiliary/Build/vcvars64.bat'))
            }
        }
    }

    $vcvars = $candidates.ToArray() | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $vcvars) {
        throw 'MSVC C++ build tools were not found. Install the Visual Studio Desktop development with C++ workload.'
    }

    $environmentLines = & cmd.exe /d /s /c "`"$vcvars`" >nul && set"
    if ($LASTEXITCODE -ne 0) { throw "vcvars64.bat failed: $vcvars" }
    foreach ($line in $environmentLines) {
        $separator = $line.IndexOf('=')
        if ($separator -le 0) { continue }
        $name = $line.Substring(0, $separator)
        $value = $line.Substring($separator + 1)
        [Environment]::SetEnvironmentVariable($name, $value, 'Process')
    }
    if (-not (Get-Command link.exe -ErrorAction SilentlyContinue)) {
        throw "MSVC environment loaded from $vcvars, but link.exe is still unavailable."
    }
    Write-Host "MSVC environment: $vcvars"
}

try {
    Write-Host "Building Windows Control Center from the versioned release source..."
    Initialize-MsvcEnvironment
    $controlTarget = Join-Path $CargoTargetDirectory 'control-center'
    $previousControlTarget = $env:CARGO_TARGET_DIR
    $env:CARGO_TARGET_DIR = $controlTarget
    try {
        Push-Location (Join-Path $vaultRoot 'tools/control-center-app')
        try {
            & cargo test
            if ($LASTEXITCODE -ne 0) { throw 'Control Center Rust tests failed.' }
            & cargo build --release
            if ($LASTEXITCODE -ne 0) { throw 'Control Center Windows build failed.' }
        } finally { Pop-Location }
    } finally {
        $env:CARGO_TARGET_DIR = $previousControlTarget
    }
    $controlCenterExe = Join-Path $controlTarget 'release/ai-os-control-center.exe'
    if (-not (Test-Path -LiteralPath $controlCenterExe)) { throw "Built Control Center is missing: $controlCenterExe" }

    if (Test-Path -LiteralPath $resources) {
        Remove-Item -LiteralPath $resources -Recurse -Force
    }
    New-Item -ItemType Directory -Path $resources | Out-Null

    Write-Host "Staging sanitized workspace template..."
    $templateDestination = Join-Path $resources "workspace-template"
    & robocopy.exe $TemplateRoot $templateDestination /E /R:1 /W:1 /XD ".git" ".local" "target" "gen" "resources" /XF "ai_os.config.json" ".mcp.json" /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -gt 7) { throw "Template staging failed with robocopy exit $LASTEXITCODE" }
    $controlBin = Join-Path $templateDestination 'tools/control-center-app/bin'
    New-Item -ItemType Directory -Force -Path $controlBin | Out-Null
    Copy-Item -LiteralPath $controlCenterExe -Destination (Join-Path $controlBin 'ai-os-control-center.exe') -Force
    Copy-Item -LiteralPath (Join-Path $vaultRoot "tools/install_ai_os_workspace.ps1") -Destination (Join-Path $resources "install_ai_os_workspace.ps1")
    Copy-Item -LiteralPath (Join-Path $vaultRoot "tools/ai_os_package_cache.psm1") -Destination (Join-Path $resources "ai_os_package_cache.psm1")
    Copy-Item -LiteralPath (Join-Path $vaultRoot "tools/ai_os_supervisor.ps1") -Destination (Join-Path $resources "ai_os_supervisor.ps1")
    Copy-Item -LiteralPath (Join-Path $vaultRoot "tools/install_ai_os_supervisor_task.ps1") -Destination (Join-Path $resources "install_ai_os_supervisor_task.ps1")

    Write-Host "Downloading and verifying MGI-Mind $MemoryVersion..."
    $memoryDownload = Join-Path $CargoTargetDirectory "downloads/memory-$MemoryVersion"
    $memory = Get-VerifiedReleaseAsset `
        -Repository "madgodinc/mgi-mind" `
        -Tag "v$MemoryVersion" `
        -AssetName "mgimind-x86_64-pc-windows-msvc.zip" `
        -ChecksumsName "mgimind-x86_64-pc-windows-msvc.zip.sha256" `
        -DestinationDirectory $memoryDownload
    $memoryExpanded = Join-Path $tmp "memory-expanded"
    Expand-Archive -LiteralPath $memory.Archive -DestinationPath $memoryExpanded -Force
    $memoryExe = Get-ChildItem -LiteralPath $memoryExpanded -Recurse -File -Filter "mgimind.exe" | Select-Object -First 1
    if (-not $memoryExe) { throw "MGI-Mind archive does not contain mgimind.exe" }
    $memoryDestination = Join-Path $resources "memory-tool"
    New-Item -ItemType Directory -Force -Path $memoryDestination | Out-Null
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/madgodinc/mgi-mind/v$MemoryVersion/LICENSE" -OutFile (Join-Path $memoryDestination "LICENSE.txt") -UseBasicParsing
    $memoryBinaryHash = (Get-FileHash -LiteralPath $memoryExe.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $memoryBinarySize = [long]$memoryExe.Length
    if ($DistributionMode -eq 'Offline') {
        Copy-Item -LiteralPath $memoryExe.FullName -Destination (Join-Path $memoryDestination "mgimind.exe")
    }

    Write-Host "Downloading and verifying Qdrant $QdrantVersion for MGI-Mind..."
    $qdrant = Get-VerifiedDigestReleaseAsset `
        -Repository 'qdrant/qdrant' `
        -Tag "v$QdrantVersion" `
        -AssetName 'qdrant-x86_64-pc-windows-msvc.zip' `
        -DestinationDirectory (Join-Path $CargoTargetDirectory "downloads/qdrant-$QdrantVersion")
    $qdrantExpanded = Join-Path $tmp 'qdrant-expanded'
    Expand-Archive -LiteralPath $qdrant.Archive -DestinationPath $qdrantExpanded -Force
    $qdrantExe = Get-ChildItem -LiteralPath $qdrantExpanded -Recurse -File -Filter 'qdrant.exe' | Select-Object -First 1
    if (-not $qdrantExe) { throw 'Qdrant archive does not contain qdrant.exe' }
    $qdrantBinaryHash = (Get-FileHash -LiteralPath $qdrantExe.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $qdrantBinarySize = [long]$qdrantExe.Length

    Write-Host "Downloading and verifying ONNX Runtime $OnnxRuntimeVersion for MGI-Mind..."
    $onnx = Get-VerifiedDigestReleaseAsset `
        -Repository 'microsoft/onnxruntime' `
        -Tag "v$OnnxRuntimeVersion" `
        -AssetName "onnxruntime-win-x64-$OnnxRuntimeVersion.zip" `
        -DestinationDirectory (Join-Path $CargoTargetDirectory "downloads/onnxruntime-$OnnxRuntimeVersion")
    $onnxExpanded = Join-Path $tmp 'onnx-expanded'
    Expand-Archive -LiteralPath $onnx.Archive -DestinationPath $onnxExpanded -Force
    $onnxDll = Get-ChildItem -LiteralPath $onnxExpanded -Recurse -File -Filter 'onnxruntime.dll' | Select-Object -First 1
    if (-not $onnxDll) { throw 'ONNX Runtime archive does not contain onnxruntime.dll' }
    $onnxBinaryHash = (Get-FileHash -LiteralPath $onnxDll.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $onnxBinarySize = [long]$onnxDll.Length
    $memoryRuntimeDestination = Join-Path $resources 'memory-runtime'
    New-Item -ItemType Directory -Force -Path $memoryRuntimeDestination | Out-Null
    if ($DistributionMode -eq 'Offline') {
        Copy-Item -LiteralPath $qdrantExe.FullName -Destination (Join-Path $memoryRuntimeDestination 'qdrant.exe')
        Copy-Item -LiteralPath $onnxDll.FullName -Destination (Join-Path $memoryRuntimeDestination 'onnxruntime.dll')
    }

    Write-Host "Downloading and verifying codebase-memory-mcp $CodeIntelVersion..."
    $codeDownload = Join-Path $CargoTargetDirectory "downloads/code-intel-$CodeIntelVersion"
    $code = Get-VerifiedReleaseAsset `
        -Repository "DeusData/codebase-memory-mcp" `
        -Tag "v$CodeIntelVersion" `
        -AssetName "codebase-memory-mcp-windows-amd64.zip" `
        -ChecksumsName "checksums.txt" `
        -DestinationDirectory $codeDownload
    $codeExpanded = Join-Path $tmp "code-intel-expanded"
    Expand-Archive -LiteralPath $code.Archive -DestinationPath $codeExpanded -Force
    $codeExe = Get-ChildItem -LiteralPath $codeExpanded -Recurse -File -Filter "codebase-memory-mcp.exe" | Select-Object -First 1
    if (-not $codeExe) { throw "codebase-memory-mcp archive does not contain codebase-memory-mcp.exe" }
    $codeDestination = Join-Path $resources "code-intel-tool"
    New-Item -ItemType Directory -Force -Path $codeDestination | Out-Null
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/v$CodeIntelVersion/LICENSE" -OutFile (Join-Path $codeDestination "LICENSE.txt") -UseBasicParsing
    $codeBinaryHash = (Get-FileHash -LiteralPath $codeExe.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $codeBinarySize = [long]$codeExe.Length
    if ($DistributionMode -eq 'Offline') {
        Copy-Item -LiteralPath $codeExe.FullName -Destination (Join-Path $codeDestination "codebase-memory-mcp.exe")
    }
    if ($DistributionMode -eq 'Online' -and
        ((Test-Path -LiteralPath (Join-Path $memoryDestination 'mgimind.exe')) -or
         (Test-Path -LiteralPath (Join-Path $memoryRuntimeDestination 'qdrant.exe')) -or
         (Test-Path -LiteralPath (Join-Path $memoryRuntimeDestination 'onnxruntime.dll')) -or
         (Test-Path -LiteralPath (Join-Path $codeDestination 'codebase-memory-mcp.exe')))) {
        throw 'Online Setup accidentally contains an offline package binary.'
    }

    $manifest = [ordered]@{
        schemaVersion = 2
        productVersion = $ProductVersion
        templateVersion = $templateVersion
        distributionMode = $DistributionMode.ToLowerInvariant()
        createdUtc = (Get-Date).ToUniversalTime().ToString("o")
        author = "Denis Labyntsev (@Ludosiel)"
        memoryTool = [ordered]@{
            name = "MGI-Mind"
            version = $MemoryVersion
            source = "https://github.com/madgodinc/mgi-mind/releases/tag/v$MemoryVersion"
            downloadUrl = $memory.DownloadUrl
            archiveName = $memory.ArchiveName
            archiveSha256 = $memory.Sha256
            archiveSizeBytes = $memory.SizeBytes
            publisherArchiveSha256 = $memory.Sha256
            sha256 = $memoryBinaryHash
            binarySizeBytes = $memoryBinarySize
        }
        memoryQdrant = [ordered]@{
            name = 'Qdrant'
            version = $QdrantVersion
            source = "https://github.com/qdrant/qdrant/releases/tag/v$QdrantVersion"
            downloadUrl = $qdrant.DownloadUrl
            archiveName = $qdrant.ArchiveName
            archiveSha256 = $qdrant.Sha256
            archiveSizeBytes = $qdrant.SizeBytes
            publisherArchiveSha256 = $qdrant.Sha256
            sha256 = $qdrantBinaryHash
            binarySizeBytes = $qdrantBinarySize
        }
        memoryOnnxRuntime = [ordered]@{
            name = 'ONNX Runtime'
            version = $OnnxRuntimeVersion
            source = "https://github.com/microsoft/onnxruntime/releases/tag/v$OnnxRuntimeVersion"
            downloadUrl = $onnx.DownloadUrl
            archiveName = $onnx.ArchiveName
            archiveSha256 = $onnx.Sha256
            archiveSizeBytes = $onnx.SizeBytes
            publisherArchiveSha256 = $onnx.Sha256
            sha256 = $onnxBinaryHash
            binarySizeBytes = $onnxBinarySize
        }
        codeIntelligence = [ordered]@{
            name = "codebase-memory-mcp"
            version = $CodeIntelVersion
            source = "https://github.com/DeusData/codebase-memory-mcp/releases/tag/v$CodeIntelVersion"
            downloadUrl = $code.DownloadUrl
            archiveName = $code.ArchiveName
            archiveSha256 = $code.Sha256
            archiveSizeBytes = $code.SizeBytes
            publisherArchiveSha256 = $code.Sha256
            sha256 = $codeBinaryHash
            binarySizeBytes = $codeBinarySize
        }
        supervisor = [ordered]@{
            scriptSha256 = (Get-FileHash -LiteralPath (Join-Path $resources "ai_os_supervisor.ps1") -Algorithm SHA256).Hash.ToLowerInvariant()
            taskInstallerSha256 = (Get-FileHash -LiteralPath (Join-Path $resources "install_ai_os_supervisor_task.ps1") -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }
    $manifestJson = $manifest | ConvertTo-Json -Depth 6
    [IO.File]::WriteAllText((Join-Path $resources "PAYLOAD_MANIFEST.json"), $manifestJson, (New-Object Text.UTF8Encoding($false)))

    $privacyExtensions = @('.md', '.json', '.ps1', '.sh', '.mdc', '.toml')
    $privacyFiles = @(Get-ChildItem -LiteralPath $templateDestination -Recurse -File | Where-Object {
        $privacyExtensions -contains $_.Extension -and
        $_.Name -notin @('build_ai_os_installer.ps1', 'build_ai_os_linux.sh')
    })
    $privacyHits = @($privacyFiles | Select-String -Pattern '(?i)(?:[a-z]:\\Users\\[^\\\s]+|/home/[^/\s]+)' -ErrorAction SilentlyContinue)
    $privatePatternFile = Join-Path $vaultRoot '.local/private-template-patterns.txt'
    if (Test-Path -LiteralPath $privatePatternFile) {
        $privatePatterns = @(Get-Content -LiteralPath $privatePatternFile -Encoding UTF8 | Where-Object {
            -not [string]::IsNullOrWhiteSpace($_) -and -not $_.TrimStart().StartsWith('#')
        })
        if ($privatePatterns.Count) {
            $privacyHits += @($privacyFiles | Select-String -SimpleMatch -Pattern $privatePatterns -ErrorAction SilentlyContinue)
        }
    }
    $unexpectedPrivacyHits = @($privacyHits | Where-Object { $_.Line -notmatch "Denis Labyntsev|@Ludosiel" })
    if ($unexpectedPrivacyHits.Count) {
        throw "Sanitization check found live-project content in the installer payload: $($unexpectedPrivacyHits[0].Path):$($unexpectedPrivacyHits[0].LineNumber)"
    }

    Write-Host "Running PowerShell installer contract tests..."
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $vaultRoot "tools/tests/test_ai_os_workspace_installer.ps1") -Root $vaultRoot
    if ($LASTEXITCODE -ne 0) { throw "Workspace installer tests failed." }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $vaultRoot "tools/tests/test_template_release_contract.ps1") -Root $vaultRoot
    if ($LASTEXITCODE -ne 0) { throw "Release payload install test failed." }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $vaultRoot "tools/tests/test_ai_os_package_cache.ps1") -Root $vaultRoot
    if ($LASTEXITCODE -ne 0) { throw "Package cache tests failed." }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $vaultRoot "tools/tests/test_ai_os_supervisor.ps1") -Root $vaultRoot
    if ($LASTEXITCODE -ne 0) { throw "Shared supervisor tests failed." }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $vaultRoot "tools/tests/test_dashboard_project_isolation.ps1") -Root $vaultRoot
    if ($LASTEXITCODE -ne 0) { throw "Dashboard project-isolation test failed." }
    & powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File (Join-Path $vaultRoot "tools/tests/test_app_icons.ps1") -Root $vaultRoot
    if ($LASTEXITCODE -ne 0) { throw "Product icon tests failed." }

    Write-Host "Running Rust tests..."
    Initialize-MsvcEnvironment
    $buildOutputExecutable = [IO.Path]::GetFullPath((Join-Path $CargoTargetDirectory 'release/ai-os-workspace-manager.exe'))
    foreach ($process in @(Get-CimInstance Win32_Process -Filter "Name='ai-os-workspace-manager.exe'" -ErrorAction SilentlyContinue | Where-Object {
        -not [string]::IsNullOrWhiteSpace([string]$_.ExecutablePath) -and
        [string]::Equals([IO.Path]::GetFullPath([string]$_.ExecutablePath), $buildOutputExecutable, [StringComparison]::OrdinalIgnoreCase)
    })) {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
        Wait-Process -Id $process.ProcessId -Timeout 10 -ErrorAction SilentlyContinue
    }
    $previousTarget = $env:CARGO_TARGET_DIR
    $previousResource = $env:AI_OS_SETUP_RESOURCE_DIR
    $env:CARGO_TARGET_DIR = $CargoTargetDirectory
    $env:AI_OS_SETUP_RESOURCE_DIR = $resources
    try {
        Push-Location $appRoot
        try {
            & cargo test
            if ($LASTEXITCODE -ne 0) { throw "Rust tests failed." }

            Write-Host "Building $DistributionMode NSIS installer with pinned Tauri CLI $TauriCliVersion..."
            $tauriArgs = @('build', '--bundles', 'nsis')
            if ($DistributionMode -eq 'Offline') {
                $tauriArgs += @('--config', 'tauri.offline.conf.json')
            }
            & npx --yes "@tauri-apps/cli@$TauriCliVersion" @tauriArgs
            if ($LASTEXITCODE -ne 0) { throw "Tauri NSIS build failed." }

            # Keep NSIS as the reliable extraction/registry engine, but never expose its
            # stock wizard. The first visible product surface is our own workspace manager.
            $nsisScript = Get-ChildItem -LiteralPath (Join-Path $CargoTargetDirectory "release/nsis") -Recurse -File -Filter "installer.nsi" |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 1
            if (-not $nsisScript) { throw "Generated NSIS script was not found." }
            $nsisText = Get-Content -LiteralPath $nsisScript.FullName -Raw -Encoding UTF8
            $installerIconPath = (Resolve-Path -LiteralPath (Join-Path $appRoot "icons/icon.ico")).Path
            $nsisText = $nsisText -replace '(?m)^!define INSTALLERICON "[^"\r\n]*"(?=\r?$)', ('!define INSTALLERICON "' + $installerIconPath + '"')
            $nsisText = $nsisText -replace '(?m)^!define UNINSTALLERICON "[^"\r\n]*"(?=\r?$)', ('!define UNINSTALLERICON "' + $installerIconPath + '"')
            if ($nsisText -notmatch '(?m)^!define INSTALLERICON "[^"\r\n]+"(?=\r?$)') {
                throw "NSIS installer icon definition is missing."
            }
            if ($nsisText -notmatch '(?m)^Icon\s+"[^\"]+"\s*$') {
                $nsisText = [regex]::Replace(
                    $nsisText,
                    '(?m)^(OutFile\s+.+)$',
                    "`$1`r`nIcon `"$installerIconPath`"`r`nUninstallIcon `"$installerIconPath`"",
                    1
                )
            }
            if ($nsisText -notmatch '(?m)^SilentInstall\s+silent\s*$') {
                $nsisText = [regex]::Replace(
                    $nsisText,
                    '(?m)^(OutFile\s+.+)$',
                    "`$1`r`nSilentInstall silent`r`nAutoCloseWindow true`r`nShowInstDetails nevershow",
                    1
                )
            }
            $launchFunction = @'
Function .onInstSuccess
  nsis_tauri_utils::RunAsUser "$INSTDIR\${MAINBINARYNAME}.exe" ""
FunctionEnd
'@
            $nsisText = [regex]::Replace(
                $nsisText,
                '(?ms)^Function \.onInstSuccess\s*.*?^FunctionEnd\s*',
                $launchFunction + "`r`n"
            )
            [IO.File]::WriteAllText($nsisScript.FullName, $nsisText, (New-Object Text.UTF8Encoding($false)))

            $makeNsis = Join-Path $env:LOCALAPPDATA "tauri/NSIS/Bin/makensis.exe"
            if (-not (Test-Path -LiteralPath $makeNsis)) {
                $makeNsis = Join-Path $env:LOCALAPPDATA "tauri/NSIS/makensis.exe"
            }
            if (-not (Test-Path -LiteralPath $makeNsis)) { throw "Tauri NSIS compiler was not found." }
            Push-Location $nsisScript.Directory.FullName
            try {
                & $makeNsis /V2 $nsisScript.Name
                if ($LASTEXITCODE -ne 0) { throw "Silent NSIS repack failed." }
                $silentBuiltInstaller = Join-Path $nsisScript.Directory.FullName "nsis-output.exe"
                if (-not (Test-Path -LiteralPath $silentBuiltInstaller)) {
                    throw "Silent NSIS output was not produced: $silentBuiltInstaller"
                }
            } finally {
                Pop-Location
            }
        } finally {
            Pop-Location
        }
    } finally {
        $env:CARGO_TARGET_DIR = $previousTarget
        $env:AI_OS_SETUP_RESOURCE_DIR = $previousResource
    }

    $rawExe = Join-Path $CargoTargetDirectory "release/ai-os-workspace-manager.exe"
    if (-not (Test-Path -LiteralPath $rawExe)) { throw "Built setup executable is missing: $rawExe" }
    $env:AI_OS_SETUP_RESOURCE_DIR = $resources
    try {
        $selftestProcess = Start-Process -FilePath $rawExe -ArgumentList '--selftest' -Wait -PassThru
        if ($selftestProcess.ExitCode -ne 0) { throw "AI OS Setup selftest failed with exit $($selftestProcess.ExitCode)." }
    } finally {
        $env:AI_OS_SETUP_RESOURCE_DIR = $null
    }

    $nsisDirectory = Join-Path $CargoTargetDirectory "release/bundle/nsis"
    if (-not $silentBuiltInstaller -or -not (Test-Path -LiteralPath $silentBuiltInstaller)) {
        throw "Silent NSIS installer was not produced."
    }
    & powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File (Join-Path $vaultRoot "tools/tests/test_embedded_windows_icons.ps1") `
        -Root $vaultRoot -SetupExecutable $silentBuiltInstaller -ControlCenterExecutable $controlCenterExe
    if ($LASTEXITCODE -ne 0) { throw "Embedded Windows icon tests failed." }
    $fileName = if ($DistributionMode -eq 'Offline') {
        "AI_OS_Offline_Kit_v${ProductVersion}_x64.exe"
    } else {
        "AI_OS_Setup_v${ProductVersion}_x64.exe"
    }
    $finalInstaller = Join-Path $OutputDirectory $fileName
    Copy-Item -LiteralPath $silentBuiltInstaller -Destination $finalInstaller -Force
    $finalSize = [long](Get-Item -LiteralPath $finalInstaller).Length
    if ($DistributionMode -eq 'Online' -and $finalSize -gt 104857600L) {
        throw "Online Setup is unexpectedly large: $finalSize bytes"
    }
    $finalHash = (Get-FileHash -LiteralPath $finalInstaller -Algorithm SHA256).Hash.ToLowerInvariant()
    Set-Content -LiteralPath ($finalInstaller + ".sha256") -Encoding ASCII -Value "$finalHash  $([IO.Path]::GetFileName($finalInstaller))"

    Write-Host "Installer built and verified: $finalInstaller"
    Write-Host "SHA-256: $finalHash"
    Write-Host "Note: this beta installer is not code-signed; Windows SmartScreen can show an unknown-publisher warning."
    exit 0
} finally {
    if (Test-Path -LiteralPath $tmp) {
        $resolvedTmp = [IO.Path]::GetFullPath($tmp)
        $tempRoot = [IO.Path]::GetFullPath($env:TEMP).TrimEnd([char]92)
        if ($resolvedTmp.StartsWith($tempRoot + [char]92, [StringComparison]::OrdinalIgnoreCase)) {
            Remove-Item -LiteralPath $resolvedTmp -Recurse -Force
        }
    }
    if ($hasBuildLock) {
        $buildMutex.ReleaseMutex()
    }
    $buildMutex.Dispose()
}
