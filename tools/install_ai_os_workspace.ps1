[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)]
    [string]$DestinationRoot,
    [string]$SourceRoot = "",
    [string]$ProjectName = "",
    [string]$UserName = "",
    [string]$ClientName = "n/a",
    [string]$CompanyName = "n/a",
    [string]$CodeRepoPath = "none yet",
    [string]$MemoryLibraryName = "",
    [string]$ProjectSummary = "",
    [string]$MemoryToolSource = "",
    [string]$MemoryToolSha256 = "",
    [string]$MemoryToolVersion = "",
    [string]$MemoryToolDownloadUrl = "",
    [string]$MemoryToolArchiveName = "",
    [string]$MemoryToolArchiveSha256 = "",
    [long]$MemoryToolArchiveSizeBytes = 0,
    [long]$MemoryToolBinarySizeBytes = 0,
    [string]$MemoryQdrantSource = "",
    [string]$MemoryQdrantSha256 = "",
    [string]$MemoryQdrantVersion = "",
    [string]$MemoryQdrantDownloadUrl = "",
    [string]$MemoryQdrantArchiveName = "",
    [string]$MemoryQdrantArchiveSha256 = "",
    [long]$MemoryQdrantArchiveSizeBytes = 0,
    [long]$MemoryQdrantBinarySizeBytes = 0,
    [string]$MemoryOnnxSource = "",
    [string]$MemoryOnnxSha256 = "",
    [string]$MemoryOnnxVersion = "",
    [string]$MemoryOnnxDownloadUrl = "",
    [string]$MemoryOnnxArchiveName = "",
    [string]$MemoryOnnxArchiveSha256 = "",
    [long]$MemoryOnnxArchiveSizeBytes = 0,
    [long]$MemoryOnnxBinarySizeBytes = 0,
    [string]$CodeIntelToolSource = "",
    [string]$CodeIntelToolSha256 = "",
    [string]$CodeIntelToolVersion = "",
    [string]$CodeIntelToolDownloadUrl = "",
    [string]$CodeIntelToolArchiveName = "",
    [string]$CodeIntelToolArchiveSha256 = "",
    [long]$CodeIntelToolArchiveSizeBytes = 0,
    [long]$CodeIntelToolBinarySizeBytes = 0,
    [string]$PowerShellRuntimeSource = "",
    [string]$SetupExecutablePath = "",
    [switch]$SkipMemory,
    [switch]$SkipCodeIntelligence,
    [switch]$SkipScheduledTasks,
    [switch]$SharedSupervisor,
    [switch]$SkipGit,
    [switch]$Repair,
    [switch]$RemoveAutomation
)

$ErrorActionPreference = "Stop"
$runningOnWindows = $PSVersionTable.PSEdition -eq 'Desktop' -or $IsWindows
$pathComparison = if ($runningOnWindows) { [StringComparison]::OrdinalIgnoreCase } else { [StringComparison]::Ordinal }
$script:PowerShellExecutable = (Get-Process -Id $PID).Path

if ($SkipScheduledTasks -and $SharedSupervisor) {
    throw "SkipScheduledTasks and SharedSupervisor cannot be used together."
}
$packageModule = Join-Path $PSScriptRoot 'ai_os_package_cache.psm1'
if (-not $RemoveAutomation) {
    if (-not (Test-Path -LiteralPath $packageModule -PathType Leaf)) {
        throw "The AI OS package cache module is missing: $packageModule"
    }
    Import-Module $packageModule -Force
}
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$warnings = New-Object System.Collections.Generic.List[string]
$components = [ordered]@{}

function Write-Step {
    param([string]$Message)
    Write-Host "[AI OS Setup] $Message"
    if ($script:installLog) {
        Add-Content -LiteralPath $script:installLog -Encoding UTF8 -Value ("[{0}] {1}" -f (Get-Date).ToString("s"), $Message)
    }
}

function Invoke-LoggedNativeCommand {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$Arguments = @(),
        [Parameter(Mandatory = $true)][string]$FailureLabel
    )

    $result = Invoke-AiOsNativeCommand -FilePath $FilePath -Arguments $Arguments
    $result.Output | ForEach-Object { Write-Step ([string]$_) }
    if ($result.ExitCode -ne 0) {
        throw "$FailureLabel failed with exit code $($result.ExitCode)"
    }
    return $result
}

