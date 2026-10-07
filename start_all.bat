@echo off
title OmniForge Starter
cd /d "%~dp0"
echo Launching OmniForge Portal and Telegram Bot in separate windows...
start "" run_portal.bat
start "" run_bot.bat
