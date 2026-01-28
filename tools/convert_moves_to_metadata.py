"""
Convert all move .pkmn files from meta dict format to MoveMetaData format.
Also adds 'from pkmn_imports import *' at the beginning and removes '# type: ignore' comments.

Usage:
    python tools/convert_moves_to_metadata.py
    python tools/convert_moves_to_metadata.py --dry-run
"""
import argparse
import re
from pathlib import Path
from typing import Dict, Any

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
MOVES_DIR = WORKSPACE_ROOT / "data" / "moves"


def parse_move_file(content: str) -> Dict[str, Any]:
    """Parse a .pkmn move file and extract its components."""
    # Extract decorator and class definition
    decorator_match = re.search(r'^@move\("([^"]+)"\)\s*(?:#\s*type:\s*ignore)?\s*\nclass\s+(\w+):', content, re.MULTILINE)
    if not decorator_match:
        return None
    
    move_name = decorator_match.group(1)
    class_name = decorator_match.group(2)
    
    # Extract meta dict
    meta_match = re.search(r'meta\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', content, re.DOTALL)
    if not meta_match:
        return None
    
    meta_dict = {}
    meta_content = meta_match.group(1)
    
    # Parse key-value pairs from meta dict
    for line in meta_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Match "key": value patterns
        match = re.match(r'"([^"]+)":\s*(.+?),?\s*$', line)
        if match:
            key = match.group(1)
            value = match.group(2).rstrip(',').strip()
            meta_dict[key] = value
    
    # Extract all other attributes (priority, flags, stat_changes, etc.)
    other_attrs = {}
    
    # Find all attribute assignments after the meta dict
    attr_pattern = r'^\s{4}(\w+)\s*=\s*(.+?)(?=\n\s{4}\w+\s*=|\Z)'
    for match in re.finditer(attr_pattern, content[meta_match.end():], re.MULTILINE | re.DOTALL):
        attr_name = match.group(1)
        if attr_name != 'meta':
            attr_value = match.group(2).strip()
            other_attrs[attr_name] = attr_value
    
    return {
        'move_name': move_name,
        'class_name': class_name,
        'meta_dict': meta_dict,
        'other_attrs': other_attrs,
    }


def convert_move_to_metadata_format(parsed: Dict[str, Any]) -> str:
    """Convert parsed move data to MoveMetaData format."""
    lines = [
        "from pkmn_imports import *",
        "",
        f'@move("{parsed["move_name"]}")',
        f'class {parsed["class_name"]}:',
    ]
    
    # Build MoveMetaData
    meta_dict = parsed['meta_dict']
    meta_lines = ["    meta = MoveMetaData("]
    
    # Required fields in order
    if 'display_name' in meta_dict:
        meta_lines.append(f'        display_name={meta_dict["display_name"]},')
    
    if 'index' in meta_dict:
        meta_lines.append(f'        index={meta_dict["index"]},')
    
    if 'type' in meta_dict:
        type_val = meta_dict['type']
        meta_lines.append(f'        type=PokemonType({type_val}),')
    
    if 'damage_class' in meta_dict:
        damage_class_val = meta_dict['damage_class']
        # Convert to DamageClass enum format
        damage_class_map = {
            '"physical"': 'DamageClass.PHYSICAL',
            '"special"': 'DamageClass.SPECIAL',
            '"status"': 'DamageClass.STATUS',
        }
        damage_class = damage_class_map.get(damage_class_val, f'DamageClass({damage_class_val})')
        meta_lines.append(f'        damage_class={damage_class},')
    
    if 'category' in meta_dict:
        category_val = meta_dict['category']
        # Convert to MoveCategory enum format
        category_map = {
            '"damage"': 'MoveCategory.DAMAGE',
            '"status"': 'MoveCategory.STATUS',
            '"damage_status"': 'MoveCategory.DAMAGE_STATUS',
        }
        category = category_map.get(category_val, f'MoveCategory({category_val})')
        meta_lines.append(f'        category={category},')
    
    if 'accuracy' in meta_dict:
        meta_lines.append(f'        accuracy={meta_dict["accuracy"]},')
    
    if 'power' in meta_dict:
        meta_lines.append(f'        power={meta_dict["power"]},')
    
    if 'pp' in meta_dict:
        meta_lines.append(f'        pp={meta_dict["pp"]},')
    
    if 'target' in meta_dict:
        target_val = meta_dict['target']
        # Convert to MoveTarget enum format
        target_map = {
            '"selected_pokemon"': 'MoveTarget.SELECTED_POKEMON',
            '"user"': 'MoveTarget.USER',
            '"all_opponents"': 'MoveTarget.ALL_OPPONENTS',
            '"all_allies"': 'MoveTarget.ALL_ALLIES',
            '"all_others"': 'MoveTarget.ALL_OTHERS',
            '"all"': 'MoveTarget.ALL',
        }
        target = target_map.get(target_val, f'MoveTarget({target_val})')
        meta_lines.append(f'        target={target},')
    
    meta_lines.append("    )")
    lines.extend(meta_lines)
    
    # Add other attributes
    for attr_name, attr_value in parsed['other_attrs'].items():
        lines.append(f"    {attr_name} = {attr_value}")
    
    return "\n".join(lines) + "\n"


def convert_moves(dry_run: bool = False):
    """Convert all move files in the moves directory."""
    if not MOVES_DIR.exists():
        print(f"Moves directory not found: {MOVES_DIR}")
        return
    
    move_files = sorted(MOVES_DIR.glob("*.pkmn"))
    converted = 0
    failed = 0
    
    print(f"Found {len(move_files)} move files to convert...\n")
    
    for move_file in move_files:
        try:
            with open(move_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip if already converted
            if content.startswith("from pkmn_imports import *"):
                print(f"[OK] {move_file.name} - Already converted")
                continue
            
            parsed = parse_move_file(content)
            if not parsed:
                print(f"[FAIL] {move_file.name} - Failed to parse")
                failed += 1
                continue
            
            converted_content = convert_move_to_metadata_format(parsed)
            
            if not dry_run:
                with open(move_file, 'w', encoding='utf-8') as f:
                    f.write(converted_content)
                print(f"[DONE] {move_file.name} - Converted")
            else:
                print(f"[DRY RUN] {move_file.name} - Would convert")
            
            converted += 1
        except Exception as e:
            print(f"[FAIL] {move_file.name} - Error: {e}")
            failed += 1
    
    print(f"\nConversion complete:")
    print(f"  Converted: {converted}")
    print(f"  Failed: {failed}")
    if dry_run:
        print("  (Dry run - no files were modified)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert move .pkmn files to use MoveMetaData format"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be converted without making changes"
    )
    
    args = parser.parse_args()
    convert_moves(dry_run=args.dry_run)
