# Type Chart Generator

Generate Pokémon type effectiveness data in multiple formats. This plugin creates comprehensive type matchup charts that define which types are strong/weak against each other, powering the damage calculation and battle systems.

## Overview

The Type Chart Generator plugin builds a complete Pokémon type effectiveness database. It generates type matchup tables showing super-effectiveness, resistance, immunity, and neutral damage relationships. The output can be used for damage calculations, team building advice, and in-game references.

**Use this plugin to:**
- Create type matchup reference charts
- Generate data for damage calculators
- Export type effectiveness for battle AI
- Support type-based game mechanics
- Build training data for move recommendations

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| output_file | File | Yes | Output file path (supports .json, .csv, .txt) |
| include_dual_types | Checkbox | No | Include dual-type matchup calculations |
| generation | Select | No | Pokémon generation (affects type mechanics) |

## Usage Examples

### Example 1: Generate JSON Type Chart

Create a machine-readable type effectiveness database.

Steps:
1. Set `output_file` to `data/types/type_chart.json`
2. Check `include_dual_types` for complete matchup data
3. Set `generation` to "9" (current generation)
4. Click Execute

Expected result: JSON file with complete type matchup data suitable for damage calculations.

### Example 2: Generate Human-Readable Chart

Create a text chart for reference.

Steps:
1. Set `output_file` to `data/types/type_chart.txt`
2. Leave `include_dual_types` unchecked for simpler output
3. Set `generation` to "9"
4. Click Execute

Expected result: Text file with formatted type matchup tables for easy reference.

### Example 3: Generate CSV for Analysis

Create a spreadsheet-compatible format for data analysis.

Steps:
1. Set `output_file` to `data/types/type_effectiveness.csv`
2. Check `include_dual_types`
3. Set `generation` to "9"
4. Click Execute

Expected result: CSV file that opens in Excel/Sheets for analysis and reporting.

## Advanced Options

### Generation Selection

Different Pokémon generations have different type matchups:
- **Gen 1-5**: Original type chart (no Fairy type)
- **Gen 6-8**: Includes Fairy type adjustments
- **Gen 9**: Latest mechanics (Stellar type for Terastallization)

Select the generation matching your game mechanics.

### Dual-Type Matchups

When `include_dual_types` is checked, the plugin calculates:
- How each type combination resists/weakens
- Optimal coverage moves for dual-type Pokémon
- Multi-type synergy analysis

### Output Formats

**JSON Format:**
```json
{
  "fire": {
    "super_effective_against": ["grass", "ice", "bug", "steel"],
    "weak_to": ["water", "ground", "rock"],
    "resists": ["fire", "grass", "ice", "bug", "steel"],
    "immune_to": []
  }
}
```

**CSV Format:**
```
Type,Super Effective Against,Weak To,Resists,Immune To
Fire,"Grass, Ice, Bug, Steel","Water, Ground, Rock","Fire, Grass, Ice, Bug, Steel",""
```

## Troubleshooting

### Issue: "Output file already exists"

**Solution:** The plugin will overwrite the file. If you want to keep the old version, rename or move it first.

### Issue: "Invalid output path"

**Solution:** Ensure the output directory exists and you have write permissions. Create directories if needed.

### Issue: "Unknown generation"

**Solution:** Select a valid generation (1-9). If you're not sure, use generation 9 (current).

### Issue: Generated data seems incomplete

**Solution:** Run the plugin again. Some API calls may timeout on first attempt. The plugin has built-in retry logic.

## Related Plugins

- [PokeAPI Downloader](pokeapi_downloader.md) - Get type data from API
- [Move Converter](move_converter.md) - Convert move data including type info
- [Pokémon Data Generator](pokemon_data.md) - Integrate type data into Pokémon database

## Version History

- **1.0.0**: Initial release
- **1.1.0**: Added generation selection
- **1.2.0**: Added CSV export support
- **1.3.0**: Improved dual-type calculations

## Technical Details

**Data Source:** Built-in type mechanics database

**Generations Supported:** 1-9 (1025+ Pokémon)

**Matchup Accuracy:** Verified against official Pokémon games

**Output Formats:** JSON, CSV, TXT

**Calculation Method:** Matrix-based effectiveness lookup
