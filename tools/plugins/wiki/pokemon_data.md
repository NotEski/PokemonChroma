# Pokémon Data Generator

Generate comprehensive Pokémon database from raw data sources. This plugin consolidates Pokémon stats, moves, abilities, and other attributes into a unified game database suitable for gameplay, AI training, and battle mechanics.

## Overview

The Pokémon Data Generator plugin creates the main Pokémon database used by the game engine. It combines data from multiple sources (PokéAPI, custom data, moves, abilities) and generates optimized lookup tables for fast access during gameplay and battle calculations.

**Use this plugin to:**
- Build complete Pokémon database from multiple sources
- Generate optimized stat lookups for performance
- Combine Pokémon, moves, and abilities data
- Create team building reference data
- Generate AI training data

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| source_dir | Folder | Yes | Directory containing Pokémon data files |
| output_dir | Folder | Yes | Directory where generated database will be saved |
| include_stats | Checkbox | No | Include detailed stat calculations and optimizations |
| generation | Select | No | Pokémon generation to generate for (1-9) |

## Usage Examples

### Example 1: Generate Complete Database

Create the main Pokémon database from all available data.

Steps:
1. Ensure all Pokémon data is in `data/pokemon`
2. Set `source_dir` to `data/pokemon`
3. Set `output_dir` to `data/pokemon/generated`
4. Check `include_stats` for full optimization
5. Set `generation` to "9"
6. Click Execute

Expected result: Complete database generated with all Pokémon, forms, moves, and optimized lookups.

### Example 2: Generate for Specific Generation

Create a database for a specific Pokémon generation (e.g., Gen 1 only).

Steps:
1. Set `source_dir` to data directory
2. Set `output_dir` to `data/gen1_database`
3. Set `generation` to "1"
4. Check `include_stats`
5. Click Execute

Expected result: Gen 1 Pokémon database with stats optimized for that generation's mechanics.

### Example 3: Quick Generation (Stats Only)

Generate without detailed optimizations for faster processing.

Steps:
1. Set `source_dir` to `data/pokemon`
2. Set `output_dir` to `data/pokemon/quick`
3. Leave `include_stats` unchecked
4. Set `generation` to "9"
5. Click Execute

Expected result: Basic database generated quickly for testing or temporary use.

## Advanced Options

### Stat Optimization

When `include_stats` is checked:
- Base stats are pre-calculated for all levels (1-100)
- EV/IV combinations are pre-computed
- Stat ranges are generated for team analysis
- Performance index is calculated

### Generation Support

Each generation has different:
- Available Pokémon and forms
- Type matchups
- Move mechanics
- Evolution methods

Select the generation matching your game configuration.

### Database Structure

Generated database includes:
```
pokemon_database/
├── pokemon_stats.db
├── move_lookup.db
├── ability_reference.db
├── item_effects.db
├── type_matchups.db
└── team_presets.db
```

## Troubleshooting

### Issue: "Source directory not found"

**Solution:** Verify the source_dir path exists and contains Pokémon data files. Run PokeAPI Downloader first if needed.

### Issue: "Insufficient data"

**Solution:** The source directory may be incomplete. Run all converters (JSON to Pokémon, Move Converter) to populate source data.

### Issue: "Generation mismatch"

**Solution:** Ensure the source data matches the selected generation. You may need to filter or pre-process data first.

### Issue: "Database generation failed"

**Solution:** Check free disk space and file permissions. The database can be large (100MB+ for full data).

### Issue: "Performance is slow"

**Solution:** Uncheck `include_stats` for faster generation. Optimization calculations are CPU-intensive.

## Related Plugins

- [PokeAPI Downloader](pokeapi_downloader.md) - Download source data
- [JSON to Pokémon Converter](json_converter.md) - Prepare data for generation
- [Move Converter](move_converter.md) - Prepare move data
- [Type Chart Generator](type_chart.md) - Generate type effectiveness

## Version History

- **1.0.0**: Initial release
- **1.1.0**: Added stat optimization
- **1.2.0**: Added generation selection
- **1.3.0**: Improved performance with caching

## Technical Details

**Input Sources:** Converted Pokémon data files

**Output Format:** Optimized binary database

**Database Size:** 100-500MB depending on options

**Pokémon Coverage:** All generations 1-9 (1025+ Pokémon)

**Processing Time:** 5-30 minutes depending on options and hardware

**Memory Requirement:** 1-4GB during generation

**Use Case:** Game runtime access, AI training, team building reference