function Ensure-MemoryLibrary {
    param(
        [Parameter(Mandatory = $true)][string]$MemoryExecutable,
        [Parameter(Mandatory = $true)][string]$LibraryName
    )

    $libraryPattern = '^\s*-\s+' + [regex]::Escape($LibraryName) + '\s*$'
    $listResult = Invoke-LoggedNativeCommand -FilePath $MemoryExecutable -Arguments @('list') -FailureLabel 'mgimind list'
    if (@($listResult.Output | Where-Object { [string]$_ -match $libraryPattern }).Count -gt 0) {
        Write-Step "Memory library '$LibraryName' already exists"
        return
    }

    Write-Step "Creating the isolated memory library '$LibraryName'"
    $createResult = Invoke-AiOsNativeCommand -FilePath $MemoryExecutable -Arguments @('create', $LibraryName)
    $createResult.Output | ForEach-Object { Write-Step ([string]$_) }
    if ($createResult.ExitCode -ne 0) {
        $retryList = Invoke-AiOsNativeCommand -FilePath $MemoryExecutable -Arguments @('list')
        if ($retryList.ExitCode -ne 0 -or @($retryList.Output | Where-Object { [string]$_ -match $libraryPattern }).Count -eq 0) {
            throw "mgimind create failed with exit code $($createResult.ExitCode)"
        }
    }

    $verifyResult = Invoke-LoggedNativeCommand -FilePath $MemoryExecutable -Arguments @('list') -FailureLabel 'mgimind list after create'
    if (@($verifyResult.Output | Where-Object { [string]$_ -match $libraryPattern }).Count -eq 0) {
        throw "Memory library '$LibraryName' was not visible after creation."
    }
}

function Add-InstallWarning {
    param([string]$Message)
    $script:warnings.Add($Message)
    Write-Warning $Message
    if ($script:installLog) {
        Add-Content -LiteralPath $script:installLog -Encoding UTF8 -Value ("[{0}] WARNING: {1}" -f (Get-Date).ToString("s"), $Message)
    }
}

