@echo off
title OmniForge Mission Control Portal
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONUNBUFFERED=1
echo ============================================================
echo   OmniForge Mission Control Web Portal
echo   Access URL: http://localhost:8080
echo ============================================================
"%~dp0.venv\Scripts\python.exe" -m uvicorn portal.server:app --host 0.0.0.0 --port 8080 --reload
pause
