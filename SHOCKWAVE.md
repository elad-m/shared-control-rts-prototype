# ShockWave with shared control: setup guide

This guide sets up one Windows PC to play the ShockWave 1.201 mod on the
shared-control build, over Radmin VPN. Every player follows the same steps.

It is written so an AI assistant can carry it out step by step. Commands are
PowerShell. Nothing here modifies the game installation.

## Status

Experimental. One 15-minute two-PC match (Windows 11 and Windows 10) has been
completed on this build. Expect rough edges.

## What you need

- Windows 10 or 11.
- Your own installed copy of Generals and Zero Hour (version 1.04).
- The ShockWave 1.201 mod, downloaded by you. This repository does not contain
  or distribute ShockWave files.
- The release zip from this repository's Releases page:
  `shared-control-rts-shockwave-test-1.zip`.
- Radmin VPN, on the same Radmin network as the other players.

Every player must use the exact same release zip. A different build ends the
match with a mismatch.

## Steps

### 1. Check the base game

Start the normal Zero Hour once and reach the main menu, then close it. This
confirms the installation works and creates the settings file.

### 2. Extract the release

Extract `shared-control-rts-shockwave-test-1.zip` into a new, empty folder that
is **not** inside the game folder. Example: `C:\Games\SharedControlShockwave`.

### 3. Get ShockWave 1.201 and place its files

The tested files are ShockWave **1.201 "GenLauncher Fix 1"**, as downloaded by
GenLauncher.

1. Install GenLauncher (<https://github.com/p0ls3r/GenLauncher>) and let it download
   **C&C Shockwave 1.201**. The mod's own page is
   <https://www.moddb.com/mods/cc-shockwave>.
2. Close GenLauncher with its own window controls. Do not end it from Task
   Manager: it rearranges the game folder while a mod runs and only restores it
   on a normal exit.
3. Find the downloaded files. GenLauncher keeps them inside the Zero Hour
   folder, in `GLM\C&C Shockwave\1.201 GenLauncher Fix 1\`. They are eleven
   files named `!Shw*.gib` plus `!0Shwpatch.gib`.
4. Copy the eleven files to `C:\ShockwaveModBig` and change each extension
   from `.gib` to `.big`:

   ```powershell
   $source = 'C:\Path\To\Zero Hour\GLM\C&C Shockwave\1.201 GenLauncher Fix 1'
   New-Item -ItemType Directory -Force -Path 'C:\ShockwaveModBig' | Out-Null
   Get-ChildItem -LiteralPath $source -Filter '*.gib' | ForEach-Object {
       Copy-Item -LiteralPath $_.FullName -Destination (Join-Path 'C:\ShockwaveModBig' ($_.BaseName + '.big'))
   }
   ```

Two rules for the mod folder:

- It must be **outside** the game folder. The game loads every `.big` file it
  finds under its own folder, with or without the mod switch.
- Its path must contain **no spaces**. The game silently ignores a mod path
  with a space in it.

### 4. Run the setup check

In the extracted release folder:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\verify-shockwave-setup.ps1
```

Use `-ModDirectory` or `-GameDirectory` if your folders differ from the
defaults. The check only reads files. Fix every `FAIL` line before playing.
`WARN` lines are worth reading but do not always block a match.

### 5. Point the game at Radmin VPN

1. Install Radmin VPN and join the shared network.
2. Note your Radmin address. It starts with `26.`.
3. Open `Documents\Command and Conquer Generals Zero Hour Data\Options.ini`
   and set both lines to that address:

   ```ini
   IPAddress = 26.x.x.x
   GameSpyIPAddress = 26.x.x.x
   ```

Radmin can hand out a new address later. If players stop seeing each other,
check this first.

### 6. Launch

Double-click `Launch ShockWave Shared Control.cmd` in the extracted folder.

If your mod folder is not `C:\ShockwaveModBig`, pass it as an argument:

```powershell
& '.\Launch ShockWave Shared Control.cmd' D:\ShockwaveModBig
```

You have the right build when the window title mentions **ShockWave V1.201**.

The first time the game opens the Network lobby, Windows Firewall asks for
access. Tick both Private and Public, then allow. Radmin VPN usually counts as
a public network.

### 7. Start a match

1. Go to **Multiplayer > Network**.
2. One player creates a game. The others join it from the lobby list.
3. Put the human allies on the same team.
4. The host can tick **Allow Mixed Allied Garrisons**. This checkbox exists
   only in the Network lobby, not in Skirmish.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Plain Zero Hour starts, no ShockWave | Mod path has a space, or the folder is wrong | Use `C:\ShockwaveModBig`; rerun the setup check |
| ShockWave content appears without the mod switch | ShockWave files are inside the game folder | Move them out; rerun the setup check |
| No mouse cursor in the game | The exe was started directly | Always start through the `.cmd` launcher. It creates a `Data` link next to the exe that the game needs |
| Game closes at once, before the menu | An overlay `d3d8.dll` (for example GenTool) conflicts with this build | Keep the `d3d8.dll` from the release zip next to `generalszh.exe` |
| Players do not see each other in the lobby | Wrong address in `Options.ini`, or firewall | Redo step 5; allow the game through the firewall on both network types |
| "Mismatch" shortly after the match starts | Players have different files | Every player runs the setup check; compare the lines that are not `OK` |
| Window is far too large | Windows display scaling | In the exe's Properties > Compatibility > Change high DPI settings, override scaling with "Application" |

`launch-last.log` in the extracted folder records the last launch.

## What the release contains

- `generalszh.exe`: the shared-control engine built from the `shockwave`
  branch of this repository (GPL, see `LICENSE.md`).
- `d3d8.dll`: the d3d8to9 Direct3D 8 to 9 wrapper by Patrick Mours, built from its
  unmodified source (commit 6cdb8a8), under the licence in `d3d8to9-LICENSE.md`.
- Launcher and check scripts, and this guide.

It contains no game data, no ShockWave data, and no proprietary DLLs.
