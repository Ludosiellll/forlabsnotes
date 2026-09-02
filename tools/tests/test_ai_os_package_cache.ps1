[CmdletBinding()]
param(
    [string]$Root = ""
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}
$module = Join-Path $Root 'tools/ai_os_package_cache.psm1'
if (-not (Test-Path -LiteralPath $module -PathType Leaf)) {
    throw "Missing package-cache module: $module"
}

$fixture = Join-Path $env:TEMP ("ai-os-package-cache-test-" + [guid]::NewGuid().ToString('N'))
$source = Join-Path $fixture 'source'
$cache = Join-Path $fixture 'data'
$destination = Join-Path $fixture 'bin'
$archive = Join-Path $fixture 'fixture-tool.zip'
$binaryName = if ($env:OS -eq 'Windows_NT') { 'fixture-tool.exe' } else { 'fixture-tool' }
$binary = Join-Path $source $binaryName

New-Item -ItemType Directory -Force -Path $source | Out-Null
try {
    [IO.File]::WriteAllBytes($binary, [byte[]](0..255))
    Compress-Archive -LiteralPath $binary -DestinationPath $archive -CompressionLevel NoCompression
    $binaryHash = (Get-FileHash -LiteralPath $binary -Algorithm SHA256).Hash.ToLowerInvariant()
    $archiveHash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    $archiveSize = [long](Get-Item -LiteralPath $archive).Length
    $binarySize = [long](Get-Item -LiteralPath $binary).Length

    Import-Module $module -Force

    $warningCommand = if ($env:OS -eq 'Windows_NT') {
        @{
            FilePath = $env:ComSpec
            Arguments = @('/d', '/s', '/c', 'echo harmless warning 1>&2 & exit /b 0')
        }
    } else {
        @{
            FilePath = '/bin/sh'
            Arguments = @('-c', 'echo harmless warning >&2; exit 0')
        }
    }
    $warningResult = Invoke-AiOsNativeCommand @warningCommand
    if ($warningResult.ExitCode -ne 0 -or ($warningResult.Output -join "`n") -notmatch 'harmless warning') {
        throw 'A native stderr warning with exit code 0 was treated as a failure.'
    }

    $failureCommand = if ($env:OS -eq 'Windows_NT') {
        @{
            FilePath = $env:ComSpec
            Arguments = @('/d', '/s', '/c', 'exit /b 7')
        }
    } else {
        @{
            FilePath = '/bin/sh'
            Arguments = @('-c', 'exit 7')
        }
    }
    $failureResult = Invoke-AiOsNativeCommand @failureCommand
    if ($failureResult.ExitCode -ne 7) {
        throw "Native command exit code was lost: expected 7, got $($failureResult.ExitCode)."
    }
    $missingResult = Invoke-AiOsNativeCommand -FilePath (Join-Path $fixture 'missing-native-command')
    if ($missingResult.ExitCode -ne -1) {
        throw "A missing native command reused a stale exit code: $($missingResult.ExitCode)."
    }

    $package = @{
        Name = 'fixture-tool'
        Version = '1.2.3'
        BinaryName = $binaryName
        ExpectedBinarySha256 = $binaryHash
        CacheRoot = $cache
        DestinationDirectory = $destination
        DownloadUrl = 'https://example.invalid/fixture-tool.zip'
        ArchiveName = 'fixture-tool.zip'
        ExpectedArchiveSha256 = $archiveHash
        ArchiveSizeBytes = $archiveSize
        BinarySizeBytes = $binarySize
        LocalArchivePath = $archive
    }

    $installed = Resolve-AiOsPackageBinary @package
    if (-not (Test-Path -LiteralPath $installed -PathType Leaf)) {
        throw 'Verified package was not installed.'
    }
    if ((Get-FileHash -LiteralPath $installed -Algorithm SHA256).Hash.ToLowerInvariant() -ne $binaryHash) {
        throw 'Installed package hash does not match the manifest.'
    }

    Remove-Item -LiteralPath $archive -Force
    [IO.File]::WriteAllText($installed, 'corrupt installed binary')
    $reused = Resolve-AiOsPackageBinary @package
    if ((Get-FileHash -LiteralPath $reused -Algorithm SHA256).Hash.ToLowerInvariant() -ne $binaryHash) {
        throw 'A valid cached binary did not repair the shared installation.'
    }

    $cachedBinary = Join-Path $cache ("packages/fixture-tool/1.2.3/$binaryName")
    [IO.File]::WriteAllText($installed, 'corrupt installed binary again')
    [IO.File]::WriteAllText($cachedBinary, 'corrupt cached binary')
    $recovered = Resolve-AiOsPackageBinary @package
    if ((Get-FileHash -LiteralPath $recovered -Algorithm SHA256).Hash.ToLowerInvariant() -ne $binaryHash) {
        throw 'The verified cached archive did not repair a corrupt cached binary.'
    }

    $bundledDestination = Join-Path $fixture 'bundled-bin'
    $bundled = Resolve-AiOsPackageBinary `
        -Name 'fixture-bundled' `
        -Version '1.0.0' `
        -BinaryName $binaryName `
        -ExpectedBinarySha256 $binaryHash `
        -CacheRoot (Join-Path $fixture 'bundled-data') `
        -DestinationDirectory $bundledDestination `
        -BundledBinary $binary
    if ((Get-FileHash -LiteralPath $bundled -Algorithm SHA256).Hash.ToLowerInvariant() -ne $binaryHash) {
        throw 'Offline bundled binary was not installed correctly.'
    }

    $badArchive = Join-Path $fixture 'bad-archive.zip'
    Compress-Archive -LiteralPath $binary -DestinationPath $badArchive -CompressionLevel NoCompression
    $badDestination = Join-Path $fixture 'bad-bin'
    $failedClosed = $false
    try {
        Resolve-AiOsPackageBinary `
            -Name 'fixture-bad' `
            -Version '1.0.0' `
            -BinaryName $binaryName `
            -ExpectedBinarySha256 $binaryHash `
            -CacheRoot (Join-Path $fixture 'bad-data') `
            -DestinationDirectory $badDestination `
            -DownloadUrl 'https://example.invalid/bad.zip' `
            -ArchiveName 'bad.zip' `
            -ExpectedArchiveSha256 ('0' * 64) `
            -ArchiveSizeBytes ([long](Get-Item $badArchive).Length) `
            -BinarySizeBytes $binarySize `
            -LocalArchivePath $badArchive | Out-Null
    } catch {
        $failedClosed = $_.Exception.Message -match 'checksum mismatch'
    }
    if (-not $failedClosed) { throw 'A package with the wrong SHA-256 was not rejected.' }
    if (Test-Path -LiteralPath (Join-Path $badDestination $binaryName)) {
        throw 'A rejected package reached the shared binary directory.'
    }

    $unsafeMetadataRejected = $false
    try {
        Resolve-AiOsPackageBinary `
            -Name '../escape' `
            -Version '1.0.0' `
            -BinaryName $binaryName `
            -ExpectedBinarySha256 $binaryHash `
            -CacheRoot $cache `
            -DestinationDirectory $destination | Out-Null
    } catch {
        $unsafeMetadataRejected = $_.Exception.Message -match 'Unsafe package name'
    }
    if (-not $unsafeMetadataRejected) { throw 'Unsafe package path metadata was accepted.' }

    Write-Host 'PASS package cache verifies native exits, reuses and repairs online/offline packages safely'
    exit 0
} finally {
    Remove-Module ai_os_package_cache -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $fixture) {
        Remove-Item -LiteralPath $fixture -Recurse -Force
    }
}
