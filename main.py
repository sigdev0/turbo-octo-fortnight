import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.bot import OmniForgeBot
from core.config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("omniforge")

async def run_simulation(cmd: str):
    bot = OmniForgeBot()
    print("=" * 60)
    print(f"⚡ SIMULATING COMMAND: {cmd}")
    print("=" * 60)
    result = await bot.simulate_command(cmd)
    print(json.dumps(result, indent=2, default=str))
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="OmniForge Engine Daemon & CLI")
    parser.add_argument("--run", action="store_true", help="Start the Telegram bot daemon in 24/7 polling mode")
    parser.add_argument("--simulate-cmd", type=str, help="Simulate executing a command directly (e.g. '/story Leo 8 space kindness')")
    parser.add_argument("--list", action="store_true", help="List all currently loaded cartridges")
    
    args = parser.parse_args()
    bot = OmniForgeBot()

    if args.simulate_cmd:
        asyncio.run(run_simulation(args.simulate_cmd))
    elif args.list:
        print("=" * 60)
        print("📦 OMNIFORGE ENGINE: LOADED CARTRIDGES")
        print("=" * 60)
        for cmd, cartridge in bot.cartridges.items():
            print(f"• Command: /{cmd}")
            print(f"  Name:        {cartridge.name}")
            print(f"  Description: {cartridge.description}")
            print("-" * 60)
        print(f"Total: {len(bot.cartridges)} cartridges registered.")
    elif args.run:
        if not TELEGRAM_BOT_TOKEN:
            print("❌ ERROR: TELEGRAM_BOT_TOKEN is not configured in .env!")
            print("Please create .env (or copy from .env.example) and add your bot token from @BotFather.")
            sys.exit(1)
        print("🚀 Starting OmniForge 24/7 Telegram Bot Daemon...")
        bot.run_polling()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
