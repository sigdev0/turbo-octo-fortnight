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
        self.user_profiles_file = DATA_DIR / "user_profiles.json"
        self.user_profiles: Dict[str, Dict[str, Any]] = self._load_user_profiles()
        self.cartridge_config_file = DATA_DIR / "cartridge_config.json"
        self.user_states: Dict[str, Dict[str, Any]] = {}
        self.load_cartridges()

    def get_cartridge_config(self) -> Dict[str, bool]:
        """Loads cartridge enabled states from data/cartridge_config.json."""
        if self.cartridge_config_file.exists():
            try:
                with open(self.cartridge_config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load cartridge config: {e}")
        return {}

    def is_cartridge_enabled(self, name_or_cmd: str) -> bool:
        """Checks if a cartridge is active based on data/cartridge_config.json."""
        config = self.get_cartridge_config()
        clean = name_or_cmd.lower().strip("/")
        if clean in config:
            return bool(config[clean])

        for cmd, instance in self.cartridges.items():
            if cmd == clean or instance.name.lower() == clean:
                if instance.name in config:
                    return bool(config[instance.name])
                if cmd in config:
                    return bool(config[cmd])
                break

        return True

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

    def _load_user_profiles(self) -> Dict[str, Dict[str, Any]]:
        if self.user_profiles_file.exists():
            try:
                with open(self.user_profiles_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load user profiles: {e}")
        return {}

    def _save_user_profiles(self) -> None:
        try:
            with open(self.user_profiles_file, "w", encoding="utf-8") as f:
                json.dump(self.user_profiles, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user profiles: {e}")

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        return self.user_profiles.get(str(user_id), {})

    def get_active_child(self, user_id: str) -> Optional[Dict[str, Any]]:
        prof = self.get_user_profile(user_id)
        story_data = prof.get("bedtime_story", {})
        children = story_data.get("children", [])
        if not children:
            return None
        active_id = story_data.get("active_child_id")
        for c in children:
            if c.get("id") == active_id:
                return c
        return children[0]

    def save_child_profile(
        self,
        user_id: str,
        name: str,
        age: int,
        gender: str = "girl",
        child_id: Optional[str] = None
    ) -> Dict[str, Any]:
        uid = str(user_id)
        if uid not in self.user_profiles:
            user_lang = self.user_languages.get(uid, "id")
            self.user_profiles[uid] = {
                "language": user_lang,
                "bedtime_story": {"children": []}
            }
        story_data = self.user_profiles[uid].setdefault("bedtime_story", {"children": []})
        children = story_data.setdefault("children", [])

        if not child_id:
            child_id = f"c_{len(children) + 1}"
            child = {
                "id": child_id,
                "name": name.strip().capitalize(),
                "age": int(age),
                "gender": gender.lower().strip()
            }
            children.append(child)
        else:
            child = next((c for c in children if c.get("id") == child_id), None)
            if child:
                child.update({
                    "name": name.strip().capitalize(),
                    "age": int(age),
                    "gender": gender.lower().strip()
                })
            else:
                child = {
                    "id": child_id,
                    "name": name.strip().capitalize(),
                    "age": int(age),
                    "gender": gender.lower().strip()
                }
                children.append(child)

        story_data["active_child_id"] = child_id
        self._save_user_profiles()
        return child

    def switch_active_child(self, user_id: str, child_id: str) -> bool:
        uid = str(user_id)
        if uid in self.user_profiles and "bedtime_story" in self.user_profiles[uid]:
            story_data = self.user_profiles[uid]["bedtime_story"]
            children = story_data.get("children", [])
            if any(c.get("id") == child_id for c in children):
                story_data["active_child_id"] = child_id
                self._save_user_profiles()
                return True
        return False

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
        story_label = "🌙 Cerita Tidur Anak" if lang == "id" else "🌙 Bedtime Story"
        morning_label = "☀️ Afirmasi Pagi" if lang == "id" else "☀️ Morning Boost"
        prof_label = "👤 Profil Anak" if lang == "id" else "👤 Child Profile"

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(story_label, callback_data="wiz_menu_story"),
                InlineKeyboardButton(morning_label, callback_data="wiz_menu_morning")
            ],
            [
                InlineKeyboardButton(prof_label, callback_data="wiz_menu_profile"),
                InlineKeyboardButton(toggle_label, callback_data=f"set_lang:{target_lang}")
            ],
            [
                InlineKeyboardButton("🌐 Mission Control Portal", callback_data="wiz_menu_portal")
            ]
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

    async def portal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_user_authorized(update):
            return
        user_lang = self.resolve_user_language(update)
        portal_url = os.getenv("PORTAL_URL", "http://100.68.13.81:8080")

        buttons = []
        if portal_url.startswith("https://"):
            from telegram import WebAppInfo
            buttons.append([InlineKeyboardButton("🌐 Buka Mission Control (Mini App)" if user_lang == "id" else "🌐 Open Mission Control (Mini App)", web_app=WebAppInfo(url=portal_url))])

        buttons.append([InlineKeyboardButton("🖥️ Buka Portal Web (Tailscale)" if user_lang == "id" else "🖥️ Open Web Portal (Tailscale)", url=portal_url)])
        kb = InlineKeyboardMarkup(buttons)

        msg = (
            "⚡ *Homelab Mission Control Portal*\n\n"
            "Pantau metrik server homelab, streaming log terminal secara langsung, dan kelola service 24/7:\n"
            f"🔗 `{portal_url}`"
            if user_lang == "id" else
            "⚡ *Homelab Mission Control Portal*\n\n"
            "Monitor homelab system metrics, stream live terminal logs, and manage 24/7 services:\n"
            f"🔗 `{portal_url}`"
        )
        await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")

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

    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_user_authorized(update):
            return
        user = update.effective_user
        uid = str(user.id) if user else "anon"
        user_lang = self.resolve_user_language(update)
        active_child = self.get_active_child(uid)
        prof = self.get_user_profile(uid)
        children = prof.get("bedtime_story", {}).get("children", [])

        if not children or not active_child:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Mulai Pengaturan Profil" if user_lang == "id" else "➕ Start Profile Setup", callback_data="prof_add")]
            ])
            await update.message.reply_text(t("profile_no_child", user_lang), reply_markup=kb, parse_mode="Markdown")
            return

        gender_label = "👧 Putri" if active_child.get("gender") in ("girl", "putri", "female") else "👦 Putra"
        if user_lang == "en":
            gender_label = "👧 Girl" if active_child.get("gender") in ("girl", "putri", "female") else "👦 Boy"

        msg = t(
            "profile_menu_title",
            user_lang,
            name=active_child["name"],
            age=active_child["age"],
            gender=gender_label,
            total=len(children)
        )
        kb = self._get_profile_keyboard(uid, user_lang)
        await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")

    async def start_story_wizard(
        self,
        update: Update,
        context: Optional[ContextTypes.DEFAULT_TYPE] = None,
        force_lang: Optional[str] = None
    ) -> None:
        user = update.effective_user
        uid = str(user.id) if user else "anon"
        user_lang = force_lang or self.resolve_user_language(update)
        active_child = self.get_active_child(uid)

        # 1st Attempt: No child profile saved -> trigger 1-time scoped onboarding
        if not active_child:
            self.user_states[uid] = {
                "state": "bedtime_story_onboarding",
                "step": "name",
                "lang": user_lang
            }
            prompt = t("onboarding_welcome", user_lang)
            if update.callback_query:
                await update.callback_query.edit_message_text(prompt, parse_mode="Markdown")
            elif update.message:
                await update.message.reply_text(prompt, parse_mode="Markdown")
            return

        # 2nd+ Attempt: Child profile exists -> Skip demographics! Jump straight to curiosity prompt!
        self.user_states[uid] = {
            "state": "bedtime_story_curiosity",
            "child_id": active_child["id"],
            "lang": user_lang
        }
        prompt = t("story_curiosity_prompt", user_lang, name=active_child["name"])
        kb = self._get_theme_keyboard(user_lang, active_child["name"], active_child["age"])
        if update.callback_query:
            await update.callback_query.edit_message_text(prompt, reply_markup=kb, parse_mode="Markdown")
        elif update.message:
            await update.message.reply_text(prompt, reply_markup=kb, parse_mode="Markdown")

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.message.text:
            return
        if not self._is_user_authorized(update):
            return

        text = update.message.text.strip()
        user = update.effective_user
        uid = str(user.id) if user else "anon"
        user_lang = self.resolve_user_language(update)
        state_info = self.user_states.get(uid, {})
        curr_state = state_info.get("state")

        # 1. Onboarding: Capturing Child Name
        if curr_state == "bedtime_story_onboarding" and state_info.get("step") == "name":
            child_name = text.split()[0].capitalize()
            self.user_states[uid]["name"] = child_name
            self.user_states[uid]["step"] = "age"
            prompt = t("onboarding_ask_age", user_lang, name=child_name)
            kb = self._get_onboarding_age_keyboard(user_lang)
            await update.message.reply_text(prompt, reply_markup=kb, parse_mode="Markdown")
            return

        # 2. Returning Parent Curiosity Mode / Direct Typed Input
        active_child = self.get_active_child(uid)
        if curr_state == "bedtime_story_curiosity" or (active_child and not text.startswith("/")):
            child_name = active_child["name"]
            child_age = active_child["age"]
            prompt_theme = text
            lesson = "kesabaran dan kebaikan" if user_lang == "id" else "patience and kindness"

            # Clear state
            self.user_states.pop(uid, None)

            status_msg = await update.message.reply_text(
                f"🌙 *Malam ini untuk {child_name}:* _{prompt_theme}_\n⏳ Merangkai dongeng tidur..."
                if user_lang == "id" else
                f"🌙 *Tonight's journey for {child_name}:* _{prompt_theme}_\n⏳ Weaving bedtime story...",
                parse_mode="Markdown"
            )
            payload = {
                "lang": user_lang,
                "name": child_name,
                "age": child_age,
                "theme": prompt_theme,
                "lesson": lesson
            }
            await self._execute_and_send_cartridge(
                target_message=update.message,
                cmd="story",
                payload=payload,
                status_msg=status_msg
            )
            return

        # 3. Default friendly hint if no state and no registered child
        await update.message.reply_text(t("text_hint_no_state", user_lang), parse_mode="Markdown")

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

    def _get_onboarding_age_keyboard(self, lang: str = "id") -> InlineKeyboardMarkup:
        label_yo = "thn" if lang == "id" else "yo"
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"🍼 1-2 {label_yo}", callback_data="onb_age:2"),
                InlineKeyboardButton(f"🧸 3 {label_yo}", callback_data="onb_age:3"),
                InlineKeyboardButton(f"🎈 4 {label_yo}", callback_data="onb_age:4")
            ],
            [
                InlineKeyboardButton(f"🎨 5 {label_yo}", callback_data="onb_age:5"),
                InlineKeyboardButton(f"🚀 6 {label_yo}", callback_data="onb_age:6"),
                InlineKeyboardButton(f"🌟 7 {label_yo}", callback_data="onb_age:7")
            ],
            [
                InlineKeyboardButton(f"📚 8+ {label_yo}", callback_data="onb_age:8")
            ]
        ])

    def _get_onboarding_gender_keyboard(self, lang: str = "id") -> InlineKeyboardMarkup:
        if lang == "id":
            return InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👧 Putri", callback_data="onb_gen:girl"),
                    InlineKeyboardButton("👦 Putra", callback_data="onb_gen:boy")
                ]
            ])
        else:
            return InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👧 Girl", callback_data="onb_gen:girl"),
                    InlineKeyboardButton("👦 Boy", callback_data="onb_gen:boy")
                ]
            ])

    def _get_profile_keyboard(self, user_id: str, lang: str = "id") -> InlineKeyboardMarkup:
        prof = self.get_user_profile(user_id)
        children = prof.get("bedtime_story", {}).get("children", [])
        active_id = prof.get("bedtime_story", {}).get("active_child_id")
        buttons = []
        for c in children:
            cid = c.get("id")
            name = c.get("name")
            age = c.get("age")
            is_active = (cid == active_id)
            label = f"{'⭐' if is_active else '👤'} {name} ({age} {'thn' if lang == 'id' else 'yo'})"
            buttons.append([InlineKeyboardButton(label, callback_data=f"prof_sw:{cid}")])

        add_label = "➕ Tambah Profil Anak" if lang == "id" else "➕ Add Sibling Profile"
        back_label = "🌙 Mulai Dongeng" if lang == "id" else "🌙 Start Story"
        buttons.append([InlineKeyboardButton(add_label, callback_data="prof_add")])
        buttons.append([InlineKeyboardButton(back_label, callback_data="wiz_menu_story")])
        return InlineKeyboardMarkup(buttons)

    def _get_child_keyboard(self, lang: str = "id", user_id: Optional[str] = None) -> InlineKeyboardMarkup:
        buttons = []
        if user_id:
            prof = self.get_user_profile(user_id)
            children = prof.get("bedtime_story", {}).get("children", [])
            for c in children:
                name = c.get("name")
                age = c.get("age")
                gender_icon = "👧" if c.get("gender") in ("girl", "putri", "female") else "👦"
                label = f"{gender_icon} {name} ({age} {'thn' if lang == 'id' else 'yo'})"
                buttons.append([InlineKeyboardButton(label, callback_data=f"wiz_child:{lang}:{name}:{age}")])

        if not buttons:
            if lang == "id":
                buttons = [
                    [
                        InlineKeyboardButton("👧 Maya (Usia 2 thn)", callback_data="wiz_child:id:Maya:2"),
                        InlineKeyboardButton("👦 Leo (Usia 8 thn)", callback_data="wiz_child:id:Leo:8")
                    ]
                ]
            else:
                buttons = [
                    [
                        InlineKeyboardButton("👧 Maya (Age 2)", callback_data="wiz_child:en:Maya:2"),
                        InlineKeyboardButton("👦 Leo (Age 8)", callback_data="wiz_child:en:Leo:8")
                    ]
                ]

        add_label = "➕ Atur Profil Baru" if lang == "id" else "➕ Setup New Child"
        custom_label = "✏️ Kustom (Ketik Sendiri)" if lang == "id" else "✏️ Custom (Type Command)"
        back_label = "🔙 Ganti Bahasa" if lang == "id" else "🔙 Change Language"
        buttons.append([InlineKeyboardButton(add_label, callback_data="prof_add")])
        buttons.append([InlineKeyboardButton(custom_label, callback_data=f"wiz_custom:{lang}")])
        buttons.append([InlineKeyboardButton(back_label, callback_data="wiz_back_lang")])
        return InlineKeyboardMarkup(buttons)

    def _get_theme_keyboard(self, lang: str, name: str, age: int) -> InlineKeyboardMarkup:
        back_label = "🔙 Kembali" if lang == "id" else "🔙 Back"
        prof_label = "👤 Profil Anak" if lang == "id" else "👤 Switch Child"
        if lang == "id":
            if age <= 3:
                buttons = [
                    [
                        InlineKeyboardButton("⛵ Perahu Pinisi Bintang", callback_data=f"wiz_gen:id:{name}:{age}:perahu pinisi:ketenangan"),
                        InlineKeyboardButton("🌿 Hutan Kalpataru", callback_data=f"wiz_gen:id:{name}:{age}:hutan kalpataru:kedamaian")
                    ],
                    [
                        InlineKeyboardButton("☁️ Negeri di Atas Awan", callback_data=f"wiz_gen:id:{name}:{age}:negeri awan:kelembutan"),
                        InlineKeyboardButton("🏮 Lentera Kunang-Kunang", callback_data=f"wiz_gen:id:{name}:{age}:lentera kunang:ketenteraman")
                    ],
                    [
                        InlineKeyboardButton("⭐ Bintang Kejora Lembut", callback_data=f"wiz_gen:id:{name}:{age}:bintang kejora:kasih sayang"),
                        InlineKeyboardButton("🏛️ Candi Borobudur Damai", callback_data=f"wiz_gen:id:{name}:{age}:candi borobudur:ketenangan")
                    ],
                    [
                        InlineKeyboardButton("🌊 Telaga Danau Toba", callback_data=f"wiz_gen:id:{name}:{age}:danau toba:kedamaian"),
                        InlineKeyboardButton("🐎 Sabana Bromo Berbisik", callback_data=f"wiz_gen:id:{name}:{age}:sabana bromo:kehangatan")
                    ],
                    [
                        InlineKeyboardButton("🚂 Kereta Uap Rimba", callback_data=f"wiz_gen:id:{name}:{age}:kereta rimba:rasa aman")
                    ],
                    [
                        InlineKeyboardButton(prof_label, callback_data="wiz_menu_profile"),
                        InlineKeyboardButton(back_label, callback_data=f"wiz_back_child:{lang}")
                    ]
                ]
            else:
                buttons = [
                    [
                        InlineKeyboardButton("⛵ Ekspedisi Pinisi Samudra", callback_data=f"wiz_gen:id:{name}:{age}:pinisi samudra:keberanian"),
                        InlineKeyboardButton("🌳 Pohon Kalpataru Ajaib", callback_data=f"wiz_gen:id:{name}:{age}:hutan kalpataru:kebijaksanaan")
                    ],
                    [
                        InlineKeyboardButton("☁️ Istana di Atas Awan", callback_data=f"wiz_gen:id:{name}:{age}:istana awan:kesabaran"),
                        InlineKeyboardButton("🏮 Lembah Kunang-Kunang", callback_data=f"wiz_gen:id:{name}:{age}:lembah kunang:kejujuran")
                    ],
                    [
                        InlineKeyboardButton("🌌 Menembus Bintang Kejora", callback_data=f"wiz_gen:id:{name}:{age}:bintang kejora:imajinasi"),
                        InlineKeyboardButton("🏛️ Misteri Relief Borobudur", callback_data=f"wiz_gen:id:{name}:{age}:candi borobudur:kebajikan")
                    ],
                    [
                        InlineKeyboardButton("🌊 Kaldera Danau Toba", callback_data=f"wiz_gen:id:{name}:{age}:danau toba:keteguhan"),
                        InlineKeyboardButton("🐎 Pasir Berbisik Bromo", callback_data=f"wiz_gen:id:{name}:{age}:sabana bromo:keberanian")
                    ],
                    [
                        InlineKeyboardButton("🚂 Kereta Rimba Nusantara", callback_data=f"wiz_gen:id:{name}:{age}:kereta rimba:kesabaran")
                    ],
                    [
                        InlineKeyboardButton(prof_label, callback_data="wiz_menu_profile"),
                        InlineKeyboardButton(back_label, callback_data=f"wiz_back_child:{lang}")
                    ]
                ]
        else:
            if age <= 3:
                buttons = [
                    [
                        InlineKeyboardButton("⛵ Starlight Pinisi Boat", callback_data=f"wiz_gen:en:{name}:{age}:pinisi boat:peacefulness"),
                        InlineKeyboardButton("🌿 Kalpataru Forest", callback_data=f"wiz_gen:en:{name}:{age}:kalpataru forest:kindness")
                    ],
                    [
                        InlineKeyboardButton("☁️ Sleepy Cloud Kingdom", callback_data=f"wiz_gen:en:{name}:{age}:cloud kingdom:gentleness"),
                        InlineKeyboardButton("🏮 Firefly Lantern River", callback_data=f"wiz_gen:en:{name}:{age}:firefly lantern:calmness")
                    ],
                    [
                        InlineKeyboardButton("⭐ Gentle Morning Star", callback_data=f"wiz_gen:en:{name}:{age}:morning star:comfort"),
                        InlineKeyboardButton("🏛️ Peaceful Borobudur", callback_data=f"wiz_gen:en:{name}:{age}:borobudur temple:peace")
                    ],
                    [
                        InlineKeyboardButton("🌊 Azure Lake Toba", callback_data=f"wiz_gen:en:{name}:{age}:lake toba:tranquility"),
                        InlineKeyboardButton("🐎 Whispering Bromo", callback_data=f"wiz_gen:en:{name}:{age}:bromo savanna:warmth")
                    ],
                    [
                        InlineKeyboardButton("🚂 Rainforest Steam Train", callback_data=f"wiz_gen:en:{name}:{age}:rainforest train:comfort")
                    ],
                    [
                        InlineKeyboardButton(prof_label, callback_data="wiz_menu_profile"),
                        InlineKeyboardButton(back_label, callback_data=f"wiz_back_child:{lang}")
                    ]
                ]
            else:
                buttons = [
                    [
                        InlineKeyboardButton("⛵ Starlight Pinisi Voyager", callback_data=f"wiz_gen:en:{name}:{age}:pinisi voyager:courage"),
                        InlineKeyboardButton("🌳 Sacred Kalpataru Woods", callback_data=f"wiz_gen:en:{name}:{age}:sacred forest:wisdom")
                    ],
                    [
                        InlineKeyboardButton("☁️ Realm Above the Clouds", callback_data=f"wiz_gen:en:{name}:{age}:cloud realm:wonder"),
                        InlineKeyboardButton("🏮 Glowing Firefly Valley", callback_data=f"wiz_gen:en:{name}:{age}:glowing fireflies:patience")
                    ],
                    [
                        InlineKeyboardButton("🌌 Journey to Morning Star", callback_data=f"wiz_gen:en:{name}:{age}:morning star:curiosity"),
                        InlineKeyboardButton("🏛️ Reliefs of Borobudur", callback_data=f"wiz_gen:en:{name}:{age}:borobudur temple:wisdom")
                    ],
                    [
                        InlineKeyboardButton("🌊 Caldera of Lake Toba", callback_data=f"wiz_gen:en:{name}:{age}:lake toba:peace"),
                        InlineKeyboardButton("🐎 Whispering Sands Bromo", callback_data=f"wiz_gen:en:{name}:{age}:bromo sands:courage")
                    ],
                    [
                        InlineKeyboardButton("🚂 Rainforest Express", callback_data=f"wiz_gen:en:{name}:{age}:rainforest express:patience")
                    ],
                    [
                        InlineKeyboardButton(prof_label, callback_data="wiz_menu_profile"),
                        InlineKeyboardButton(back_label, callback_data=f"wiz_back_child:{lang}")
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

        if not self.is_cartridge_enabled(cartridge.name):
            lang = self.resolve_user_language(update)
            msg = (
                f"⚠️ Cartridge *{cartridge.name}* (/{cmd}) sedang dinonaktifkan di OmniForge Mission Control."
                if lang == "id" else
                f"⚠️ Cartridge *{cartridge.name}* (/{cmd}) is currently disabled in OmniForge Mission Control."
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
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
                return await self.start_story_wizard(update, context, force_lang=wizard_lang)

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
            if prefix == "wiz_menu_main":
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
                story_label = "🌙 Cerita Tidur Anak" if lang == "id" else "🌙 Bedtime Story"
                morning_label = "☀️ Afirmasi Pagi" if lang == "id" else "☀️ Morning Boost"
                prof_label = "👤 Profil Anak" if lang == "id" else "👤 Child Profile"

                kb = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(story_label, callback_data="wiz_menu_story"),
                        InlineKeyboardButton(morning_label, callback_data="wiz_menu_morning")
                    ],
                    [
                        InlineKeyboardButton(prof_label, callback_data="wiz_menu_profile"),
                        InlineKeyboardButton(toggle_label, callback_data=f"set_lang:{target_lang}")
                    ],
                    [
                        InlineKeyboardButton("🌐 Mission Control Portal", callback_data="wiz_menu_portal")
                    ]
                ])
                await query.edit_message_text(msg, reply_markup=kb, parse_mode="Markdown")

            elif prefix == "wiz_menu_story":
                await self.start_story_wizard(update, context)

            elif prefix == "wiz_menu_morning":
                user_lang = self.resolve_user_language(update)
                await query.edit_message_text(
                    t("wiz_morning_prompt", user_lang),
                    reply_markup=self._get_morning_keyboard(),
                    parse_mode="Markdown"
                )

            elif prefix == "wiz_menu_portal":
                user_lang = self.resolve_user_language(update)
                portal_url = os.getenv("PORTAL_URL", "http://100.68.13.81:8080")
                buttons = []
                if portal_url.startswith("https://"):
                    from telegram import WebAppInfo
                    buttons.append([InlineKeyboardButton("🌐 Buka Mini App" if user_lang == "id" else "🌐 Open Mini App", web_app=WebAppInfo(url=portal_url))])
                buttons.append([InlineKeyboardButton("🖥️ Buka Portal Web" if user_lang == "id" else "🖥️ Open Web Portal", url=portal_url)])
                buttons.append([InlineKeyboardButton("🔙 Menu Utama" if user_lang == "id" else "🔙 Main Menu", callback_data="wiz_menu_main")])
                kb = InlineKeyboardMarkup(buttons)
                msg = (
                    "⚡ *Homelab Mission Control Portal*\n\n"
                    "Pantau metrik server homelab, streaming log terminal secara langsung, dan kelola service 24/7:\n"
                    f"🔗 `{portal_url}`"
                    if user_lang == "id" else
                    "⚡ *Homelab Mission Control Portal*\n\n"
                    "Monitor homelab system metrics, stream live terminal logs, and manage 24/7 services:\n"
                    f"🔗 `{portal_url}`"
                )
                await query.edit_message_text(msg, reply_markup=kb, parse_mode="Markdown")

            elif prefix == "wiz_menu_profile":
                user = update.effective_user
                uid = str(user.id) if user else "anon"
                user_lang = self.resolve_user_language(update)
                active_child = self.get_active_child(uid)
                prof = self.get_user_profile(uid)
                children = prof.get("bedtime_story", {}).get("children", [])
                if not children or not active_child:
                    kb = InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ Mulai Pengaturan Profil" if user_lang == "id" else "➕ Start Profile Setup", callback_data="prof_add")]
                    ])
                    await query.edit_message_text(t("profile_no_child", user_lang), reply_markup=kb, parse_mode="Markdown")
                else:
                    gender_label = "👧 Putri" if active_child.get("gender") in ("girl", "putri", "female") else "👦 Putra"
                    if user_lang == "en":
                        gender_label = "👧 Girl" if active_child.get("gender") in ("girl", "putri", "female") else "👦 Boy"
                    msg = t(
                        "profile_menu_title",
                        user_lang,
                        name=active_child["name"],
                        age=active_child["age"],
                        gender=gender_label,
                        total=len(children)
                    )
                    kb = self._get_profile_keyboard(uid, user_lang)
                    await query.edit_message_text(msg, reply_markup=kb, parse_mode="Markdown")

            elif prefix == "onb_age":
                age = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 4
                user = update.effective_user
                uid = str(user.id) if user else "anon"
                user_lang = self.resolve_user_language(update)
                self.user_states.setdefault(uid, {})
                self.user_states[uid]["age"] = age
                self.user_states[uid]["step"] = "gender"
                child_name = self.user_states[uid].get("name", "Little Explorer")
                prompt = t("onboarding_ask_gender", user_lang, name=child_name)
                kb = self._get_onboarding_gender_keyboard(user_lang)
                await query.edit_message_text(prompt, reply_markup=kb, parse_mode="Markdown")

            elif prefix == "onb_gen":
                gender = parts[1] if len(parts) > 1 else "girl"
                user = update.effective_user
                uid = str(user.id) if user else "anon"
                user_lang = self.resolve_user_language(update)
                st = self.user_states.get(uid, {})
                child_name = st.get("name", "Little Explorer")
                child_age = st.get("age", 4)
                child = self.save_child_profile(uid, child_name, child_age, gender)
                self.user_states[uid] = {
                    "state": "bedtime_story_curiosity",
                    "child_id": child["id"],
                    "lang": user_lang
                }
                gender_str = "Putri" if gender == "girl" else "Putra"
                if user_lang == "en":
                    gender_str = "Girl" if gender == "girl" else "Boy"
                conf_text = t("onboarding_success", user_lang, name=child_name, age=child_age, gender=gender_str)
                curiosity_text = t("story_curiosity_prompt", user_lang, name=child_name)
                kb = self._get_theme_keyboard(user_lang, child_name, child_age)
                await query.edit_message_text(f"{conf_text}\n\n{curiosity_text}", reply_markup=kb, parse_mode="Markdown")

            elif prefix == "prof_sw":
                cid = parts[1] if len(parts) > 1 else ""
                user = update.effective_user
                uid = str(user.id) if user else "anon"
                user_lang = self.resolve_user_language(update)
                self.switch_active_child(uid, cid)
                active_child = self.get_active_child(uid)
                if active_child:
                    self.user_states[uid] = {
                        "state": "bedtime_story_curiosity",
                        "child_id": active_child["id"],
                        "lang": user_lang
                    }
                    succ_msg = t("profile_switched", user_lang, name=active_child["name"], age=active_child["age"])
                    curiosity_prompt = t("story_curiosity_prompt", user_lang, name=active_child["name"])
                    kb = self._get_theme_keyboard(user_lang, active_child["name"], active_child["age"])
                    await query.edit_message_text(f"{succ_msg}\n\n{curiosity_prompt}", reply_markup=kb, parse_mode="Markdown")

            elif prefix == "prof_add":
                user = update.effective_user
                uid = str(user.id) if user else "anon"
                user_lang = self.resolve_user_language(update)
                self.user_states[uid] = {
                    "state": "bedtime_story_onboarding",
                    "step": "name",
                    "lang": user_lang
                }
                await query.edit_message_text(t("onboarding_welcome", user_lang), parse_mode="Markdown")

            elif prefix == "set_lang":
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
        self.app.add_handler(CommandHandler("portal", self.portal_command))
        self.app.add_handler(CommandHandler("control", self.portal_command))
        self.app.add_handler(CommandHandler("lang", self.lang_command))
        self.app.add_handler(CommandHandler("reload", self.reload_command))
        self.app.add_handler(CommandHandler("idea", self.idea_command))
        self.app.add_handler(CommandHandler("profile", self.profile_command))
        self.app.add_handler(CommandHandler("profil", self.profile_command))

        # Dynamic cartridge commands
        for cmd in self.cartridges.keys():
            self.app.add_handler(CommandHandler(cmd, self.handle_cartridge_command))

        # Indonesian Aliases
        for alias in ("cerita", "afirmasi", "pagi", "klip"):
            self.app.add_handler(CommandHandler(alias, self.handle_cartridge_command))
        self.app.add_handler(CommandHandler("ide", self.idea_command))

        # Interactive Callback Query Handler
        self.app.add_handler(CallbackQueryHandler(self.handle_callback_query))

        # Contextual Text Message Handler (Onboarding child name & Direct theme input)
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))

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

        if cmd in ("profile", "profil"):
            user_id = args[0] if args else "sim_user_1"
            active_child = self.get_active_child(user_id)
            prof = self.get_user_profile(user_id)
            return {
                "status": "success",
                "command": cmd,
                "user_id": user_id,
                "active_child": active_child,
                "children": prof.get("bedtime_story", {}).get("children", [])
            }

        if cmd == "idea":
            idea_text = " ".join(args)
            res = await self.autoforge.forge_cartridge(idea_prompt=idea_text)
            self.load_cartridges()
            return res

        cartridge = self.cartridges.get(cmd)
        if not cartridge:
            return {"status": "error", "message": f"Cartridge '{cmd}' not found"}

        if not self.is_cartridge_enabled(cartridge.name):
            return {
                "status": "error",
                "message": f"Cartridge '{cartridge.name}' (/{cmd}) is currently disabled in Mission Control."
            }

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


if __name__ == "__main__":
    bot = OmniForgeBot()
    bot.run_polling()
