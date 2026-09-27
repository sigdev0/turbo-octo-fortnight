import asyncio
import importlib
import importlib.util
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from core.config import (
    CARTRIDGES_DIR,
    OUTPUT_DIR,
    DATA_DIR,
    TELEGRAM_BOT_TOKEN,
    ALLOWED_TELEGRAM_USERS,
    DEFAULT_LANGUAGE
)
from cartridges.base import BaseCartridge
from core.autoforge import AutoForge
from core.i18n import t

logger = logging.getLogger(__name__)

class OmniForgeBot:
    def __init__(self, token: Optional[str] = None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.cartridges: Dict[str, BaseCartridge] = {}
        self.start_time = time.time()
        self.app: Optional[Application] = None
        self.autoforge = AutoForge()
        self.session_counter = 0
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_prefs_file = DATA_DIR / "user_preferences.json"
        self.user_languages: Dict[str, str] = self._load_user_preferences()
        self.load_cartridges()

    def _load_user_preferences(self) -> Dict[str, str]:
        if self.user_prefs_file.exists():
            try:
                with open(self.user_prefs_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load user preferences: {e}")
        return {}

    def _save_user_preferences(self) -> None:
        try:
            with open(self.user_prefs_file, "w", encoding="utf-8") as f:
                json.dump(self.user_languages, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user preferences: {e}")

    def resolve_user_language(self, update: Optional[Update] = None, explicit_lang: Optional[str] = None) -> str:
        """
        Determines user language using the resolution hierarchy:
        1. Explicit request flag ('id' or 'en')
        2. Saved user preference
        3. Telegram client language code (e.g. 'id' vs 'en')
        4. Config DEFAULT_LANGUAGE fallback
        """
        if explicit_lang:
            return "id" if explicit_lang.lower().strip() in ("id", "id-id", "indonesia", "indo") else "en"

        user = update.effective_user if update else None
        if user:
            uid = str(user.id)
            if uid in self.user_languages:
                return self.user_languages[uid]

            if user.language_code:
                code = user.language_code.lower()
                if code.startswith("id"):
                    return "id"
                return "en"

        return "id" if DEFAULT_LANGUAGE.lower() in ("id", "indonesia") else "en"

    def _set_user_language(self, user_id: str, lang: str) -> None:
        clean_lang = "id" if lang.lower().strip() in ("id", "id-id", "indonesia", "indo") else "en"
        self.user_languages[str(user_id)] = clean_lang
        self._save_user_preferences()

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

        lang = self.resolve_user_language(update)
        msg = (
            f"{t('start_title', lang)}\n\n"
            f"{t('start_subtitle', lang)}\n\n"
            f"{t('start_commands_header', lang)}\n"
            f"{t('start_cmd_story', lang)}\n"
            f"{t('start_cmd_morning', lang)}\n"
            f"{t('start_cmd_clip', lang)}\n"
            f"{t('start_cmd_idea', lang)}\n\n"
            f"{t('start_cmd_system', lang)}"
        )
        toggle_label = "🇬🇧 Switch to English" if lang == "id" else "🇮🇩 Ubah ke Bahasa Indonesia"
        target_lang = "en" if lang == "id" else "id"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(toggle_label, callback_data=f"set_lang:{target_lang}")]
        ])
        await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        lang = self.resolve_user_language(update)
        msg = (
            f"{t('help_title', lang)}\n\n"
            f"{t('help_story_section', lang)}\n\n"
            f"{t('help_morning_section', lang)}\n\n"
            f"{t('help_clip_section', lang)}\n\n"
            f"{t('help_idea_section', lang)}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def lang_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_user_authorized(update):
            return

        user = update.effective_user
        user_id = str(user.id) if user else "anon"

        args = list(context.args or [])
        if args:
            target = args[0].lower().strip()
            new_lang = "id" if target in ("id", "indonesia", "indo") else "en"
            self._set_user_language(user_id, new_lang)
            msg_key = "lang_switched_id" if new_lang == "id" else "lang_switched_en"
            await update.message.reply_text(t(msg_key, new_lang), parse_mode="Markdown")
            return

        curr_lang = self.resolve_user_language(update)
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇮🇩 Bahasa Indonesia" + (" (Aktif)" if curr_lang == "id" else ""), callback_data="set_lang:id"),
                InlineKeyboardButton("🇬🇧 Global English" + (" (Active)" if curr_lang == "en" else ""), callback_data="set_lang:en")
            ]
        ])
        await update.message.reply_text(t("lang_picker_prompt", curr_lang), reply_markup=kb, parse_mode="Markdown")

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

    def _store_session(self, data: Dict[str, Any]) -> str:
        """Stores a short-lived interaction session for callback queries."""
        self.session_counter += 1
        sess_id = f"s_{self.session_counter}"
        self.sessions[sess_id] = {**data, "_ts": time.time()}
        if len(self.sessions) > 200:
            oldest = sorted(self.sessions.keys(), key=lambda k: self.sessions[k].get("_ts", 0))[:50]
            for k in oldest:
                self.sessions.pop(k, None)
        return sess_id

    def _get_story_lang_keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data="wiz_lang:id"),
                InlineKeyboardButton("🇬🇧 English", callback_data="wiz_lang:en")
            ],
            [
                InlineKeyboardButton("💡 Panduan / Format Manual", callback_data="wiz_help")
            ]
        ])

    def _get_child_keyboard(self, lang: str = "id") -> InlineKeyboardMarkup:
        if lang == "id":
            return InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👧 Maya (Usia 2 thn)", callback_data="wiz_child:id:Maya:2"),
                    InlineKeyboardButton("👦 Leo (Usia 8 thn)", callback_data="wiz_child:id:Leo:8")
                ],
                [
                    InlineKeyboardButton("✏️ Kustom (Ketik Sendiri)", callback_data="wiz_custom:id")
                ],
                [
                    InlineKeyboardButton("🔙 Ganti Bahasa", callback_data="wiz_back_lang")
                ]
            ])
        else:
            return InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👧 Maya (Age 2)", callback_data="wiz_child:en:Maya:2"),
                    InlineKeyboardButton("👦 Leo (Age 8)", callback_data="wiz_child:en:Leo:8")
                ],
                [
                    InlineKeyboardButton("✏️ Custom (Type Command)", callback_data="wiz_custom:en")
                ],
                [
                    InlineKeyboardButton("🔙 Change Language", callback_data="wiz_back_lang")
                ]
            ])

    def _get_theme_keyboard(self, lang: str, name: str, age: int) -> InlineKeyboardMarkup:
        if lang == "id":
            if age <= 3:
                buttons = [
                    [
                        InlineKeyboardButton("☁️ Negeri Awan Lembut", callback_data=f"wiz_gen:id:{name}:{age}:awan lembut:kelembutan"),
                        InlineKeyboardButton("🐰 Hewan Hutan Tidur", callback_data=f"wiz_gen:id:{name}:{age}:hewan hutan tidur:kedamaian")
                    ],
                    [
                        InlineKeyboardButton("🌊 Bawah Laut Bintang", callback_data=f"wiz_gen:id:{name}:{age}:bawah laut bintang:ketenangan"),
                        InlineKeyboardButton("🎈 Balon Udara Bulan", callback_data=f"wiz_gen:id:{name}:{age}:balon udara bulan:kasih sayang")
                    ],
                    [
                        InlineKeyboardButton("🔙 Kembali", callback_data=f"wiz_back_child:{lang}")
                    ]
                ]
            else:
                buttons = [
                    [
                        InlineKeyboardButton("🚀 Penjelajah Antariksa", callback_data=f"wiz_gen:id:{name}:{age}:luar angkasa dan bintang:keberanian"),
                        InlineKeyboardButton("🦁 Hutan Kristal Ajaib", callback_data=f"wiz_gen:id:{name}:{age}:hutan kristal ajaib:kesabaran")
                    ],
                    [
                        InlineKeyboardButton("🏰 Kastil Bintang", callback_data=f"wiz_gen:id:{name}:{age}:misteri kastil bintang:kejujuran"),
                        InlineKeyboardButton("🦖 Sahabat Dinosaurus", callback_data=f"wiz_gen:id:{name}:{age}:sahabat dinosaurus:persahabatan")
                    ],
                    [
                        InlineKeyboardButton("🔙 Kembali", callback_data=f"wiz_back_child:{lang}")
                    ]
                ]
        else:
            if age <= 3:
                buttons = [
                    [
                        InlineKeyboardButton("☁️ Sleepy Clouds", callback_data=f"wiz_gen:en:{name}:{age}:sleepy clouds:gentleness"),
                        InlineKeyboardButton("🐰 Woodland Friends", callback_data=f"wiz_gen:en:{name}:{age}:woodland friends:peacefulness")
                    ],
                    [
                        InlineKeyboardButton("🌊 Ocean Stars", callback_data=f"wiz_gen:en:{name}:{age}:ocean stars:calmness"),
                        InlineKeyboardButton("🎈 Moonlit Balloon", callback_data=f"wiz_gen:en:{name}:{age}:moonlit balloon:love")
                    ],
                    [
                        InlineKeyboardButton("🔙 Back", callback_data=f"wiz_back_child:{lang}")
                    ]
                ]
            else:
                buttons = [
                    [
                        InlineKeyboardButton("🚀 Starlight Explorer", callback_data=f"wiz_gen:en:{name}:{age}:starlight explorer:courage"),
                        InlineKeyboardButton("🦁 Whispering Woods", callback_data=f"wiz_gen:en:{name}:{age}:whispering woods:patience")
                    ],
                    [
                        InlineKeyboardButton("🏰 Castle of Dreams", callback_data=f"wiz_gen:en:{name}:{age}:castle of dreams:kindness"),
                        InlineKeyboardButton("🦕 Gentle Dinosaur", callback_data=f"wiz_gen:en:{name}:{age}:gentle dinosaur:friendship")
                    ],
                    [
                        InlineKeyboardButton("🔙 Back", callback_data=f"wiz_back_child:{lang}")
                    ]
                ]
        return InlineKeyboardMarkup(buttons)

    def _get_morning_keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👧 Maya (Bahasa Indonesia)", callback_data="wiz_morn:id:Maya:keberanian dan kebaikan"),
                InlineKeyboardButton("👦 Leo (Bahasa Indonesia)", callback_data="wiz_morn:id:Leo:fokus dan semangat belajar")
            ],
            [
                InlineKeyboardButton("🇮🇩 Semangat Pagi (Umum)", callback_data="wiz_morn:id:Sahabat:semangat dan rasa syukur"),
                InlineKeyboardButton("🇬🇧 Daily Boost (English)", callback_data="wiz_morn:en:Friend:courage and strength")
            ]
        ])

    async def _execute_and_send_cartridge(
        self,
        target_message,
        cmd: str,
        payload: Dict[str, Any],
        status_msg=None
    ) -> None:
        """
        Executes a cartridge with live progress reporting and sends resulting media back to chat.
        """
        cartridge = self.cartridges.get(cmd)
        if not cartridge:
            error_text = f"❌ Unknown cartridge `/{cmd}`."
            if status_msg:
                await status_msg.edit_text(error_text)
            else:
                await target_message.reply_text(error_text)
            return

        lang = payload.get("lang", "en")
        prep_text = f"⚡ *Menyiapkan aset `/{cmd}`...*" if lang == "id" else f"⚡ *Preparing `/{cmd}` asset...*"
        if not status_msg:
            status_msg = await target_message.reply_text(prep_text, parse_mode="Markdown")
        else:
            await status_msg.edit_text(prep_text, parse_mode="Markdown")

        async def on_progress(step_msg: str):
            try:
                proc_hdr = f"⚙️ *Proses `/{cmd}`:*" if lang == "id" else f"⚙️ *Processing `/{cmd}`:*"
                await status_msg.edit_text(f"{proc_hdr}\n{step_msg}", parse_mode="Markdown")
            except Exception:
                pass

        payload["on_progress"] = on_progress

        try:
            result = await cartridge.generate(payload)
            if result.get("status") != "success":
                err = result.get('message', result.get('error', 'Unknown error'))
                await status_msg.edit_text(f"❌ Error: {err}")
                return

            output_file = result.get("output_file")
            output_files = result.get("output_files", [output_file] if output_file else [])
            title = result.get("title", f"Generated {cmd.title()}")

            upload_text = (
                f"✨ *Rendering Selesai:* {title}\nMengirim media ke chat Anda..."
                if lang == "id" else
                f"✨ *Rendering Complete:* {title}\nUploading media to your chat..."
            )
            await status_msg.edit_text(upload_text, parse_mode="Markdown")

            for file_path in output_files:
                p = Path(file_path)
                if not p.exists():
                    continue

                suffix = p.suffix.lower()
                if suffix in (".mp4", ".mov", ".mkv"):
                    await target_message.reply_video(
                        video=open(p, "rb"),
                        caption=f"🎬 *{title}* ({p.name})",
                        parse_mode="Markdown"
                    )
                elif suffix in (".mp3", ".wav", ".m4a"):
                    script_snippet = result.get('script', '')[:200]
                    caption = f"🎧 *{title}*"
                    if script_snippet:
                        caption += f"\n\n_{script_snippet}..._"
                    await target_message.reply_audio(
                        audio=open(p, "rb"),
                        title=title,
                        performer="OmniForge Audio",
                        caption=caption,
                        parse_mode="Markdown"
                    )
                else:
                    await target_message.reply_document(
                        document=open(p, "rb"),
                        caption=f"📄 *{title}* ({p.name})"
                    )

            try:
                await status_msg.delete()
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Error executing cartridge `/{cmd}`: {e}", exc_info=True)
            await status_msg.edit_text(f"❌ Gagal memproses `/{cmd}`: {str(e)}")

    async def handle_cartridge_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Generic handler for all registered cartridges (e.g. /story, /cerita, /morning, /afirmasi, /clip).
        """
        if not self._is_user_authorized(update):
            return

        raw_cmd = update.message.text.split()[0].lstrip("/").lower()
        cmd = raw_cmd
        payload: Dict[str, Any] = {}
        explicit_lang = False

        # Indonesian Aliases
        if cmd == "cerita":
            cmd = "story"
            payload["lang"] = "id"
            explicit_lang = True
        elif cmd in ("afirmasi", "pagi"):
            cmd = "morning"
            payload["lang"] = "id"
            explicit_lang = True
        elif cmd == "klip":
            cmd = "clip"
        elif cmd == "ide":
            return await self.idea_command(update, context)

        cartridge = self.cartridges.get(cmd)
        if not cartridge:
            await update.message.reply_text(f"Unknown command `/{raw_cmd}`. Use `/start` to see available commands.")
            return

        # Parse args
        args = list(context.args or [])
        if "id" in [a.lower() for a in args]:
            payload["lang"] = "id"
            explicit_lang = True
            args = [a for a in args if a.lower() != "id"]
        elif "en" in [a.lower() for a in args]:
            payload["lang"] = "en"
            explicit_lang = True
            args = [a for a in args if a.lower() != "en"]

        if cmd == "story":
            user_lang = self.resolve_user_language(update)
            # Flow 1: If no args given -> launch interactive wizard in user's language!
            if not args:
                wizard_lang = "id" if raw_cmd == "cerita" else user_lang
                prompt_text = t("wiz_child_prompt", wizard_lang)
                await update.message.reply_text(
                    prompt_text,
                    reply_markup=self._get_child_keyboard(wizard_lang),
                    parse_mode="Markdown"
                )
                return

            # Args given: parse them
            if len(args) >= 1:
                payload["name"] = args[0]
            if len(args) >= 2:
                try:
                    payload["age"] = int(args[1])
                except ValueError:
                    payload["age"] = 8
            else:
                payload["age"] = 8

            if len(args) >= 3:
                payload["theme"] = args[2]
            else:
                payload["theme"] = "petualangan bintang" if (explicit_lang and payload.get("lang") == "id") else "starlight adventure"

            if len(args) >= 4:
                payload["lesson"] = " ".join(args[3:])
            else:
                payload["lesson"] = "kesabaran dan kebaikan" if (explicit_lang and payload.get("lang") == "id") else "patience and kindness"

            # If language was NOT explicitly set via /cerita or 'id'/'en' flags:
            if not explicit_lang:
                user_id = str(update.effective_user.id) if update.effective_user else ""
                if user_id in self.user_languages:
                    payload["lang"] = self.user_languages[user_id]
                else:
                    sess_id = self._store_session({"cmd": "story", "payload": payload})
                    prompt_msg = t(
                        "story_lang_prompt",
                        user_lang,
                        name=payload['name'],
                        age=payload['age'],
                        theme=payload['theme'],
                        lesson=payload['lesson']
                    )
                    await update.message.reply_text(
                        prompt_msg,
                        reply_markup=InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data=f"pick_lang:{sess_id}:id"),
                                InlineKeyboardButton("🇬🇧 Global English", callback_data=f"pick_lang:{sess_id}:en")
                            ]
                        ]),
                        parse_mode="Markdown"
                    )
                    return

        elif cmd == "morning":
            user_lang = self.resolve_user_language(update)
            if not args:
                await update.message.reply_text(
                    t("wiz_morning_prompt", user_lang),
                    reply_markup=self._get_morning_keyboard(),
                    parse_mode="Markdown"
                )
                return

            payload["name"] = args[0]
            if len(args) > 1:
                payload["theme"] = " ".join(args[1:])

            if not explicit_lang:
                user_id = str(update.effective_user.id) if update.effective_user else ""
                if user_id in self.user_languages:
                    payload["lang"] = self.user_languages[user_id]
                else:
                    sess_id = self._store_session({"cmd": "morning", "payload": payload})
                    await update.message.reply_text(
                        t("morning_lang_prompt", user_lang, name=payload['name'], theme=payload.get('theme', 'courage')),
                        reply_markup=InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data=f"pick_lang:{sess_id}:id"),
                                InlineKeyboardButton("🇬🇧 Global English", callback_data=f"pick_lang:{sess_id}:en")
                            ]
                        ]),
                        parse_mode="Markdown"
                    )
                    return

        elif cmd == "clip":
            if not args:
                await update.message.reply_text(
                    "🎬 *How to use /clip:*\n"
                    "`/clip <YouTube_URL> [style] [max_clips]`\n\n"
                    "Examples:\n"
                    "• `/clip https://youtu.be/LlhTEttKcwQ`\n"
                    "• `/clip https://youtu.be/... hormozi 3`",
                    parse_mode="Markdown"
                )
                return
            payload["url"] = args[0]
            if len(args) >= 2:
                payload["style"] = args[1]
            if len(args) >= 3 and args[2].isdigit():
                payload["max_clips"] = int(args[2])
        else:
            if args:
                payload["name"] = args[0]
                if len(args) > 1:
                    payload["theme"] = " ".join(args[1:])

        # Execute
        await self._execute_and_send_cartridge(update.message, cmd, payload)

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles interactive inline keyboard button clicks for wizards and language selection.
        """
        query = update.callback_query
        if not query:
            return

        if not self._is_user_authorized(update):
            await query.answer("⛔ Access restricted.")
            return

        await query.answer()
        data = query.data or ""
        parts = data.split(":")
        prefix = parts[0]

        try:
            if prefix == "set_lang":
                new_lang = parts[1] if len(parts) > 1 else "id"
                user = update.effective_user
                if user:
                    self._set_user_language(str(user.id), new_lang)
                msg_key = "lang_switched_id" if new_lang == "id" else "lang_switched_en"
                await query.edit_message_text(t(msg_key, new_lang), parse_mode="Markdown")

            elif prefix == "wiz_lang":
                lang = parts[1] if len(parts) > 1 else "id"
                user = update.effective_user
                if user:
                    self._set_user_language(str(user.id), lang)
                prompt_text = t("wiz_child_prompt", lang)
                await query.edit_message_text(
                    prompt_text,
                    reply_markup=self._get_child_keyboard(lang),
                    parse_mode="Markdown"
                )

            elif prefix == "wiz_back_lang":
                await query.edit_message_text(
                    "🌙 *OmniForge Bedtime Story Studio* 🌙\n\n"
                    "Choose story language / Pilih bahasa cerita:",
                    reply_markup=self._get_story_lang_keyboard(),
                    parse_mode="Markdown"
                )

            elif prefix == "wiz_child":
                # wiz_child:<lang>:<name>:<age>
                lang = parts[1] if len(parts) > 1 else "id"
                name = parts[2] if len(parts) > 2 else "Maya"
                age = int(parts[3]) if len(parts) > 3 else 2

                if lang == "id":
                    voice_note = "Gadis Neural (Lembut & Menenangkan 🌸)" if age <= 3 else "Ardi Neural (Bijaksana & Menenangkan 🦉)"
                else:
                    voice_note = "Gentle Female Lullaby 🌸" if age <= 3 else "British Storyteller 🦉"

                prompt_text = t("wiz_theme_prompt", lang, name=name, age=age, voice=voice_note)
                await query.edit_message_text(
                    prompt_text,
                    reply_markup=self._get_theme_keyboard(lang, name, age),
                    parse_mode="Markdown"
                )

            elif prefix == "wiz_back_child":
                lang = parts[1] if len(parts) > 1 else "id"
                prompt_text = t("wiz_child_prompt", lang)
                await query.edit_message_text(
                    prompt_text,
                    reply_markup=self._get_child_keyboard(lang),
                    parse_mode="Markdown"
                )

            elif prefix == "wiz_custom":
                lang = parts[1] if len(parts) > 1 else "id"
                await query.edit_message_text(t("wiz_custom_prompt", lang), parse_mode="Markdown")

            elif prefix == "wiz_help":
                curr_lang = self.resolve_user_language(update)
                await query.edit_message_text(t("wiz_help_prompt", curr_lang), parse_mode="Markdown")

            elif prefix == "wiz_gen":
                # wiz_gen:<lang>:<name>:<age>:<theme>:<lesson>
                lang = parts[1]
                name = parts[2]
                age = int(parts[3])
                theme = parts[4]
                lesson = parts[5] if len(parts) > 5 else "kebaikan"

                payload = {
                    "lang": lang,
                    "name": name,
                    "age": age,
                    "theme": theme,
                    "lesson": lesson
                }
                await self._execute_and_send_cartridge(
                    target_message=query.message,
                    cmd="story",
                    payload=payload,
                    status_msg=query.message
                )

            elif prefix == "pick_lang":
                # pick_lang:<sess_id>:<lang>
                sess_id = parts[1]
                lang = parts[2]
                sess = self.sessions.get(sess_id)
                if not sess:
                    await query.edit_message_text("⌛ Sesi telah berakhir. Silakan ulangi perintah Anda.")
                    return

                cmd = sess["cmd"]
                payload = dict(sess["payload"])
                payload["lang"] = lang

                await self._execute_and_send_cartridge(
                    target_message=query.message,
                    cmd=cmd,
                    payload=payload,
                    status_msg=query.message
                )

            elif prefix == "wiz_morn":
                # wiz_morn:<lang>:<name>:<theme>
                lang = parts[1]
                name = parts[2]
                theme = parts[3]
                payload = {
                    "lang": lang,
                    "name": name,
                    "theme": theme
                }
                await self._execute_and_send_cartridge(
                    target_message=query.message,
                    cmd="morning",
                    payload=payload,
                    status_msg=query.message
                )

        except Exception as e:
            logger.error(f"Error in handle_callback_query: {e}", exc_info=True)
            try:
                await query.edit_message_text(f"❌ Terjadi kesalahan interaksi: {str(e)}")
            except Exception:
                pass

    def build_application(self) -> Application:
        """Configures and returns the python-telegram-bot Application."""
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured in .env or config.py")

        self.app = Application.builder().token(self.token).build()

        # Core handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("lang", self.lang_command))
        self.app.add_handler(CommandHandler("reload", self.reload_command))
        self.app.add_handler(CommandHandler("idea", self.idea_command))

        # Dynamic cartridge commands
        for cmd in self.cartridges.keys():
            self.app.add_handler(CommandHandler(cmd, self.handle_cartridge_command))

        # Indonesian Aliases
        for alias in ("cerita", "afirmasi", "pagi", "klip"):
            self.app.add_handler(CommandHandler(alias, self.handle_cartridge_command))
        self.app.add_handler(CommandHandler("ide", self.idea_command))

        # Interactive Callback Query Handler
        self.app.add_handler(CallbackQueryHandler(self.handle_callback_query))

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
        payload: Dict[str, Any] = {}

        # Indonesian Aliases
        if cmd == "cerita":
            cmd = "story"
            payload["lang"] = "id"
        elif cmd in ("afirmasi", "pagi"):
            cmd = "morning"
            payload["lang"] = "id"
        elif cmd == "klip":
            cmd = "clip"

        if "id" in [a.lower() for a in args]:
            payload["lang"] = "id"
            args = [a for a in args if a.lower() != "id"]
        elif "en" in [a.lower() for a in args]:
            payload["lang"] = "en"
            args = [a for a in args if a.lower() != "en"]

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

        if cmd == "story":
            payload["name"] = args[0] if len(args) >= 1 else "Little Explorer"
            payload["age"] = int(args[1]) if len(args) >= 2 and args[1].isdigit() else 8
            payload["theme"] = args[2] if len(args) >= 3 else "Starlight Forest"
            payload["lesson"] = " ".join(args[3:]) if len(args) >= 4 else "patience"
        elif cmd == "clip":
            payload["url"] = args[0] if args else ""
            if len(args) >= 2:
                payload["style"] = args[1]
            if len(args) >= 3 and args[2].isdigit():
                payload["max_clips"] = int(args[2])
        else:
            payload["name"] = args[0] if args else "Friend"
            payload["theme"] = " ".join(args[1:]) if len(args) > 1 else "courage"

        return await cartridge.generate(payload)

    def run_polling(self) -> None:
        """Starts the Telegram bot in polling mode."""
        app = self.build_application()
        logger.info(f"Starting OmniForge Telegram Bot with {len(self.cartridges)} cartridges...")
        app.run_polling(drop_pending_updates=True)
