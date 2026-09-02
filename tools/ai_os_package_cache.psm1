Set-StrictMode -Version Latest

function Test-AiOsSha256Value {
    param([string]$Value)
    return -not [string]::IsNullOrWhiteSpace($Value) -and $Value -match '^[a-fA-F0-9]{64}$'
}

function Assert-AiOsSafePackageSegment {
    param([string]$Value, [string]$Label)
    if ([string]::IsNullOrWhiteSpace($Value) -or $Value -notmatch '^[A-Za-z0-9._-]+$') {
        throw "Unsafe $Label in package metadata: $Value"
    }
}

function Test-AiOsVerifiedFile {
    param([string]$Path, [string]$ExpectedSha256)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    $actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
    return $actual.Equals($ExpectedSha256, [StringComparison]::OrdinalIgnoreCase)
}

function Copy-AiOsFileAtomically {
    param([string]$Source, [string]$Destination)

    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    $temporary = "$Destination.partial-$([guid]::NewGuid().ToString('N'))"
    try {
        Copy-Item -LiteralPath $Source -Destination $temporary -Force
        if (Test-Path -LiteralPath $Destination) {
            Remove-Item -LiteralPath $Destination -Force
        }
        Move-Item -LiteralPath $temporary -Destination $Destination -Force
    } finally {
        if (Test-Path -LiteralPath $temporary) {
            Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
        }
    }
}

function Set-AiOsPackageExecutable {
    param([string]$Path)

    if ($env:OS -eq 'Windows_NT') {
        Unblock-File -LiteralPath $Path -ErrorAction SilentlyContinue
        return
    }
    & chmod 755 -- $Path
    if ($LASTEXITCODE -ne 0) { throw "Could not mark package executable: $Path" }
}

function Assert-AiOsDownloadUri {
    param([string]$DownloadUrl, [switch]$AllowInsecureLocalhost)

    $uri = $null
    if (-not [Uri]::TryCreate($DownloadUrl, [UriKind]::Absolute, [ref]$uri)) {
        throw "Invalid package download URL: $DownloadUrl"
    }
    if ($uri.Scheme -eq 'https') { return $uri }
    $localHosts = @('localhost', '127.0.0.1', '::1')
    if ($AllowInsecureLocalhost -and $uri.Scheme -eq 'http' -and $localHosts -contains $uri.Host) {
        return $uri
    }
    throw "Package downloads must use HTTPS: $DownloadUrl"
}

function Invoke-AiOsResumableDownload {
    param(
        [string]$DownloadUrl,
        [string]$PartialPath,
        [switch]$AllowInsecureLocalhost
    )

    $uri = Assert-AiOsDownloadUri -DownloadUrl $DownloadUrl -AllowInsecureLocalhost:$AllowInsecureLocalhost
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl -and $env:OS -ne 'Windows_NT') {
        $curl = Get-Command curl -ErrorAction SilentlyContinue
    }
    if ($curl) {
        $common = @(
            '--location', '--fail', '--silent', '--show-error',
            '--retry', '3', '--retry-delay', '2', '--connect-timeout', '15',
            '--output', $PartialPath
        )
        if ($uri.Scheme -eq 'https') {
            $common += @('--proto', '=https', '--proto-redir', '=https')
        }
        $resume = (Test-Path -LiteralPath $PartialPath) -and (Get-Item -LiteralPath $PartialPath).Length -gt 0
        $arguments = @($common)
        if ($resume) { $arguments += @('--continue-at', '-') }
        $arguments += $DownloadUrl
        & $curl.Source @arguments
        $exitCode = $LASTEXITCODE
        if ($exitCode -eq 33 -and $resume) {
            Remove-Item -LiteralPath $PartialPath -Force -ErrorAction SilentlyContinue
            $arguments = @($common) + @($DownloadUrl)
            & $curl.Source @arguments
            $exitCode = $LASTEXITCODE
        }
        if ($exitCode -ne 0) {
            throw "Package download failed with curl exit code $exitCode"
        }
        return
    }

    $temporary = "$PartialPath.download-$([guid]::NewGuid().ToString('N'))"
    try {
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $temporary -UseBasicParsing -MaximumRedirection 8
        Move-Item -LiteralPath $temporary -Destination $PartialPath -Force
    } finally {
        if (Test-Path -LiteralPath $temporary) {
            Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
        }
    }
}

