#!/usr/bin/env bash
set -e

echo "🚀 Setting up OmniForge on WSL..."

# 1. Install system prerequisites
echo "📦 Updating apt and installing dependencies (ffmpeg, python3-venv, git)..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip ffmpeg git curl

# 2. Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "📦 Installing Python requirements..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# 3. Create .env if it does not exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env configuration..."
    cat << 'EOF' > .env
TELEGRAM_BOT_TOKEN=8515629377:AAGPgo5QwB8fzJdNN3S8xc_InwEhvHsoiNk
ALLOWED_TELEGRAM_USERS=
ROUTER_API_BASE=http://127.0.0.1:20128/v1
ROUTER_API_KEY=
ROUTER_MODEL=claude-3-5-sonnet
DEFAULT_LANGUAGE=id
EOF
    echo "✅ .env configured with Telegram token and local 9router base."
fi

# 4. Ensure directories exist
mkdir -p output data backlog assets/music

echo ""
echo "=========================================================="
echo "🎉 OmniForge is ready on your WSL environment!"
echo "=========================================================="
echo ""
echo "To run interactively in terminal:"
echo "    .venv/bin/python main.py --run"
echo ""
echo "To run 24/7 in background:"
echo "    nohup .venv/bin/python main.py --run > omniforge.log 2>&1 &"
echo ""
