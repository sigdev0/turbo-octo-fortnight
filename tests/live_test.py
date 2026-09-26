import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from cartridges.bedtime_story import BedtimeStoryCartridge

async def main():
    print("=" * 60)
    print("🌟 OMNIFORGE ENGINE: SPRINT 1 LIVE TEST 🌟")
    print("=" * 60)

    cartridge = BedtimeStoryCartridge()
    print(f"Loaded Cartridge: {cartridge.name}")
    print(f"Description: {cartridge.description}\n")

    # Test 1: For the 8-Year-Old
    print("Generating Bedtime Audio Adventure for 8-year-old ('Leo')...")
    result_8yo = await cartridge.generate({
        "name": "Leo",
        "age": 8,
        "theme": "the Secret Planet of Whispering Trees",
        "lesson": "courage and patience",
        "voice_profile": "bedtime_british"
    })
    print(f"✅ Success! Title: {result_8yo['title']}")
    print(f"📁 Output File: {result_8yo['output_file']}")
    print("-" * 60)

    # Test 2: For the 2-Year-Old
    print("Generating Soothing Lullaby Story for 2-year-old ('Maya')...")
    result_2yo = await cartridge.generate({
        "name": "Maya",
        "age": 2,
        "theme": "the Fluffy Cloud Castle",
        "lesson": "gentleness",
        "voice_profile": "bedtime_female"
    })
    print(f"✅ Success! Title: {result_2yo['title']}")
    print(f"📁 Output File: {result_2yo['output_file']}")
    print("=" * 60)
    print("🎉 Both tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
