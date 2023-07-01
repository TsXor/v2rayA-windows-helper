@echo off
cd /d %~dp0
msbuild.exe EdgeBrowserApp.sln /v:q /nologo /p:Configuration=Release
move /Y x64\Release\* dist
rmdir x64\Release
rmdir x64