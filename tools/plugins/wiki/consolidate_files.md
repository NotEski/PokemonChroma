# Consolidate Files

Organize and consolidate scattered game data files into a unified directory structure. This plugin moves, renames, and reorganizes downloaded and converted data files to match the game engine's expected file layout.

## Overview

The Consolidate Files plugin organizes game data from multiple sources into the standardized directory structure required by the game engine. It handles file movement, naming normalization, duplicate detection, and structure validation to ensure data is accessible and organized for efficient game operations.

**Use this plugin to:**
- Organize raw downloads into game structure
- Consolidate data from multiple sources
- Detect and handle duplicate files
- Normalize file naming conventions
- Validate file organization

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| source_dir | Folder | Yes | Directory containing files to consolidate |
| target_dir | Folder | Yes | Root game data directory (consolidation target) |
| file_type | Select | No | Filter to specific file types (all, pokemon, moves, items, abilities) |
| handle_duplicates | Select | No | How to handle duplicates (skip, overwrite, merge) |

## Usage Examples

### Example 1: Consolidate All Downloaded Data

Organize all downloaded artwork and data into game structure.

Steps:
1. Set `source_dir` to temp download directory
2. Set `target_dir` to `data/`
3. Set `file_type` to "all"
4. Set `handle_duplicates` to "merge" (keep best copy)
5. Click Execute

Expected result: All files organized into proper directories with duplicates resolved.

### Example 2: Consolidate Only Pokémon Data

Organize only Pokémon-related files.

Steps:
1. Set `source_dir` to `data/pokemon/raw`
2. Set `target_dir` to `data/`
3. Set `file_type` to "pokemon"
4. Set `handle_duplicates` to "skip"
5. Click Execute

Expected result: Pokémon files organized into `data/pokemon/` with proper naming.

### Example 3: Consolidate and Overwrite

Replace existing data with newer files.

Steps:
1. Set `source_dir` to new data download
2. Set `target_dir` to `data/`
3. Set `file_type` to "all"
4. Set `handle_duplicates` to "overwrite"
5. Click Execute

Expected result: All data updated with newest versions from source.

## Advanced Options

### File Type Filtering

Filter consolidation to specific data types:
- **all**: All data files
- **pokemon**: Pokémon sprites, artwork, data
- **moves**: Move data and effects
- **items**: Item artwork and data
- **abilities**: Ability descriptions and effects

### Duplicate Handling

Choose how to handle duplicate files:
- **skip**: Keep existing files, don't copy duplicates
- **overwrite**: Replace with new copies
- **merge**: Keep best copy based on file size/date

### Directory Structure

Consolidation creates this structure:
```
data/
├── pokemon/
│   ├── 0001-Bulbasaur/
│   ├── 0002-Ivysaur/
│   └── ...
├── moves/
│   ├── move_data.json
│   └── ...
├── items/
│   ├── item_data.json
│   └── ...
└── abilities/
    └── ability_data.json
```

## Troubleshooting

### Issue: "Source directory not found"

**Solution:** Verify source_dir path exists and contains files. Check spelling and full path.

### Issue: "Permission denied - cannot write to target"

**Solution:** Ensure you have write permissions to target_dir. Try running as administrator.

### Issue: "Files not organized as expected"

**Solution:** Check if files match expected naming patterns. The plugin uses file extensions and content analysis.

### Issue: "Duplicate resolution failed"

**Solution:** Try different `handle_duplicates` option. Review the log to see which duplicates caused issues.

### Issue: "Target directory structure mismatch"

**Solution:** Ensure target_dir is a game data directory. Create it fresh or verify it has expected subdirectories.

## Related Plugins

- [Asset Downloader](asset_downloader.md) - Download files to consolidate
- [PokeAPI Downloader](pokeapi_downloader.md) - Download data to consolidate
- [JSON to Pokémon Converter](json_converter.md) - Prepare files before consolidation
- [Pokémon Data Generator](pokemon_data.md) - Generate database from consolidated data

## Version History

- **1.0.0**: Initial release
- **1.1.0**: Added file type filtering
- **1.2.0**: Improved duplicate detection
- **1.3.0**: Added merge option for smart duplicate handling

## Technical Details

**Supported File Types:** PNG, JSON, CSV, TXT, DB

**File Matching:** Name-based and content-based matching

**Duplicate Detection:** File hash comparison

**Performance:** Handles 10,000+ files efficiently

**Safe Operation:** Never deletes source files, only copies/moves
