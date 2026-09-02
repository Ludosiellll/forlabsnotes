[CmdletBinding()]
param(
    [string]$Root = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}
$Root = (Resolve-Path -LiteralPath $Root).Path

function Get-PngInfo {
    param([string]$Path)

    $bytes = [IO.File]::ReadAllBytes($Path)
    $signature = @(137, 80, 78, 71, 13, 10, 26, 10)
    if ($bytes.Length -lt 26) { throw "PNG is truncated: $Path" }
    for ($index = 0; $index -lt $signature.Count; $index++) {
        if ($bytes[$index] -ne $signature[$index]) { throw "PNG signature is invalid: $Path" }
    }
    $width = ($bytes[16] -shl 24) -bor ($bytes[17] -shl 16) -bor ($bytes[18] -shl 8) -bor $bytes[19]
    $height = ($bytes[20] -shl 24) -bor ($bytes[21] -shl 16) -bor ($bytes[22] -shl 8) -bor $bytes[23]
    [pscustomobject]@{ Width = $width; Height = $height; ColorType = [int]$bytes[25] }
}

function Assert-Ico {
    param([string]$Path)

    $bytes = [IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 6 -or $bytes[0] -ne 0 -or $bytes[1] -ne 0 -or $bytes[2] -ne 1 -or $bytes[3] -ne 0) {
        throw "ICO header is invalid: $Path"
    }
    $imageCount = $bytes[4] -bor ($bytes[5] -shl 8)
    if ($imageCount -lt 4) { throw "ICO must contain at least four resolutions: $Path" }
}

$products = @(
    @{ Name = "setup"; Dir = "tools/ai-os-installer-app/icons"; TemplateDir = "distribution/workspace-template/tools/ai-os-installer-app/icons" },
    @{ Name = "control-center"; Dir = "tools/control-center-app/icons"; TemplateDir = "distribution/workspace-template/tools/control-center-app/icons" }
)
$hasNestedTemplate = Test-Path -LiteralPath (Join-Path $Root "distribution/workspace-template")

foreach ($product in $products) {
    foreach ($file in @("32x32.png", "128x128.png", "icon.ico")) {
        $live = Join-Path $Root (Join-Path $product.Dir $file)
        if (-not (Test-Path -LiteralPath $live)) {
            throw "$($product.Name) icon is missing: $file"
        }
        if ($hasNestedTemplate) {
            $template = Join-Path $Root (Join-Path $product.TemplateDir $file)
            if (-not (Test-Path -LiteralPath $template)) {
                throw "$($product.Name) template icon is missing: $file"
            }
            if ((Get-FileHash -LiteralPath $live -Algorithm SHA256).Hash -ne
                (Get-FileHash -LiteralPath $template -Algorithm SHA256).Hash) {
                throw "$($product.Name) icon drift: $file"
            }
        }
    }

    $small = Get-PngInfo (Join-Path $Root (Join-Path $product.Dir "32x32.png"))
    $large = Get-PngInfo (Join-Path $Root (Join-Path $product.Dir "128x128.png"))
    if ($small.Width -ne 32 -or $small.Height -ne 32 -or $small.ColorType -notin @(4, 6)) {
        throw "$($product.Name) 32px icon must be RGBA and exactly 32x32."
    }
    if ($large.Width -ne 128 -or $large.Height -ne 128 -or $large.ColorType -notin @(4, 6)) {
        throw "$($product.Name) 128px icon must be RGBA and exactly 128x128."
    }
    Assert-Ico (Join-Path $Root (Join-Path $product.Dir "icon.ico"))
}

$setupHash = (Get-FileHash -LiteralPath (Join-Path $Root "tools/ai-os-installer-app/icons/128x128.png") -Algorithm SHA256).Hash
$controlHash = (Get-FileHash -LiteralPath (Join-Path $Root "tools/control-center-app/icons/128x128.png") -Algorithm SHA256).Hash
if ($setupHash -eq $controlHash) { throw "Setup and Control Center must use distinct product marks." }

$mirrorDetail = if ($hasNestedTemplate) { " and mirrored" } else { "" }
Write-Host "PASS Setup and Control Center icons are distinct, transparent-capable, multi-resolution$mirrorDetail"
