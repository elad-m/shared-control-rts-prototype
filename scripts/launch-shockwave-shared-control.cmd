@echo off
setlocal
rem Starts the shared-control build with the ShockWave mod.
rem Usage: "Launch ShockWave Shared Control.cmd" [mod folder]
rem The mod folder must hold the eleven !Shw*.big files, must be outside the game
rem folder, and its path must not contain spaces.

set "MOD_DIR=%~1"
if "%MOD_DIR%"=="" set "MOD_DIR=C:\ShockwaveModBig"

if not exist "%MOD_DIR%\!Shw_ini.big" (
    echo ShockWave files were not found in "%MOD_DIR%".
    echo See SHOCKWAVE.md, step 3.
    pause
    exit /b 1
)

if not "%MOD_DIR%"=="%MOD_DIR: =%" (
    echo The mod folder path contains a space: "%MOD_DIR%"
    echo The game ignores such a path. Move the folder, for example to C:\ShockwaveModBig.
    pause
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0run-zero-hour-lan-client.ps1' -SharedControl -AdditionalArguments '-mod','%MOD_DIR%'"
if errorlevel 1 (
    echo.
    echo ShockWave shared-control launch failed. Review the error above.
    pause
)
