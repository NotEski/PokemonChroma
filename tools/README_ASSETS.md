# Pokemon Asset Downloader

Downloads Generation V sprites (including animations) and cries for Pokemon from PokeAPI data. Processes Pokemon sequentially, downloading all assets for each Pokemon before moving to the next.

## Features

- Downloads Generation V sprites (static and animated)
- Downloads Pokemon cries (sound effects)
- Processes Pokemon one at a time (not by file type)
- Automatically renames files from generic names (like "1") to descriptive names
- Organized folder structure by Pokemon
- Can download by ID range or by Pokemon names
- Supports quiet mode and verbose progress tracking

## Prerequisites

Before using this tool, you must first download Pokemon data:

```bash
python download_pokeapi.py --endpoints pokemon
```

This creates the `pokeapi_database/pokemon/` directory with Pokemon JSON files.

## CLI Usage

### Download Generation 1 (Pokemon 1-151)

```bash
python download_assets.py --range 1 151
```

### Download specific Pokemon by name

```bash
python download_assets.py --names bulbasaur pikachu charizard eevee
```

### Download all available Pokemon

```bash
python download_assets.py --all
```

### Custom directories

```bash
python download_assets.py --range 1 151 --output my_assets --source my_pokeapi/pokemon
```

### Quiet mode

```bash
python download_assets.py --range 1 151 --quiet
```

### Interactive mode

```bash
python download_assets.py
```

This will prompt you to choose between Gen 1, Gen 1-5, or all Pokemon.

## Module Usage

### Basic Usage

```python
from tools.download_assets import download_pokemon_assets

# Download Gen 1 Pokemon (1-151)
results = download_pokemon_assets(start_id=1, end_id=151)
print(f"Downloaded: {results}")
```

### Using the PokemonAssetDownloader Class

```python
from tools.download_assets import PokemonAssetDownloader

# Create downloader instance
downloader = PokemonAssetDownloader(
    pokeapi_dir="pokeapi_database/pokemon",
    output_dir="assets",
    verbose=True
)

# Download by range
results = downloader.download_range(start_id=1, end_id=151)

# Download specific Pokemon by name
results = downloader.download_by_names(["bulbasaur", "pikachu", "charizard"])

# Download a single Pokemon from file
from pathlib import Path
pokemon_file = Path("pokeapi_database/pokemon/0025-pikachu.json")
results = downloader.download_pokemon_assets(pokemon_file)
```

### Quiet Mode

```python
from tools.download_assets import download_pokemon_assets

# Download without progress output
results = download_pokemon_assets(
    start_id=1,
    end_id=10,
    verbose=False
)
```

## What Gets Downloaded

### Generation V Sprites

For each Pokemon, the following Generation V sprites are downloaded:

**Black/White (Static):**
- `black-white_front_default.png` - Front view
- `black-white_back_default.png` - Back view
- `black-white_front_shiny.png` - Shiny front view
- `black-white_back_shiny.png` - Shiny back view

**Black/White (Animated):**
- `black-white_animated_front_default.gif` - Animated front view
- `black-white_animated_back_default.gif` - Animated back view
- `black-white_animated_front_shiny.gif` - Animated shiny front
- `black-white_animated_back_shiny.gif` - Animated shiny back

### Cries

- `cry_latest.ogg` - Modern cry sound
- `cry_legacy.ogg` - Original cry sound (if available)

## Output Structure

Assets are organized by Pokemon in the following structure:

```
assets/
├── 0001-Bulbasaur/
│   ├── black-white_front_default.png
│   ├── black-white_back_default.png
│   ├── black-white_front_shiny.png
│   ├── black-white_back_shiny.png
│   ├── black-white_animated_front_default.gif
│   ├── black-white_animated_back_default.gif
│   ├── black-white_animated_front_shiny.gif
│   ├── black-white_animated_back_shiny.gif
│   ├── cry_latest.ogg
│   └── cry_legacy.ogg
├── 0025-Pikachu/
│   ├── black-white_front_default.png
│   ├── black-white_back_default.png
│   └── ...
└── 0133-Eevee/
    ├── black-white_front_default.png
    └── ...
```

