# JSON to .pkmn Converter

Converts Pokemon JSON data files (`base_pokemon.json`) into `.pkmn` Python class definition files.

## Usage

```bash
python tools/json_to_pkmn_converter.py
```

This will scan all directories in `data/pokemon/` and convert any `base_pokemon.json` files that don't already have a corresponding `.pkmn` file.

## What It Does

- **Reads**: `data/pokemon/<pokemon_name>/base_pokemon.json`
- **Generates**: `data/pokemon/<pokemon_name>/<pokemon_name>.pkmn`
- **Skips**: Any pokemon that already has a `.pkmn` file
- **Handles**: Both regular pokemon and mega evolutions/variants

## Output Format

The generated `.pkmn` files use Python class syntax with decorators:

```python
from shared.pokemon.stats import BaseStats, EffortYield

@pokemon("pokemon_name")
class PokemonName:
    display_name = "Display Name"
    id = 1
    types = ["type1", "type2"]
    base_stats = BaseStats(...)
    # ... more attributes
```

For mega evolutions and variants:

```python
@mega_evolution("mega_pokemon_name")
class MegaPokemon:
    display_name = "Mega Pokemon"
    id = 10001
    base_stats = BaseStats(...)
    # ... mega-specific attributes
```

## Notes

- Existing `.pkmn` files are never overwritten
- All move data (level, machine, tutor, egg) is preserved
- Ability data including slots and hidden ability status is included
- Works with all pokemon variants (regional forms, mega evolutions, gigantamax forms, etc.)
