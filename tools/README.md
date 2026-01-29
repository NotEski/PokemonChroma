# Tools Directory

This directory contains utilities and scripts for managing Pokemon data and assets. All tools can be run through the **unified GUI interface** (default) or via CLI.

## Quick Start

### Using the GUI (Recommended)

The toolbox provides a visual interface with tabs for each tool:

```bash
# Launch GUI (default)
python tools/toolbox.py

# Or from tools directory
cd tools
python toolbox.py
```

**GUI Features:**
- Plugin tabs in notebook interface
- Dynamic forms for each tool
- Real-time output log with color coding
- Progress tracking
- Help button for each plugin with full documentation
- Refresh plugins on the fly
- No need to remember CLI arguments

### Using the Toolbox CLI

For automation and scripting, CLI mode is available:

```bash
# List available plugins
python tools/toolbox.py --cli list

# Run a specific tool
python tools/toolbox.py --cli run asset_downloader -- --range 1 151
python tools/toolbox.py --cli run pokeapi_downloader -- --endpoints pokemon
python tools/toolbox.py --cli run pokemon_data -- --help

# Interactive mode
python tools/toolbox.py --cli interactive
```

See [README_TOOLBOX.md](README_TOOLBOX.md) for more details on the CLI system.

## Available Tools

### GUI Features

The GUI organizes all tools into dedicated tabs:

- **Asset Downloader** - Download Pokemon sprites and cries with mode selection (Range/Names/All)
- **PokeAPI Downloader** - Download raw API data with endpoint selection
- **Pokemon Data Generator** - Generate game data from PokeAPI cache
- **Type Chart Generator** - Generate type effectiveness chart
- **JSON Converter** - Convert JSON files to .pkmn format
- **File Consolidator** - Consolidate distributed Pokemon files
- **Move Converter** - Convert moves to metadata format

Each tab includes:
- Dynamic forms with appropriate widgets (text, spinbox, checkboxes, file pickers)
- Validation and required field indicators
- Pre-populated defaults from configuration
- Execute buttons with progress tracking
- Real-time output log at bottom of window
- **Help button** with comprehensive plugin documentation

For complete GUI implementation details, see [GUI_IMPLEMENTATION.md](GUI_IMPLEMENTATION.md).

---

### 1. PokeAPI Downloader (`download_pokeapi.py`)

Downloads raw data from the PokeAPI database.

**CLI Usage:**
```bash
# Download specific endpoints
python tools/download_pokeapi.py --endpoints pokemon move ability

# Download all endpoints
python tools/download_pokeapi.py --all

# List available endpoints
python tools/download_pokeapi.py --list
```

**Module Usage:**
```python
from tools.download_pokeapi import download_pokemon_data

results = download_pokemon_data(
    output_dir="pokeapi_database",
    endpoints=["pokemon", "move", "ability"]
)
```

**Features:**
- Download specific endpoints or all available data
- Concurrent downloads with configurable workers
- Progress tracking and verbose/quiet modes
- Automatic retry and error handling
- Organized folder structure with index files

---

### 2. Asset Downloader (`download_assets.py`)

Downloads Generation V sprites (including animations) and cries for Pokemon.

**Prerequisites:**
```bash
python tools/download_pokeapi.py --endpoints pokemon
```

**CLI Usage:**
```bash
# Download Generation 1 (Pokemon 1-151)
python tools/download_assets.py --range 1 151

# Download specific Pokemon by name
python tools/download_assets.py --names bulbasaur pikachu charizard eevee

# Download all available Pokemon
python tools/download_assets.py --all
```

**Module Usage:**
```python
from tools.download_assets import download_pokemon_assets

# Download Gen 1
results = download_pokemon_assets(start_id=1, end_id=151)
```

**Features:**
- Downloads Generation V sprites (static and animated)
- Downloads Pokemon cries (sound effects)
- Processes Pokemon one at a time
- Automatically renames files from generic names to descriptive names
- Organized folder structure by Pokemon
- Can download by ID range or by Pokemon names

**Output Structure:**
```
assets/
├── 0001-Bulbasaur/
│   ├── black-white_front_default.png
│   ├── black-white_animated_front_default.gif
│   ├── cry_latest.ogg
│   └── ... (7 more sprites + 1 more cry)
└── 0025-Pikachu/
    └── ... (10 files)
```

---

### 3. Pokemon Data Generator (`generate_pokemon_data.py`)

Generates Pokemon, move, item, and ability data from cached PokeAPI JSON.

**Prerequisites:**
```bash
python tools/download_pokeapi.py --endpoints pokemon move item ability
```

**CLI Usage:**
```bash
# Generate all data
python tools/generate_pokemon_data.py

# Custom directories
python tools/generate_pokemon_data.py \
  --source pokeapi_database \
  --out-pokemon data/pokemon \
  --out-moves data/moves \
  --out-items data/items \
  --out-abilities data/abilities
```

**Features:**
- Generates `.pkmn` files for Pokemon with stats, types, abilities, and move lists
- Generates `.pkmn` files for moves with damage, accuracy, PP, and effects
- Copies item JSON files with proper naming
- Generates ability `.pkmn` files
- Generates status condition files from SQLite data

**Output:**
- `data/pokemon/NNNN-pokemon-name.pkmn`
- `data/moves/NNNN-move-name.pkmn`
- `data/items/NNNN-item-name.json`
- `data/abilities/ability-name.pkmn`
- `data/status/status-name.pkmn`

---

### 4. Type Chart Generator (`generate_type_chart.py`)

Generates type effectiveness charts from PokeAPI data.

