import json
import os
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[1]
TYPE_DIR = ROOT / "pokeapi_database" / "type"
OUTPUT_FILE = ROOT / "engine" / "battle" / "type_effectiveness_generated.py"


HEADER = """# Auto-generated from pokeapi_database/type/*.json\n# Do not edit by hand. Regenerate via tools/generate_type_chart.py\n\nfrom typing import Mapping\nfrom shared.pokemon.types import PokemonType\n\nTYPE_EFFECTIVENESS: Mapping[PokemonType, dict[PokemonType, float]] = {\n"""

FOOTER = "}\n"

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


def name_to_enum(name: str) -> str:
    # PokeAPI uses lowercase names matching our PokemonType values
    # Map to enum member: PokemonType.FIRE etc.
    return f"PokemonType.{name.replace('-', '_').upper()}"


def build_effectiveness_map():
    # attacker -> defender -> multiplier
    chart: dict[str, dict[str, float]] = {}

    for type_name, data in load_type_jsons():
        rel = get_damage_relations(data)
        attacker_enum = name_to_enum(type_name)
        defender_map: dict[str, float] = {}

        # Relations list names are defender types
        for defender in rel.get("double_damage_to", []):
            defender_map[name_to_enum(defender["name"])] = 2.0
        for defender in rel.get("half_damage_to", []):
            defender_map[name_to_enum(defender["name"])] = 0.5
        for defender in rel.get("no_damage_to", []):
            defender_map[name_to_enum(defender["name"])] = 0.0

        chart[attacker_enum] = defender_map

    return chart


def emit_chart(chart: dict[str, dict[str, float]]) -> str:
    lines = [HEADER]
    first_attacker = True
    for attacker_enum, defenders in sorted(chart.items()):
        prefix = "    " if first_attacker else "    "
        lines.append(f"    {attacker_enum}: {{\n")
        # Sort defenders for stable output
        for defender_enum, mult in sorted(defenders.items()):
            lines.append(f"        {defender_enum}: {mult},\n")
        lines.append("    },\n")
        first_attacker = False
    lines.append(FOOTER)
    return "".join(lines)


def main():
    chart = build_effectiveness_map()
    output = emit_chart(chart)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        f.write(output)
    print(f"Wrote type effectiveness to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
