# Asset Downloader

Download and organize Pokémon artwork from official sources. This plugin retrieves high-quality artwork, sprites, and official artwork for all Pokémon and saves them organized by Pokédex number.

## Overview

The Asset Downloader plugin automates the process of downloading Pokémon artwork from official sources (primarily PokéAPI) and organizing them into a structured directory hierarchy. Each Pokémon gets its own folder containing artwork in multiple formats and resolutions.

**Use this plugin to:**
- Download complete artwork collections for game assets
- Organize artwork by Pokédex number
- Maintain consistent directory structure across art assets
- Support multiple image formats (official artwork, sprites, shiny variants)

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| output_dir | Folder | Yes | Directory where downloaded artwork will be saved |
| start_pokemon | Number | No | Pokédex number to start from (default: 1, Bulbasaur) |
| end_pokemon | Number | No | Pokédex number to end at (default: 1025, Pecharunt) |
| overwrite | Checkbox | No | Overwrite existing files if they already exist |

## Usage Examples

### Example 1: Download All Pokémon Artwork

Download the complete official artwork collection for all Pokémon.

Steps:
1. Click the folder icon next to "output_dir" and select `C:\PokemonFanGame\assets\pokemon`
2. Leave `start_pokemon` and `end_pokemon` empty (defaults to all)
3. Leave `overwrite` unchecked (preserve existing files)
4. Click Execute

Expected result: All 1025 Pokémon artwork files are downloaded and organized into numbered directories (0001-Bulbasaur/, 0002-Ivysaur/, etc.)

### Example 2: Download Specific Range

Download artwork for only the first generation (Pokédex #1-151).

Steps:
1. Set output directory to your assets folder
2. Set `start_pokemon` to `1`
3. Set `end_pokemon` to `151`
4. Click Execute

Expected result: Only Gen 1 Pokémon artwork is downloaded, saving time and bandwidth.

### Example 3: Update with Overwrite

Re-download artwork, replacing any outdated files.

Steps:
1. Set output directory
2. Set `start_pokemon` to `1`
3. Set `end_pokemon` to `100`
4. Check the `overwrite` checkbox
5. Click Execute

Expected result: Even if artwork exists, it will be re-downloaded and replaced with the latest version.

## Advanced Options

### Resuming Interrupted Downloads

If a download is interrupted, restart the plugin with the same settings. It will skip already-downloaded files and continue where it left off (unless `overwrite` is checked).

### Bandwidth Considerations

- Full collection (all 1025 Pokémon): ~500MB-1GB
- Gen 1 only (151 Pokémon): ~50-100MB
- Use `start_pokemon` and `end_pokemon` to download in batches

### Artwork Organization

Downloaded artwork follows this structure:
```
assets/pokemon/
├── 0001-Bulbasaur/
│   ├── official.png
│   └── metadata.json
├── 0002-Ivysaur/
│   ├── official.png
│   └── metadata.json
└── ...
```

## Troubleshooting

### Issue: "Network error" or connection timeout

**Solution:** Check your internet connection and try again. If the issue persists, the API service may be temporarily unavailable. Wait a few minutes and retry.

### Issue: Permission denied on output_dir

**Solution:** Ensure you have write permissions to the directory. Try running as administrator or choose a different directory you have access to.

### Issue: Disk space error

**Solution:** You may not have enough free space. Check available storage and ensure at least 1GB is free for full collection download.

### Issue: Some files show 404 errors

**Solution:** This is normal—some official artwork may not be available for newer Pokémon or variants. The plugin logs which files succeeded; failed downloads won't block the process.

## Related Plugins

- [PokeAPI Downloader](pokeapi_downloader.md) - Download comprehensive Pokémon data
- [Type Chart Generator](type_chart.md) - Generate type effectiveness data
- [Consolidate Files](consolidate_files.md) - Organize downloaded assets

## Version History

- **1.0.0**: Initial release
- **1.1.0**: Added overwrite option and improved error handling
- **1.2.0**: Optimized for large collections with resume capability

## Technical Details

**Data Source:** PokéAPI (https://pokeapi.co/)

**File Formats:** PNG images with metadata JSON

**Rate Limiting:** Respectful API usage with delays between requests
