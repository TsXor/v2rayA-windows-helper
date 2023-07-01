@echo off
cd /d %~dp0
msbuild.exe EdgeBrowserApp.sln /v:q /nologo /p:Configuration=Release