function Resolve-AiOsPackageBinary {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Version,
        [Parameter(Mandatory = $true)][string]$BinaryName,
        [Parameter(Mandatory = $true)][string]$ExpectedBinarySha256,
        [Parameter(Mandatory = $true)][string]$CacheRoot,
        [Parameter(Mandatory = $true)][string]$DestinationDirectory,
        [string]$BundledBinary = '',
        [string]$DownloadUrl = '',
        [string]$ArchiveName = '',
        [string]$ExpectedArchiveSha256 = '',
        [long]$ArchiveSizeBytes = 0,
        [long]$BinarySizeBytes = 0,
        [string]$LocalArchivePath = '',
        [switch]$AllowInsecureLocalhost
    )

    Assert-AiOsSafePackageSegment -Value $Name -Label 'package name'
    Assert-AiOsSafePackageSegment -Value $Version -Label 'package version'
    Assert-AiOsSafePackageSegment -Value $BinaryName -Label 'binary name'
    if (-not (Test-AiOsSha256Value $ExpectedBinarySha256)) {
        throw "Invalid binary SHA-256 for $Name $Version"
    }

    $destination = Join-Path $DestinationDirectory $BinaryName
    if (Test-AiOsVerifiedFile -Path $destination -ExpectedSha256 $ExpectedBinarySha256) {
        Set-AiOsPackageExecutable -Path $destination
        Write-Host "[AI OS Packages] $Name $Version is already installed."
        return $destination
    }

    if (-not [string]::IsNullOrWhiteSpace($BundledBinary) -and (Test-Path -LiteralPath $BundledBinary -PathType Leaf)) {
        if (-not (Test-AiOsVerifiedFile -Path $BundledBinary -ExpectedSha256 $ExpectedBinarySha256)) {
            throw "Bundled binary checksum mismatch for $Name $Version"
        }
        Copy-AiOsFileAtomically -Source $BundledBinary -Destination $destination
        Set-AiOsPackageExecutable -Path $destination
        Write-Host "[AI OS Packages] Installed verified bundled $Name $Version."
        return $destination
    }

    Assert-AiOsSafePackageSegment -Value $ArchiveName -Label 'archive name'
    if (-not (Test-AiOsSha256Value $ExpectedArchiveSha256)) {
        throw "Invalid archive SHA-256 for $Name $Version"
    }
    if (-not $ArchiveName.EndsWith('.zip', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Only ZIP package archives are supported: $ArchiveName"
    }

    $packageRoot = Join-Path (Join-Path (Join-Path $CacheRoot 'packages') $Name) $Version
    $cachedBinary = Join-Path $packageRoot $BinaryName
    $archive = Join-Path $packageRoot $ArchiveName
    $partial = "$archive.partial"
    New-Item -ItemType Directory -Force -Path $packageRoot | Out-Null

    $mutexSeed = [Text.Encoding]::UTF8.GetBytes("$Name|$Version")
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $mutexSuffix = (($sha.ComputeHash($mutexSeed) | ForEach-Object { $_.ToString('x2') }) -join '').Substring(0, 16)
    } finally {
        $sha.Dispose()
    }
    $mutexName = if ($env:OS -eq 'Windows_NT') { "Local\AI_OS_Package_$mutexSuffix" } else { "AI_OS_Package_$mutexSuffix" }
    $mutex = New-Object Threading.Mutex($false, $mutexName)
    $locked = $false
    try {
        try {
            $locked = $mutex.WaitOne([TimeSpan]::FromMinutes(10))
        } catch [Threading.AbandonedMutexException] {
            $locked = $true
        }
        if (-not $locked) { throw "Timed out waiting for the shared package cache: $Name $Version" }

        if (Test-AiOsVerifiedFile -Path $destination -ExpectedSha256 $ExpectedBinarySha256) {
            return $destination
        }
        if (Test-AiOsVerifiedFile -Path $cachedBinary -ExpectedSha256 $ExpectedBinarySha256) {
            Copy-AiOsFileAtomically -Source $cachedBinary -Destination $destination
            Set-AiOsPackageExecutable -Path $destination
            Write-Host "[AI OS Packages] Reused cached $Name $Version."
            return $destination
        }
        if (Test-Path -LiteralPath $cachedBinary) {
            Remove-Item -LiteralPath $cachedBinary -Force
        }

        if (Test-Path -LiteralPath $archive -PathType Leaf) {
            if (-not (Test-AiOsVerifiedFile -Path $archive -ExpectedSha256 $ExpectedArchiveSha256)) {
                Remove-Item -LiteralPath $archive -Force
            }
        }

        if (-not (Test-Path -LiteralPath $archive -PathType Leaf)) {
            if ($ArchiveSizeBytes -gt 0 -or $BinarySizeBytes -gt 0) {
                $driveRoot = [IO.Path]::GetPathRoot([IO.Path]::GetFullPath($packageRoot))
                $required = [Math]::Max(268435456L, ($ArchiveSizeBytes * 2L) + $BinarySizeBytes)
                $available = (New-Object IO.DriveInfo -ArgumentList $driveRoot).AvailableFreeSpace
                if ($available -lt $required) {
                    throw "Not enough free space for $Name. Required: $required bytes; available: $available bytes."
                }
            }

            if (-not [string]::IsNullOrWhiteSpace($LocalArchivePath)) {
                if (-not (Test-Path -LiteralPath $LocalArchivePath -PathType Leaf)) {
                    throw "Local package archive was not found: $LocalArchivePath"
                }
                Copy-Item -LiteralPath $LocalArchivePath -Destination $partial -Force
            } else {
                if ([string]::IsNullOrWhiteSpace($DownloadUrl)) {
                    throw "No verified download URL is available for $Name $Version"
                }
                Write-Host "[AI OS Packages] Downloading $Name $Version. An interrupted download will continue on the next run."
                Invoke-AiOsResumableDownload -DownloadUrl $DownloadUrl -PartialPath $partial -AllowInsecureLocalhost:$AllowInsecureLocalhost
            }
            if (-not (Test-AiOsVerifiedFile -Path $partial -ExpectedSha256 $ExpectedArchiveSha256)) {
                Remove-Item -LiteralPath $partial -Force -ErrorAction SilentlyContinue
                throw "Downloaded archive checksum mismatch for $Name $Version"
            }
            Move-Item -LiteralPath $partial -Destination $archive -Force
        }

        $expanded = Join-Path $packageRoot ("expanded-" + [guid]::NewGuid().ToString('N'))
        try {
            Expand-Archive -LiteralPath $archive -DestinationPath $expanded -Force
            $candidates = @(Get-ChildItem -LiteralPath $expanded -Recurse -File | Where-Object { $_.Name -eq $BinaryName })
            if ($candidates.Count -ne 1) {
                throw "Expected one $BinaryName in $ArchiveName, found $($candidates.Count)"
            }
            if (-not (Test-AiOsVerifiedFile -Path $candidates[0].FullName -ExpectedSha256 $ExpectedBinarySha256)) {
                throw "Extracted binary checksum mismatch for $Name $Version"
            }
            Copy-AiOsFileAtomically -Source $candidates[0].FullName -Destination $cachedBinary
        } finally {
            if (Test-Path -LiteralPath $expanded) {
                Remove-Item -LiteralPath $expanded -Recurse -Force -ErrorAction SilentlyContinue
            }
        }

        Copy-AiOsFileAtomically -Source $cachedBinary -Destination $destination
        Set-AiOsPackageExecutable -Path $destination
        Write-Host "[AI OS Packages] Installed and cached $Name $Version."
        return $destination
    } finally {
        if ($locked) { $mutex.ReleaseMutex() }
        $mutex.Dispose()
    }
}

