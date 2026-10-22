@echo off
setlocal
rem Starts the shared-control build with the Zero Hour Escalated mod.
rem Usage: "Launch Escalated Shared Control.cmd" [mod folder]
rem The mod folder is made by setup-escalated.ps1. It must be outside the game
rem folder, and its path must not contain spaces.

set "MOD_DIR=%~1"
if "%MOD_DIR%"=="" set "MOD_DIR=C:\EscalatedModBig"

if not exist "%MOD_DIR%\!!!ZZSharedControlFixes.big" (
    echo Escalated is not set up in "%MOD_DIR%".
    echo Run setup-escalated.ps1 first. See ESCALATED.md, step 3.
    pause
    exit /b 1
)

if not "%MOD_DIR%"=="%MOD_DIR: =%" (
    echo The mod folder path contains a space: "%MOD_DIR%"
    echo The game ignores such a path. Use a folder such as C:\EscalatedModBig.
    pause
    exit /b 1
)

rem Escalated ships its own AI and multiplayer scripts. The base game's loose copies in
rem Data\Scripts would be used instead, so they are hidden from this build.
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0run-zero-hour-lan-client.ps1' -SharedControl -HideLooseDataFolders 'Scripts' -AdditionalArguments '-mod','%MOD_DIR%'"
if errorlevel 1 (
    echo.
    echo Escalated shared-control launch failed. Review the error above.
    pause
)