function Resolve-FullPath {
    param([string]$Path, [switch]$AllowMissing)

    if ([string]::IsNullOrWhiteSpace($Path)) { return "" }
    if ($AllowMissing) {
        return [System.IO.Path]::GetFullPath($Path).TrimEnd('\')
    }
    return (Resolve-Path -LiteralPath $Path).Path.TrimEnd('\')
}

function Get-AiOsDataRoot {
    if ($runningOnWindows) {
        return (Join-Path $env:LOCALAPPDATA 'AI OS')
    }
    if (-not [string]::IsNullOrWhiteSpace($env:XDG_DATA_HOME)) {
        return (Join-Path $env:XDG_DATA_HOME 'ai-os')
    }
    return (Join-Path $HOME '.local/share/ai-os')
}

function Copy-DirectoryContents {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination,
        [string[]]$ExcludedDirectories = @(),
        [string[]]$ExcludedFiles = @()
    )

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    $sourceFull = [IO.Path]::GetFullPath($Source).TrimEnd('\', '/')
    foreach ($item in @(Get-ChildItem -LiteralPath $sourceFull -Force -Recurse -ErrorAction Stop)) {
        $relative = [IO.Path]::GetRelativePath($sourceFull, $item.FullName)
        $parts = $relative -split '[\\/]'
        if (@($parts | Where-Object { $ExcludedDirectories -contains $_ }).Count) { continue }
        if (-not $item.PSIsContainer -and $ExcludedFiles -contains $item.Name) { continue }
        $target = Join-Path $Destination $relative
        if ($item.PSIsContainer) {
            New-Item -ItemType Directory -Force -Path $target | Out-Null
        } else {
            $parent = Split-Path -Parent $target
            if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
            Copy-Item -LiteralPath $item.FullName -Destination $target -Force
        }
    }
}

function Stop-WorkspaceControlCenter {
    param([Parameter(Mandatory = $true)][string]$Root)

    $binaryName = if ($runningOnWindows) { 'ai-os-control-center.exe' } else { 'ai-os-control-center' }
    $target = [IO.Path]::GetFullPath((Join-Path $Root "tools/control-center-app/bin/$binaryName"))
    if ($runningOnWindows) {
        $matches = @(Get-CimInstance Win32_Process -Filter "Name='ai-os-control-center.exe'" -ErrorAction SilentlyContinue | Where-Object {
            -not [string]::IsNullOrWhiteSpace([string]$_.ExecutablePath) -and
            [string]::Equals([IO.Path]::GetFullPath([string]$_.ExecutablePath), $target, $pathComparison)
        })
        foreach ($process in $matches) {
            Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
        }
        foreach ($process in $matches) {
            Wait-Process -Id $process.ProcessId -Timeout 5 -ErrorAction SilentlyContinue
        }
        $remaining = @(Get-CimInstance Win32_Process -Filter "Name='ai-os-control-center.exe'" -ErrorAction SilentlyContinue | Where-Object {
            -not [string]::IsNullOrWhiteSpace([string]$_.ExecutablePath) -and
            [string]::Equals([IO.Path]::GetFullPath([string]$_.ExecutablePath), $target, $pathComparison)
        })
        if ($remaining.Count) {
            throw "Could not stop the existing AI OS project center before repair."
        }
        return
    }

    $instanceState = Join-Path $Root '.local/control-center-instance.json'
    if (Test-Path -LiteralPath $instanceState) {
        try {
            $knownPid = [int](Get-Content -LiteralPath $instanceState -Raw -Encoding UTF8 | ConvertFrom-Json).pid
            if ($knownPid -gt 0) {
                Stop-Process -Id $knownPid -Force -ErrorAction SilentlyContinue
                Wait-Process -Id $knownPid -Timeout 5 -ErrorAction SilentlyContinue
            }
        } catch {
            Write-Step "Could not stop the previous Linux project center cleanly: $($_.Exception.Message)"
        }
    }
}

function Update-ManagedRuntime {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    $sourceTools = Join-Path $Source 'tools'
    $destinationTools = Join-Path $Destination 'tools'
    if (-not (Test-Path -LiteralPath $sourceTools -PathType Container)) {
        throw "The installer payload does not contain the managed tools directory."
    }
    Stop-WorkspaceControlCenter -Root $Destination
    if ($runningOnWindows) {
        & robocopy.exe $sourceTools $destinationTools /E /IS /IT /R:1 /W:1 /XD 'target' 'gen' 'resources' /XF 'ai_os.config.json' /NFL /NDL /NJH /NJS /NP | Out-Null
        if ($LASTEXITCODE -gt 7) {
            throw "Managed runtime refresh failed with robocopy exit $LASTEXITCODE"
        }
    } else {
        Copy-DirectoryContents -Source $sourceTools -Destination $destinationTools -ExcludedDirectories @('target', 'gen', 'resources') -ExcludedFiles @('ai_os.config.json')
        $controlCenter = Join-Path $destinationTools 'control-center-app/bin/ai-os-control-center'
        if (Test-Path -LiteralPath $controlCenter) {
            & chmod 755 -- $controlCenter
            if ($LASTEXITCODE -ne 0) { throw "Could not mark the refreshed project center executable." }
        }
    }
}

function Install-PowerShellRuntime {
    if ($runningOnWindows) { return $script:PowerShellExecutable }
    if ([string]::IsNullOrWhiteSpace($PowerShellRuntimeSource) -or -not (Test-Path -LiteralPath (Join-Path $PowerShellRuntimeSource 'pwsh'))) {
        throw 'The verified PowerShell runtime was not included in this Linux package.'
    }
    $destination = Join-Path (Get-AiOsDataRoot) 'runtime/powershell'
    if (-not (Test-Path -LiteralPath (Join-Path $destination 'pwsh'))) {
        Copy-DirectoryContents -Source $PowerShellRuntimeSource -Destination $destination
    }
    $pwsh = Join-Path $destination 'pwsh'
    & chmod 755 -- $pwsh
    if ($LASTEXITCODE -ne 0) { throw "Could not mark PowerShell runtime executable: $pwsh" }
    return $pwsh
}

function Test-DangerousDestination {
    param([string]$Path)

    $dangerous = @([System.IO.Path]::GetPathRoot($Path))
    if ($runningOnWindows) {
        $dangerous += @($env:USERPROFILE, [Environment]::GetFolderPath('MyDocuments'), [Environment]::GetFolderPath('Desktop'), $env:LOCALAPPDATA, $env:APPDATA, $env:ProgramFiles)
    } else {
        $dangerous += @($HOME, (Join-Path $HOME 'Documents'), (Join-Path $HOME 'Desktop'), $env:XDG_DATA_HOME, $env:XDG_CONFIG_HOME, $env:XDG_STATE_HOME)
    }
    $dangerous = $dangerous | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object {
        [System.IO.Path]::GetFullPath($_).TrimEnd('\')
    }
    return @($dangerous | Where-Object { $_.Equals($Path, $pathComparison) }).Count -gt 0
}

function Get-TemplateVersion {
    param([string]$Root)

    $changelog = Join-Path $Root 'CHANGELOG.md'
    if (-not (Test-Path -LiteralPath $changelog)) { return 'unknown' }
    $text = Get-Content -LiteralPath $changelog -Raw -Encoding UTF8
    $match = [regex]::Match($text, '(?m)^##\s+(\d+\.\d+\.\d+)\b')
    if ($match.Success) { return $match.Groups[1].Value }
    return 'unknown'
}

function Replace-WorkspaceTokens {
    param(
        [string]$Root,
        [hashtable]$Values
    )

    $textExtensions = @('.md', '.mdc', '.txt', '.json', '.ps1', '.sh', '.toml', '.yml', '.yaml', '.ini')
    $protectedPrefixes = @(
        (Join-Path $Root 'tools'),
        (Join-Path $Root 'template-skills'),
        (Join-Path $Root '.agents/skills'),
        (Join-Path $Root '.claude/skills')
    ) | ForEach-Object { [IO.Path]::GetFullPath($_).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar }
    $files = Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction Stop | Where-Object {
        $candidatePath = [IO.Path]::GetFullPath($_.FullName)
        $insideProtectedArea = @($protectedPrefixes | Where-Object { $candidatePath.StartsWith($_, $pathComparison) }).Count -gt 0
        $_.FullName -notmatch '[\\/]\.git[\\/]' -and
        $_.FullName -notmatch '[\\/]\.local[\\/]' -and
        $_.FullName -notmatch '[\\/]target[\\/]' -and
        $_.FullName -notmatch '[\\/]gen[\\/]' -and
        -not $insideProtectedArea -and
        ($textExtensions -contains $_.Extension -or $_.Name -eq '.gitignore')
    }

    foreach ($file in $files) {
        $text = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
        $changed = $false
        foreach ($token in $Values.Keys) {
            if ($text.Contains($token)) {
                $text = $text.Replace($token, [string]$Values[$token])
                $changed = $true
            }
        }
        if ($changed) {
            [System.IO.File]::WriteAllText($file.FullName, $text, $utf8NoBom)
        }
    }
}

function Set-SeedContext {
    param([string]$Root, [string]$Summary)

    $today = (Get-Date).ToString('yyyy-MM-dd')
    foreach ($relative in @(
        '01_Index/People.md',
        '01_Index/User_Working_Profile.md',
        '10_Project/Project_Brief.md',
        '10_Project/Current_Focus.md',
        '30_Tech/Tech_Map.md'
    )) {
        $path = Join-Path $Root $relative
        if (-not (Test-Path -LiteralPath $path)) { continue }
        $text = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
        $text = [regex]::Replace($text, '(?m)^updated:\s*YYYY-MM-DD\s*$', "updated: $today", 1)
        [System.IO.File]::WriteAllText($path, $text, $utf8NoBom)
    }

    $cleanSummary = ($Summary -replace '[\r\n]+', ' ').Trim()
    if (-not [string]::IsNullOrWhiteSpace($cleanSummary)) {
        $briefPath = Join-Path $Root '10_Project/Project_Brief.md'
        if (Test-Path -LiteralPath $briefPath) {
            $text = [System.IO.File]::ReadAllText($briefPath, [System.Text.Encoding]::UTF8)
            $text = [regex]::Replace(
                $text,
                '(?ms)(## Summary\s+).*?(?=\r?\n\r?\n## |\z)',
                ('$1' + $cleanSummary),
                1
            )
            [System.IO.File]::WriteAllText($briefPath, $text, $utf8NoBom)
        }

        $focusPath = Join-Path $Root '10_Project/Current_Focus.md'
        if (Test-Path -LiteralPath $focusPath) {
            $text = [System.IO.File]::ReadAllText($focusPath, [System.Text.Encoding]::UTF8)
            $text = [regex]::Replace(
                $text,
                '(?ms)(## Now\s+)- Example:[^\r\n]*(\r?\n)',
                ('$1- ' + $cleanSummary + '$2'),
                1
            )
            [System.IO.File]::WriteAllText($focusPath, $text, $utf8NoBom)
        }
    }
}

function Remove-WorkspaceAutomation {
    param([string]$Root)

    if (-not $runningOnWindows) { return @() }
    $escapedRoot = [regex]::Escape($Root)
    $removed = New-Object System.Collections.Generic.List[string]
    foreach ($task in @(Get-ScheduledTask -ErrorAction SilentlyContinue)) {
        $actionText = (($task.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments) $($_.WorkingDirectory)" }) -join ' ')
        if ($task.TaskName -like 'AI-OS*' -and $actionText -match $escapedRoot) {
            Stop-ScheduledTask -TaskName $task.TaskName -ErrorAction SilentlyContinue
            Unregister-ScheduledTask -TaskName $task.TaskName -Confirm:$false -ErrorAction Stop
            $removed.Add($task.TaskName)
        }
    }
    return $removed.ToArray()
}

$DestinationRoot = Resolve-FullPath -Path $DestinationRoot -AllowMissing
if (Test-DangerousDestination $DestinationRoot) {
    throw "Unsafe destination. Choose a dedicated project folder, not a drive or profile/system folder: $DestinationRoot"
}

if ($RemoveAutomation) {
    $removed = @(Remove-WorkspaceAutomation -Root $DestinationRoot)
    Write-Host "Removed $($removed.Count) legacy AI OS automation item(s). Workspace notes were kept."
    exit 0
}

if (-not $Repair) {
    if ([string]::IsNullOrWhiteSpace($ProjectName) -or [string]::IsNullOrWhiteSpace($UserName)) {
        throw "ProjectName and UserName are required."
    }
    if ([string]::IsNullOrWhiteSpace($MemoryLibraryName)) {
        $MemoryLibraryName = (($ProjectName.ToLowerInvariant() -replace '[^a-z0-9]+', '-') -replace '^-|-$', '')
        if ($MemoryLibraryName.Length -lt 2) {
            $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($ProjectName))
            $MemoryLibraryName = 'workspace-' + (($hashBytes | ForEach-Object { $_.ToString('x2') }) -join '').Substring(0, 8)
        }
    }
    if ($MemoryLibraryName -notmatch '^[A-Za-z0-9][A-Za-z0-9_-]{1,63}$') {
        throw "MemoryLibraryName must contain only letters, numbers, underscore or dash (2-64 characters)."
    }
    if ([string]::IsNullOrWhiteSpace($SourceRoot)) {
        throw "SourceRoot is required for a fresh install."
    }
    $SourceRoot = Resolve-FullPath -Path $SourceRoot
    if ($SourceRoot.Equals($DestinationRoot, $pathComparison)) {
        throw "SourceRoot and DestinationRoot must be different for a fresh install."
    }
    $sourcePrefix = $SourceRoot.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    if ($DestinationRoot.StartsWith($sourcePrefix, $pathComparison)) {
        throw "DestinationRoot cannot be inside the clean source template."
    }
    foreach ($required in @('AGENTS.md', 'TEMPLATE_SETUP.md', 'CHANGELOG.md', 'tools/check_ai_os_readiness.ps1', 'tools/sync_agent_skills.ps1')) {
        if (-not (Test-Path -LiteralPath (Join-Path $SourceRoot $required))) {
            throw "Source template is incomplete; missing $required"
        }
    }
    if (Test-Path -LiteralPath $DestinationRoot) {
        $existing = @(Get-ChildItem -LiteralPath $DestinationRoot -Force -ErrorAction Stop)
        if ($existing.Count) {
            throw "Destination is not empty. Choose a new folder or use -Repair for an installed AI OS workspace."
        }
    } else {
        New-Item -ItemType Directory -Force -Path $DestinationRoot | Out-Null
    }

    Write-Step "Copying the clean workspace template"
    if ($runningOnWindows) {
        & robocopy.exe $SourceRoot $DestinationRoot /E /R:1 /W:1 /XD '.git' '.local' 'target' 'gen' 'resources' /XF 'ai_os.config.json' '.mcp.json' /NFL /NDL /NJH /NJS /NP | Out-Null
        if ($LASTEXITCODE -gt 7) {
            throw "Template copy failed with robocopy exit $LASTEXITCODE"
        }
    } else {
        Copy-DirectoryContents -Source $SourceRoot -Destination $DestinationRoot `
            -ExcludedDirectories @('.git', '.local', 'target', 'gen', 'resources') `
            -ExcludedFiles @('ai_os.config.json', '.mcp.json')
    }
} else {
    if (-not (Test-Path -LiteralPath (Join-Path $DestinationRoot 'AGENTS.md')) -or
        -not (Test-Path -LiteralPath (Join-Path $DestinationRoot '.local/install-state.json'))) {
        throw "Repair is allowed only for a workspace previously created by AI OS Setup."
    }
    $existingState = Get-Content -LiteralPath (Join-Path $DestinationRoot '.local/install-state.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace($ProjectName)) { $ProjectName = [string]$existingState.projectName }
    if ([string]::IsNullOrWhiteSpace($MemoryLibraryName)) {
        $configPath = Join-Path $DestinationRoot 'tools/ai_os.config.json'
        if (Test-Path -LiteralPath $configPath) {
            $MemoryLibraryName = [string](Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json).memoryLibrary
        }
    }
    if ([string]::IsNullOrWhiteSpace($MemoryLibraryName)) {
        $MemoryLibraryName = (($ProjectName.ToLowerInvariant() -replace '[^a-z0-9]+', '-') -replace '^-|-$', '')
        if ($MemoryLibraryName.Length -lt 2) {
            $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($ProjectName))
            $MemoryLibraryName = 'workspace-' + (($hashBytes | ForEach-Object { $_.ToString('x2') }) -join '').Substring(0, 8)
        }
    }
    Write-Step "Repair mode: user notes will not be copied or replaced"
}

$localDir = Join-Path $DestinationRoot '.local'
New-Item -ItemType Directory -Force -Path $localDir | Out-Null
$script:installLog = Join-Path $localDir 'install.log'
if ($Repair) {
    Write-Step 'Repair started'
    Write-Step 'Refreshing managed AI OS runtime without touching user notes'
    Update-ManagedRuntime -Source $SourceRoot -Destination $DestinationRoot
} else {
    Write-Step 'Fresh install started'
}

$script:PowerShellExecutable = Install-PowerShellRuntime

if (-not $Repair) {
    if ($runningOnWindows) {
        Get-ChildItem -LiteralPath $DestinationRoot -Recurse -File -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue
    }
    $tokenValues = @{
        '{{PROJECT_NAME}}' = $ProjectName
        '{{USER_NAME}}' = $UserName
        '{{CLIENT_NAME}}' = $ClientName
        '{{COMPANY_NAME}}' = $CompanyName
        '{{CODE_REPO_PATH}}' = $CodeRepoPath
        '{{MEMORY_LIBRARY_NAME}}' = $MemoryLibraryName
        '{{PROJECT_ROOT}}' = $DestinationRoot
    }
    Replace-WorkspaceTokens -Root $DestinationRoot -Values $tokenValues
    Set-SeedContext -Root $DestinationRoot -Summary $ProjectSummary
    $components['workspace'] = 'installed'
} else {
    $components['workspace'] = 'preserved'
}

Write-Step "Activating bundled skills"
$skillSource = Join-Path $DestinationRoot 'template-skills'
$skillDestination = Join-Path $DestinationRoot '.agents/skills'
if (Test-Path -LiteralPath $skillSource) {
    New-Item -ItemType Directory -Force -Path $skillDestination | Out-Null
    foreach ($skill in @(Get-ChildItem -LiteralPath $skillSource -Directory)) {
        Copy-Item -LiteralPath $skill.FullName -Destination (Join-Path $skillDestination $skill.Name) -Recurse -Force
    }
    $syncSkills = Join-Path $DestinationRoot 'tools/sync_agent_skills.ps1'
    & $script:PowerShellExecutable -NoProfile -File $syncSkills -Root $DestinationRoot
    if ($LASTEXITCODE -ne 0) { throw "Skill activation failed." }
    $components['skills'] = 'installed'
} else {
    Add-InstallWarning "template-skills folder is missing; workspace rules work, but bundled skills were not installed."
    $components['skills'] = 'missing'
}

$memoryReady = $false
$memoryPath = $null
if ($SkipMemory) {
    $components['memory'] = 'skipped-by-user'
} else {
    try {
        if ([string]::IsNullOrWhiteSpace($MemoryToolSource) -and -not [string]::IsNullOrWhiteSpace($SourceRoot)) {
            $memoryName = if ($runningOnWindows) { 'mgimind.exe' } else { 'mgimind' }
            $candidate = Join-Path (Split-Path -Parent $SourceRoot) "memory-tool/$memoryName"
            if (Test-Path -LiteralPath $candidate) { $MemoryToolSource = $candidate }
        }
        $memoryName = if ($runningOnWindows) { 'mgimind.exe' } else { 'mgimind' }
        $memoryVersion = if ([string]::IsNullOrWhiteSpace($MemoryToolVersion)) { 'bundled' } else { $MemoryToolVersion }
        $memoryPath = Resolve-AiOsPackageBinary `
            -Name 'mgi-mind' `
            -Version $memoryVersion `
            -BinaryName $memoryName `
            -ExpectedBinarySha256 $MemoryToolSha256 `
            -CacheRoot (Get-AiOsDataRoot) `
            -DestinationDirectory (Join-Path (Get-AiOsDataRoot) 'bin') `
            -BundledBinary $MemoryToolSource `
            -DownloadUrl $MemoryToolDownloadUrl `
            -ArchiveName $MemoryToolArchiveName `
            -ExpectedArchiveSha256 $MemoryToolArchiveSha256 `
            -ArchiveSizeBytes $MemoryToolArchiveSizeBytes `
            -BinarySizeBytes $MemoryToolBinarySizeBytes
        if (-not $memoryPath) {
            throw "The verified memory executable was not included in this installer."
        }
        if ($runningOnWindows) {
            $memoryBin = Join-Path (Get-AiOsDataRoot) 'bin'
            Resolve-AiOsPackageBinary `
                -Name 'qdrant' `
                -Version $MemoryQdrantVersion `
                -BinaryName 'qdrant.exe' `
                -ExpectedBinarySha256 $MemoryQdrantSha256 `
                -CacheRoot (Get-AiOsDataRoot) `
                -DestinationDirectory $memoryBin `
                -BundledBinary $MemoryQdrantSource `
                -DownloadUrl $MemoryQdrantDownloadUrl `
                -ArchiveName $MemoryQdrantArchiveName `
                -ExpectedArchiveSha256 $MemoryQdrantArchiveSha256 `
                -ArchiveSizeBytes $MemoryQdrantArchiveSizeBytes `
                -BinarySizeBytes $MemoryQdrantBinarySizeBytes | Out-Null
            Resolve-AiOsPackageBinary `
                -Name 'onnxruntime' `
                -Version $MemoryOnnxVersion `
                -BinaryName 'onnxruntime.dll' `
                -ExpectedBinarySha256 $MemoryOnnxSha256 `
                -CacheRoot (Get-AiOsDataRoot) `
                -DestinationDirectory $memoryBin `
                -BundledBinary $MemoryOnnxSource `
                -DownloadUrl $MemoryOnnxDownloadUrl `
                -ArchiveName $MemoryOnnxArchiveName `
                -ExpectedArchiveSha256 $MemoryOnnxArchiveSha256 `
                -ArchiveSizeBytes $MemoryOnnxArchiveSizeBytes `
                -BinarySizeBytes $MemoryOnnxBinarySizeBytes | Out-Null
        }
        Write-Step "Preparing local semantic memory (the first run can download model files)"
        Invoke-LoggedNativeCommand -FilePath $memoryPath -Arguments @('init') -FailureLabel 'mgimind init'
        Invoke-LoggedNativeCommand -FilePath $memoryPath -Arguments @('doctor', '--fix') -FailureLabel 'mgimind doctor --fix'
        Invoke-LoggedNativeCommand -FilePath $memoryPath -Arguments @('doctor') -FailureLabel 'mgimind doctor'

        [ordered]@{
            memoryToolPath = $memoryPath
            memoryLibrary = $MemoryLibraryName
            powershellPath = $script:PowerShellExecutable
        } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $DestinationRoot 'tools/ai_os.config.json') -Encoding UTF8
        $startMemory = Join-Path $DestinationRoot 'tools/start_mgimind.ps1'
        & $script:PowerShellExecutable -NoProfile -File $startMemory -Root $DestinationRoot
        if ($LASTEXITCODE -ne 0) { throw "local memory service failed to start" }
        Ensure-MemoryLibrary -MemoryExecutable $memoryPath -LibraryName $MemoryLibraryName
        $syncMemory = Join-Path $DestinationRoot 'tools/sync_mgimind.ps1'
        & $script:PowerShellExecutable -NoProfile -File $syncMemory -Root $DestinationRoot
        if ($LASTEXITCODE -ne 0) { throw "initial memory import failed" }
        $memoryReady = $true
        $components['memory'] = 'installed'
    } catch {
        Add-InstallWarning "Memory setup is pending: $($_.Exception.Message)"
        $components['memory'] = 'pending'
    }
}

$workspaceConfigPath = Join-Path $DestinationRoot 'tools/ai_os.config.json'
if (Test-Path -LiteralPath $workspaceConfigPath) {
    $workspaceConfig = Get-Content -LiteralPath $workspaceConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $workspaceConfig | Add-Member -NotePropertyName powershellPath -NotePropertyValue $script:PowerShellExecutable -Force
} else {
    $workspaceConfig = [ordered]@{
        memoryToolPath = ''
        memoryLibrary = $MemoryLibraryName
        powershellPath = $script:PowerShellExecutable
    }
}
if ($workspaceConfig -is [System.Collections.IDictionary]) {
    $workspaceConfig['setupExecutablePath'] = $SetupExecutablePath
} else {
    $workspaceConfig | Add-Member -NotePropertyName setupExecutablePath -NotePropertyValue $SetupExecutablePath -Force
}
$workspaceConfig | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $workspaceConfigPath -Encoding UTF8

$codeIntelReady = $false
$codeIntelPath = $null
if ($SkipCodeIntelligence) {
    $components['codeIntelligence'] = 'skipped-by-user'
} else {
    try {
        $codeIntelName = if ($runningOnWindows) { 'codebase-memory-mcp.exe' } else { 'codebase-memory-mcp' }
        $codeIntelVersion = if ([string]::IsNullOrWhiteSpace($CodeIntelToolVersion)) { 'bundled' } else { $CodeIntelToolVersion }
        $codeIntelPath = Resolve-AiOsPackageBinary `
            -Name 'codebase-memory-mcp' `
            -Version $codeIntelVersion `
            -BinaryName $codeIntelName `
            -ExpectedBinarySha256 $CodeIntelToolSha256 `
            -CacheRoot (Get-AiOsDataRoot) `
            -DestinationDirectory (Join-Path (Get-AiOsDataRoot) 'bin') `
            -BundledBinary $CodeIntelToolSource `
            -DownloadUrl $CodeIntelToolDownloadUrl `
            -ArchiveName $CodeIntelToolArchiveName `
            -ExpectedArchiveSha256 $CodeIntelToolArchiveSha256 `
            -ArchiveSizeBytes $CodeIntelToolArchiveSizeBytes `
            -BinarySizeBytes $CodeIntelToolBinarySizeBytes
        if (-not $codeIntelPath) {
            throw "The verified code-intelligence executable was not included in this installer."
        }
        Invoke-LoggedNativeCommand -FilePath $codeIntelPath -Arguments @('config', 'set', 'auto_index', 'false') -FailureLabel 'code-intelligence configuration'
        $codeIntelReady = $true
        $components['codeIntelligence'] = 'installed-not-indexed'
    } catch {
        Add-InstallWarning "Code-intelligence setup is pending: $($_.Exception.Message)"
        $components['codeIntelligence'] = 'pending'
    }
}

if (-not $Repair -or $memoryReady -or $codeIntelReady) {
    $servers = [ordered]@{}
    if ($memoryReady) {
        $servers['memory'] = [ordered]@{ command = $memoryPath; args = @('mcp') }
    }
    if ($codeIntelReady) {
        $servers['codebase-memory'] = [ordered]@{ command = $codeIntelPath; args = @() }
    }
    [ordered]@{ mcpServers = $servers } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $DestinationRoot '.mcp.json') -Encoding UTF8
}
if (-not (Test-Path -LiteralPath (Join-Path $DestinationRoot '.mcp.json'))) {
    [ordered]@{ mcpServers = [ordered]@{} } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $DestinationRoot '.mcp.json') -Encoding UTF8
}

