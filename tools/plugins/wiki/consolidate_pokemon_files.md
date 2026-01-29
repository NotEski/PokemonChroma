# Pokemon File Consolidator

Reorganizes Pokemon data files by moving .pkmn files from subdirectories to the parent directory and cleaning up unnecessary JSON files and empty folders.

## Overview

This plugin restructures the Pokemon data directory from:
```
data/pokemon/
  ├── 0001-Bulbasaur/
  │   ├── 0001-Bulbasaur.pkmn
  │   └── base_pokemon.json
  ├── 0002-Ivysaur/
  │   ├── 0002-Ivysaur.pkmn
  │   └── base_pokemon.json
```

To:
```
data/pokemon/
  ├── 0001-Bulbasaur.pkmn
  ├── 0002-Ivysaur.pkmn
```

This consolidation simplifies file organization and reduces directory clutter.

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| pokemon_dir | Directory | Yes | Path to data/pokemon directory containing Pokemon subdirectories |
| dry_run | Checkbox | No | Preview changes without modifying files (recommended first run) |

## Usage Examples

### Example 1: Preview Changes (Recommended First)

**Steps:**
1. Leave "Pokemon Directory" at default: `data/pokemon`
2. Ensure "Dry Run" is checked ✓
3. Click "Execute"
4. Review what would be changed in the output
5. If satisfied, uncheck "Dry Run" and click Execute again

**Result:** No files modified, but you see exactly what will happen.

### Example 2: Apply Consolidation

**Steps:**
1. Follow Example 1 to preview changes
2. Uncheck "Dry Run (Preview Changes)"
3. Click "Execute"
4. Wait for completion
5. Verify results in your file browser

**Result:** Pokemon files reorganized and cleaned up.

### Example 3: Custom Pokemon Directory

**Steps:**
1. Click the folder icon next to "Pokemon Directory"
2. Navigate to a custom location if needed
3. Check "Dry Run" first
4. Click Execute

**Result:** Consolidation performed on custom directory structure.

## Understanding the Results

### Output Information

**Files Moved:** Number of .pkmn files successfully moved to parent directory

**JSON Files Deleted:** Number of base_pokemon.json and other JSON files removed

**Directories Removed:** Number of now-empty Pokemon subdirectories deleted

**Files Skipped:** Number of Pokemon subdirectories that didn't have .pkmn files (may indicate corrupted data)

### Safety Features

**Dry Run Mode (Enabled by Default):**
- Shows exactly what would happen
- Makes NO file changes
- Safe to run multiple times
- Always use this first!

**Error Reporting:**
- Lists any files that couldn't be moved/deleted
- Shows which directories couldn't be removed (if not empty)
- Helps identify data corruption

## Advanced Options

### When to Use This Plugin

**Use if:**
- Reorganizing Pokemon data after import
- Cleaning up after PokeAPI download
- Standardizing directory structure
- Reducing filesystem depth

**Don't use if:**
- Your Pokemon directory already has .pkmn files in parent directory
- You have custom JSON files in subdirectories you want to keep
- Your directory structure differs from standard format

### Backup Recommendations

Before running (without Dry Run):
1. Create a backup of `data/pokemon/` directory
2. Copy to `data/pokemon_backup/`
3. Then run consolidation
4. Verify results match expectations

### Handling Errors

**If you see "Files skipped":**
- These Pokemon directories don't have matching .pkmn files
- Check if they're corrupted or have different naming
- May need manual cleanup

**If directory removal fails:**
- Directory has other files besides JSON
- These files are preserved (good!)
- May need manual cleanup if unwanted
- Check for `.DS_Store`, `.gitkeep`, or other hidden files

## Troubleshooting

### Issue: "Pokemon directory not found"

**Solution:** Verify the path exists. Default is `data/pokemon/` relative to toolbox root.

### Issue: "Files skipped" count is high

**Causes:**
1. Pokemon files have different names than parent directory
2. Data corruption
3. Mixed naming conventions

**Solutions:**
1. Verify your data structure is correct
2. Run PokeAPI Downloader to repopulate database
3. Manually check skipped directories

### Issue: Directory removal fails

**Cause:** Directory still contains files other than .pkmn and JSON

**Solution:**
1. Manually inspect the directory
2. Remove or move non-JSON files
3. Re-run consolidation

### Issue: Changes not applied even after unchecking Dry Run

**Cause:** Still in Dry Run mode

**Solution:**
1. Check the "Dry Run" checkbox is really unchecked
2. The output should show "CONSOLIDATION IN PROGRESS" not "DRY RUN MODE"
3. Click Execute again

## Related Plugins

- [PokeAPI Downloader](pokeapi_downloader.md) - Download Pokemon data
- [Pokemon Data Generator](pokemon_data.py.md) - Generate game database
- [Asset Downloader](asset_downloader.md) - Download Pokemon artwork

## Technical Details

### What This Plugin Does

1. **Discovery** - Scans all subdirectories in pokemon_dir
2. **Extraction** - Finds {name}/{name}.pkmn files
3. **Moving** - Relocates .pkmn files to parent directory
4. **Cleaning** - Deletes .json files in subdirectories
5. **Removal** - Deletes now-empty subdirectories

### File Matching

- Expects subdirectory name to match .pkmn filename
- Example: `0001-Bulbasaur/0001-Bulbasaur.pkmn`
- Skips if names don't match

### Safety Considerations

- Uses shutil for atomic moves
- Deletes only .json files (JSON safety check)
- Only removes completely empty directories
- Full error reporting
- Dry Run mode for preview

## Performance

- **Speed:** Varies with number of Pokemon (usually < 5 seconds)
- **Memory:** Very low - processes files individually
- **Disk I/O:** Moderate - file moving operation

## Version History

- **1.0.0** (Jan 2026): Initial release
  - Consolidation to parent directory
  - JSON file cleanup
  - Dry Run mode
  - Error reporting
