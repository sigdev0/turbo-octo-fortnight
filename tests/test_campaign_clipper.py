import asyncio
import json
import os
import sys
from pathlib import Path
import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cartridges.podcast_clipper import CLIPPER_SRC, PodcastClipperCartridge

if str(CLIPPER_SRC) not in sys.path:
    sys.path.insert(0, str(CLIPPER_SRC))

from clipper.clip import render_banner_overlay, resolve_font
from clipper.pipeline import load_campaign_profile, list_campaigns


def test_resolve_font():
    font = resolve_font(32, bold=True)
    assert font is not None


def test_render_banner_overlay_disabled(tmp_path):
    out_png = str(tmp_path / "disabled.png")
    # When disabled, should return None and not write file
    res = render_banner_overlay(
        out_png_path=out_png,
        text="Sample Headline",
        banner_cfg={"enabled": False},
        logo_path=None,
        logo_cfg={"enabled": False},
    )
    assert res is None
    assert not os.path.exists(out_png)


def test_render_banner_overlay_pill(tmp_path):
    out_png = str(tmp_path / "test_pill.png")
    res = render_banner_overlay(
        out_png_path=out_png,
        text="THE 15 SECOND HUG RULE EXPLAINED",
        banner_cfg={
            "enabled": True,
            "style": "pill",
            "font_size": 42,
            "text_color": "#FFEB3B",
            "bg_color": [18, 18, 22, 220],
            "border_color": [255, 235, 59, 180],
            "border_width": 3,
            "y": 150,
        },
        logo_path=None,
        logo_cfg={"enabled": False},
        width=1080,
        height=1920,
    )
    assert res == out_png
    assert os.path.exists(out_png)

    # Verify PNG properties
    with Image.open(out_png) as img:
        assert img.size == (1080, 1920)
        assert img.mode == "RGBA"


def test_render_banner_overlay_with_logo(tmp_path):
    # Create mock logo
    logo_file = tmp_path / "mock_logo.png"
    mock_logo = Image.new("RGBA", (100, 50), (255, 0, 0, 255))
    mock_logo.save(str(logo_file))

    out_png = str(tmp_path / "test_logo.png")
    res = render_banner_overlay(
        out_png_path=out_png,
        text="RELATIONSHIP ADVICE",
        banner_cfg={"enabled": True},
        logo_path=str(logo_file),
        logo_cfg={"enabled": True, "position": "top-right"},
        width=1080,
        height=1920,
    )
    assert res == out_png
    assert os.path.exists(out_png)


def test_campaign_profiles_exist():
    campaigns = list_campaigns()
    assert "habits_pill_banner" in campaigns
    assert "raw_podcast_minimal" in campaigns
    assert "general_winner" in campaigns

    habits = load_campaign_profile("habits_pill_banner")
    assert habits["banner"]["enabled"] is True
    assert habits["ambience"]["enabled"] is True
    assert habits["caption"]["style"] == "hormozi"

    minimal = load_campaign_profile("raw_podcast_minimal")
    assert minimal["banner"]["enabled"] is False
    assert minimal["ambience"]["enabled"] is False


def test_podcast_cartridge_interface():
    cart = PodcastClipperCartridge()
    assert cart.name == "podcast_clipper"
    assert cart.command == "clip"

    # Test error handling when url is missing
    res = asyncio.run(cart.generate({}))
    assert res["status"] == "error"
    assert "Missing" in res["message"]


def test_bot_guide_keyboards():
    from core.bot import OmniForgeBot
    bot = OmniForgeBot(token="TEST_TOKEN")

    # Main menu has clip and guides buttons
    main_kb = bot._get_main_menu_keyboard("id")
    buttons_data = [btn.callback_data for row in main_kb.inline_keyboard for btn in row]
    assert "wiz_menu_clip" in buttons_data
    assert "wiz_menu_guides" in buttons_data

    # Clip guide keyboard has the 3 winner presets
    clip_kb = bot._get_clip_guide_keyboard("id")
    clip_buttons = [btn.callback_data for row in clip_kb.inline_keyboard for btn in row]
    assert "clip_preset:habits_pill_banner" in clip_buttons
    assert "clip_preset:raw_podcast_minimal" in clip_buttons
    assert "clip_preset:general_winner" in clip_buttons
    assert "clip_guide:custom_brief" in clip_buttons

    # General guides catalog
    catalog_kb = bot._get_guides_catalog_keyboard("id")
    catalog_buttons = [btn.callback_data for row in catalog_kb.inline_keyboard for btn in row]
    assert "wiz_menu_clip" in catalog_buttons
    assert "guide_detail:story" in catalog_buttons
    assert "guide_detail:culture" in catalog_buttons
