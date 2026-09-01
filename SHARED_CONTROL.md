# Shared Control RTS Prototype

## Status

This is an unofficial, experimental modification of the GPL-covered engine
source. Version 0.2.0 has been tested in two-player LAN matches with allied
human armies and an AI opponent. Internet play is the next milestone and has
not yet been verified.

With shared control enabled, allied human players can:

- select and move each other's units;
- issue Stop, Guard, Attack Move, and ordinary attack orders;
- command mixed selections containing units from multiple allied armies;
- issue simultaneous orders to the same allied units;
- see allied Guard and special-power targeting radii;
- see rally-point markers and paths for allied production buildings;
- use allied production, construction, garrison, upgrade, and cancellation
  controls, with costs charged to the object's owner;
- recall allied units through control groups; and
- see and use allied General Powers and superweapon shortcuts, separated and
  outlined with their owner's color.

Allied satellite scans and Strategy Center intelligence reveal their results
to the alliance. General Powers purchasing has been verified through rank 5,
and multi-unit USA drone purchases have been verified.

The current development build adds explicit allied resource transfers through
the Diplomacy screen. A player may send $500, $1,000, or $5,000 from their own
wallet to an active ally.

A selected, completed allied building can also be transferred from the
Diplomacy screen with the building-transfer button. Because faction category
flags are inconsistent, the current build uses a short denylist rather than an
allowlist. Any completed empty structure can transfer except Command Centers,
superweapons, science/advanced-technology buildings, Internet Centers,
Airfields, and fake structures. Occupied structures remain blocked. Empty
tunnels and production buildings are therefore testable, while their known
special cases remain staged in `ROADMAP.html`.

The generic `FS_TECHNOLOGY` marker is deliberately not used as an exclusion:
USA defenses, Supply Drop Zones, and GLA Black Markets can carry that marker.
The dedicated Command Center, superweapon, advanced-tech, Internet Center,
Airfield, and fake-structure markers define the exclusions instead.

The prototype preserves each unit's original owner. It does not merge armies,
resources, general points, production, defeat states, or player colors.

Enemy units remain viewable but cannot be commanded. Production ordered through
an allied building is paid for by that building's owner, and the completed unit
belongs to that owner.

## Requirements

- Windows 8.1 or newer;
- a legitimate local installation of the original game and expansion;
- for the currently verified workflow, a private LAN where all players can
  already see and join the same match; and
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

- Recalling a control group selects allied units and allows commands, but the
  group number is not drawn above units owned by another player.
- Pilots cannot currently enter allied vehicles.
- Units owned by different allies cannot currently share one garrisoned
  building.
- A shared wallet and ownership transfer are not implemented. Direct money
  transfer is available in the current development build but is not part of the
  verified 0.2.0 release.
- Internet play through C&C:Online has not yet been verified. Version 0.2.0
  should be treated as a LAN-tested release.

Enemy units remain uncontrollable.

## Internet-play milestone

The shared-control rules operate in the synchronized game-command layer rather
than in the LAN discovery code. The Online lobby also advertises executable and
INI CRC values, so every participant must use the exact same build, game data,
and `-sharedControl` option. Do not mix this prototype with an ordinary retail
client.

The next development stage is to validate version 0.2.0 in a private
C&C:Online room using the current GenTool/C&C:Online setup. That work includes
checking that the release launcher loads the required integration, that two
matching clients can see and join the room, and that a complete match remains
synchronized. Online support will not be claimed until those checks pass.

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
.\scripts\package-shared-control-release.ps1 -Version prototype-0.2.0
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
