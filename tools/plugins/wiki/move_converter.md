# Move Converter

Convert and normalize Pokémon move data into game-ready metadata format. This plugin processes raw move data, extracts mechanics, calculates effects, and generates the standardized move metadata used by the battle engine.

## Overview

The Move Converter plugin transforms raw move data into game-specific metadata format. It handles move parsing, effect calculation, priority normalization, and category classification. The output powers move selection, damage calculation, and battle AI decision-making.

**Use this plugin to:**
- Convert raw move data to game format
- Generate move metadata from JSON sources
- Extract move effects and mechanics
- Validate move data integrity
- Build move reference database for AI

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| input_file | File | Yes | Input move data file (JSON or raw text) |
| output_file | File | Yes | Output metadata file path |
| include_flavor_text | Checkbox | No | Include move descriptions and flavor text |
| generation | Select | No | Pokémon generation for move mechanics |

## Usage Examples

### Example 1: Convert Move JSON to Metadata

Convert downloaded JSON move data to game format.

Steps:
1. Set `input_file` to `data/moves/moves.json`
2. Set `output_file` to `data/moves/move_metadata.txt`
3. Check `include_flavor_text` for complete descriptions
4. Set `generation` to "9"
5. Click Execute

Expected result: Move metadata file with all moves properly formatted for the game engine.

### Example 2: Convert Multiple Move Files

Process a batch of move data files.

Steps:
1. First, organize move files in a source directory
2. Run converter on each file or use batch input
3. Specify output directory
4. Set generation to match your game version
5. Click Execute

Expected result: All move files converted and organized in output directory.

### Example 3: Update Move Generation

Convert existing move data to a newer generation's mechanics.

Steps:
1. Set `input_file` to current moves data
2. Set `output_file` to new generation output
3. Set `generation` to target generation (e.g., "9" for Gen 9)
4. Click Execute

Expected result: Moves updated with new generation mechanics and type changes.

## Advanced Options

### Generation Selection

Different generations have different move mechanics:
- **Gen 1-5**: Classic movepool
- **Gen 6-8**: Physical/Special split, new moves
- **Gen 9**: Latest moves, mechanics updates

### Move Data Processing

The converter handles:
- **Power and Accuracy**: Normalizing and validating values
- **Move Types**: Validating type assignments
- **Categories**: Physical/Special/Status classification
- **Effects**: Parsing secondary effects and probabilities
- **Priority**: Handling priority levels (-7 to +5)
- **Targets**: Single/Multi/Self/User targeting

### Output Format

Generated metadata includes:
```
MOVE:Thunder Bolt
ID:24
TYPE:Electric
POWER:90
ACCURACY:100
CATEGORY:Special
PRIORITY:0
EFFECT:10% chance to paralyze
DESCRIPTION:A powerful Electric-type move...
```

## Troubleshooting

### Issue: "Invalid move data format"

**Solution:** Verify input file matches expected JSON or raw format. Check file for corruption.

### Issue: "Parsing error on line X"

**Solution:** The specific line has invalid data. Edit that line or remove it and retry.

### Issue: "Unknown move type"

**Solution:** Ensure move types are valid Pokémon types (Fire, Water, Electric, etc.)

### Issue: "Output file already exists"

**Solution:** The converter will overwrite by default. Rename the output file if you want to preserve it.

### Issue: "Generation incompatible"

**Solution:** Select a supported generation (1-9). If using custom moves, select the closest standard generation.

## Related Plugins

- [PokeAPI Downloader](pokeapi_downloader.md) - Download move data source
- [JSON to Pokémon Converter](json_converter.md) - General data conversion
- [Type Chart Generator](type_chart.md) - Generate type effectiveness for moves

## Version History

- **1.0.0**: Initial release
- **1.1.0**: Added generation selection
- **1.2.0**: Improved effect parsing
- **1.3.0**: Added flavor text support
- **1.4.0**: Better error recovery

## Technical Details

**Input Formats:** JSON, Raw text, CSV

**Output Format:** Game-native move metadata

**Supported Generations:** 1-9 (1000+ moves)

**Processing Method:** Line-by-line parsing with effect extraction

**Validation:** Checks all moves against official movepool data

**Performance:** Processes 100+ moves per second
