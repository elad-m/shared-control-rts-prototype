@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-zero-hour-lan-client.ps1" -UseCleanDataProjection -SharedControl
if errorlevel 1 (
    echo.
    echo Shared-control launch failed. Review the error above.
    pause
)
