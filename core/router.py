import os
import json
import logging
import re
from typing import List, Dict, Any, Optional
import httpx
from core.config import ROUTER_API_BASE, ROUTER_API_KEY, ROUTER_MODEL

logger = logging.getLogger(__name__)

class LLMRouter:
    def __init__(
        self,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None
    ):
        self.api_base = (api_base or ROUTER_API_BASE).rstrip("/")
        self.api_key = api_key or ROUTER_API_KEY
        self.default_model = default_model or ROUTER_MODEL

    @property
    def is_configured(self) -> bool:
        """Returns True if an API key or base is provided."""
        return bool(self.api_key)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2500,
        json_mode: bool = False
    ) -> str:
        """
        Sends a chat completion request to the OpenAI-compatible router endpoint.
        """
        if not self.is_configured:
            logger.warning("ROUTER_API_KEY is not configured; using fallback generator.")
            return self._fallback_chat(messages)

        target_model = model or self.default_model
        endpoint = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(endpoint, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generates clean Python code from an LLM prompt and strips markdown fences.
        """
        sys_prompt = system_prompt or (
            "You are an expert autonomous Python architect for the OmniForge engine. "
            "Write production-grade, bug-free, self-contained Python code implementing BaseCartridge. "
            "Return ONLY executable Python code within ```python ... ``` blocks, with no markdown or explanations outside."
        )
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ]

        if not self.is_configured:
            return self._fallback_code_scaffold(prompt)

        raw_response = await self.chat(messages=messages, temperature=0.2)
        return self.extract_code(raw_response)

    def extract_code(self, text: str) -> str:
        """Extracts python code from markdown backticks or returns text as-is."""
        match = re.search(r"```(?:python)?\s*\n(.*?)\n```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    def _fallback_chat(self, messages: List[Dict[str, str]]) -> str:
        """Fallback responses when no live API key is set."""
        last_msg = messages[-1]["content"].lower()
        if "story" in last_msg or "bedtime" in last_msg:
            return (
                "Once upon a time, beneath a canopy of shimmering twilight stars, "
                "a brave young explorer embarked on a peaceful journey where courage and kindness "
                "lit the way into a realm of sweet, gentle dreams."
            )
        return "Acknowledged by OmniForge local fallback brain."

    def _fallback_code_scaffold(self, prompt: str) -> str:
        """
        Intelligent local fallback generator that creates a working BaseCartridge
        even when offline or without an active API key.
        """
        slug = "morning_affirmation" if "affirmation" in prompt.lower() else "custom_audio"
        class_name = "".join(part.capitalize() for part in slug.split("_")) + "Cartridge"
        clean_desc = prompt.replace("\n", " ").replace('"', "'")[:80]
        
        return f'''import asyncio
from pathlib import Path
from typing import Dict, Any
from cartridges.base import BaseCartridge
from core.config import OUTPUT_DIR
from core.voice import VoiceSynthesizer
from core.media import MediaMixer

class {class_name}(BaseCartridge):
    @property
    def name(self) -> str:
        return "{slug}"

    @property
    def command(self) -> str:
        return "{slug.split('_')[0]}"

    @property
    def description(self) -> str:
        return "Autonomous cartridge generated for: {clean_desc}"

    async def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        target_name = payload.get("name", "Friend").capitalize()
        theme = payload.get("theme", "courage and strength")
        voice_profile = payload.get("voice_profile", "energetic_affirmation")

        # Craft message script
        script_text = (
            f"Good morning, {{target_name}}! Today is a brand new day full of opportunity. "
            f"Remember that your courage is bigger than any challenge, and your kindness is your superpower. "
            f"Take a deep breath, believe in yourself, and let your light shine bright today. You've got this!"
        )

        safe_name = target_name.lower().replace(" ", "_")
        raw_voice_file = OUTPUT_DIR / f"voice_{{safe_name}}_{{self.name}}.mp3"
        final_file = OUTPUT_DIR / f"{{self.name}}_{{safe_name}}.mp3"

        voice_engine = VoiceSynthesizer(profile_name=voice_profile)
        await voice_engine.synthesize(
            text=script_text,
            output_path=str(raw_voice_file),
            profile_name=voice_profile
        )

        mixer = MediaMixer()
        mixer.mix_voice_and_music(
            voice_path=str(raw_voice_file),
            output_path=str(final_file),
            music_volume=0.15,
            voice_volume=1.0,
            fade_out_sec=2.0
        )

        if raw_voice_file.exists():
            raw_voice_file.unlink()

        return {{
            "status": "success",
            "title": f"{{target_name}}'s Daily Boost",
            "output_file": str(final_file),
            "script": script_text,
            "metadata": {{
                "target_name": target_name,
                "theme": theme,
                "cartridge": self.name
            }}
        }}
'''