**Prerequisites:**
```bash
python tools/download_pokeapi.py --endpoints type
```

**CLI Usage:**
```bash
python tools/generate_type_chart.py
```

**Output:**
- `data/types/type_effectiveness.json` - Complete type chart

---

### 5. JSON to PKMN Converter (`json_to_pkmn_converter.py`)

Converts Pokemon JSON files to `.pkmn` format with MoveMetaData.

**CLI Usage:**
```bash
# Convert all files in a directory
python tools/json_to_pkmn_converter.py --input data/pokemon --output data/pokemon_pkmn

# Convert a single file
python tools/json_to_pkmn_converter.py --input data/pokemon/0001-bulbasaur.json --output data/pokemon/0001-bulbasaur.pkmn
```

See [JSON_TO_PKMN_CONVERTER.md](JSON_TO_PKMN_CONVERTER.md) for detailed documentation.

---

### 6. Consolidate Pokemon Files (`consolidate_pokemon_files.py`)

Merges distributed Pokemon data files into a single consolidated directory.

**CLI Usage:**
```bash
python tools/consolidate_pokemon_files.py
```

---

### 7. Convert Moves to Metadata (`convert_moves_to_metadata.py`)

Converts all move `.pkmn` files from meta dict format to MoveMetaData format.

**CLI Usage:**
```bash
python tools/convert_moves_to_metadata.py
```

---

## Configuration

Tools can be configured via `toolbox.ini`:

```ini
[toolbox]
default_plugin = asset_downloader

[plugin:asset_downloader]
output_dir = assets
concurrency = 4

[plugin:pokeapi_downloader]
database_dir = pokeapi_database

[plugin:pokemon_data]
source = pokeapi_database
out_pokemon = data/pokemon
out_moves = data/moves
out_items = data/items
```

Override config via CLI:
```bash
python tools/toolbox.py run asset_downloader -c output_dir=my_assets -c concurrency=8 -- --range 1 151
```

---

## Typical Workflow

1. **Download PokeAPI data:**
   ```bash
   python tools/download_pokeapi.py --endpoints pokemon move item ability type
   ```

2. **Generate game data:**
   ```bash
   python tools/generate_pokemon_data.py
   python tools/generate_type_chart.py
   ```

3. **Download assets (optional):**
   ```bash
   python tools/download_assets.py --range 1 151
   ```

---

## Plugin System

The toolbox uses a modular plugin architecture. All plugins are self-contained with embedded business logic and are located in `tools/plugins/`.

### Available Plugins

All plugins include integrated GUI forms, CLI support, and comprehensive documentation:

1. **Asset Downloader** - Download and organize Pokemon artwork
2. **PokeAPI Downloader** - Download comprehensive Pokemon data from the PokéAPI
3. **Pokémon Data Generator** - Generate game database from downloaded data
4. **Type Chart Generator** - Create type effectiveness data
5. **JSON Converter** - Convert JSON data to game format
6. **Consolidate Files** - Organize scattered data files
7. **Move Converter** - Convert move data to game metadata format

### Plugin Documentation

Each plugin includes comprehensive wiki documentation accessible via the GUI Help button:

- **GUI Help** - Click "Help" button in any plugin tab to view formatted documentation with examples
- **Wiki Files** - See `tools/plugins/wiki/{plugin_id}.md` for raw markdown documentation
- **Development** - See `tools/plugins/PLUGIN_DEVELOPMENT.md` for creating new plugins

### Shared Utilities

Utilities are organized in `tools/shared/`:

- `plugin_base.py` - Base class for all plugins with wiki support
- `wiki_loader.py` - Parse and load wiki documentation from markdown
- `run_script.py` - Script execution utilities
- `utils.py` - Common utility functions

---

## Documentation Structure

### Plugin Wiki Files

Located in `tools/plugins/wiki/`:
- Each plugin has a dedicated markdown file: `{plugin_id}.md`
- Contains: Overview, Form Fields, Usage Examples, Troubleshooting, Advanced Options
- Accessible via GUI Help button or direct file viewing for AI/programmatic access

### Plugin Development Guide

- **File:** `tools/plugins/PLUGIN_DEVELOPMENT.md`
- Complete plugin creation template with examples
- Mandatory reading for creating new plugins
- Includes: architecture overview, step-by-step guide, boilerplate code, patterns, API reference

### Legacy Documentation

Specialized reference documentation:
- [JSON_TO_PKMN_CONVERTER.md](JSON_TO_PKMN_CONVERTER.md) - Data conversion technical details
- [MOVE_SYSTEM_GUIDE.md](MOVE_SYSTEM_GUIDE.md) - Move mechanics and systems
- [GUI_IMPLEMENTATION.md](GUI_IMPLEMENTATION.md) - GUI architecture and Tkinter integration

---

## Testing

Test files are located in `/tests`:
- `test_asset_downloader.py` - Tests asset downloading
- `test_moves.py` - Tests move data generation

Run tests from the repository root:
```bash
pytest tests/test_asset_downloader.py
pytest tests/test_moves.py
```

---

## Creating New Plugins

To create a new plugin:

1. Read `tools/plugins/PLUGIN_DEVELOPMENT.md` (mandatory)
2. Create your plugin file: `tools/plugins/my_plugin.py`
3. Implement `PluginBase` with required methods
4. Create wiki file: `tools/plugins/wiki/my_plugin.md`
5. Add unit tests: `tests/test_my_plugin.py`

The plugin will be automatically discovered and loaded in the toolbox GUI.

---

**For more information:** See individual plugin documentation via GUI Help button or `tools/plugins/wiki/` directory.