if ($SkipGit) {
    $components['git'] = 'skipped-by-user'
} elseif (-not $Repair) {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) {
        Add-InstallWarning "Git is not installed; the workspace has no local change history yet."
        $components['git'] = 'pending'
    } else {
        Write-Step "Creating local Git history"
        & $git.Source -C $DestinationRoot init | Out-Null
        $gitName = (& $git.Source config --global user.name 2>$null)
        $gitEmail = (& $git.Source config --global user.email 2>$null)
        if ($gitName -and $gitEmail) {
            & $git.Source -C $DestinationRoot add -A
            & $git.Source -C $DestinationRoot commit -m 'Initialize AI OS workspace' | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $components['git'] = 'initialized-and-committed'
            } else {
                Add-InstallWarning "Git was initialized, but the first commit failed."
                $components['git'] = 'initialized'
            }
        } else {
            Add-InstallWarning "Git was initialized; the first commit was skipped because user.name or user.email is not configured."
            $components['git'] = 'initialized'
        }
    }
}

if ($SharedSupervisor) {
    $components['automation'] = 'shared-supervisor'
} elseif ($SkipScheduledTasks) {
    $components['automation'] = 'skipped-by-user'
} elseif (-not $runningOnWindows) {
    Add-InstallWarning 'Linux uses the shared supervisor; enable background checks in AI OS Setup and run repair.'
    $components['automation'] = 'pending'
} else {
    try {
        $effectivePolicy = Get-ExecutionPolicy
        $currentUserPolicy = Get-ExecutionPolicy -Scope CurrentUser
        if ($effectivePolicy -eq 'Restricted' -and $currentUserPolicy -in @('Undefined', 'Restricted')) {
            Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
            Write-Step "Enabled local signed-or-local PowerShell scripts for the current Windows user"
        } elseif ($effectivePolicy -eq 'AllSigned') {
            Add-InstallWarning "PowerShell policy is AllSigned; unsigned workspace tasks may require organization approval."
        }

        $taskInstaller = Join-Path $DestinationRoot 'tools/install_ai_os_scheduled_tasks.ps1'
        $taskArgs = @('-NoProfile', '-File', $taskInstaller, '-Root', $DestinationRoot, '-ProjectName', $ProjectName, '-IncludeControlCenter')
        if ($memoryReady) { $taskArgs += '-IncludeMemory' }
        & $script:PowerShellExecutable @taskArgs
        if ($LASTEXITCODE -ne 0) { throw "scheduled-task installer returned $LASTEXITCODE" }
        $components['automation'] = 'installed'
    } catch {
        Add-InstallWarning "Background automation is pending: $($_.Exception.Message)"
        $components['automation'] = 'pending'
    }
}

