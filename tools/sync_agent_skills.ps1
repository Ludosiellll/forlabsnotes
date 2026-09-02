[CmdletBinding(SupportsShouldProcess = $true)]
param([string]$Root = "")

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent $PSScriptRoot
}
$Root = (Resolve-Path -LiteralPath $Root).Path
$source = Join-Path $Root ".agents/skills"
$destination = Join-Path $Root ".claude/skills"

if (-not (Test-Path -LiteralPath $source)) {
    throw "Canonical skill directory is missing: $source"
}
if (-not (Test-Path -LiteralPath $destination)) {
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
}

$skills = @(Get-ChildItem -LiteralPath $source -Directory | Where-Object {
    Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md")
})
if (-not $skills.Count) { throw "No skills with SKILL.md found under $source" }

$runningOnWindows = $PSVersionTable.PSEdition -eq 'Desktop' -or $IsWindows
$pathComparison = if ($runningOnWindows) { [StringComparison]::OrdinalIgnoreCase } else { [StringComparison]::Ordinal }
$destinationRoot = [IO.Path]::GetFullPath($destination).TrimEnd('\', '/')
foreach ($skill in $skills) {
    $target = Join-Path $destination $skill.Name
    $targetFull = [IO.Path]::GetFullPath($target)
    if (-not $targetFull.StartsWith($destinationRoot + [IO.Path]::DirectorySeparatorChar, $pathComparison)) {
        throw "Unsafe Claude skill target: $targetFull"
    }
    if ($PSCmdlet.ShouldProcess($target, "Create Claude bridge to canonical .agents skill")) {
        if (Test-Path -LiteralPath $targetFull) {
            Remove-Item -LiteralPath $targetFull -Recurse -Force
        }
        New-Item -ItemType Directory -Force -Path $targetFull | Out-Null

        $canonicalSkill = Join-Path $skill.FullName "SKILL.md"
        $raw = Get-Content -LiteralPath $canonicalSkill -Raw -Encoding UTF8
        $frontmatterMatch = [regex]::Match($raw, '(?s)\A---\s*\r?\n.*?\r?\n---')
        if (-not $frontmatterMatch.Success) {
            throw "Skill '$($skill.Name)' has no valid YAML frontmatter."
        }
        $canonicalRelative = ".agents/skills/$($skill.Name)/SKILL.md"
        $bridge = @"
$($frontmatterMatch.Value)

# Canonical skill bridge

The shared implementation for this skill lives at ``$canonicalRelative``.
When this skill applies, read that canonical file completely and follow it. Resolve its relative references from ``.agents/skills/$($skill.Name)/``. Do not maintain a second copy under ``.claude/skills``.
"@
        Set-Content -LiteralPath (Join-Path $targetFull "SKILL.md") -Value $bridge -Encoding UTF8
    }
}

$mismatches = New-Object System.Collections.Generic.List[string]
foreach ($skill in $skills) {
    $bridgePath = Join-Path $destination "$($skill.Name)/SKILL.md"
    $canonicalRelative = ".agents/skills/$($skill.Name)/SKILL.md"
    if (-not (Test-Path -LiteralPath $bridgePath)) {
        $mismatches.Add("missing bridge: $($skill.Name)")
    } elseif ((Get-Content -LiteralPath $bridgePath -Raw -Encoding UTF8) -notmatch [regex]::Escape($canonicalRelative)) {
        $mismatches.Add("wrong target: $($skill.Name)")
    }
}
if ($mismatches.Count) {
    throw "Claude skill sync verification failed: $($mismatches -join '; ')"
}

Write-Host "Claude skill bridges synchronized: $($skills.Count) bridges -> .agents/skills"
exit 0
