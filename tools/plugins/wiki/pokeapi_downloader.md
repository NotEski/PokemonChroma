# PokeAPI Downloader

Download comprehensive Pokémon data from the PokéAPI. This plugin retrieves detailed information about Pokémon, moves, items, abilities, and more, storing it for offline access and game reference.

## Overview

The PokeAPI Downloader plugin fetches extensive Pokémon data from the public PokéAPI service and stores it locally. This includes all Pokémon stats, moves, abilities, items, types, and game mechanics. The downloaded data powers many game features and can be used for analysis and reference.

**Use this plugin to:**
- Download all Pokémon species and form data
- Get complete move lists with mechanics and effects
- Retrieve item information and effects
- Download ability descriptions and mechanics
- Build offline database for game operations

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| output_dir | Folder | Yes | Directory where JSON data files will be saved |
| data_type | Select | Yes | Type of data to download (pokemon, moves, items, abilities, types) |
| include_descriptions | Checkbox | No | Download verbose descriptions and flavor text |

## Usage Examples

### Example 1: Download All Pokémon Data

Get complete data for all Pokémon species and forms.

Steps:
1. Select output directory (e.g., `data/pokemon`)
2. Set `data_type` to "pokemon"
3. Check `include_descriptions` for full details
4. Click Execute

Expected result: JSON files for all Pokémon are downloaded into organized subdirectories.

### Example 2: Download Move Reference Data

Get complete move mechanics and descriptions.

Steps:
1. Select output directory (e.g., `data/moves`)
2. Set `data_type` to "moves"
3. Check `include_descriptions` for move flavor text
4. Click Execute

Expected result: Comprehensive move reference with all mechanics, effects, and power data.

### Example 3: Download Item Database

Get all item information for inventory system.

Steps:
1. Select output directory (e.g., `data/items`)
2. Set `data_type` to "items"
3. Check `include_descriptions`
4. Click Execute

Expected result: Item reference data with effects, held item mechanics, and descriptions.

## Advanced Options

### Selective Data Downloads

Download only the data you need:
- **pokemon**: Pokémon stats, forms, evolutions
- **moves**: Move mechanics, effects, power/accuracy
- **items**: Item effects, held item mechanics
- **abilities**: Ability descriptions and effects
- **types**: Type matchups, effectiveness, weaknesses

### Incremental Updates

Run the plugin multiple times with different `data_type` values to build your database incrementally.

### Data Organization

Downloaded data is organized by type:
```
data/
├── pokemon/
│   ├── bulbasaur.json
│   ├── ivysaur.json
│   └── ...
├── moves/
│   ├── absorb.json
│   ├── acid.json
│   └── ...
└── items/
    ├── pokedex.json
    ├── pokeball.json
    └── ...
```

## Troubleshooting

### Issue: "API rate limit exceeded"

**Solution:** The API limits requests. Wait a few minutes and retry. Large downloads may take 10-30 minutes.

### Issue: "Connection timeout"

**Solution:** Your internet connection may be unstable. Check connectivity and retry.

### Issue: Incomplete data files

**Solution:** If the plugin was interrupted, some files may be partial. Delete the output directory and restart the download.

### Issue: "Data validation failed"

**Solution:** Some API responses may have issues. Delete and retry the specific data_type. Report issues on the project repository.

## Related Plugins

- [Asset Downloader](asset_downloader.md) - Download Pokémon artwork
- [Type Chart Generator](type_chart.md) - Generate type effectiveness charts
- [Pokémon Data Generator](pokemon_data.md) - Consolidate data into game format

## Version History

- **1.0.0**: Initial release
- **1.1.0**: Added incremental download support
- **1.2.0**: Improved error recovery and data validation

## Technical Details

**Data Source:** PokéAPI (https://pokeapi.co/)

**File Format:** JSON with nested structure

**Data Coverage:** Pokémon Generations 1-9 (2500+ entries)

**Update Frequency:** API is continuously updated with new Pokémon and mechanics
