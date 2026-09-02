[CmdletBinding()]
param(
    [string]$Root = "",
    [Parameter(Mandatory = $true)]
    [string]$SetupExecutable,
    [Parameter(Mandatory = $true)]
    [string]$ControlCenterExecutable
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
}
$Root = (Resolve-Path -LiteralPath $Root).Path
$SetupExecutable = (Resolve-Path -LiteralPath $SetupExecutable).Path
$ControlCenterExecutable = (Resolve-Path -LiteralPath $ControlCenterExecutable).Path

Add-Type -AssemblyName System.Drawing

function Assert-EmbeddedIconMatches {
    param(
        [string]$Name,
        [string]$Executable,
        [string]$ExpectedPng
    )

    # Windows caches associated icons by path. Probe a uniquely named copy so a
    # rebuilt binary can never inherit the icon from an older file at that path.
    $probeExecutable = Join-Path $env:TEMP ("ai-os-icon-probe-" + [guid]::NewGuid().ToString("N") + ".exe")
    Copy-Item -LiteralPath $Executable -Destination $probeExecutable -Force
    $icon = [Drawing.Icon]::ExtractAssociatedIcon($probeExecutable)
    if (-not $icon) {
        Remove-Item -LiteralPath $probeExecutable -Force -ErrorAction SilentlyContinue
        throw "$Name has no embedded Windows icon: $Executable"
    }
    try {
        $actual = $icon.ToBitmap()
        try {
            $expected = New-Object Drawing.Bitmap($ExpectedPng)
            try {
                if ($actual.Width -ne $expected.Width -or $actual.Height -ne $expected.Height) {
                    throw "$Name embedded icon is $($actual.Width)x$($actual.Height), expected $($expected.Width)x$($expected.Height)."
                }

                $different = 0
                $total = $actual.Width * $actual.Height
                for ($y = 0; $y -lt $actual.Height; $y++) {
                    for ($x = 0; $x -lt $actual.Width; $x++) {
                        $a = $actual.GetPixel($x, $y)
                        $e = $expected.GetPixel($x, $y)
                        if ($a.A -eq 0 -and $e.A -eq 0) { continue }
                        $delta = [math]::Abs([int]$a.A - [int]$e.A) +
                            [math]::Abs([int]$a.R - [int]$e.R) +
                            [math]::Abs([int]$a.G - [int]$e.G) +
                            [math]::Abs([int]$a.B - [int]$e.B)
                        if ($delta -gt 12) { $different++ }
                    }
                }
                $ratio = $different / [double]$total
                if ($ratio -gt 0.03) {
                    throw ("{0} embedded icon differs from its source PNG at {1:P1} of pixels." -f $Name, $ratio)
                }
                Write-Host ("PASS {0} embedded icon matches ({1:P2} pixel difference)" -f $Name, $ratio)
            } finally {
                $expected.Dispose()
            }
        } finally {
            $actual.Dispose()
        }
    } finally {
        $icon.Dispose()
        Remove-Item -LiteralPath $probeExecutable -Force -ErrorAction SilentlyContinue
    }
}

Assert-EmbeddedIconMatches `
    -Name "Setup" `
    -Executable $SetupExecutable `
    -ExpectedPng (Join-Path $Root "tools/ai-os-installer-app/icons/32x32.png")
Assert-EmbeddedIconMatches `
    -Name "Control Center" `
    -Executable $ControlCenterExecutable `
    -ExpectedPng (Join-Path $Root "tools/control-center-app/icons/32x32.png")
