import asyncio
import importlib
import importlib.util
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from core.config import (
    CARTRIDGES_DIR,
    OUTPUT_DIR,
    TELEGRAM_BOT_TOKEN,
    ALLOWED_TELEGRAM_USERS
)
from cartridges.base import BaseCartridge
from core.autoforge import AutoForge

logger = logging.getLogger(__name__)

class OmniForgeBot:
    def __init__(self, token: Optional[str] = None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.cartridges: Dict[str, BaseCartridge] = {}
        self.start_time = time.time()
        self.app: Optional[Application] = None
        self.autoforge = AutoForge()
        self.load_cartridges()

    def load_cartridges(self) -> None:
        """
        Dynamically scans CARTRIDGES_DIR and registers all BaseCartridge subclasses.
        """
        self.cartridges.clear()
        sys.path.insert(0, str(CARTRIDGES_DIR.parent))

        for file_path in CARTRIDGES_DIR.glob("*.py"):
            if file_path.name.startswith("__") or file_path.name == "base.py":
                continue

            module_name = f"cartridges.{file_path.stem}"
            try:
                if module_name in sys.modules:
                    module = importlib.reload(sys.modules[module_name])
                else:
                    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseCartridge) and attr is not BaseCartridge:
                        instance: BaseCartridge = attr()
                        cmd = instance.command.lower().strip("/")
                        self.cartridges[cmd] = instance
                        logger.info(f"Loaded Cartridge: {instance.name} (command: /{cmd})")
            except Exception as e:
                logger.error(f"Failed to load cartridge from {file_path.name}: {e}")

    def _is_user_authorized(self, update: Update) -> bool:
        """Checks whether the sender is in ALLOWED_TELEGRAM_USERS (if whitelist is active)."""
        if not ALLOWED_TELEGRAM_USERS:
            return True

        user = update.effective_user
        if not user:
            return False

        username = (user.username or "").lower()
        user_id = str(user.id)
        for allowed in ALLOWED_TELEGRAM_USERS:
            allowed_clean = allowed.lower().lstrip("@")
            if allowed_clean in (username, user_id):
                return True
        return False

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_user_authorized(update):
            await update.message.reply_text("⛔ Access restricted. Contact admin to authorize your Telegram account.")
            return

        cartridge_lines = [
            f"• `/{cmd}` — {c.description}"
            for cmd, c in self.cartridges.items()
        ]
        cartridges_text = "\n".join(cartridge_lines) if cartridge_lines else "No cartridges loaded."

        msg = (
            "🌟 *Welcome to OmniForge Engine* 🌟\n\n"
            "Your decoupled asset generator and autonomous micro-SaaS factory is live!\n\n"
            "📦 *Loaded Cartridges:*\n"
            f"{cartridges_text}\n\n"
            "💡 *Autonomous AutoForge (While Driving):*\n"
            "• `/idea <your idea>` — I will write the code, self-test it, and register the new command live!\n\n"
            "⚙️ *System Commands:*\n"
            "• `/status` — Check server health, uptime & asset count\n"
            "• `/reload` — Refresh cartridges from disk\n"
            "• `/help` — Detailed command guide"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        msg = (
            "📖 *OmniForge Command Guide*\n\n"
            "*1. Bedtime Stories (`/story`):*\n"
            "`/story <Name> <Age> <Theme> <Lesson>`\n"
            "Example: `/story Leo 8 space kindness`\n"
            "Example: `/story Maya 2 clouds gentleness`\n\n"
            "*2. AutoForge (`/idea`):*\n"
            "`/idea <describe what you want>`\n"
            "Example: `/idea 3-minute morning courage affirmations for kids`\n\n"
            "*3. Voice Notes:*\n"
            "Send any voice memo, and I'll forward it to AutoForge to execute while you're away!"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        uptime_sec = int(time.time() - self.start_time)
        hrs, rem = divmod(uptime_sec, 3600)
        mins, secs = divmod(rem, 60)

        output_files = list(OUTPUT_DIR.glob("*.*"))
        total_size_mb = sum(f.stat().st_size for f in output_files) / (1024 * 1024)

        msg = (
            "📊 *OmniForge Engine Health Status*\n\n"
            f"⏱️ *Uptime:* {hrs}h {mins}m {secs}s\n"
            f"📦 *Active Cartridges:* {len(self.cartridges)} ({', '.join(f'/{c}' for c in self.cartridges)})\n"
            f"📁 *Generated Assets:* {len(output_files)} files ({total_size_mb:.1f} MB)\n"
            f"🧠 *LLM Router:* {'Configured' if self.autoforge.router.is_configured else 'Local Template Fallback'}\n"
            "⚡ *Status:* All systems operational."
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def reload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.load_cartridges()
        await update.message.reply_text(
            f"🔄 Reloaded cartridges from disk! Active: {', '.join(f'/{c}' for c in self.cartridges)}"
        )

    async def idea_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_user_authorized(update):
            return

        if not context.args:
            await update.message.reply_text("💡 Please provide your idea: `/idea <describe feature or asset>`", parse_mode="Markdown")
            return

        idea_text = " ".join(context.args)
        status_msg = await update.message.reply_text(f"🧠 *AutoForge received idea:* \"{idea_text}\"\nInitializing autonomous pipeline...", parse_mode="Markdown")

        async def update_status(text: str):
            try:
                await status_msg.edit_text(f"⚙️ *AutoForge Progress:*\n{text}", parse_mode="Markdown")
            except Exception:
                pass

        try:
            result = await self.autoforge.forge_cartridge(
                idea_prompt=idea_text,
                on_status=update_status
            )
            self.load_cartridges()

            success_text = (
                f"🚀 *New Cartridge Live on Your Bot!*\n\n"
                f"🏷️ *Command:* `/{result['command']}`\n"
                f"📝 *Description:* {result['description']}\n"
                f"🎵 *Test Title:* {result['title']}\n\n"
                f"You can now trigger it anytime using `/{result['command']}`!"
            )
            await status_msg.edit_text(success_text, parse_mode="Markdown")

            # Send test audio sample if generated
            sample_path = result.get("sample_output_file")
            if sample_path and Path(sample_path).exists():
                await update.message.reply_audio(
                    audio=open(sample_path, "rb"),
                    title=result.get("title", f"Sample {result['command'].title()}"),
                    performer="OmniForge AutoForge",
                    caption=f"🔊 Verified test render for `/{result['command']}`"
                )
        except Exception as e:
            logger.error(f"Error in idea_command: {e}", exc_info=True)
            await status_msg.edit_text(f"❌ *AutoForge execution failed:* {str(e)}", parse_mode="Markdown")

    async def handle_cartridge_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Generic handler for all registered cartridges (e.g. /story, /affirmation).
        """
        if not self._is_user_authorized(update):
            return

        cmd = update.message.text.split()[0].lstrip("/").lower()
        cartridge = self.cartridges.get(cmd)

        if not cartridge:
            await update.message.reply_text(f"Unknown command `/{cmd}`. Use `/start` to see available commands.")
            return

        # Parse args
        args = context.args or []
        payload: Dict[str, Any] = {}

        if cmd == "story":
            if len(args) >= 1:
                payload["name"] = args[0]
            if len(args) >= 2:
                try:
                    payload["age"] = int(args[1])
                except ValueError:
                    payload["age"] = 8
            if len(args) >= 3:
                payload["theme"] = args[2]
            if len(args) >= 4:
                payload["lesson"] = " ".join(args[3:])
            
            # If no args given, prompt with simple quick example
            if not args:
                await update.message.reply_text(
                    "🌙 *How to use /story:*\n"
                    "`/story <Name> <Age> <Theme> <Lesson>`\n\n"
                    "Examples:\n"
                    "• `/story Leo 8 space courage`\n"
                    "• `/story Maya 2 clouds gentleness`",
                    parse_mode="Markdown"
                )
                return
        else:
            if args:
                payload["name"] = args[0]
                if len(args) > 1:
                    payload["theme"] = " ".join(args[1:])

        status_msg = await update.message.reply_text(f"⚡ *Triggering cartridge `/{cmd}`...*", parse_mode="Markdown")

        async def on_progress(step_msg: str):
            try:
                await status_msg.edit_text(f"⚙️ *Rendering `/{cmd}`:*\n{step_msg}", parse_mode="Markdown")
            except Exception:
                pass

        payload["on_progress"] = on_progress

        try:
            result = await cartridge.generate(payload)
            if result.get("status") != "success":
                await status_msg.edit_text(f"❌ Error generating asset: {result.get('error', 'Unknown error')}")
                return

            output_file = result.get("output_file")
            title = result.get("title", f"Generated {cmd.title()}")

            await status_msg.edit_text(f"✨ *Rendering Complete:* {title}\nUploading audio to your chat...", parse_mode="Markdown")

            if output_file and Path(output_file).exists():
                await update.message.reply_audio(
                    audio=open(output_file, "rb"),
                    title=title,
                    performer="OmniForge Audio",
                    caption=f"🎧 *{title}*\n\n_{result.get('script', '')[:200]}..._",
                    parse_mode="Markdown"
                )
                await status_msg.delete()
        except Exception as e:
            logger.error(f"Error executing cartridge `/{cmd}`: {e}", exc_info=True)
            await status_msg.edit_text(f"❌ Error executing `/{cmd}`: {str(e)}")

    def build_application(self) -> Application:
        """Configures and returns the python-telegram-bot Application."""
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured in .env or config.py")

        self.app = Application.builder().token(self.token).build()

        # Core handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("reload", self.reload_command))
        self.app.add_handler(CommandHandler("idea", self.idea_command))

        # Dynamic cartridge commands
        for cmd in self.cartridges.keys():
            self.app.add_handler(CommandHandler(cmd, self.handle_cartridge_command))

        return self.app

    async def simulate_command(self, command_line: str) -> Dict[str, Any]:
        """
        Simulates executing a command directly in the terminal without contacting Telegram servers.
        Perfect for automated testing, debugging, and offline verification.
        """
        parts = command_line.strip().split()
        if not parts:
            return {"status": "error", "message": "Empty command"}

        cmd = parts[0].lstrip("/").lower()
        args = parts[1:]

        if cmd in ("start", "help", "status", "reload"):
            return {
                "status": "success",
                "command": cmd,
                "active_cartridges": list(self.cartridges.keys())
            }

        if cmd == "idea":
            idea_text = " ".join(args)
            res = await self.autoforge.forge_cartridge(idea_prompt=idea_text)
            self.load_cartridges()
            return res

        cartridge = self.cartridges.get(cmd)
        if not cartridge:
            return {"status": "error", "message": f"Cartridge '{cmd}' not found"}

        payload = {}
        if cmd == "story":
            payload["name"] = args[0] if len(args) >= 1 else "Little Explorer"
            payload["age"] = int(args[1]) if len(args) >= 2 and args[1].isdigit() else 8
            payload["theme"] = args[2] if len(args) >= 3 else "Starlight Forest"
            payload["lesson"] = " ".join(args[3:]) if len(args) >= 4 else "patience"
        else:
            payload["name"] = args[0] if args else "Friend"
            payload["theme"] = " ".join(args[1:]) if len(args) > 1 else "courage"

        return await cartridge.generate(payload)

    def run_polling(self) -> None:
        """Starts the Telegram bot in polling mode."""
        app = self.build_application()
        logger.info(f"Starting OmniForge Telegram Bot with {len(self.cartridges)} cartridges...")
        app.run_polling(drop_pending_updates=True)
