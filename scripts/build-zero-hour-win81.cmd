@echo off
setlocal

set "VSDEVCMD=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\Common7\Tools\VsDevCmd.bat"
set "CMAKE_EXE=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
if not exist "%VSDEVCMD%" (
    echo Visual Studio 2019 Build Tools were not found.
    exit /b 1
)
if not exist "%CMAKE_EXE%" (
    echo CMake from Visual Studio 2022 Build Tools was not found.
    exit /b 1
)

call "%VSDEVCMD%" -arch=x86 -host_arch=x64 -winsdk=10.0.19041.0
if errorlevel 1 exit /b %errorlevel%

"%CMAKE_EXE%" --preset win32 -B build\win32-vs2019
if errorlevel 1 exit /b %errorlevel%

"%CMAKE_EXE%" --build build\win32-vs2019 --config Release --target generalszh.exe
exit /b %errorlevel%
