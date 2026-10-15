[CmdletBinding()]
param(
    [string]$ModDirectory = 'C:\ShockwaveModBig',
    [string]$GameDirectory
)

# Checks that this computer is ready for a ShockWave + shared-control match.
# It only reads files and settings. It changes nothing.
# Every player must pass the FAIL checks, or the match ends in a mismatch.

$ErrorActionPreference = 'Stop'
$failures = 0
$warnings = 0

function Write-Check([string]$Level, [string]$Message) {
    $color = @{ OK = 'Green'; WARN = 'Yellow'; FAIL = 'Red'; INFO = 'Gray' }[$Level]
    Write-Host ("[{0,-4}] {1}" -f $Level, $Message) -ForegroundColor $color
    if ($Level -eq 'FAIL') { $script:failures++ }
    if ($Level -eq 'WARN') { $script:warnings++ }
}

# ShockWave 1.201 "GenLauncher Fix 1". All eleven files must match exactly.
$modFiles = [ordered]@{
    '!0Shwpatch.big'     = 'F633324E257FA5CD60A44BC200DDFC3F04C66E05ACB8EA62FD19486A98E9E034'
    '!Shw_Challenge.big' = '26700BDAE61BE8954EEAF7AF1D6AA542EEDF8AD14D4F2711967E479BE11F4DD0'
    '!Shw_ini.big'       = '46DAB5FE59A8713F1B3E73B544D883432442A585A10062473C24141DE64D96E2'
    '!Shw_maps.big'      = '3183505212F61810E099963EC59C1EE1317D1640ACFEA62329CD878DD7036E58'
    '!Shw_scripts.big'   = 'D5926738A8498840F749A8EEF0F22C3286C7F06059B7AB48A95DDB2ADAAA8382'
    '!Shw_wnd.big'       = 'C287FAC27B3657ED94113E255FAC86515B7EF752C58EEB1780A04AC824364035'
    '!Shw2DArt.big'      = '994494915B28196CA3C70F3F82ECBF88834EBDA30FA5E9A00BBD409CA2B65F15'
    '!ShwAudio.big'      = '8B077BDC40C8E1446F56378077F997914C9D7E5768617E4772DE310A8CC478DE'
    '!ShwTextures.big'   = 'D8021F85D32578FA04BE2E3AF5B3A44E1EA9EBD48A58C2560E9AD4A263E21415'
    '!ShwVoice.big'      = 'DB30C03A885C0BF53315E7DA224F4B449C13A1D05C26271ED3B19C1ED7321BBD'
    '!ShwW3D.big'        = 'B652C0BD948BEEF6673B4B64932C88A5C6EB30FCCBD14B0D8DB73B7809FBBC3E'
}

# Base-game files that feed the match checksums. These must match the host.
$requiredBaseFiles = [ordered]@{
    'INIZH.big'                           = '1A6D41A7A2CB31E67AD2F868ACA9264AD069C275E0074F8A0D970A336071E9A0'
    'PatchINI.big'                        = '16028D315C8C4D279BEED15F1836A8998FF5C9A4D0D621D4A3D37213A0D9FE62'
    'PatchData.big'                       = '90952433EFE55A774ED3F8375B7700B0A16C8206A760B5CDB3D8707A0E66FC0B'
    'PatchZH.big'                         = '450276FBABD19F79DC0143F70FE755E44A99B22C552BC00C5854FC810E615722'
    'Data\Scripts\SkirmishScripts.scb'    = '8F93862B751F289B052206B87170CC840044CB66660FBF6AE30D5782C1D73776'
    'Data\Scripts\MultiplayerScripts.scb' = '86D6BD295DD56DC17C6C1289F9A530506C755B0DBC3E868448D93DD468738AB6'
}

