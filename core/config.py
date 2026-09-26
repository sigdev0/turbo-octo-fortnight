import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = BASE_DIR / "core"
CARTRIDGES_DIR = BASE_DIR / "cartridges"
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
TEMPLATES_DIR = ASSETS_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"
BACKLOG_DIR = BASE_DIR / "backlog"

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

# Ensure required directories exist
for p in [MUSIC_DIR, TEMPLATES_DIR, OUTPUT_DIR, BACKLOG_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
_allowed_users_raw = os.getenv("ALLOWED_TELEGRAM_USERS", "")
ALLOWED_TELEGRAM_USERS = [u.strip() for u in _allowed_users_raw.split(",") if u.strip()]

# LLM Router Configuration (Works with 9router, OpenCode, OpenAI, Groq, Ollama, etc.)
ROUTER_API_BASE = os.getenv("ROUTER_API_BASE", "https://api.openai.com/v1").rstrip("/")
ROUTER_API_KEY = os.getenv("ROUTER_API_KEY", "")
ROUTER_MODEL = os.getenv("ROUTER_MODEL", "claude-3-5-sonnet")

# Default Language ('id' for Bahasa Indonesia, 'en' for English)
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "id")

# Voice Profiles
VOICE_PROFILES = {
    "bedtime_british": {
        "voice": "en-GB-RyanNeural",
        "rate": "-12%",
        "volume": "+0%",
        "pitch": "-2Hz"
    },
    "bedtime_american": {
        "voice": "en-US-ChristopherNeural",
        "rate": "-10%",
        "volume": "+0%",
        "pitch": "-2Hz"
    },
    "bedtime_female": {
        "voice": "en-US-JennyNeural",
        "rate": "-10%",
        "volume": "+0%",
        "pitch": "+0Hz"
    },
    "indonesian_female": {
        "voice": "id-ID-GadisNeural",
        "rate": "-10%",
        "volume": "+0%",
        "pitch": "+0Hz"
    },
    "indonesian_male": {
        "voice": "id-ID-ArdiNeural",
        "rate": "-10%",
        "volume": "+0%",
        "pitch": "-2Hz"
    },
    "indonesian_warm": {
        "voice": "id-ID-ArdiNeural",
        "rate": "-10%",
        "volume": "+0%",
        "pitch": "-2Hz"
    },
    "energetic_affirmation": {
        "voice": "en-US-GuyNeural",
        "rate": "+0%",
        "volume": "+0%",
        "pitch": "+0Hz"
    },
    "indonesian_affirmation": {
        "voice": "id-ID-GadisNeural",
        "rate": "+0%",
        "volume": "+0%",
        "pitch": "+0Hz"
    }
}

DEFAULT_BEDTIME_VOICE = "bedtime_british"
