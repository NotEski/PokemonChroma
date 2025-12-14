# Pokemon Asset Downloader - Quick Start Guide

## Summary

Created a new module `download_assets.py` that downloads Generation V sprites (static and animated) and cries for Pokemon. The module processes Pokemon one at a time, automatically renaming files from generic names to descriptive ones.

## Features

✓ Downloads Generation V Black/White sprites (static PNG and animated GIF)
✓ Downloads Pokemon cries (latest and legacy)
✓ Processes Pokemon sequentially (one at a time, not by file type)
✓ Automatically renames files with descriptive names
✓ Organized folder structure: `assets/0001-Bulbasaur/`, `assets/0025-Pikachu/`, etc.
✓ Can download by ID range or by Pokemon names
✓ Skip existing files (re-run safe)
✓ Works as both CLI tool and Python module

## Prerequisites

First, download Pokemon data from PokeAPI:

```bash
python tools/download_pokeapi.py --endpoints pokemon
```

This creates `pokeapi_database/pokemon/` with Pokemon JSON files.

## Quick Usage

### Download Generation 1 Pokemon (1-151)

```bash
python tools/download_assets.py --range 1 151
```

### Download specific Pokemon

```bash
python tools/download_assets.py --names bulbasaur pikachu charizard eevee
```

### Download all available Pokemon

```bash
python tools/download_assets.py --all
```

### As a Python module

```python
from tools.download_assets import download_pokemon_assets

# Download Gen 1
results = download_pokemon_assets(start_id=1, end_id=151)
print(f"Downloaded {results['pokemon_processed']} Pokemon")
```

## What Gets Downloaded

For each Pokemon, you get:

**Sprites (8 files):**
- `black-white_front_default.png` - Static front
- `black-white_back_default.png` - Static back
- `black-white_front_shiny.png` - Static shiny front
- `black-white_back_shiny.png` - Static shiny back
- `black-white_animated_front_default.gif` - Animated front
- `black-white_animated_back_default.gif` - Animated back
- `black-white_animated_front_shiny.gif` - Animated shiny front
- `black-white_animated_back_shiny.gif` - Animated shiny back

**Cries (2 files):**
- `cry_latest.ogg` - Modern cry sound
- `cry_legacy.ogg` - Original cry sound

## Output Structure

```
assets/
├── 0001-Bulbasaur/
│   ├── black-white_front_default.png
│   ├── black-white_animated_front_default.gif
│   ├── cry_latest.ogg
│   └── ... (7 more sprites + 1 more cry)
├── 0025-Pikachu/
│   └── ... (10 files)
└── 0133-Eevee/
    └── ... (10 files)
```

## Test Before Full Download

Run the test suite to verify everything works:

```bash
python tools/test_asset_downloader.py
```

This downloads assets for just 3 Pokemon to test the functionality.

## Estimated Download Times

- Gen 1 (151 Pokemon): ~10-15 minutes
- Gen 1-5 (649 Pokemon): ~30-45 minutes
- All Pokemon (~1000+): ~60-90 minutes

Times may vary based on network speed.

## Files Created

- `tools/download_assets.py` - Main asset downloader module
- `tools/example_asset_download.py` - Usage examples
- `tools/test_asset_downloader.py` - Test suite
- `tools/README_ASSETS.md` - Full documentation

## More Examples

See `tools/example_asset_download.py` for detailed usage examples or read `tools/README_ASSETS.md` for complete documentation.

## Command Reference

```bash
# Download by range
python tools/download_assets.py --range 1 151

# Download by names
python tools/download_assets.py --names bulbasaur pikachu

# Download all
python tools/download_assets.py --all

# Custom output directory
python tools/download_assets.py --range 1 151 --output my_assets

# Quiet mode (no progress)
python tools/download_assets.py --range 1 151 --quiet

# List help
python tools/download_assets.py --help
```

## Notes

- Files are NOT re-downloaded if they already exist
- Downloads happen one Pokemon at a time (not by file type)
- Small delay between Pokemon to be respectful to servers
- Files are automatically renamed from generic "1.png" to descriptive names
- Works with your existing `assets/` directory structure
