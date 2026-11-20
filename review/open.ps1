[CmdletBinding()]
param([switch]$SmokeTest, [string]$Distro = 'Ubuntu-24.04')

$ErrorActionPreference = 'Stop'
Push-Location -LiteralPath $PSScriptRoot
try {
    $gds = Join-Path $PSScriptRoot 'inputs/tt_um_eleva_ccro_adc.gds'
    $expected = '3d8a8502549ad4229debe27ae7c428059759af6e9657fcf2ff3c616e27a74d25'
    if ((Get-FileHash -LiteralPath $gds -Algorithm SHA256).Hash -ne $expected) {
        throw 'GDS hash mismatch.'
    }
    if ($SmokeTest) {
        & wsl.exe -d $Distro -- bash ./open.sh --smoke
    } else {
        & wsl.exe -d $Distro -- sha256sum --quiet -c logs/review_files.sha256
        if ($LASTEXITCODE -ne 0) { throw 'Evidence hash mismatch.' }
        Invoke-Item -LiteralPath (Join-Path $PSScriptRoot 'index.html')
        & wsl.exe -d $Distro -- bash ./open.sh
    }
    if ($LASTEXITCODE -ne 0) { throw "EDA launcher returned $LASTEXITCODE." }
} finally {
    Pop-Location
}

