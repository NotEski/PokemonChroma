#!/usr/bin/env python3
"""
Consolidate Pokemon files by moving .pkmn files to the parent directory
and deleting JSON files and empty subdirectories.

This tool:
1. Moves data/pokemon/<name>/<name>.pkmn to data/pokemon/<name>.pkmn
2. Deletes base_pokemon.json files
3. Removes empty pokemon subdirectories
"""

import argparse
import shutil
from pathlib import Path


def consolidate_pokemon_files(dry_run: bool = False):
    """Move .pkmn files up one level and clean up subdirectories."""
    
    pokemon_data_dir = Path("data/pokemon")
    
    if not pokemon_data_dir.exists():
        print(f"Error: {pokemon_data_dir} does not exist")
        return
    
    pokemon_dirs = sorted([d for d in pokemon_data_dir.iterdir() if d.is_dir()])
    
    moved = 0
    deleted_json = 0
    deleted_dirs = 0
    
    for pokemon_dir in pokemon_dirs:
        pokemon_name = pokemon_dir.name
        
        # Look for the .pkmn file
        pkmn_file = pokemon_dir / f"{pokemon_name}.pkmn"
        if not pkmn_file.exists():
            print(f"Skipping {pokemon_name} - no .pkmn file found")
            continue
        
        # Target location (parent directory)
        target_file = pokemon_data_dir / f"{pokemon_name}.pkmn"
        
        if dry_run:
            print(f"[DRY RUN] Would move: {pkmn_file} -> {target_file}")
        else:
            # Move the .pkmn file
            shutil.move(str(pkmn_file), str(target_file))
            print(f"Moved: {pokemon_name}.pkmn")
            moved += 1
        
        # Delete JSON files in the directory
        json_files = list(pokemon_dir.glob("*.json"))
        for json_file in json_files:
            if dry_run:
                print(f"[DRY RUN] Would delete: {json_file}")
            else:
                json_file.unlink()
                deleted_json += 1
        
        # Remove the now-empty directory
        if not dry_run:
            try:
                # Check if directory is empty or only has files we don't care about
                remaining_files = list(pokemon_dir.iterdir())
                if not remaining_files:
                    pokemon_dir.rmdir()
                    deleted_dirs += 1
                else:
                    print(f"Warning: {pokemon_dir} not empty, contains: {[f.name for f in remaining_files]}")
            except Exception as e:
                print(f"Error removing {pokemon_dir}: {e}")
    
    print(f"\nConsolidation complete:")
    print(f"  Moved: {moved} .pkmn files")
    print(f"  Deleted: {deleted_json} JSON files")
    print(f"  Removed: {deleted_dirs} directories")


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate Pokemon files by moving .pkmn files up and removing JSON files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it"
    )
    args = parser.parse_args()
    
    if args.dry_run:
        print("=== DRY RUN MODE - No files will be modified ===\n")
    
    consolidate_pokemon_files(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
