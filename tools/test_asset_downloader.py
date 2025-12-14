"""
Quick test of the asset downloader to verify it works correctly.
Run this to test with just a few Pokemon before downloading everything.
"""

from pathlib import Path
import sys

# Add tools directory to path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

from download_assets import PokemonAssetDownloader


def test_sprite_extraction():
    """Test that we can extract sprite URLs correctly."""
    print("Test 1: Sprite URL Extraction")
    print("=" * 60)
    
    # Use paths relative to project root
    project_root = Path(__file__).parent.parent
    
    downloader = PokemonAssetDownloader(
        pokeapi_dir=project_root / "pokeapi_database" / "pokemon",
        verbose=False
    )
    
    # Load Bulbasaur data
    bulbasaur_file = project_root / "pokeapi_database" / "pokemon" / "0001-bulbasaur.json"
    
    if not bulbasaur_file.exists():
        print("❌ Bulbasaur data file not found!")
        print("   Please run: python download_pokeapi.py --endpoints pokemon")
        return False
    
    pokemon_data = downloader._get_pokemon_data(bulbasaur_file)
    if not pokemon_data:
        print("❌ Failed to load Pokemon data")
        return False
    
    # Extract sprites
    sprites = downloader._extract_sprite_urls(pokemon_data)
    print(f"✓ Found {len(sprites)} sprite URLs")
    
    for name, url in sprites.items():
        print(f"  - {name}: {url[:50]}...")
    
    # Extract cries
    cries = downloader._extract_cry_urls(pokemon_data)
    print(f"\n✓ Found {len(cries)} cry URLs")
    
    for name, url in cries.items():
        print(f"  - {name}: {url}")
    
    # Verify we got the expected sprites
    expected_sprites = [
        "black-white_front_default",
        "black-white_back_default",
        "black-white_front_shiny",
        "black-white_back_shiny",
        "black-white_animated_front_default",
        "black-white_animated_back_default",
        "black-white_animated_front_shiny",
        "black-white_animated_back_shiny",
    ]
    
    missing = [s for s in expected_sprites if s not in sprites]
    if missing:
        print(f"\n⚠ Missing expected sprites: {missing}")
    else:
        print(f"\n✓ All expected sprites found!")
    
    return len(sprites) > 0 and len(cries) > 0


def test_single_pokemon_download():
    """Test downloading assets for a single Pokemon."""
    print("\n\nTest 2: Single Pokemon Download")
    print("=" * 60)
    
    # Use paths relative to project root
    project_root = Path(__file__).parent.parent
    
    downloader = PokemonAssetDownloader(
        pokeapi_dir=project_root / "pokeapi_database" / "pokemon",
        output_dir=project_root / "assets_test",
        verbose=True
    )
    
    bulbasaur_file = project_root / "pokeapi_database" / "pokemon" / "0001-bulbasaur.json"
    
    if not bulbasaur_file.exists():
        print("❌ Bulbasaur data file not found!")
        return False
    
    print("Downloading Bulbasaur assets...")
    stats = downloader.download_pokemon_assets(bulbasaur_file)
    
    print(f"\n✓ Download complete!")
    print(f"  Sprites downloaded: {stats['sprites_downloaded']}")
    print(f"  Sprites failed: {stats['sprites_failed']}")
    print(f"  Cries downloaded: {stats['cries_downloaded']}")
    print(f"  Cries failed: {stats['cries_failed']}")
    
    # Check that files were created
    bulbasaur_dir = project_root / "assets_test" / "0001-Bulbasaur"
    if bulbasaur_dir.exists():
        files = list(bulbasaur_dir.glob("*"))
        print(f"\n✓ Created {len(files)} files in {bulbasaur_dir}")
        print("  Files:")
        for f in sorted(files):
            print(f"    - {f.name}")
    else:
        print(f"\n❌ Directory not created: {bulbasaur_dir}")
        return False
    
    return stats['sprites_downloaded'] > 0


def test_range_download():
    """Test downloading a small range of Pokemon."""
    print("\n\nTest 3: Range Download (Pokemon 1-3)")
    print("=" * 60)
    
    # Use paths relative to project root
    project_root = Path(__file__).parent.parent
    
    downloader = PokemonAssetDownloader(
        pokeapi_dir=project_root / "pokeapi_database" / "pokemon",
        output_dir=project_root / "assets_test",
        verbose=True
    )
    
    stats = downloader.download_range(start_id=1, end_id=3)
    
    print(f"\n✓ Range download complete!")
    print(f"  Pokemon processed: {stats['pokemon_processed']}")
    print(f"  Total sprites: {stats['sprites_downloaded']}")
    print(f"  Total cries: {stats['cries_downloaded']}")
    
    return stats['pokemon_processed'] == 3


def main():
    """Run all tests."""
    print("Pokemon Asset Downloader - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Sprite Extraction", test_sprite_extraction),
        ("Single Pokemon Download", test_single_pokemon_download),
        ("Range Download", test_range_download),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"\n✓ {test_name} PASSED")
            else:
                failed += 1
                print(f"\n❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} FAILED with exception:")
            print(f"   {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ All tests passed! The asset downloader is working correctly.")
        print("\nYou can now run:")
        print("  python download_assets.py --range 1 151")
        print("to download all Gen 1 Pokemon assets.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()
