# Move Effects Analyzer

Comprehensive analysis tool that scans all move effects in the Pokemon database to identify required functions and variables for implementing move mechanics.

## Overview

This plugin performs deep analysis of move effects to help with:

1. **Function Requirements** - What functions need to be implemented to handle all move types
2. **Variable Tracking** - What battle state variables must be tracked to resolve move effects
3. **Implementation Planning** - Guidance on how to structure the move system

The analyzer scans every move in the database and categorizes effects by the mechanics they require.

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| moves_dir | Directory | Yes | Path to pokeapi_database/move containing all move JSON files |

## Usage Examples

### Example 1: Analyze Default Database

**Steps:**
1. Keep "Moves Directory" at default: `pokeapi_database/move`
2. Click "Analyze"
3. Wait for scan to complete (takes 10-30 seconds depending on database size)
4. Review results in the output area

**Result:** Complete breakdown of all required functions and variables.

### Example 2: Save Results for Development

**Steps:**
1. Run analysis as above
2. Results are printed to console (can be redirected to file)
3. Copy-paste output to documentation
4. Use categories as implementation roadmap

**Result:** A checklist of function categories and variables to implement.

## Understanding the Results

### Summary Section

Shows:
- Total unique move effects found
- Number of function categories identified
- Number of variable types to track
- Top 10 most common functions
- Top 10 most common variables

### Function Categories

Categories of moves that require specific handling:

- **drain** - Moves that restore user HP based on damage
- **recoil** - Moves that damage the user
- **healing** - Moves that restore HP
- **status_condition** - Moves that apply status effects
- **raise_stats** - Moves that boost stats
- **lower_stats** - Moves that reduce stats
- **weather** - Weather-setting moves
- **field_effect** - Terrain and field hazards
- **protect** - Protective/shielding moves
- **stat_swap** - Stat copying/swapping
- **type_change** - Moves that change types
- **accuracy** - Accuracy-modifying moves
- **evasion** - Evasion-modifying moves
- **multi_turn** - Multi-turn charging moves
- **conditional** - Conditional effect moves
- **priority** - Priority-based moves
- **item** - Item interaction moves
- **ability** - Ability interaction moves
- **flinch** - Flinching moves
- **trap** - Trapping moves
- **substitute** - Substitute-related moves
- **damage_scale** - Damage scaling moves
- **switch** - Switch/escape moves
- **forced_move** - Forced action moves
- **contact** - Contact-based moves
- **spread** - Multi-target moves

### Variable Types

Variables that must be tracked:

- **status_condition** - Current status effects on each Pokemon
- **field_effects** - Active field hazards and screens
- **drain_recoil** - HP drain/recoil calculations
- **healing_percentage** - Healing amount calculations
- **stat_changes** - Stat modification tracking
- **type_tracking** - Current Pokemon types
- **turn_counter** - Multi-turn move timing
- **target_tracking** - Target selection data
- **item_tracking** - Held item status
- **ability_tracking** - Active ability data
- **priority_tracking** - Move priority values
- **damage_taken** - Recent damage history
- **previous_state** - Previous turn state
- **hit_count** - Number of hits
- **accuracy_evasion** - Current accuracy/evasion

## Advanced Options

### Interpreting the Analysis

The plugin shows which effects use each function/variable:

- **Most common categories** = Should implement first
- **Few effects per category** = May be optional or low-priority
- **High-count variables** = Core battle state to track

### Development Strategy

1. Start with highest-count functions (most moves affected)
2. Implement core variable tracking
3. Gradually add less common function categories
4. Test thoroughly as you implement

## Troubleshooting

### Issue: "Moves directory not found"

**Solution:** Ensure the path exists and contains `*.json` files from the PokeAPI.

### Issue: Analysis shows very few effects

**Possible Causes:**
1. Database not downloaded
2. Effect data missing from move files
3. Wrong directory path

**Solution:**
1. Run PokeAPI Downloader plugin first
2. Verify move files have `effect_entries` field
3. Check directory path is correct

### Issue: Analysis takes too long

**Cause:** Large database with thousands of moves

**Solution:** This is normal. Analysis is thorough. Run during low-activity times.

### Issue: Some effects missing

**Cause:** Analysis uses regex patterns which may miss some effects

**Solution:** Patterns are updated as new effect types are discovered. Consider:
1. Running multiple analyses
2. Manually reviewing unusual effects
3. Reporting patterns that need updating

## Technical Details

### How the Analysis Works

1. **Scanning** - Reads all `.json` files in the moves directory
2. **Extraction** - Pulls `short_effect` field from `effect_entries`
3. **Pattern Matching** - Uses regex patterns to categorize effects
4. **Grouping** - Collects effects by function and variable needs
5. **Reporting** - Generates summary and detailed breakdown

### Data Format Expected

Move files should follow this structure:
```json
{
  "name": "move_name",
  "effect_entries": [
    {
      "short_effect": "Effect description"
    }
  ]
}
```

### Pattern Matching

The analyzer uses regex patterns to identify effect types. Patterns match keywords like:
- "drain", "absorb", "leech" for drain effects
- "recoil", "backfire" for recoil effects
- "burn", "freeze", "paralyze" for status effects
- And many more...

## Integration with Other Plugins

### Related Plugins

- [Field Effects Analyzer](analyze_field_effects.md) - Specific field effect analysis
- [PokeAPI Downloader](pokeapi_downloader.md) - Download move database
- [Move Converter](move_converter.md) - Convert effects to game format

### Output Use Cases

Results can feed into:
1. Move system implementation planning
2. Battle engine variable requirements
3. Status effect system design
4. Field/terrain system design
5. Damage calculation system

## Performance Notes

- **Speed:** 10-30 seconds depending on database size
- **Memory:** Low - processes files one at a time
- **Output:** Can be quite large (100+ KB) for full databases
- **CPU:** Single-threaded, moderate usage

## Version History

- **1.0.0** (Jan 2026): Initial release
  - Function categorization
  - Variable requirement analysis
  - Comprehensive reporting
  - GUI output display
