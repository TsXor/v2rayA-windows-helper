@echo off
chcp 65001
cd /d %~dp0

if "%1"=="" (rem) else (
    echo 你需要指定编译版本
    goto END
)

if not exist build (mkdir build)
if not exist build\x64 (mkdir build\x64)
if not exist build\x32 (mkdir build\x32)

echo **********
echo make 32bit
echo **********
cd build\x32
cmake -G"Visual Studio 17 2022" -A Win32 -D ARCH=x32 ..\..
cmake --build . --config %1
cd ..\..

echo **********
echo make 64bit
echo **********
cd build\x64
cmake -G"Visual Studio 17 2022" -A x64   -D ARCH=x64 ..\..
cmake --build . --config %1
cd ..\..

xcopy /Y hook_minimize_button.bat dist\%1\

:END