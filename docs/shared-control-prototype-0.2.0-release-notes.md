# Shared Control Prototype 0.2.0

This is the first broadly playable LAN-tested shared-control build. Allied
human players keep separate armies and economies while being able to command
each other's forces and infrastructure.

## Changes since 0.1.1

- Allied General Powers and superweapon shortcuts are separated and outlined
  with the owning player's color.
- Allied satellite scans and Strategy Center intelligence reveal their results
  to the alliance.
- Allied production, construction, garrison, upgrade, and cancellation actions
  are authorized while costs and new units remain with the object's owner.
- Control groups recall allied units and accept commands.
- General Powers shortcuts no longer rebuild the UI while being used, fixing
  blocked purchases across allied armies. Purchasing was verified through
  rank 5.
- Multi-selected units can purchase object upgrades such as USA drones.
- Guard/special-power radii and allied rally-point markers remain visible.

## Known limitations

- The control-group number is not drawn above allied-owned units, although the
  units are recalled and receive commands.
- Pilots cannot enter allied vehicles.
- Units belonging to different allies cannot share one garrison.
- Money transfer, a shared wallet, and ownership transfer are not implemented.
- Internet play is the next milestone and has not yet been verified. This
  release should currently be treated as LAN-tested.

## Requirements

- Windows 8.1 or newer.
- A legitimate local installation of Generals and Zero Hour.
- The exact same 0.2.0 executable and `-sharedControl` option on every player.

Extract the ZIP into a new empty folder and run `Launch Shared Control.cmd`.
The archive contains no retail game assets, product keys, cracks, or
third-party proprietary DLLs.

This is an unofficial modified version, provided without warranty and not
endorsed or supported by Electronic Arts or the upstream maintainers. Complete
corresponding source is available under the release tag
`shared-control-prototype-0.2.0`.