# Other archives present on the host. A difference is reported, not failed:
# language and art packs can differ between legitimate installs.
$hostBaseArchives = @(
    '990_DecalsZH.big', 'AudioEnglishZH.big', 'AudioZH.big', 'EnglishZH.big', 'Gensec.big', 'GensecZH.big',
    'INIZH.big', 'MapsZH.big', 'Music.big', 'MusicZH.big', 'PatchData.big', 'PatchINI.big', 'PatchWindow.big',
    'PatchZH.big', 'ShadersZH.big', 'SpeechEnglishZH.big', 'SpeechZH.big', 'TerrainZH.big', 'TexturesZH.big',
    'W3DEnglishZH.big', 'W3DZH.big', 'WindowZH.big'
)

Write-Host ''
Write-Host '--- Game installation ---'
if ([string]::IsNullOrWhiteSpace($GameDirectory)) {
    foreach ($key in @(
            'HKLM:\SOFTWARE\Wow6432Node\Electronic Arts\EA Games\Command and Conquer Generals Zero Hour',
            'HKLM:\SOFTWARE\Electronic Arts\EA Games\Command and Conquer Generals Zero Hour',
            'HKCU:\SOFTWARE\Electronic Arts\EA Games\Command and Conquer Generals Zero Hour')) {
        if (Test-Path -LiteralPath $key) {
            $candidate = (Get-ItemProperty -LiteralPath $key).InstallPath
            if (-not [string]::IsNullOrWhiteSpace($candidate)) { $GameDirectory = $candidate; break }
        }
    }
}
if ([string]::IsNullOrWhiteSpace($GameDirectory)) {
    Write-Check FAIL 'Zero Hour was not found in the registry. Pass -GameDirectory "<path>".'
    exit 1
}
$GameDirectory = [IO.Path]::GetFullPath($GameDirectory).TrimEnd('\')
$nested = Join-Path $GameDirectory 'Command and Conquer Generals Zero Hour'
if (-not (Test-Path -LiteralPath (Join-Path $GameDirectory 'INIZH.big')) -and (Test-Path -LiteralPath (Join-Path $nested 'INIZH.big'))) {
    $GameDirectory = $nested
}
Write-Check INFO "Zero Hour folder: $GameDirectory"

foreach ($entry in $requiredBaseFiles.GetEnumerator()) {
    $path = Join-Path $GameDirectory $entry.Key
    if (-not (Test-Path -LiteralPath $path)) { Write-Check FAIL "$($entry.Key) is missing."; continue }
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -eq $entry.Value) { Write-Check OK $entry.Key }
    else { Write-Check FAIL "$($entry.Key) differs from the host's copy." }
}

$presentArchives = @(Get-ChildItem -LiteralPath $GameDirectory -Filter '*.big' -File | ForEach-Object { $_.Name })
foreach ($name in $presentArchives) {
    if ($hostBaseArchives -notcontains $name) { Write-Check WARN "Extra archive the host does not have: $name" }
}
foreach ($name in $hostBaseArchives) {
    if ($presentArchives -notcontains $name) { Write-Check WARN "Archive the host has but this PC does not: $name" }
}

Write-Host ''
Write-Host '--- Leftovers from mod launchers ---'
$strayMod = @(Get-ChildItem -LiteralPath $GameDirectory -Force | Where-Object { $_.Name -like '!Shw*' })
$strayGlr = @(Get-ChildItem -LiteralPath $GameDirectory -Recurse -Force -Filter '*.GLR' -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notlike '*\GLM\*' })
if ($strayMod.Count -eq 0) { Write-Check OK 'No ShockWave files inside the game folder.' }
else { Write-Check FAIL "ShockWave files are inside the game folder ($($strayMod.Count)). Close GenLauncher properly, or move them out." }
if ($strayGlr.Count -eq 0) { Write-Check OK 'No .GLR backup files (GenLauncher restored the game folder).' }
else { Write-Check WARN "$($strayGlr.Count) .GLR backup file(s) found. GenLauncher may not have restored the game folder. Start and close GenLauncher normally." }

