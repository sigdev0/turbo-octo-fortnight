@echo off
title OmniForge Telegram Bot Daemon
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONUNBUFFERED=1
echo ============================================================
echo   OmniForge 24/7 Telegram Bot Daemon
echo ============================================================
"%~dp0.venv\Scripts\python.exe" main.py --run
pause
