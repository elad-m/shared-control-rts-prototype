[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9._-]*$')]
    [string]$Version,
    [string]$ExecutablePath,
    [string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'

$repositoryRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ExecutablePath)) {
    $ExecutablePath = Join-Path $repositoryRoot 'build\win32-vs2019\GeneralsMD\Release\generalszh.exe'
}
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $repositoryRoot 'artifacts'
}

$requiredFiles = @(
    $ExecutablePath,
    (Join-Path $PSScriptRoot 'run-zero-hour-lan-client.ps1'),
    (Join-Path $PSScriptRoot 'launch-shared-control.cmd'),
    (Join-Path $repositoryRoot 'SHARED_CONTROL.md'),
    (Join-Path $repositoryRoot 'MODIFICATION_NOTICE.md'),
    (Join-Path $repositoryRoot 'LICENSE.md')
)
foreach ($requiredFile in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Required release file was not found: $requiredFile"
    }
}

$outputRoot = [System.IO.Path]::GetFullPath($OutputDirectory).TrimEnd('\')
$stagingDirectory = Join-Path $outputRoot "shared-control-rts-$Version"
$archivePath = "$stagingDirectory.zip"

if (-not (Test-Path -LiteralPath $outputRoot)) {
    New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
}
if (Test-Path -LiteralPath $stagingDirectory) {
    Remove-Item -LiteralPath $stagingDirectory -Recurse -Force
}
if (Test-Path -LiteralPath $archivePath) {
    Remove-Item -LiteralPath $archivePath -Force
}
New-Item -ItemType Directory -Path $stagingDirectory | Out-Null

Copy-Item -LiteralPath $ExecutablePath -Destination (Join-Path $stagingDirectory 'generalszh.exe')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'run-zero-hour-lan-client.ps1') -Destination $stagingDirectory
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'launch-shared-control.cmd') -Destination (Join-Path $stagingDirectory 'Launch Shared Control.cmd')
Copy-Item -LiteralPath (Join-Path $repositoryRoot 'SHARED_CONTROL.md') -Destination (Join-Path $stagingDirectory 'README.md')
Copy-Item -LiteralPath (Join-Path $repositoryRoot 'MODIFICATION_NOTICE.md') -Destination $stagingDirectory
Copy-Item -LiteralPath (Join-Path $repositoryRoot 'LICENSE.md') -Destination $stagingDirectory

$executableHash = (Get-FileHash -LiteralPath (Join-Path $stagingDirectory 'generalszh.exe') -Algorithm SHA256).Hash
Set-Content `
    -LiteralPath (Join-Path $stagingDirectory 'SHA256SUMS.txt') `
    -Value "$executableHash  generalszh.exe" `
    -Encoding ASCII

Compress-Archive -LiteralPath $stagingDirectory -DestinationPath $archivePath -CompressionLevel Optimal
$archiveHash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash

[pscustomobject]@{
    Version = $Version
    Archive = $archivePath
    ArchiveSHA256 = $archiveHash
    ExecutableSHA256 = $executableHash
}
