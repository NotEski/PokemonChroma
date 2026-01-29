# Field Effects Analyzer

Analyzes and categorizes field effects in move data, helping understand the game's field-based mechanics.

## Overview

This plugin scans the Pokemon move database and identifies all moves that have field effects, such as:
- Room effects (Trick Room, Wonder Room, Magic Room)
- Protective barriers (Reflect, Light Screen, Aurora Veil)
- Hazards (Stealth Rock, Spikes, Toxic Spikes, Sticky Web)
- Status effects (Safeguard, Mist)
- Speed/Initiative effects (Tailwind)
- G-Max effects
- Other field manipulation moves

The analyzer **excludes** weather and terrain effects to focus specifically on persistent field effects.

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| moves_dir | Directory | Yes | Path to the pokeapi_database/move directory containing move JSON files |

## Usage Examples

### Example 1: Default Analysis

**Steps:**
1. Leave "Moves Directory" at default: `pokeapi_database/move`
2. Click "Analyze"
3. Wait for analysis to complete
4. Review results in the output area

**Result:** Complete categorized list of all field effect moves with their descriptions.

### Example 2: Custom Move Database

**Steps:**
1. Click the folder icon next to "Moves Directory"
2. Navigate to a custom moves database location
3. Select the folder and click "Analyze"

**Result:** Analysis performed on custom move data.

## Understanding the Results

### Output Sections

**Header Information:**
- Total count of moves with field effects
- Number of effect categories found

### Field Effect Categories

The results are organized into these categories:

- **Trick Room** - Reverses speed order
- **Wonder Room** - Equalizes Defense/Sp.Def stats
- **Magic Room** - Disables held items
- **Reflect** - Physical damage barrier
- **Light Screen** - Special damage barrier
- **Aurora Veil** - Combined barrier effect
- **Stealth Rock** - Entry hazard
- **Spikes** - Layer-based entry hazard
- **Toxic Spikes** - Poisoning entry hazard
- **Sticky Web** - Speed reduction entry hazard
- **Safeguard** - Status protection
- **Mist** - Stat reduction prevention
- **Tailwind** - Speed boost aura
- **G-Max Effects** - Gigantamax-exclusive effects
- **Other Field Effects** - Miscellaneous field effects

## Advanced Options

### Filtering Results

The analyzer automatically excludes:
- Weather-related moves (Rain, Sunny, Hail, Sandstorm, Snow)
- Terrain moves (Electric Terrain, Grassy Terrain, Misty Terrain, Psychic Terrain)

This keeps the results focused on **persistent field effects** rather than temporary weather changes.

## Troubleshooting

### Issue: "Moves directory not found"

**Solution:** Ensure the path exists and points to a directory containing move JSON files. The default path is `pokeapi_database/move` relative to the toolbox root.

### Issue: No results or very few results

**Possible Causes:**
1. Move database not populated - Run the PokeAPI downloader first
2. Incorrect directory path - Verify the moves directory contains `.json` files
3. Move data missing effect_entries - Some moves may not have effect data

**Solution:** 
1. Use the PokeAPI Downloader plugin to populate the database
2. Verify the directory structure manually
3. Check individual move files for proper formatting

### Issue: Analysis takes a long time

**Cause:** Large move databases with thousands of files

**Solution:** This is normal. The plugin processes each move file individually. Consider running this during off-peak times.

## Technical Details

### How It Works

1. **Discovery:** Scans all `.json` files in the moves directory
2. **Filtering:** Skips the `_index.json` file
3. **Extraction:** Reads `effect_entries` from each move
4. **Exclusion:** Filters out weather/terrain keywords
5. **Detection:** Looks for field effect keywords in move descriptions
6. **Categorization:** Groups moves by effect type
7. **Output:** Generates formatted analysis

### Data Format

Input files should be JSON with structure:
```json
{
  "name": "move_name",
  "effect_entries": [
    {
      "short_effect": "Effect description",
      ...
    }
  ],
  ...
}
```

## Related Plugins

- [Move Analyzer](analyze_moves.md) - Analyze all move effects
- [PokeAPI Downloader](pokeapi_downloader.md) - Populate the move database
- [Move Converter](move_converter.md) - Convert move data to game format

## Version History

- **1.0.0** (Jan 2026): Initial release
  - Field effect categorization
  - Weather/terrain filtering
  - GUI analysis interface
  - Formatted text output
