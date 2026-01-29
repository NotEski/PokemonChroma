# Move Metadata Converter

Converts move .pkmn files from the legacy meta dict format to the modern MoveMetaData format, enabling compatibility with the updated move system.

## Overview

This plugin automatically converts move files from:

```python
# Old format
@move("tackle")
class Tackle:
    meta = {
        "display_name": "Tackle",
        "index": 33,
        "type": "normal",
        "damage_class": "physical",
        "category": "damage",
        "accuracy": 100,
        "power": 40,
        "pp": 35,
        "target": "selected_pokemon",
    }
    # ... attributes
```

To:

```python
# New format
from pkmn_imports import *

@move("tackle")
class Tackle:
    meta = MoveMetaData(
        display_name="Tackle",
        index=33,
        type=PokemonType("normal"),
        damage_class=DamageClass.PHYSICAL,
        category=MoveCategory.DAMAGE,
        accuracy=100,
        power=40,
        pp=35,
        target=MoveTarget.SELECTED_POKEMON,
    )
    # ... attributes
```

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| moves_dir | Directory | Yes | Path to data/moves directory containing move .pkmn files |
| dry_run | Checkbox | No | Preview changes without modifying files (recommended first run) |

## Usage Examples

### Example 1: Preview Conversions (Recommended First)

**Steps:**
1. Leave "Moves Directory" at default: `data/moves`
2. Ensure "Dry Run" is checked ✓
3. Click "Execute"
4. Review what would be converted in the output
5. Check for any errors that need fixing
6. If satisfied, uncheck "Dry Run" and run again

**Result:** No files modified, but you see exactly what will happen.

### Example 2: Apply Conversion

**Steps:**
1. Follow Example 1 to preview changes
2. Uncheck "Dry Run (Preview Changes)"
3. Click "Execute"
4. Wait for completion
5. Verify your move files are updated

**Result:** All eligible move files converted to new format.

### Example 3: Custom Moves Directory

**Steps:**
1. Click the folder icon next to "Moves Directory"
2. Navigate to a custom location if needed
3. Check "Dry Run" first
4. Click Execute

**Result:** Conversion performed on custom directory.

## Understanding the Results

### Output Information

**Files Converted:** Move files successfully converted to MoveMetaData format

**Already Converted:** Move files that were already in the new format (skipped)

**Failed:** Move files that couldn't be converted (check errors)

### Conversion Details

The plugin automatically:
1. Adds `from pkmn_imports import *` import
2. Converts meta dict to MoveMetaData constructor
3. Converts string values to appropriate enum types:
   - `"physical"` → `DamageClass.PHYSICAL`
   - `"special"` → `DamageClass.SPECIAL`
   - `"status"` → `DamageClass.STATUS`
   - `"damage"` → `MoveCategory.DAMAGE`
   - `"status"` → `MoveCategory.STATUS`
   - And similar for other enum fields
4. Wraps type values with `PokemonType()`
5. Preserves all other class attributes unchanged

## Safety Features

### Dry Run Mode (Enabled by Default)

- Shows exactly what would be converted
- Makes NO file changes
- Lists which files are already converted
- Reports any parsing errors
- Safe to run multiple times

### Skip Already-Converted Files

- Detects if file already has new import statement
- Skips these files automatically
- Prevents re-conversion

### Error Reporting

- Lists files that couldn't be parsed
- Shows which files had errors during conversion
- Preserves original files if errors occur

## Advanced Options

### When to Use This Plugin

**Use if:**
- Updating move files to new system
- After importing from PokeAPI
- Standardizing your move format
- Preparing for type system upgrade

**Don't use if:**
- Your moves are already in MoveMetaData format
- You have custom move format not following meta dict structure
- You want to preserve legacy format

### Backup Recommendations

Before running (without Dry Run):
1. Create a backup of `data/moves/` directory
2. Copy to `data/moves_backup/`
3. Then run conversion
4. Verify all files converted successfully

## Troubleshooting

### Issue: "Moves directory not found"

**Solution:** Verify the path exists and contains `.pkmn` files.

### Issue: Many files show "Failed to parse"

**Causes:**
1. Files don't match expected meta dict format
2. Move files have been manually edited or corrupted
3. Different naming conventions

**Solutions:**
1. Verify files follow standard @move decorator and meta dict format
2. Manually inspect failed files
3. Report the format difference for pattern update

### Issue: Enums not being converted correctly

**Example:** `"physical"` not becoming `DamageClass.PHYSICAL`

**Cause:** Value format doesn't match expected pattern (e.g., missing quotes)

**Solution:**
1. Check the original file format
2. Report specific examples for pattern fix
3. May require manual conversion of special cases

### Issue: Other attributes missing after conversion

**Cause:** Regex pattern for other_attrs didn't match all attributes

**Solution:**
1. Manually add missing attributes
2. Report the attribute format for pattern update
3. Consider manually editing files with complex structures

### Issue: Conversion reverted after running again

**Cause:** Re-running with dry_run=false on already converted file

**Solution:**
1. Plugin detects already-converted files and skips them
2. If re-running: uncheck "Dry Run" only for actual conversion
3. Check the import statement to verify if converted

## Technical Details

### Conversion Process

1. **Scanning** - Finds all `.pkmn` files in directory
2. **Detection** - Checks if already converted (has import statement)
3. **Parsing** - Extracts move metadata using regex patterns
4. **Extraction** - Pulls decorator, class name, meta dict, other attributes
5. **Conversion** - Transforms to MoveMetaData format with enum wrapping
6. **Writing** - Writes converted content back to file

### Parsing Patterns

The converter uses regex to extract:
- `@move("name")` decorator and class name
- Meta dict with key-value pairs
- Additional class attributes

Handles:
- Quoted string values
- Nested structures
- Multi-line formatting
- Comments

### Data Format Expected

Move files should follow structure:
```python
@move("move_name")
class MoveName:
    meta = {
        "display_name": "...",
        "index": ...,
        "type": "...",
        ...
    }
    
    # Other attributes
    priority = 0
    accuracy = 100
    ...
```

## Integration with Other Plugins

### Related Plugins

- [Move Analyzer](analyze_moves.md) - Analyze move effects
- [Field Effects Analyzer](analyze_field_effects.md) - Analyze field effects
- [PokeAPI Downloader](pokeapi_downloader.md) - Generate move data

### Output Uses

Converted files can be:
1. Imported by the game engine
2. Analyzed for move mechanics
3. Extended with new effects
4. Integrated with type system

## Performance

- **Speed:** Depends on number of moves (usually < 5 seconds)
- **Memory:** Very low - processes files individually
- **Disk I/O:** Moderate - file reading and writing

## Version History

- **1.0.0** (Jan 2026): Initial release
  - Meta dict to MoveMetaData conversion
  - Enum type wrapping
  - Already-converted detection
  - Error reporting
  - Dry Run mode
