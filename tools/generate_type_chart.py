import json
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[1]
TYPE_DIR = ROOT / "pokeapi_database" / "type"
OUTPUT_DIR = ROOT / "data" / "types"

def load_type_jsons():
    for p in TYPE_DIR.glob("*.json"):
        # Skip index/summary files if present
        if p.name in {"_index.json", "summary.json"}:
            continue
        with p.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue
        yield p.stem, data


def get_damage_relations(type_data: dict) -> dict:
    return type_data.get("damage_relations", {})


def format_type_name(name: str) -> str:
    """Convert type name to lowercase with underscores (e.g., 'ice' or 'ice_shard')"""
    return name.replace('-', '_').lower()


def format_class_name(name: str) -> str:
    """Convert type name to class name (e.g., 'IceType')"""
    return ''.join(word.capitalize() for word in name.replace('-', ' ').split()) + 'Type'


def format_display_name(name: str) -> str:
    """Convert type name to display name (e.g., 'Ice')"""
    return name.replace('-', ' ').title()


def build_type_data():
    """Build type data for each type"""
    type_data = {}
    
    for type_name, data in load_type_jsons():
        rel = get_damage_relations(data)
        effectiveness = {}
        
        # Relations list names are defender types
        for defender in rel.get("double_damage_to", []):
            defender_name = format_type_name(defender["name"])
            effectiveness[defender_name] = 2.0
        for defender in rel.get("half_damage_to", []):
            defender_name = format_type_name(defender["name"])
            effectiveness[defender_name] = 0.5
        for defender in rel.get("no_damage_to", []):
            defender_name = format_type_name(defender["name"])
            effectiveness[defender_name] = 0.0
        
        type_data[type_name] = effectiveness
    
    return type_data


def emit_pkmn_file(type_name: str, effectiveness: dict) -> str:
    """Generate .pkmn file content for a type"""
    formatted_name = format_type_name(type_name)
    class_name = format_class_name(type_name)
    display_name = format_display_name(type_name)
    
    lines = [
        f'@pokemon_type("{formatted_name}")\n',
        f'class {class_name}:\n',
        f'    name = "{display_name}"\n',
        f'    icon = b""  # Placeholder for icon bytes\n',
        f'    effectiveness = {{\n'
    ]
    
    # Sort for stable output
    for defender, mult in sorted(effectiveness.items()):
        lines.append(f'        "{defender}": {mult},\n')
    
    lines.append('    }\n')
    
    return ''.join(lines)


def main():
    type_data = build_type_data()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for type_name, effectiveness in type_data.items():
        formatted_name = format_type_name(type_name)
        output_file = OUTPUT_DIR / f"{formatted_name}.pkmn"
        content = emit_pkmn_file(type_name, effectiveness)
        
        with output_file.open("w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Wrote {output_file.name}")
    
    print(f"\nGenerated {len(type_data)} type files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
