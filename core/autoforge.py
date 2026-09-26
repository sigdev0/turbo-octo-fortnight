import ast
import asyncio
import importlib
import importlib.util
import logging
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from core.config import CARTRIDGES_DIR, OUTPUT_DIR
from core.router import LLMRouter

logger = logging.getLogger(__name__)

AUTONOMOUS_CARTRIDGE_PROMPT = """
You are the autonomous code synthesizer for OmniForge Engine.
Your mission is to take an idea prompt and generate a COMPLETE, PRODUCTION-READY, FULLY FUNCTIONAL Python cartridge.

The cartridge MUST:
1. Inherit from `BaseCartridge` in `cartridges.base`.
2. Define:
   - `@property def name(self) -> str`: unique slug (e.g. 'morning_affirmation')
   - `@property def command(self) -> str`: short slash command for Telegram (e.g. 'affirmation')
   - `@property def description(self) -> str`: short summary of what it does
   - `async def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]`
3. Use available OmniForge core tools:
   - `from cartridges.base import BaseCartridge`
   - `from core.config import OUTPUT_DIR`
   - `from core.voice import VoiceSynthesizer`
   - `from core.media import MediaMixer`
4. The `generate()` method MUST:
   - Extract parameters from `payload` with safe fallbacks (e.g. `payload.get('name', 'Friend')`).
   - Craft or generate the narrative script.
   - Synthesize speech using `VoiceSynthesizer(profile_name=...)`.
   - Mix background audio using `MediaMixer().mix_voice_and_music(...)` (creates ambient bed automatically).
   - Return a dict with:
     {
         "status": "success",
         "title": "...",
         "output_file": str(final_path),
         "script": "...",
         "metadata": { ... }
     }
5. Return ONLY executable Python code within a single ```python ... ``` fence.
"""

class AutoForge:
    def __init__(self, router: Optional[LLMRouter] = None):
        self.router = router or LLMRouter()

    def _validate_ast(self, code_str: str) -> None:
        """Parses AST to verify syntax validity."""
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in generated code: {e}")

        # Basic safety checks
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
                    raise ValueError(f"Prohibited call '{node.func.id}' detected in generated code.")

    def _extract_command_and_slug(self, code_str: str) -> tuple[str, str]:
        """Extracts name and command properties from code."""
        name_match = re.search(r"def name\(self\)[^:]*:\s+return [\"']([^\"']+)[\"']", code_str)
        cmd_match = re.search(r"def command\(self\)[^:]*:\s+return [\"']([^\"']+)[\"']", code_str)
        
        slug = name_match.group(1) if name_match else "custom_cartridge"
        command = cmd_match.group(1) if cmd_match else slug.split("_")[0]
        return slug, command

    async def forge_cartridge(
        self,
        idea_prompt: str,
        on_status: Optional[Callable[[str], Any]] = None
    ) -> Dict[str, Any]:
        """
        Takes an idea, writes the cartridge code, self-tests it, and saves it.
        """
        async def notify(msg: str):
            if on_status:
                try:
                    res = on_status(msg)
                    if asyncio.iscoroutine(res):
                        await res
                except Exception as e:
                    logger.warning(f"Error in on_status callback: {e}")

        await notify("🧠 Analyzing your idea and synthesizing cartridge architecture...")

        # 1. Generate Python Code
        generation_prompt = f"User Idea: {idea_prompt}\n\nGenerate the complete Python cartridge implementation."
        code = await self.router.generate_code(
            prompt=generation_prompt,
            system_prompt=AUTONOMOUS_CARTRIDGE_PROMPT
        )

        await notify("🔍 Auditing code syntax and verifying security invariants...")
        self._validate_ast(code)
        slug, command = self._extract_command_and_slug(code)

        target_file = CARTRIDGES_DIR / f"{slug}.py"

        # 2. Write to cartridges directory
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(code)

        await notify(f"🧪 Running autonomous dry-run self-test for '/{command}'...")

        # 3. Dynamic Import & Self-Test
        try:
            module_name = f"cartridges.{slug}"
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                spec = importlib.util.spec_from_file_location(module_name, str(target_file))
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

            # Find the BaseCartridge subclass
            from cartridges.base import BaseCartridge
            cartridge_cls = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseCartridge) and attr is not BaseCartridge:
                    cartridge_cls = attr
                    break

            if not cartridge_cls:
                raise ValueError("No BaseCartridge subclass found in generated module.")

            instance: BaseCartridge = cartridge_cls()

            # Execute dry-run test
            test_payload = {
                "name": "Alex",
                "test": True,
                "theme": "courage and inspiration"
            }
            test_result = await instance.generate(test_payload)

            if test_result.get("status") != "success":
                raise RuntimeError(f"Dry-run test returned non-success: {test_result}")

            sample_file = test_result.get("output_file")
            await notify(f"🚀 Success! Cartridge '/{command}' is verified and ready for live use.")

            return {
                "status": "success",
                "cartridge_name": instance.name,
                "command": instance.command,
                "description": instance.description,
                "file_path": str(target_file),
                "sample_output_file": sample_file,
                "title": test_result.get("title", f"Sample {instance.command.title()}"),
                "script": test_result.get("script", "")
            }

        except Exception as e:
            logger.error(f"AutoForge dry-run test failed: {e}", exc_info=True)
            # Remove failed file so it doesn't pollute workspace
            if target_file.exists():
                target_file.unlink()
            raise RuntimeError(f"AutoForge self-test failed: {e}")
