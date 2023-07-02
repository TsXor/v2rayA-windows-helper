@echo off
chcp 65001
cd /d %~dp0

if not exist build (mkdir build)

if "%1"=="x32" ( goto make32bit )
if "%1"=="x64" ( goto make64bit )
echo please give x32 or x64 for the first parameter
goto END

:make32bit
echo **********
echo make 32bit
echo **********
if not exist build\x32 (mkdir build\x32)
cd build\x32
cmake -G"Visual Studio 17 2022" -A Win32 -D ARCH=x32 ..\..
cmake --build . --target install --config Release
cd ..\..
goto END

:make64bit
echo **********
echo make 64bit
echo **********
if not exist build\x64 (mkdir build\x64)
cd build\x64
cmake -G"Visual Studio 17 2022" -A x64   -D ARCH=x64 ..\..
cmake --build . --target install --config Release
cd ..\..
goto END

:END