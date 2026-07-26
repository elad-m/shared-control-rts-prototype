# Shared Control RTS Prototype

## Status

This is an unofficial, experimental modification of the GPL-covered engine
source. It has been tested in a two-player LAN match with allied human armies
and an AI opponent.

With shared control enabled, allied human players can:

- select and move each other's units;
- issue Stop, Guard, Attack Move, and ordinary attack orders;
- command mixed selections containing units from multiple allied armies; and
- issue simultaneous orders to the same allied units.

The prototype preserves each unit's original owner. It does not merge armies,
resources, general points, production, defeat states, or player colors.

## Requirements

- Windows 8.1 or newer;
- a legitimate local installation of the original game and expansion;
- a private LAN where all players can already see and join the same match; and
- the exact same shared-control executable on every participating computer.

This repository and its release archives intentionally exclude retail `.big`
archives, product keys, cracks, third-party patch files, videos, audio, models,
textures, and proprietary runtime DLLs.

## Running a binary release

1. Install the original game and expansion normally.
2. Extract the shared-control release into a new empty folder.
3. Double-click `Launch Shared Control.cmd`.
4. If automatic installation detection fails, open PowerShell in the extracted
   folder and run:

   ```powershell
   .\run-zero-hour-lan-client.ps1 `
     -GameDirectory "C:\Path\To\Your\Installed\Game" `
     -UseCleanDataProjection `
     -SharedControl
   ```

The launcher refers to the player's own installed assets. It creates local
junctions and hard links inside the extracted test folder; it does not modify
or redistribute the official installation.

Every player must launch with `-sharedControl`. In the LAN lobby, place the
human players on the same team. Players on opposing teams must remain
uncontrollable.

## Known limitations

- Some ownership-specific visual indicators are missing for allied units,
  including the visible Guard radius.
- Allied superweapons can be commanded by selecting the allied building, but
  their buttons may not appear in the other player's global shortcut panel.
- Pilots cannot currently enter allied vehicles.
- Units owned by different allies cannot currently share one garrisoned
  building.
- Resource spending and production initiated through an allied building need
  more focused testing.

These limitations are deliberately left outside the first network-safety
prototype. Ownership transfer and a shared global wallet are not implemented.

## Building from source

The normal upstream build instructions remain in [README.md](README.md). The
tested Windows 8.1-compatible build used Visual Studio 2019's v142 compiler,
Windows SDK 10.0.19041, and:

```cmd
scripts\build-zero-hour-win81.cmd
```

The resulting executable is:

```text
build\win32-vs2019\GeneralsMD\Release\generalszh.exe
```

## Creating a source-matched release archive

After building the exact Git revision that will be tagged, run:

```powershell
.\scripts\package-shared-control-release.ps1 -Version prototype-0.1.0
```

The archive contains the executable, launcher, license, and this guide. Publish
the Git tag/source archive alongside the binary archive so recipients can
obtain the complete corresponding source for that exact executable.

## License and origin

Electronic Arts released the engine source under GNU GPL version 3 with
additional terms. Those terms are preserved verbatim in [LICENSE.md](LICENSE.md).
This modified version is clearly identified as modified and is provided without
warranty.

The modification is based on the community-maintained
`TheSuperHackers/GeneralsGameCode` project. It is unaffiliated with and not
endorsed or supported by Electronic Arts or the upstream maintainers.
