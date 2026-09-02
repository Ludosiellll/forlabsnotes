[CmdletBinding()]
param(
    [string]$Root = "",
    [string]$OutputDirectory = "",
    [int]$StaleAfterDays = 120,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent $PSScriptRoot
}
$Root = (Resolve-Path -LiteralPath $Root).Path

if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $Root ".local"
}
if (-not (Test-Path -LiteralPath $OutputDirectory)) {
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
}
$OutputDirectory = (Resolve-Path -LiteralPath $OutputDirectory).Path

$importDirs = @(
    "01_Index",
    "10_Project",
    "20_Domain",
    "30_Tech",
    "40_Decisions",
    "50_Meetings",
    "60_Tasks",
    "70_Resources"
)
$errors = New-Object System.Collections.Generic.List[string]

function Get-RelativePath {
    param([string]$Path)

    $trimChars = [char[]]@('\', '/')
    $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd($trimChars)
    $pathFull = [System.IO.Path]::GetFullPath($Path)
    $comparison = if ([System.IO.Path]::DirectorySeparatorChar -eq '\') {
        [System.StringComparison]::OrdinalIgnoreCase
    } else {
        [System.StringComparison]::Ordinal
    }
    $prefix = $rootFull + [System.IO.Path]::DirectorySeparatorChar
    if (-not $pathFull.StartsWith($prefix, $comparison)) {
        throw "Path is outside the workspace root: $pathFull"
    }
    return $pathFull.Substring($prefix.Length).Replace('\', '/')
}

function Get-PortableLeafName {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) { return '' }
    $normalized = $Path.Replace('\', '/').TrimEnd('/')
    return ($normalized -split '/')[-1]
}

function Get-CanonicalNotes {
    $files = New-Object System.Collections.Generic.List[object]
    foreach ($dir in $importDirs) {
        $path = Join-Path $Root $dir
        if (-not (Test-Path -LiteralPath $path)) { continue }
        foreach ($file in (Get-ChildItem -LiteralPath $path -Recurse -File -Filter "*.md" -ErrorAction SilentlyContinue)) {
            if ($file.FullName -match "[\\/]_transcripts[\\/]|[\\/]_to_delete[\\/]") { continue }
            $files.Add($file)
        }
    }
    return $files.ToArray()
}

$notes = @(Get-CanonicalNotes)
$allMarkdown = @(Get-ChildItem -LiteralPath $Root -Recurse -File -Filter "*.md" -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch "[\\/]\.git[\\/]" -and
        $_.FullName -notmatch "[\\/]\.local[\\/]" -and
        $_.FullName -notmatch "[\\/]\.agents[\\/]skills[\\/]" -and
        $_.FullName -notmatch "[\\/]\.claude[\\/]skills[\\/]" -and
        $_.FullName -notmatch "[\\/]template-skills[\\/]" -and
        $_.FullName -notmatch "[\\/]_transcripts[\\/]" -and
        $_.FullName -notmatch "[\\/]_to_delete[\\/]"
    })

$existingBasenames = @{}
foreach ($file in $allMarkdown) {
    $existingBasenames[$file.Name.ToLowerInvariant()] = $true
}

$linkedNames = @{}
$stale = New-Object System.Collections.Generic.List[string]
$frontmatterMissing = New-Object System.Collections.Generic.List[string]
$today = (Get-Date).Date

foreach ($file in $notes) {
    try {
        $text = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
        foreach ($match in [regex]::Matches($text, '\[\[([^\]|#]+)')) {
            $target = $match.Groups[1].Value.Trim().Replace('/', '\')
            $leaf = Get-PortableLeafName $target
            if (-not $leaf.EndsWith('.md', [StringComparison]::OrdinalIgnoreCase)) {
                $leaf += '.md'
            }
            $linkedNames[$leaf.ToLowerInvariant()] = $true
        }

        $statusMatch = [regex]::Match($text, '(?m)^status:\s*([^\r\n]+)')
        $updatedFieldMatch = [regex]::Match($text, '(?m)^updated:\s*([^\r\n]+)')
        if (-not $statusMatch.Success -or -not $updatedFieldMatch.Success) {
            $frontmatterMissing.Add((Get-RelativePath $file.FullName))
            continue
        }

        $status = $statusMatch.Groups[1].Value.Trim().ToLowerInvariant()
        $updatedMatch = [regex]::Match($updatedFieldMatch.Groups[1].Value.Trim(), '^(\d{4}-\d{2}-\d{2})$')
        $updated = [datetime]::MinValue
        if ($updatedMatch.Success -and
            $status -eq 'active' -and
            [datetime]::TryParseExact(
                $updatedMatch.Groups[1].Value,
                'yyyy-MM-dd',
                [System.Globalization.CultureInfo]::InvariantCulture,
                [System.Globalization.DateTimeStyles]::None,
                [ref]$updated
            ) -and
            $updated.Date -lt $today.AddDays(-1 * $StaleAfterDays)) {
            $stale.Add((Get-RelativePath $file.FullName))
        }
    } catch {
        $errors.Add("Could not inspect $($file.FullName): $($_.Exception.Message)")
    }
}

$indexNames = @(
    'AI_Context.md',
    'Project_Map.md',
    'People.md',
    'Glossary.md',
    'Domain_Map.md',
    'Meeting_Log.md',
    'Decision_Log.md',
    'Task_Log.md'
)
$unlinked = @($notes |
    Where-Object {
        $indexNames -notcontains $_.Name -and
        -not $linkedNames.ContainsKey($_.Name.ToLowerInvariant())
    } |
    ForEach-Object { Get-RelativePath $_.FullName } |
    Sort-Object -Unique)

$memory = [ordered]@{
    status = 'skipped'
    library = $null
    scanned = 0
    exactDuplicates = 0
    nearDuplicates = 0
    cold = 0
    orphanSources = @()
    detail = 'Memory layer is not configured for this workspace.'
}

$configPath = Join-Path $Root 'tools/ai_os.config.json'
if (Test-Path -LiteralPath $configPath) {
    try {
        $config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $memoryTool = [string]$config.memoryToolPath
        $library = [string]$config.memoryLibrary
        if ([string]::IsNullOrWhiteSpace($memoryTool) -or
            [string]::IsNullOrWhiteSpace($library) -or
            $memoryTool -match '\{\{' -or
            $library -match '\{\{' -or
            -not (Test-Path -LiteralPath $memoryTool)) {
            $memory.detail = 'Memory config exists but is incomplete or points to a missing executable.'
        } else {
            $memory.library = $library
            $consolidate = @()
            $consolidateExit = 1
            foreach ($attempt in 1..3) {
                $consolidate = @(& $memoryTool consolidate --library $library --near-dup-threshold 0.97 --decay-days 180 2>&1)
                $consolidateExit = $LASTEXITCODE
                if ($consolidateExit -eq 0) { break }
                if ($attempt -lt 3) { Start-Sleep -Milliseconds (500 * $attempt) }
            }
            $consolidateText = $consolidate -join "`n"
            if ($consolidateExit -ne 0) {
                throw "Memory dry-run failed: $consolidateText"
            }
            if ($consolidateText -match '--apply|Re-run with --apply') {
                # The tool prints the suggested apply command. The checker itself never invokes it.
            }
            foreach ($field in @(
                @{ Pattern = 'Scanned:\s+(\d+)'; Name = 'scanned' },
                @{ Pattern = 'Exact duplicates:\s+(\d+)'; Name = 'exactDuplicates' },
                @{ Pattern = 'Near-duplicates:\s+(\d+)'; Name = 'nearDuplicates' },
                @{ Pattern = 'Cold \(old \+ unused\):\s+(\d+)'; Name = 'cold' }
            )) {
                $match = [regex]::Match($consolidateText, $field.Pattern)
                if ($match.Success) {
                    $memory[$field.Name] = [int]$match.Groups[1].Value
                }
            }

            $exportDir = Join-Path ([System.IO.Path]::GetTempPath()) ("ai-os-context-export-" + [guid]::NewGuid().ToString('N'))
            New-Item -ItemType Directory -Path $exportDir | Out-Null
            try {
                $exportOutput = @()
                $exportExit = 1
                foreach ($attempt in 1..3) {
                    $exportOutput = @(& $memoryTool export --format json --output $exportDir 2>&1)
                    $exportExit = $LASTEXITCODE
                    if ($exportExit -eq 0) { break }
                    if ($attempt -lt 3) { Start-Sleep -Milliseconds (500 * $attempt) }
                }
                if ($exportExit -ne 0) {
                    throw "Memory export failed: $($exportOutput -join ' ')"
                }
                $libraryExport = Join-Path $exportDir ($library + '.json')
                if (-not (Test-Path -LiteralPath $libraryExport)) {
                    $candidates = @(Get-ChildItem -LiteralPath $exportDir -File -Filter '*.json')
                    if ($candidates.Count -eq 1) {
                        $libraryExport = $candidates[0].FullName
                    }
                }
                if (Test-Path -LiteralPath $libraryExport) {
                    $parsedEntries = Get-Content -LiteralPath $libraryExport -Raw -Encoding UTF8 | ConvertFrom-Json
                    $entryList = New-Object System.Collections.Generic.List[object]
                    foreach ($entry in $parsedEntries) {
                        $entryList.Add($entry)
                    }
                    $entries = $entryList.ToArray()
                    $orphanSources = @($entries |
                        ForEach-Object { [string]$_.source } |
                        Where-Object {
                            -not [string]::IsNullOrWhiteSpace($_) -and
                            -not $existingBasenames.ContainsKey((Get-PortableLeafName $_).ToLowerInvariant())
                        } |
                        ForEach-Object { Get-PortableLeafName $_ } |
                        Sort-Object -Unique)
                    $memory.orphanSources = @($orphanSources)
                }
            } finally {
                if (Test-Path -LiteralPath $exportDir) {
                    Remove-Item -LiteralPath $exportDir -Recurse -Force
                }
            }

            $memory.status = 'checked'
            $memory.detail = 'Dry-run only; no memory entries were changed.'
        }
    } catch {
        $memory.status = 'error'
        $memory.detail = $_.Exception.Message
        $errors.Add($_.Exception.Message)
    }
}

$claudeAutoMemory = [ordered]@{
    status = 'not-configured'
    detail = 'No project Claude settings file was found.'
}
$claudeSettingsPath = Join-Path $Root '.claude/settings.json'
if (Test-Path -LiteralPath $claudeSettingsPath) {
    try {
        $settings = Get-Content -LiteralPath $claudeSettingsPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $property = $settings.PSObject.Properties['autoMemoryEnabled']
        if ($property -and $property.Value -eq $false) {
            $claudeAutoMemory.status = 'disabled'
            $claudeAutoMemory.detail = 'Claude auto-memory is disabled; canonical workspace notes remain the only truth store.'
        } else {
            $claudeAutoMemory.status = 'enabled-or-default'
            $claudeAutoMemory.detail = 'Claude auto-memory can create a second project memory. Review or disable it for a single-source-of-truth workspace.'
        }
    } catch {
        $claudeAutoMemory.status = 'error'
        $claudeAutoMemory.detail = $_.Exception.Message
        $errors.Add("Could not parse .claude/settings.json: $($_.Exception.Message)")
    }
}

$report = [ordered]@{
    schemaVersion = 1
    generatedAt = (Get-Date).ToString('o')
    root = $Root
    mode = 'report-only'
    notes = [ordered]@{
        scanned = $notes.Count
        unlinked = @($unlinked)
        staleActive = @($stale.ToArray() | Sort-Object -Unique)
        missingFrontmatter = @($frontmatterMissing.ToArray() | Sort-Object -Unique)
    }
    memory = $memory
    claudeAutoMemory = $claudeAutoMemory
    errors = $errors.ToArray()
}

$jsonPath = Join-Path $OutputDirectory 'context-hygiene.json'
$markdownPath = Join-Path $OutputDirectory 'context-hygiene.md'
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$memoryWarnings = [int]$memory.exactDuplicates + [int]$memory.nearDuplicates + @($memory.orphanSources).Count
$status = if ($errors.Count) { 'ERROR' } elseif ($memoryWarnings -or $unlinked.Count -or $stale.Count -or $claudeAutoMemory.status -eq 'enabled-or-default') { 'REVIEW' } else { 'CLEAN' }
$markdown = @(
    '# Context Hygiene Report',
    '',
    "- Status: **$status**",
    "- Generated: $($report.generatedAt)",
    '- Mode: report-only; no notes or memory entries were changed.',
    "- Notes scanned: $($notes.Count)",
    "- Unlinked notes: $($unlinked.Count)",
    "- Stale active notes: $($stale.Count)",
    "- Notes missing frontmatter fields: $($frontmatterMissing.Count)",
    "- Memory duplicates: exact=$($memory.exactDuplicates), near=$($memory.nearDuplicates), cold=$($memory.cold)",
    "- Orphan memory sources: $(@($memory.orphanSources).Count)",
    "- Claude auto-memory: $($claudeAutoMemory.status)",
    '',
    '## Review',
    ''
)
if ($unlinked.Count) { $markdown += @($unlinked | Select-Object -First 30 | ForEach-Object { "- Unlinked: ``$_``" }) }
if ($stale.Count) { $markdown += @($stale | Select-Object -First 30 | ForEach-Object { "- Stale active: ``$_``" }) }
if (@($memory.orphanSources).Count) { $markdown += @($memory.orphanSources | Select-Object -First 30 | ForEach-Object { "- Orphan memory source: ``$_``" }) }
if (-not $unlinked.Count -and -not $stale.Count -and -not @($memory.orphanSources).Count) { $markdown += '- Nothing requires review.' }
$markdown | Set-Content -LiteralPath $markdownPath -Encoding UTF8

if (-not $Quiet) {
    Write-Host "Context hygiene: $status"
    Write-Host "Notes=$($notes.Count) Unlinked=$($unlinked.Count) Stale=$($stale.Count) MissingFrontmatter=$($frontmatterMissing.Count)"
    Write-Host "Memory=$($memory.status) Exact=$($memory.exactDuplicates) Near=$($memory.nearDuplicates) Cold=$($memory.cold) Orphans=$(@($memory.orphanSources).Count)"
    Write-Host "ClaudeAutoMemory=$($claudeAutoMemory.status)"
    Write-Host "Reports: $jsonPath ; $markdownPath"
}

if ($errors.Count) { exit 1 }
exit 0
