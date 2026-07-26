[CmdletBinding()]
param(
    [string]$GameDirectory,
    [ValidateRange(640, 7680)]
    [int]$Width = 1280,
    [ValidateRange(480, 4320)]
    [int]$Height = 720,
    [ValidateRange(100, 1000)]
    [int]$MaxCameraHeight = 450,
    [switch]$UseCleanDataProjection,
    [switch]$SharedControl,
    [string[]]$AdditionalArguments = @()
)

$ErrorActionPreference = 'Stop'

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
    if (Test-Path -LiteralPath $dataLinkPath) {
        $dataEntry = Get-Item -LiteralPath $dataLinkPath -Force
        $actualTarget = @($dataEntry.Target)[0]
        if ($dataEntry.LinkType -ne 'Junction' -or [string]::IsNullOrWhiteSpace($actualTarget)) {
            throw "The test-client Data path already exists and is not a junction: $dataLinkPath"
        }

        $actualTarget = [System.IO.Path]::GetFullPath($actualTarget).TrimEnd('\')
        if (-not $actualTarget.Equals($expectedTarget, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "The test-client Data junction targets '$actualTarget', not '$expectedTarget'."
        }
    }
    else {
        New-Item -ItemType Junction -Path $dataLinkPath -Target $officialDataDirectory | Out-Null
    }
}

$gameArguments = @(
    '-win',
    '-xres', $Width,
    '-yres', $Height,
    '-maxCameraHeight', $MaxCameraHeight
)

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
