@echo off
cd /d %~dp0
start /b x32\hook_minimize_button.exe %1
start /b x64\hook_minimize_button.exe %1