[CmdletBinding()]
param(
    [string]$GameDirectory,
    # Window size. Leave both at 0 to use the resolution saved in the game's Options, as long
    # as the screen can show it. Pass both to force a size for this launch.
    [ValidateScript({ $_ -eq 0 -or ($_ -ge 640 -and $_ -le 7680) })]
    [int]$Width = 0,
    [ValidateScript({ $_ -eq 0 -or ($_ -ge 480 -and $_ -le 4320) })]
    [int]$Height = 0,
    [ValidateRange(100, 1000)]
    [int]$MaxCameraHeight = 450,
    [switch]$UseCleanDataProjection,
    [switch]$SharedControl,
    [string[]]$AdditionalArguments = @(),
    # Official Data child folders to keep out of sight, so a mod's archive copies are used.
    [string[]]$HideLooseDataFolders = @(),
    # Set up the Data layout and stop before starting the game.
    [switch]$PrepareOnly
)

$ErrorActionPreference = 'Stop'
$launchLogPath = Join-Path $PSScriptRoot 'launch-last.log'
Start-Transcript -LiteralPath $launchLogPath -Force | Out-Null

if ([string]::IsNullOrWhiteSpace($GameDirectory)) {
    $registryPaths = @(
        'HKLM:\SOFTWARE\Wow6432Node\Electronic Arts\EA Games\Command and Conquer Generals Zero Hour',
        'HKLM:\SOFTWARE\Electronic Arts\EA Games\Command and Conquer Generals Zero Hour',
        'HKCU:\SOFTWARE\Electronic Arts\EA Games\Command and Conquer Generals Zero Hour'
    )

    foreach ($registryPath in $registryPaths) {
        if (Test-Path -LiteralPath $registryPath) {
            $candidate = (Get-ItemProperty -LiteralPath $registryPath).InstallPath
            if (-not [string]::IsNullOrWhiteSpace($candidate)) {
                $GameDirectory = $candidate
                break
            }
        }
    }
}

if ([string]::IsNullOrWhiteSpace($GameDirectory)) {
    throw 'The Zero Hour installation directory was not supplied and could not be found in the registry.'
}

$GameDirectory = [System.IO.Path]::GetFullPath($GameDirectory).TrimEnd('\')
$nestedEaGameDirectory = Join-Path $GameDirectory 'Command and Conquer Generals Zero Hour'
if (-not (Test-Path -LiteralPath (Join-Path $GameDirectory 'Data\Scripts\SkirmishScripts.scb')) -and
        (Test-Path -LiteralPath (Join-Path $nestedEaGameDirectory 'Data\Scripts\SkirmishScripts.scb'))) {
    $GameDirectory = $nestedEaGameDirectory
}
$executablePath = Join-Path $PSScriptRoot 'generalszh.exe'
$officialDataDirectory = Join-Path $GameDirectory 'Data'
$dataLinkPath = Join-Path $PSScriptRoot 'Data'

$requiredPaths = @(
    $executablePath,
    (Join-Path $GameDirectory 'Generals.exe'),
    (Join-Path $officialDataDirectory 'Scripts\SkirmishScripts.scb'),
    (Join-Path $officialDataDirectory 'Cursors\sccpointer.ani')
)

foreach ($requiredPath in $requiredPaths) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Required Zero Hour test-client file was not found: $requiredPath"
    }
}