$readiness = Join-Path $DestinationRoot 'tools/check_ai_os_readiness.ps1'
Write-Step "Running the final self-check"
$readinessOutput = @(& $script:PowerShellExecutable -NoProfile -File $readiness -Root $DestinationRoot 2>&1)
$readinessExit = $LASTEXITCODE
if ($readinessExit -ne 0) {
    $components['readiness'] = 'failed'
    $readinessOutput | Select-Object -First 12 | ForEach-Object { Write-Step ([string]$_) }
    throw "Installed workspace failed readiness. Read $script:installLog"
}
$components['readiness'] = 'passed'

$templateVersion = Get-TemplateVersion -Root $DestinationRoot
$installStatus = if ($warnings.Count) { 'ready-with-warnings' } else { 'ready' }
$state = [ordered]@{
    schemaVersion = 1
    status = $installStatus
    installedAt = (Get-Date).ToString('o')
    templateVersion = $templateVersion
    projectName = $ProjectName
    workspaceRoot = $DestinationRoot
    components = $components
    warnings = $warnings.ToArray()
    notes = 'No secrets or account credentials are stored in this file.'
}
$state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $localDir 'install-state.json') -Encoding UTF8

Write-Step "Setup complete: $installStatus"
Write-Host "Workspace: $DestinationRoot"
Write-Host "State: $(Join-Path $localDir 'install-state.json')"
exit 0
