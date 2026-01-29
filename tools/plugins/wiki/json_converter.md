# JSON to Pokémon Converter

Convert raw JSON data into Pokémon game format. This plugin transforms data from PokéAPI and other JSON sources into the standardized Pokémon data format used throughout the game engine.

## Overview

The JSON to Pokémon Converter plugin reads JSON data files and converts them into the game's native Pokémon format. It processes Pokémon stats, moves, abilities, items, and other game elements, handling data validation, type conversion, and format normalization.

**Use this plugin to:**
- Convert PokéAPI JSON into game format
- Process downloaded Pokémon data into usable format
- Validate and normalize Pokémon data
- Handle data import from external sources
- Support data pipeline from API to game database

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| input_dir | Folder | Yes | Directory containing input JSON files |
| output_dir | Folder | Yes | Directory where converted Pokémon files will be saved |
| conversion_type | Select | Yes | Data type to convert (pokemon, moves, items, abilities) |
| validate_data | Checkbox | No | Validate converted data and report errors |

## Usage Examples

### Example 1: Convert Downloaded Pokémon JSON

Convert downloaded JSON Pokémon data to game format.

Steps:
1. Set `input_dir` to where PokeAPI data was downloaded (e.g., `data/pokemon/raw`)
2. Set `output_dir` to `data/pokemon`
3. Set `conversion_type` to "pokemon"
4. Check `validate_data` to catch any issues
5. Click Execute

Expected result: All JSON files are converted and saved as `.pkmn` format in the output directory with proper structure.

### Example 2: Convert and Validate Move Data

Convert move data with full validation.

Steps:
1. Set `input_dir` to `data/moves/raw`
2. Set `output_dir` to `data/moves`
3. Set `conversion_type` to "moves"
4. Check `validate_data`
5. Click Execute

Expected result: Move data is converted with validation errors logged for manual review.

### Example 3: Batch Convert Multiple Data Types

Run converter multiple times for different data types:

Steps:
1. First pass: conversion_type = "pokemon"
2. Second pass: conversion_type = "moves"
3. Third pass: conversion_type = "items"
4. Each with respective input/output directories
5. Click Execute for each

Expected result: Full game database built from JSON sources.

## Advanced Options

### Data Validation

When `validate_data` is checked:
- All required fields are verified to exist
- Data types are checked for correctness
- Cross-references are validated
- Invalid entries are logged but don't stop conversion

### Format Details

**Input Format (JSON):**
```json
{
  "id": 1,
  "name": "Bulbasaur",
  "base_stats": {
    "hp": 45,
    "attack": 49
  }
}
```

**Output Format (.pkmn):**
```
PKMN:V1
ID:1
NAME:Bulbasaur
HP:45
ATK:49
...
```

### Error Handling

If a JSON file has errors:
- The conversion continues with other files
- Errors are logged with file names and line numbers
- Summary report shows success/failure count

## Troubleshooting

### Issue: "Input directory not found"

**Solution:** Verify the input_dir path exists and contains JSON files. Run PokeAPI Downloader first if you haven't downloaded data yet.

### Issue: "Conversion failed - invalid JSON"

**Solution:** Some JSON files may be corrupted. Delete them and re-download using PokeAPI Downloader.

### Issue: "Type conversion error"

**Solution:** Check if the JSON structure matches expected format. Look at the log for specific field causing issues.

### Issue: "Output files are incomplete"

**Solution:** If conversion was interrupted, delete the output directory and retry. The plugin should complete all files.

### Issue: Validation errors reported

**Solution:** These don't stop conversion but indicate data quality issues. Review the log and consider using older/stable data sources.

## Related Plugins

- [PokeAPI Downloader](pokeapi_downloader.md) - Download JSON data to convert
- [Move Converter](move_converter.md) - Specialized move data conversion
- [Consolidate Files](consolidate_files.md) - Organize converted files

## Version History

- **1.0.0**: Initial release
- **1.1.0**: Added validation support
- **1.2.0**: Improved error reporting
- **1.3.0**: Added batch conversion for multiple types

## Technical Details

**Input Formats:** JSON (PokéAPI compatible)

**Output Format:** Game-native .pkmn format

**Supported Data Types:**
- Pokémon (species, forms, stats)
- Moves (power, accuracy, effects)
- Items (effects, held item mechanics)
- Abilities (descriptions, effects)

**Processing:** Line-by-line with streaming for large files

**Memory Efficient:** Can handle hundreds of files without excessive memory usage
