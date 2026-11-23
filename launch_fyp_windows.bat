@echo off
cd /d "%~dp0"
uv run fyp-launcher
if errorlevel 1 pause
