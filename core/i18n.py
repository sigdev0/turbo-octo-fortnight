"""
Internationalization (i18n) Module for OmniForge Engine.
Provides native, culturally resonant strings for Bahasa Indonesia and Global English markets.
"""

from typing import Dict, Any, Optional

MESSAGES: Dict[str, Dict[str, str]] = {
    # /start
    "start_title": {
        "en": "🌟 *Welcome to OmniForge Engine* 🌟",
        "id": "🌟 *Selamat Datang di OmniForge Engine* 🌟"
    },
    "start_subtitle": {
        "en": "Your personal autonomous AI asset creator and personalized audio studio.",
        "id": "Asisten pembuat aset otomatis dan audio personal anak Anda siap digunakan!"
    },
    "start_commands_header": {
        "en": "📦 *Available Commands:*",
        "id": "📦 *Pilihan Perintah:*"
    },
    "start_cmd_story": {
        "en": "• `/story` — *Interactive Bedtime Story Studio* (One-tap adventure for kids!)\n"
              "  Example: `/story Leo 8 space courage`\n"
              "  Example: `/story Maya 2 clouds gentleness`",
        "id": "• `/cerita` atau `/story` — *Studio Cerita Pengantar Tidur* (1 Sentuhan!)\n"
              "  Contoh: `/cerita Maya 2 awan kelembutan`\n"
              "  Contoh: `/cerita Leo 8 bintang kesabaran`"
    },
    "start_cmd_morning": {
        "en": "• `/morning` — *Daily Uplifting Affirmations* for children and adults",
        "id": "• `/afirmasi` atau `/morning` — *Afirmasi Pagi Ceria* untuk anak & dewasa"
    },
    "start_cmd_clip": {
        "en": "• `/clip <YouTube_URL>` — *Autonomous 9:16 Viral Shorts Generator*",
        "id": "• `/klip <YouTube_URL>` (atau `/clip`) — *Pembuat Video Shorts 9:16 Otomatis*"
    },
    "start_cmd_idea": {
        "en": "• `/idea <new feature idea>` — AutoForge writes code, tests, and deploys live!",
        "id": "• `/idea` atau `/ide <ide baru>` — AutoForge buat kode, uji, dan aktifkan langsung!"
    },
    "start_cmd_system": {
        "en": "⚙️ *System:* `/status` | `/lang` | `/help`",
        "id": "⚙️ *Sistem:* `/status` | `/lang` | `/help`"
    },

    # /help
    "help_title": {
        "en": "📖 *OmniForge Command Guide*",
        "id": "📖 *Panduan Perintah OmniForge*"
    },
    "help_story_section": {
        "en": "🌙 *Bedtime Audio Stories (Screen-Free):*\n"
              "• `/story` — Tap without arguments to open the quick mobile wizard\n"
              "• Manual format: `/story <Name> <Age> <Theme> <Lesson>`\n"
              "  🎙️ Toddlers (≤3 yrs): *Gentle Female Lullaby*\n"
              "  🎙️ Kids (≥4 yrs): *Warm British Storyteller*",
        "id": "🌙 *Cerita Pengantar Tidur (Screen-Free):*\n"
              "• `/cerita` atau `/story` — Kirim tanpa argumen untuk menu tombol interaktif\n"
              "• Format manual: `/cerita <Nama> <Usia> <Tema> <Pelajaran>`\n"
              "  🎙️ Balita (≤3 thn): *Gadis Neural* (Lembut & menenangkan)\n"
              "  🎙️ Anak (≥4 thn): *Ardi Neural* (Bijaksana & ramah)"
    },
    "help_morning_section": {
        "en": "☀️ *Morning Affirmations:*\n"
              "• `/morning` — Quick boosts for courage, focus, and joy",
        "id": "☀️ *Afirmasi Pagi:*\n"
              "• `/afirmasi` atau `/morning` — Semangat pagi untuk keberanian dan fokus"
    },
    "help_clip_section": {
        "en": "🎬 *Podcast Video Clipper:*\n"
              "• `/clip <YouTube_URL> [style] [max_clips]` — Generates vertical clips with subtitles",
        "id": "🎬 *Video Podcast Clipper:*\n"
              "• `/klip <YouTube_URL>` atau `/clip <URL>` — Buat video shorts vertikal dengan subtitle"
    },
    "help_idea_section": {
        "en": "💡 *Autonomous AutoForge:*\n"
              "• `/idea <describe feature or tool>` — Synthesizes and tests new bot cartridges",
        "id": "💡 *Autonomous AutoForge:*\n"
              "• `/ide <deskripsi fitur atau aset>` — Sintesis dan uji modul bot baru otomatis"
    },

    # /lang
    "lang_picker_prompt": {
        "en": "🌐 *Choose Your Preferred Interface Language:*",
        "id": "🌐 *Pilih Bahasa Tampilan yang Anda Inginkan:*"
    },
    "lang_switched_en": {
        "en": "🇬🇧 Language set to **Global English**. All menus, narrations, and guides will now default to English.",
        "id": "🇬🇧 Bahasa diatur ke **Global English**. Semua menu, narasi, dan panduan akan menggunakan Bahasa Inggris."
    },
    "lang_switched_id": {
        "en": "🇮🇩 Bahasa berhasil diubah ke **Bahasa Indonesia**. Semua menu, narasi dongeng, dan panduan kini menggunakan Bahasa Indonesia.",
        "id": "🇮🇩 Bahasa berhasil diubah ke **Bahasa Indonesia**. Semua menu, narasi dongeng, dan panduan kini menggunakan Bahasa Indonesia."
    },

    # Live Progress Messages
    "progress_composing": {
        "en": "📖 Composing personalized bedtime adventure...",
        "id": "📖 Merangkai cerita pengantar tidur yang menenangkan..."
    },
    "progress_synthesizing": {
        "en": "🎙️ Synthesizing soothing neural voiceover ({voice})...",
        "id": "🎙️ Merekam suara narator yang menenangkan ({voice})..."
    },
    "progress_mixing": {
        "en": "🎵 Mixing harmonic ambient sleep soundtrack & audio ducking...",
        "id": "🎵 Menggabungkan musik tidur ambient & audio ducking..."
    },
    "progress_uploading": {
        "en": "✨ Rendering complete: *{title}*\nUploading audio to your chat...",
        "id": "✨ Rendering selesai: *{title}*\nMengirim audio ke chat Anda..."
    },
    "progress_done": {
        "en": "🎉 Bedtime adventure ready! Have sweet dreams. 🌙",
        "id": "🎉 Cerita selesai dibuat! Selamat tidur dan bermimpi indah. 🌙"
    },

    # Wizard Prompts
    "wiz_child_prompt": {
        "en": "👶 *Who is listening to the story tonight?*",
        "id": "👶 *Siapa yang akan mendengarkan cerita malam ini?*"
    },
    "wiz_theme_prompt": {
        "en": "🎨 *Choose Bedtime Adventure for {name} (Age {age}):*\n🎙️ Voice: {voice}",
        "id": "🎨 *Pilih Tema Cerita Pengantar Tidur untuk {name} ({age} thn):*\n🎙️ Suara: {voice}"
    },
    "wiz_custom_prompt": {
        "en": "✏️ *Custom Story Command Format:*\n\n"
              "Type in chat:\n"
              "`/story <Name> <Age> <Theme> <Lesson>`\n\n"
              "Example:\n"
              "• `/story Leo 8 galaxy courage`\n"
              "• `/story Maya 2 clouds gentleness`",
        "id": "✏️ *Format Perintah Cerita Manual:*\n\n"
              "Ketik langsung di chat dengan format:\n"
              "`/cerita <Nama> <Usia> <Tema> <Pelajaran>`\n\n"
              "Contoh:\n"
              "• `/cerita Maya 2 awan kelembutan`\n"
              "• `/cerita Leo 8 luar angkasa keberanian`"
    },
    "wiz_help_prompt": {
        "en": "💡 *OmniForge Quick Tips:*\n\n"
              "• Tap the interactive buttons to create custom stories in 3 taps.\n"
              "• Or type full commands anytime: `/story Leo 8 space`\n"
              "• Use `/lang` to switch between English and Bahasa Indonesia.",
        "id": "💡 *Panduan Cepat OmniForge:*\n\n"
              "• Tekan tombol wizard di menu ini untuk membuat cerita instan dalam 3 sentuhan.\n"
              "• Atau ketik perintah lengkap kapan saja: `/cerita Maya 2 awan`\n"
              "• Gunakan `/lang` untuk beralih antara Bahasa Indonesia dan English."
    },
    "wiz_morning_prompt": {
        "en": "☀️ *OmniForge Morning Affirmation Studio* ☀️\n\nSelect morning affirmation preset:",
        "id": "☀️ *OmniForge Morning Affirmation Studio* ☀️\n\nPilih profil afirmasi pagi:"
    },
    "story_lang_prompt": {
        "en": "🌐 *Choose Language for {name}'s Story:*\n• Age: {age} yrs\n• Theme: {theme}\n• Lesson: {lesson}",
        "id": "🌐 *Pilih Bahasa untuk Cerita {name}:*\n• Usia: {age} tahun\n• Tema: {theme}\n• Pelajaran: {lesson}"
    },
    "morning_lang_prompt": {
        "en": "🌐 *Choose Language for {name}'s Affirmation:*\n• Theme: {theme}",
        "id": "🌐 *Pilih Bahasa Afirmasi {name}:*\n• Tema: {theme}"
    }
}

def t(key: str, lang: str = "en", **kwargs: Any) -> str:
    """
    Translates a key into the specified language ('en' or 'id').
    Falls back to English if the key or language is not found.
    Interpolates any keyword arguments provided.
    """
    clean_lang = "id" if lang and lang.lower().strip() in ("id", "id-id", "indonesia", "indo") else "en"
    entry = MESSAGES.get(key, {})
    template = entry.get(clean_lang) or entry.get("en", key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template