Write-Host ''
Write-Host '--- ShockWave mod folder ---'
if ($ModDirectory -match '\s') { Write-Check FAIL "The mod folder path contains a space: $ModDirectory" }
$fullMod = [IO.Path]::GetFullPath($ModDirectory).TrimEnd('\')
if ($fullMod.StartsWith($GameDirectory, [StringComparison]::OrdinalIgnoreCase)) {
    Write-Check FAIL 'The mod folder is inside the game folder. Move it out, for example to C:\ShockwaveModBig.'
}
if (-not (Test-Path -LiteralPath $ModDirectory)) {
    Write-Check FAIL "The mod folder does not exist: $ModDirectory"
}
else {
    foreach ($entry in $modFiles.GetEnumerator()) {
        $path = Join-Path $ModDirectory $entry.Key
        if (-not (Test-Path -LiteralPath $path)) { Write-Check FAIL "$($entry.Key) is missing."; continue }
        if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -eq $entry.Value) { Write-Check OK $entry.Key }
        else { Write-Check FAIL "$($entry.Key) differs. Use ShockWave 1.201 'GenLauncher Fix 1'." }
    }
    $extra = @(Get-ChildItem -LiteralPath $ModDirectory -Filter '*.big' -File | Where-Object { -not $modFiles.Contains($_.Name) })
    foreach ($file in $extra) { Write-Check FAIL "Unexpected archive in the mod folder: $($file.Name)" }
}

Write-Host ''
Write-Host '--- Shared-control executable ---'
$exePath = Join-Path $PSScriptRoot 'generalszh.exe'
$sumsPath = Join-Path $PSScriptRoot 'SHA256SUMS.txt'
if (-not (Test-Path -LiteralPath $exePath)) {
    Write-Check FAIL 'generalszh.exe is not next to this script. Run the script from the extracted release folder.'
}
elseif (Test-Path -LiteralPath $sumsPath) {
    $expected = ((Get-Content -LiteralPath $sumsPath | Where-Object { $_ -match 'generalszh\.exe' }) -split '\s+')[0]
    $actual = (Get-FileHash -LiteralPath $exePath -Algorithm SHA256).Hash
    if ($actual -eq $expected) { Write-Check OK "generalszh.exe matches the release ($($actual.Substring(0, 12))...)" }
    else { Write-Check FAIL 'generalszh.exe does not match SHA256SUMS.txt. Extract the release again.' }
}
else {
    Write-Check INFO ("generalszh.exe SHA-256: " + (Get-FileHash -LiteralPath $exePath -Algorithm SHA256).Hash)
}

Write-Host ''
Write-Host '--- Network (Radmin VPN) ---'
$radmin = @(Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object { $_.IPAddress -like '26.*' })
if ($radmin.Count -eq 0) {
    Write-Check WARN 'No Radmin VPN address (26.x.x.x) found. Install Radmin VPN and join the shared network.'
}
else {
    $address = $radmin[0].IPAddress
    Write-Check INFO "Radmin VPN address: $address"
    $options = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Command and Conquer Generals Zero Hour Data\Options.ini'
    if (Test-Path -LiteralPath $options) {
        $configured = @(Select-String -LiteralPath $options -Pattern '^\s*IPAddress\s*=\s*(\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
        if ($configured -contains $address) { Write-Check OK 'Options.ini uses the Radmin VPN address.' }
        else { Write-Check WARN "Options.ini does not use the Radmin address. Set both IPAddress and GameSpyIPAddress to $address (see SHOCKWAVE.md, step 5)." }
    }
    else {
        Write-Check WARN 'Options.ini not found yet. Start the game once, close it, then run this check again.'
    }
}

Write-Host ''
if ($failures -gt 0) {
    Write-Host "$failures problem(s) must be fixed before playing. $warnings warning(s)." -ForegroundColor Red
    exit 1
}
Write-Host "Ready. $warnings warning(s)." -ForegroundColor Green