function Invoke-AiOsNativeCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$Arguments = @()
    )

    # Windows PowerShell can turn a native program's stderr into a terminating
    # NativeCommandError when the caller uses ErrorActionPreference=Stop. Keep
    # stderr as diagnostic output and decide success from the process exit code.
    $previousErrorActionPreference = $ErrorActionPreference
    $lastExitVariable = Get-Variable -Name LASTEXITCODE -Scope Global -ErrorAction SilentlyContinue
    $previousLastExitCode = if ($lastExitVariable) { $lastExitVariable.Value } else { $null }
    try {
        $ErrorActionPreference = 'Continue'
        $global:LASTEXITCODE = $null
        try {
            $output = @(& $FilePath @Arguments 2>&1)
            $exitCode = if ($null -eq $global:LASTEXITCODE) { -1 } else { $global:LASTEXITCODE }
        } catch {
            $output = @($_)
            $exitCode = -1
        }
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
        if ($lastExitVariable) {
            $global:LASTEXITCODE = $previousLastExitCode
        } else {
            Remove-Variable -Name LASTEXITCODE -Scope Global -ErrorAction SilentlyContinue
        }
    }

    [pscustomobject]@{
        ExitCode = [int]$exitCode
        Output = @($output | ForEach-Object { [string]$_ })
    }
}

Export-ModuleMember -Function Resolve-AiOsPackageBinary, Invoke-AiOsNativeCommand
