#!/usr/bin/env python3
"""
Convert Pokemon JSON files to .pkmn Python files.

This tool reads base_pokemon.json files from the data/pokemon directories
and generates corresponding .pkmn files with Python class definitions.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, List


def convert_json_to_pkmn(json_data: Dict[str, Any], pokemon_name: str) -> str:
    """Convert a JSON pokemon definition to a .pkmn Python file format."""
    
    lines = []
    lines.append("from shared.pokemon.stats import BaseStats, EffortYield")
    lines.append("")
    lines.append("")
    
    # Check if this is a mega evolution (has no moves and different pokedex number)
    is_mega = (
        json_data.get("moves", {}).get("level", {}) == {} and
        json_data.get("moves", {}).get("machine", []) == [] and
        json_data.get("pokedex_number", 0) > 10000
    )
    
    moves_data = json_data.get("moves", {})
    level_moves = moves_data.get("level", {})
    machine_moves = moves_data.get("machine", [])
    tutor_moves = moves_data.get("tutor", [])
    egg_moves = moves_data.get("egg_moves", [])
    
    if is_mega:
        # Mega Evolution class
        base_name = json_data.get("name", pokemon_name).replace("_mega", "").replace("_gmax", "")
        class_name = "".join(word.capitalize() for word in base_name.split("_"))
        
        # Get the mega form name for the decorator
        mega_form = json_data.get("name", pokemon_name)
        
        lines.append(f'@mega_evolution("{mega_form}")')
        lines.append(f"class Mega{class_name}:")
        lines.append(f'    display_name = "{json_data.get("display_name", class_name)}"')
        lines.append(f'    id = {json_data.get("pokedex_number", 0)}')
        
    else:
        # Regular Pokemon class
        class_name = "".join(word.capitalize() for word in pokemon_name.split("_"))
        
        lines.append(f'@pokemon("{pokemon_name}")')
        lines.append(f"class {class_name}:")
        lines.append(f'    display_name = "{json_data.get("display_name", class_name)}"')
        lines.append(f'    id = {json_data.get("pokedex_number", 0)}')
        
        # Types
        types = json_data.get("types", [])
        if types:
            lines.append(f'    types = {types}')
    
    # Base stats
    base_stats = json_data.get("base_stats", {})
    lines.append("    base_stats = BaseStats(")
    lines.append(f"        hp={base_stats.get('hp', 0)},")
    lines.append(f"        attack={base_stats.get('attack', 0)},")
    lines.append(f"        defense={base_stats.get('defense', 0)},")
    lines.append(f"        special_attack={base_stats.get('special_attack', 0)},")
    lines.append(f"        special_defense={base_stats.get('special_defense', 0)},")
    lines.append(f"        speed={base_stats.get('speed', 0)}")
    lines.append("    )")
    
    if not is_mega:
        # EV Yield
        ev_yield = json_data.get("ev_yield", {})
        lines.append("    ev_yield = EffortYield(")
        lines.append(f"        hp={ev_yield.get('hp', 0)},")
        lines.append(f"        attack={ev_yield.get('attack', 0)},")
        lines.append(f"        defense={ev_yield.get('defense', 0)},")
        lines.append(f"        special_attack={ev_yield.get('special_attack', 0)},")
        lines.append(f"        special_defense={ev_yield.get('special_defense', 0)},")
        lines.append(f"        speed={ev_yield.get('speed', 0)}")
        lines.append("    )")
        
        lines.append(f'    catch_rate = {json_data.get("capture_rate", 45)}')
        lines.append(f'    base_experience_yield = {json_data.get("base_experience_yield", 64)}')
        lines.append(f'    base_happiness = {json_data.get("base_happiness", 70)}')
        lines.append(f'    gender_rate = {json_data.get("gender_rate", 4)}')
        
        # Abilities
        abilities = json_data.get("abilities", [])
        if abilities:
            lines.append("    abilities: list[dict[str, str|int|bool]] = [")
            for ability in abilities:
                lines.append("        {")
                lines.append(f'            "ability": "{ability.get("ability", "")}",')
                lines.append(f'            "slot": {ability.get("slot", 1)},')
                lines.append(f'            "is_hidden": {str(ability.get("is_hidden", False))}')
                lines.append("        },")
            lines.append("    ]")
        
        lines.append(f'    height_m = {json_data.get("height_m", 1.0)}')
        lines.append(f'    weight_kg = {json_data.get("weight_kg", 1.0)}')
        
        # Egg groups
        egg_groups = json_data.get("egg_groups", [])
        if egg_groups:
            lines.append(f'    egg_groups = {egg_groups}')
        
        lines.append(f'    growth_rate = "{json_data.get("growth_rate", "medium")}"')
        
        # Level moves
        if level_moves:
            lines.append("    level_moves: dict[int, list[str]] = {")
            for level, moves in sorted((int(k), v) for k, v in level_moves.items()):
                lines.append(f"            {level}: [")
                for move in moves:
                    lines.append(f'                "{move}",')
                lines.append("            ],")
            lines.append("        }")
        
        # Machine moves
        if machine_moves:
            lines.append("    machine_moves = [")
            for move in machine_moves:
                lines.append(f'        "{move}",')
            lines.append("    ]")
        
        # Tutor moves
        if tutor_moves:
            lines.append("    tutor_moves = [")
            for move in tutor_moves:
                lines.append(f'        "{move}",')
            lines.append("    ]")
        
        # Egg moves
        if egg_moves:
            lines.append("    egg_moves = [")
            for move in egg_moves:
                lines.append(f'        "{move}",')
            lines.append("    ]")
        else:
            lines.append("    egg_moves = []")
    else:
        # Mega evolution fields
        lines.append(f'    mega_evolution_item = "{json_data.get("mega_evolution_item", "")}"')
        lines.append(f'    base_experience_yield = {json_data.get("base_experience_yield", 64)}')
        lines.append(f'    height_m = {json_data.get("height_m", 1.0)}')
        lines.append(f'    weight_kg = {json_data.get("weight_kg", 1.0)}')
    
    return "\n".join(lines)


def process_pokemon_directory(pokemon_dir: Path, overwrite: bool = False) -> bool:
    """Process a single pokemon directory. Returns True if a .pkmn file was created."""
    
    json_file = pokemon_dir / "base_pokemon.json"
    if not json_file.exists():
        return False
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading {json_file}: {e}")
        return False
    
    pokemon_name = json_data.get("name", pokemon_dir.name)
    pkmn_file = pokemon_dir / f"{pokemon_name}.pkmn"
    
    # Check if .pkmn file already exists
    if pkmn_file.exists() and not overwrite:
        print(f"Skipping {pokemon_name} - .pkmn file already exists")
        return False
    
    try:
        pkmn_content = convert_json_to_pkmn(json_data, pokemon_name)
        with open(pkmn_file, 'w', encoding='utf-8') as f:
            f.write(pkmn_content)
        print(f"Created {pkmn_file}")
        return True
    except Exception as e:
        print(f"Error creating .pkmn for {pokemon_name}: {e}")
        return False


def main():
    """Main entry point. Convert all pokemon JSON files to .pkmn files."""
    
    parser = argparse.ArgumentParser(description="Convert Pokemon JSON files to .pkmn Python files")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing .pkmn files")
    args = parser.parse_args()
    
    pokemon_data_dir = Path("data/pokemon")
    
    if not pokemon_data_dir.exists():
        print(f"Error: {pokemon_data_dir} does not exist")
        return
    
    pokemon_dirs = sorted([d for d in pokemon_data_dir.iterdir() if d.is_dir()])
    
    created = 0
    skipped = 0
    
    for pokemon_dir in pokemon_dirs:
        if process_pokemon_directory(pokemon_dir, overwrite=args.overwrite):
            created += 1
        else:
            skipped += 1
    
    print(f"\nConversion complete: {created} created, {skipped} skipped")


if __name__ == "__main__":
    main()
