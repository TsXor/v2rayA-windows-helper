@echo off
cd /d %~dp0
mkdir cmake-build-windows >NUL
cd cmake-build-windows
cmake -G"MinGW Makefiles" ..\..
cmake --build . --target install
