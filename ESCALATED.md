# Zero Hour Escalated with shared control: setup guide

This guide sets up one Windows PC to play the Zero Hour Escalated 7.1.2 mod on
the shared-control build, over Radmin VPN. Every player follows the same steps.

It is written so an AI assistant can carry it out step by step. Commands are
PowerShell. Nothing here modifies the game installation or Escalated's own files.

## Status

Experimental. Two-PC matches (Windows 11 and Windows 10) against AI players of
the new factions have been played on this build.

## What you need

- Windows 10 or 11.
- Your own installed copy of Generals and Zero Hour (version 1.04).
- The Zero Hour Escalated 7.1.2 mod, downloaded by you through GenLauncher. This
  repository does not contain or distribute Escalated files.
- The release zip from this repository's Releases page:
  `shared-control-rts-0.5.0.zip` (the first release with Escalated support).
- Radmin VPN, on the same Radmin network as the other players.

Every player must use the exact same release zip. A different build ends the
match with a mismatch.

## What the setup adds to Escalated

The setup script builds one extra file, `!!!ZZSharedControlFixes.big`, from your
own Escalated files. The game loads it after Escalated's files, so it overrides
these three parts:

- **Build hotkeys.** Israel and Ukraine build power plants with **R**, as USA and
  China do. Israel's C-RAM moves from R to **M**.
- **Skirmish AI for Russia, North Korea, Baath and Ukraine.** In Escalated 7.1.2
  their AI scripts still name the buildings and units of the original generals
  they replace (Tank, Nuke, Demolition and Toxin), which these factions cannot
  build. Those AI players sit idle. The fix renames those references to each
  faction's own buildings and units (`scripts/escalated-ai-fixes.json`).
- **Baath and Ukraine openings on Easy and Normal.** Their supply buildings need
  a power plant first. Escalated's Hard AI already builds one; the fix gives the
  Easy and Normal AI the same opening. North Korea's default base defence also
  moves from China's Gattling Cannon to its own Turret Bunker.

The script checks the result against a known checksum, so every player ends up
with identical files.

## Steps

### 1. Check the base game

Start the normal Zero Hour once and reach the main menu, then close it.

### 2. Download Escalated with GenLauncher

1. Install GenLauncher (<https://github.com/p0ls3r/GenLauncher>) and let it
   download **Zero Hour Escalated 7.1.2**. The mod's own page is
   <https://www.moddb.com/mods/zero-hour-escalated>.
2. Close GenLauncher with its own window controls, not from Task Manager.

GenLauncher keeps the files inside the Zero Hour folder, in
`GLM\Zero Hour Escalated\7.1.2\`, as 39 files named `!!!*.gib`.

### 3. Extract the release and run the setup

Extract the release zip into a new, empty folder that is **not** inside the game
folder. In that folder, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup-escalated.ps1
```

It copies Escalated's files to `C:\EscalatedModBig` as `.big` files and builds
the fixes file there. Use `-ModDirectory` for a different folder (outside the
game folder, no spaces in its path), and `-GameDirectory` or
`-EscalatedDirectory` if the script cannot find your folders. Every line must
read `OK`. Running it again is safe.

### 4. Point the game at Radmin VPN

Follow step 5 of [SHOCKWAVE.md](SHOCKWAVE.md): set `IPAddress` and
`GameSpyIPAddress` in `Options.ini` to your Radmin address.

### 5. Launch

Double-click `Launch Escalated Shared Control.cmd` in the extracted folder. If
your mod folder is not `C:\EscalatedModBig`, pass it as an argument:

```powershell
& '.\Launch Escalated Shared Control.cmd' D:\EscalatedModBig
```

You have the right build when the window title starts with
**Shared Control 0.5.0**. Every player's title must show the same release.

### 6. Start a match

1. Go to **Multiplayer > Network**.
2. One player creates a game. The others join it from the lobby list.
3. Put the human allies on the same team. AI players of any faction can be added.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Plain Zero Hour starts, no Escalated | Mod path has a space, or the folder is wrong | Use `C:\EscalatedModBig`; run the setup again |
| Setup reports a file that differs | A different Escalated version | Download 7.1.2 with GenLauncher |
| Setup says the fixes file came out different | A file changed on the way | Report it; do not play with that copy |
| Russia, North Korea, Baath or Ukraine AI stays idle | The fixes file is missing, or the base game's scripts were used | Start through `Launch Escalated Shared Control.cmd`; run the setup again |
| "Mismatch" shortly after the match starts | Players have different files | Every player runs the setup; all lines must read `OK` |

For anything else, see the troubleshooting table in [SHOCKWAVE.md](SHOCKWAVE.md);
the same launcher rules apply.