$expectedTarget = [System.IO.Path]::GetFullPath($officialDataDirectory).TrimEnd('\')
$workingDirectory = $GameDirectory
if ($UseCleanDataProjection) {
    if (-not (Test-Path -LiteralPath $dataLinkPath -PathType Container)) {
        New-Item -ItemType Directory -Path $dataLinkPath | Out-Null
    }

    $dataEntry = Get-Item -LiteralPath $dataLinkPath -Force
    if ($dataEntry.LinkType -eq 'Junction') {
        throw "Clean data projection requested, but the test-client Data path is still a junction: $dataLinkPath"
    }

    foreach ($childName in @('Cursors', 'English', 'Movies', 'Scripts', 'WaterPlane')) {
        $sourceChild = Join-Path $officialDataDirectory $childName
        $projectedChild = Join-Path $dataLinkPath $childName
        if (-not (Test-Path -LiteralPath $sourceChild -PathType Container)) {
            throw "Required official Data folder was not found: $sourceChild"
        }

        if (Test-Path -LiteralPath $projectedChild) {
            $projectedEntry = Get-Item -LiteralPath $projectedChild -Force
            $actualTarget = @($projectedEntry.Target)[0]
            if ($projectedEntry.LinkType -ne 'Junction' -or [string]::IsNullOrWhiteSpace($actualTarget)) {
                throw "Projected Data child exists but is not a junction: $projectedChild"
            }
            $actualTarget = [System.IO.Path]::GetFullPath($actualTarget).TrimEnd('\')
            $expectedChild = [System.IO.Path]::GetFullPath($sourceChild).TrimEnd('\')
            if (-not $actualTarget.Equals($expectedChild, [System.StringComparison]::OrdinalIgnoreCase)) {
                throw "Projected Data child targets '$actualTarget', not '$expectedChild'."
            }
        }
        else {
            New-Item -ItemType Junction -Path $projectedChild -Target $sourceChild | Out-Null
        }
    }

    $cleanIniDirectory = Join-Path $dataLinkPath 'INI'
    if (-not (Test-Path -LiteralPath $cleanIniDirectory)) {
        New-Item -ItemType Directory -Path $cleanIniDirectory | Out-Null
    }

    $weatherEntries = @(
        'Data\INI\Default\Weather.ini',
        'Data\INI\Weather.ini'
    )
    $weatherArchive = Join-Path $GameDirectory 'INIZH.big'
    if (-not (Test-Path -LiteralPath $weatherArchive -PathType Leaf)) {
        throw "Required Zero Hour archive was not found: $weatherArchive"
    }

    $archiveStream = [System.IO.File]::OpenRead($weatherArchive)
    $archiveReader = New-Object System.IO.BinaryReader($archiveStream)
    try {
        $archiveIdentifier = [System.Text.Encoding]::ASCII.GetString($archiveReader.ReadBytes(4))
        if ($archiveIdentifier -ne 'BIGF') {
            throw "Unexpected archive identifier in $weatherArchive"
        }

        $archiveReader.ReadBytes(4) | Out-Null
        $fileCountBytes = $archiveReader.ReadBytes(4)
        [Array]::Reverse($fileCountBytes)
        $fileCount = [BitConverter]::ToInt32($fileCountBytes, 0)
        $archiveReader.ReadBytes(4) | Out-Null

        $weatherMetadata = @{}
        for ($index = 0; $index -lt $fileCount; $index++) {
            $offsetBytes = $archiveReader.ReadBytes(4)
            [Array]::Reverse($offsetBytes)
            $offset = [BitConverter]::ToInt32($offsetBytes, 0)

            $sizeBytes = $archiveReader.ReadBytes(4)
            [Array]::Reverse($sizeBytes)
            $size = [BitConverter]::ToInt32($sizeBytes, 0)

            $nameBytes = New-Object 'System.Collections.Generic.List[byte]'
            while (($nameByte = $archiveReader.ReadByte()) -ne 0) {
                $nameBytes.Add($nameByte)
            }
            $entryName = [System.Text.Encoding]::ASCII.GetString($nameBytes.ToArray())

            if ($weatherEntries -contains $entryName) {
                $weatherMetadata[$entryName] = @{
                    Offset = $offset
                    Size = $size
                }
            }
        }

        foreach ($entryName in $weatherEntries) {
            if (-not $weatherMetadata.ContainsKey($entryName)) {
                throw "Required archive entry was not found in INIZH.big: $entryName"
            }

            $metadata = $weatherMetadata[$entryName]
            $destination = Join-Path $PSScriptRoot $entryName
            $destinationDirectory = Split-Path -Parent $destination
            if (-not (Test-Path -LiteralPath $destinationDirectory)) {
                New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null
            }

            $archiveStream.Position = $metadata.Offset
            $entryBytes = $archiveReader.ReadBytes($metadata.Size)
            if ($entryBytes.Length -ne $metadata.Size) {
                throw "Could not read the complete archive entry: $entryName"
            }
            [System.IO.File]::WriteAllBytes($destination, $entryBytes)
        }
    }
    finally {
        $archiveReader.Dispose()
        $archiveStream.Dispose()
    }

    foreach ($archive in Get-ChildItem -LiteralPath $GameDirectory -Filter '*.big' -File) {
        $projectedArchive = Join-Path $PSScriptRoot $archive.Name
        if (Test-Path -LiteralPath $projectedArchive) {
            if ((Get-Item -LiteralPath $projectedArchive).Length -ne $archive.Length) {
                throw "Projected archive has the wrong size: $projectedArchive"
            }
        }
        else {
            New-Item -ItemType HardLink -Path $projectedArchive -Target $archive.FullName | Out-Null
        }
    }

    $workingDirectory = $PSScriptRoot
}
else {
    # Two layouts for the Data path beside the executable:
    #   plain   - one junction to the official Data folder (the default);
    #   partial - a real folder holding one junction per official child folder, minus the
    #             ones named in -HideLooseDataFolders.
    # The engine opens loose files before archive files. A mod that ships its own copy of a
    # loose base-game file (ShockWave ships Data\Scripts) is ignored unless the loose copy is
    # hidden. Nothing in the official installation is changed either way.
    $hiddenFolders = @($HideLooseDataFolders | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

    function Get-JunctionTarget([string]$Path) {
        $entry = Get-Item -LiteralPath $Path -Force
        $target = @($entry.Target)[0]
        if ($entry.LinkType -ne 'Junction' -or [string]::IsNullOrWhiteSpace($target)) { return $null }
        return [System.IO.Path]::GetFullPath($target).TrimEnd('\')
    }

    # Deletes the link only. A non-recursive delete cannot remove a real folder with content.
    function Remove-Junction([string]$Path) {
        if ($null -eq (Get-JunctionTarget $Path)) { throw "Refusing to remove a path that is not a junction: $Path" }
        [System.IO.Directory]::Delete($Path, $false)
    }

    if (Test-Path -LiteralPath $dataLinkPath) {
        $plainTarget = Get-JunctionTarget $dataLinkPath
        if ($null -ne $plainTarget) {
            if (-not $plainTarget.Equals($expectedTarget, [System.StringComparison]::OrdinalIgnoreCase)) {
                throw "The test-client Data junction targets '$plainTarget', not '$expectedTarget'."
            }
            if ($hiddenFolders.Count -gt 0) { Remove-Junction $dataLinkPath }
        }
        else {
            # A partial layout from an earlier launch: take it apart, then rebuild what is wanted.
            foreach ($child in Get-ChildItem -LiteralPath $dataLinkPath -Force) {
                if ($null -eq (Get-JunctionTarget $child.FullName)) {
                    throw "The test-client Data folder holds something that is not a junction: $($child.FullName)"
                }
                Remove-Junction $child.FullName
            }
            [System.IO.Directory]::Delete($dataLinkPath, $false)
        }
    }

    if ($hiddenFolders.Count -eq 0) {
        if (-not (Test-Path -LiteralPath $dataLinkPath)) {
            New-Item -ItemType Junction -Path $dataLinkPath -Target $officialDataDirectory | Out-Null
        }
    }
    else {
        New-Item -ItemType Directory -Path $dataLinkPath | Out-Null
        foreach ($child in Get-ChildItem -LiteralPath $officialDataDirectory -Directory -Force) {
            if ($hiddenFolders -contains $child.Name) { continue }
            New-Item -ItemType Junction -Path (Join-Path $dataLinkPath $child.Name) -Target $child.FullName | Out-Null
        }
    }
}

# Window size. The game saves the resolution chosen in its Options menu, but a size given on
# the command line overrides it. So pass a size only when one is forced, or when the saved one
# does not fit this screen; the saved setting itself is never rewritten.
function Get-ScreenPixelSize {
    Add-Type -AssemblyName System.Windows.Forms
    if (-not ('ZeroHourLauncher.Dpi' -as [type])) {
        Add-Type -Namespace ZeroHourLauncher -Name Dpi -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();'
    }
    # The game is DPI-aware and works in real pixels, so measure the screen the same way.
    [ZeroHourLauncher.Dpi]::SetProcessDPIAware() | Out-Null
    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    return @($bounds.Width, $bounds.Height)
}

function Get-SavedResolution {
    $optionsPath = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Command and Conquer Generals Zero Hour Data\Options.ini'
    if (-not (Test-Path -LiteralPath $optionsPath)) { return $null }
    $match = Select-String -LiteralPath $optionsPath -Pattern '^\s*Resolution\s*=\s*(\d+)\s+(\d+)\s*$' | Select-Object -Last 1
    if (-not $match) { return $null }
    return @([int]$match.Matches[0].Groups[1].Value, [int]$match.Matches[0].Groups[2].Value)
}

# Decides the size arguments for one launch. $Saved and $Screen are @(width, height); $Saved
# may be $null. Returns @{ Arguments = ...; Note = ... }.
function Select-Resolution([int]$ForcedWidth, [int]$ForcedHeight, $Saved, $Screen) {
    if ($ForcedWidth -gt 0 -and $ForcedHeight -gt 0) {
        return @{ Arguments = @('-xres', $ForcedWidth, '-yres', $ForcedHeight); Note = "forced to ${ForcedWidth}x${ForcedHeight}" }
    }
    if ($ForcedWidth -gt 0 -or $ForcedHeight -gt 0) {
        throw 'Pass both -Width and -Height, or neither.'
    }
    if ($Saved -and $Saved[0] -le $Screen[0] -and $Saved[1] -le $Screen[1]) {
        return @{ Arguments = @(); Note = "saved $($Saved[0])x$($Saved[1]) (fits the $($Screen[0])x$($Screen[1]) screen)" }
    }

    # For this launch only: the largest common size the screen can show, or 1280x720 first
    # when nothing has been saved yet.
    $candidates = @(@(1920, 1080), @(1600, 900), @(1366, 768), @(1280, 720), @(1024, 768), @(800, 600))
    if (-not $Saved) { $candidates = @(, @(1280, 720)) + $candidates }
    $fallback = $candidates | Where-Object { $_[0] -le $Screen[0] -and $_[1] -le $Screen[1] } | Select-Object -First 1
    if (-not $fallback) { $fallback = @(800, 600) }
    $reason = if ($Saved) { "saved $($Saved[0])x$($Saved[1]) does not fit the $($Screen[0])x$($Screen[1]) screen" } else { 'no saved resolution' }
    return @{ Arguments = @('-xres', $fallback[0], '-yres', $fallback[1]); Note = "$($fallback[0])x$($fallback[1]) for this launch ($reason)" }
}

$resolution = Select-Resolution $Width $Height (Get-SavedResolution) (Get-ScreenPixelSize)
$resolutionArguments = $resolution.Arguments
$resolutionNote = $resolution.Note

if ($PrepareOnly) {
    Write-Host "Prepared the Data layout beside $executablePath without starting the game."
    Write-Host "Resolution: $resolutionNote"
    if (@($HideLooseDataFolders).Count -gt 0) { Write-Host "Hidden loose folders: $($HideLooseDataFolders -join ', ')" }
    return
}

$gameArguments = @('-win') + $resolutionArguments + @('-maxCameraHeight', $MaxCameraHeight)

if ($SharedControl) {
    $gameArguments += '-sharedControl'
}

$gameArguments += $AdditionalArguments

$previousPath = $env:Path
try {
    # Load proprietary runtime DLLs from the user's own installation without
    # copying or packaging them with this GPL-covered test client.
    $env:Path = "$GameDirectory;$previousPath"
    $process = Start-Process `
        -FilePath $executablePath `
        -WorkingDirectory $workingDirectory `
        -ArgumentList $gameArguments `
        -PassThru
}
finally {
    $env:Path = $previousPath
}

Write-Host "Started Zero Hour LAN test client (PID $($process.Id))."
Write-Host "Executable: $executablePath"
Write-Host "Game data:  $expectedTarget"
Write-Host "Working dir: $workingDirectory"
Write-Host "Resolution:  $resolutionNote"
