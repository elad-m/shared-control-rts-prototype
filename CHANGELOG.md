# Shared Control releases

What each release adds. One zip plays plain Zero Hour, ShockWave 1.201 and
Zero Hour Escalated 7.1.2. Every player must use the same release; the window
title shows which one is running. Downloads:
<https://github.com/elad-m/shared-control-rts-prototype/releases>

Setup guides: [SHOCKWAVE.md](SHOCKWAVE.md), [ESCALATED.md](ESCALATED.md),
[SHARED_CONTROL.md](SHARED_CONTROL.md).

## 0.7.0

- **Artillery slayer** (Zero Hour, ShockWave, Escalated). Select units, press
  **Y**, then click a destination. The cursor turns red and black. The units
  attack-move there but only stop to destroy enemy artillery seen near the
  route; other enemies don't stop them. They give up a chase that takes them
  more than twice their sight range away. When the move ends, they drive back
  in reverse to where the order was given. Any new order cancels the return.
  Press Y again before clicking to cancel.
  - Artillery means an enemy vehicle whose main weapon has a minimum range of
    50 or more, or a range of 250 or more. Soldiers never count. The Mobile
    Anti-Tank Guns and the Tank General's ECM Tank don't count either.
- The window title reads **Shared Control 0.7.0**.

## 0.6.0

- **General Powers tabs**: coloured tabs above the General Powers shortcut
  column, one per player who has powers. Click a tab to see and fire that
  player's powers; the column snaps back to yours after you use an ally's
  power. An amber dot marks a tab with a power ready.

## 0.5.0

- **Pilot auto-return** (Zero Hour): an ejected pilot runs to the nearest
  vehicle it may enter, or else to its owner's Command Center. Any order
  cancels it.
- **Zero Hour Escalated support**: `setup-escalated.ps1` prepares your own
  Escalated download and adds fixes (power plants on R for Israel and
  Ukraine; skirmish AI for Russia, North Korea, Baath and Ukraine builds
  bases and armies).

## Earlier

Shared control itself (commanding allied units, production, garrisons,
General Powers, money transfers), reverse move on **Z**, and ShockWave
support. See [SHARED_CONTROL.md](SHARED_CONTROL.md) for the full list.
