#!/usr/bin/env bash
export TELEGRAM_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
export TELEGRAM_ALLOWED_USER_ID="${ALLOWED_TELEGRAM_USERS:-}"
export GROQ_API_KEY="${GROQ_API_KEY:-}"
export NINE_ROUTER_API_KEY="${ROUTER_API_KEY:-}"
cd "$(dirname "$0")/.."
exec python3 bot/clipbot.py