Each Pokemon has its own directory with:
- **ID prefix**: `0001-`, `0025-`, etc.
- **Capitalized name**: `Bulbasaur`, `Pikachu`, etc.
- **Descriptive filenames**: No more generic "1.png" files!

## How It Works

The downloader processes Pokemon **one at a time**, not by file type:

1. Reads Pokemon data from `pokeapi_database/pokemon/0001-bulbasaur.json`
2. Extracts all Generation V sprite URLs
3. Extracts cry URLs
4. Downloads all sprites for Bulbasaur
5. Downloads all cries for Bulbasaur
6. Moves to the next Pokemon (0002-ivysaur.json)
7. Repeats

This ensures complete asset sets per Pokemon and makes it easy to track progress.

## API Reference

### `PokemonAssetDownloader`

Main class for downloading Pokemon assets.

**Constructor:**
```python
PokemonAssetDownloader(
    pokeapi_dir: Union[str, Path] = "pokeapi_database/pokemon",
    output_dir: Union[str, Path] = "assets",
    verbose: bool = True
)
```

**Methods:**

- `download_range(start_id: int, end_id: Optional[int], skip_existing: bool = True) -> Dict[str, int]`
  - Download assets for Pokemon in ID range
  - Returns statistics dictionary

- `download_by_names(pokemon_names: List[str], skip_existing: bool = True) -> Dict[str, int]`
  - Download assets for specific Pokemon by name
  - Returns statistics dictionary

- `download_pokemon_assets(pokemon_file: Path, skip_existing: bool = True) -> Dict[str, int]`
  - Download assets for a single Pokemon
  - Returns statistics dictionary

### `download_pokemon_assets`

Convenience function for quick downloads.

```python
download_pokemon_assets(
    start_id: int = 1,
    end_id: Optional[int] = None,
    output_dir: Union[str, Path] = "assets",
    pokeapi_dir: Union[str, Path] = "pokeapi_database/pokemon",
    verbose: bool = True
) -> Dict[str, int]
```

### Return Statistics

All download methods return a dictionary with:
```python
{
    "pokemon_processed": 151,
    "sprites_downloaded": 1208,
    "sprites_failed": 0,
    "cries_downloaded": 302,
    "cries_failed": 0
}
```

## Examples

### Example 1: Download Starter Pokemon

```python
from tools.download_assets import PokemonAssetDownloader

downloader = PokemonAssetDownloader()
downloader.download_by_names([
    "bulbasaur", "charmander", "squirtle",
    "pikachu", "eevee"
])
```

### Example 2: Download Gen 1 Quietly

```python
from tools.download_assets import download_pokemon_assets

stats = download_pokemon_assets(1, 151, verbose=False)
print(f"✓ Downloaded {stats['pokemon_processed']} Pokemon")
```

### Example 3: Custom Organization

```python
from tools.download_assets import PokemonAssetDownloader

# Download to a different location
downloader = PokemonAssetDownloader(
    output_dir="game_assets/sprites"
)
downloader.download_range(1, 151)
```

## Troubleshooting

### No Pokemon files found

**Error:** `No Pokemon files found in pokeapi_database/pokemon`

**Solution:** Run the PokeAPI downloader first:
```bash
python download_pokeapi.py --endpoints pokemon
```

### Some sprites missing

Some Pokemon may not have all sprite variations available in the API. The downloader will skip missing sprites and report them in the statistics.

### Network errors

If downloads fail due to network issues, simply re-run the command. The downloader skips already-downloaded files by default.

## Performance

- Downloads are sequential (one Pokemon at a time)
- Small delay between Pokemon to be respectful to servers
- Files are cached - re-running won't re-download existing files
- Gen 1 (151 Pokemon): ~5-10 minutes
- Gen 1-5 (649 Pokemon): ~20-30 minutes
- All Pokemon (~1000+): ~40-60 minutes

## Notes

- Files are not re-downloaded if they already exist
- File extensions are automatically detected from URLs
- Pokemon directories use capitalized names
- Progress is shown by default (use `--quiet` to suppress)
- Works with the existing `assets/` directory structure in your project
