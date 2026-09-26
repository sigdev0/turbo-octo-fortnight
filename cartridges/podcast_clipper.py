import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable

from cartridges.base import BaseCartridge
from core.config import OUTPUT_DIR

# Root of the embedded podcast-clipper project
CLIPPER_ROOT = Path(__file__).resolve().parent / "podcast-clipper"
CLIPPER_SRC = CLIPPER_ROOT / "src"

if str(CLIPPER_SRC) not in sys.path:
    sys.path.insert(0, str(CLIPPER_SRC))

class PodcastClipperCartridge(BaseCartridge):
    @property
    def name(self) -> str:
        return "podcast_clipper"

    @property
    def command(self) -> str:
        return "clip"

    @property
    def description(self) -> str:
        return "Extracts viral 9:16 vertical shorts from podcasts & YouTube URLs."

    def _run_clipping_pipeline(
        self,
        url: str,
        style: str,
        max_clips: int,
        preset: str,
        name: str
    ) -> Dict[str, Any]:
        """Synchronous wrapper executed in background thread."""
        cwd_before = os.getcwd()
        try:
            # Change working directory to CLIPPER_ROOT for settings/config relative paths
            os.chdir(str(CLIPPER_ROOT))

            from clipper.download import load_settings
            from clipper.pipeline import process

            settings = load_settings()
            
            # Route output to OmniForge output directory
            settings["paths"]["output_dir"] = str(OUTPUT_DIR)

            res = process(
                url=url,
                settings=settings,
                name=name,
                style=style,
                max_clips=max_clips,
                preset=preset
            )
            return res
        finally:
            os.chdir(cwd_before)

    async def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        on_progress: Optional[Callable[[str], Any]] = payload.get("on_progress")
        url = payload.get("url") or payload.get("theme") or ""

        if not url:
            return {
                "status": "error",
                "message": "Missing YouTube or podcast video URL. Usage: /clip <url>"
            }

        style = payload.get("style", "hormozi")
        max_clips = int(payload.get("max_clips", 3))
        preset = payload.get("preset", "shorts")

        import hashlib
        name_slug = hashlib.md5(url.encode()).hexdigest()[:8]

        if on_progress:
            await on_progress("⬇️ Downloading video and extracting audio...")

        try:
            # Run heavy processing in background thread
            res = await asyncio.to_thread(
                self._run_clipping_pipeline,
                url=url,
                style=style,
                max_clips=max_clips,
                preset=preset,
                name=name_slug
            )

            made_clips = res.get("clips", [])
            output_files = [m["clip"] for m in made_clips if "clip" in m]
            dl_info = res.get("download", {})
            title = dl_info.get("title", f"Clip_{name_slug}")

            return {
                "status": "success",
                "title": title,
                "output_file": output_files[0] if output_files else None,
                "output_files": output_files,
                "metadata": {
                    "url": url,
                    "clips_count": len(output_files),
                    "style": style,
                    "preset": preset,
                    "raw_result": made_clips
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Podcast clipping failed: {str(e)}"
            }
