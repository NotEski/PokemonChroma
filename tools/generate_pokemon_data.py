"""
Generate per-Pokémon base data from cached PokeAPI JSON.

Outputs folders under data/pokemon/NNNN-name/ with base_pokemon.json
aligned to PokemonBase fields.

- Uses sword-shield version-group for move learnsets.
- Per-field fallback: for attributes available in multiple places, use the
    latest if present, otherwise fallback to next available.
- Abilities and types/growth_rate/egg_groups are stored as kebab-case slugs.
- Height/weight converted: dm -> meters (÷10), hg -> kilograms (÷10)

Usage:
        python -m tools.generate_pokemon_data --limit 10 --overwrite

"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = WORKSPACE_ROOT / "pokeapi_database"
DEFAULT_OUT = WORKSPACE_ROOT / "data" / "pokemon"

# Helpers

def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def to_upper_snake(s: str) -> str:
    # Convert kebab or spaces to snake, uppercase
    s = s.strip()
    s = s.replace("-", "_").replace(" ", "_")
    return s.upper()


def to_kebab(s: str) -> str:
    # Normalize to kebab-case: underscores/spaces to hyphens, lowercased
    s = s.strip()
    s = s.replace("_", "-").replace(" ", "-")
    return s.lower()


def to_title_spaces(s: str) -> str:
    # Convert kebab to title-cased with spaces: "medium-fast" -> "Medium Fast"
    parts = re.split(r"[-_ ]+", s)
    parts = [p.capitalize() for p in parts if p]
    return " ".join(parts)


def zero_pad_id(num: int, width: int = 4) -> str:
    return str(num).zfill(width)


# Version-group handling

def sorted_version_groups(version_group_dir: Path) -> List[str]:
    """Return version-group names sorted by order, descending (newest first)."""
    if not version_group_dir.exists():
        return []
    groups: List[Tuple[int, str]] = []
    for p in version_group_dir.glob("*.json"):
        data = read_json(p)
        order = data.get("order", -1)
        name = data.get("name")
        if isinstance(order, int) and name:
            groups.append((order, name))
    # Sort by order descending
    groups.sort(key=lambda x: x[0], reverse=True)
    return [name for _, name in groups]


# Field mappers

def map_base_stats(pokemon_data: Dict[str, Any]) -> Dict[str, int]:
    stats = {
        "hp": 0,
        "attack": 0,
        "defense": 0,
        "special_attack": 0,
        "special_defense": 0,
        "speed": 0,
    }
    for entry in pokemon_data.get("stats", []):
        base = entry.get("base_stat", 0)
        name = entry.get("stat", {}).get("name")
        if name == "hp":
            stats["hp"] = base
        elif name == "attack":
            stats["attack"] = base
        elif name == "defense":
            stats["defense"] = base
        elif name == "special-attack":
            stats["special_attack"] = base
        elif name == "special-defense":
            stats["special_defense"] = base
        elif name == "speed":
            stats["speed"] = base
    return stats


def map_ev_yield(pokemon_data: Dict[str, Any]) -> Dict[str, int]:
    evs = {"hp": 0, "attack": 0, "defense": 0, "special_attack": 0, "special_defense": 0, "speed": 0}
    for entry in pokemon_data.get("stats", []):
        effort = entry.get("effort", 0)
        name = entry.get("stat", {}).get("name")
        if name == "hp":
            evs["hp"] = effort
        elif name == "attack":
            evs["attack"] = effort
        elif name == "defense":
            evs["defense"] = effort
        elif name == "special-attack":
            evs["special_attack"] = effort
        elif name == "special-defense":
            evs["special_defense"] = effort
        elif name == "speed":
            evs["speed"] = effort
    return evs


def map_types(pokemon_data: Dict[str, Any]) -> List[str]:
    types: List[str] = []
    for entry in sorted(pokemon_data.get("types", []), key=lambda e: e.get("slot", 0)):
        tname = entry.get("type", {}).get("name", "")
        if tname:
            types.append(to_kebab(tname))
    return types


def map_abilities(pokemon_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    mapped: List[Dict[str, Any]] = []
    for entry in sorted(pokemon_data.get("abilities", []), key=lambda e: e.get("slot", 0)):
        aname = entry.get("ability", {}).get("name", "")
        slot = entry.get("slot", 0)
        hidden = bool(entry.get("is_hidden", False))
        if aname:
            mapped.append({
                "ability": aname,
                "slot": slot,
                "is_hidden": hidden,
            })
    return mapped


def map_moves_sword_shield(pokemon_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract moves from sword-shield version group."""
    moves = {"level": {}, "machine": [], "tutor": [], "egg_moves": []}
    target_vg = "sword-shield"
    
    for m in pokemon_data.get("moves", []):
        mname = m.get("move", {}).get("name")
        if not mname:
            continue
        # Filter to entries in sword-shield version-group only
        vg_entries = [d for d in m.get("version_group_details", []) if d.get("version_group", {}).get("name") == target_vg]
        if not vg_entries:
            continue
        # Process moves from sword-shield
        for d in vg_entries:
            method = (d.get("move_learn_method", {}) or {}).get("name")
            level = d.get("level_learned_at", 0)
            if method == "level-up":
                key = str(level)
                moves["level"].setdefault(key, [])
                moves["level"][key].append(mname)
            elif method == "machine":
                moves["machine"].append(mname)
            elif method == "tutor":
                moves["tutor"].append(mname)
            elif method == "egg":
                moves["egg_moves"].append(mname)
    
    # Deduplicate and sort
    moves["machine"] = sorted(list(set(moves["machine"])))
    moves["tutor"] = sorted(list(set(moves["tutor"])))
    moves["egg_moves"] = sorted(list(set(moves["egg_moves"])))
    for lvl in list(moves["level"].keys()):
        moves["level"][lvl] = sorted(list(set(moves["level"][lvl])))
    return moves


def map_name_readable(species_data: Dict[str, Any], fallback_slug: str) -> str:
    for entry in species_data.get("names", []):
        lang = (entry.get("language", {}) or {}).get("name")
        if lang == "en":
            nm = entry.get("name")
            if nm:
                return nm
    # Fallback to title-cased slug
    return to_title_spaces(fallback_slug)


def extract_evolution_chain_id(species_data: Dict[str, Any]) -> Optional[int]:
    url = (species_data.get("evolution_chain", {}) or {}).get("url")
    if not url:
        return None
    m = re.search(r"/evolution-chain/(\d+)/", url)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


# Main processing per Pokémon

def build_pokemon_payload(pokemon_path: Path, species_dir: Path) -> Optional[Tuple[str, Dict[str, Any]]]:
    try:
        pokemon_data = read_json(pokemon_path)
    except Exception:
        return None
    name_slug = pokemon_data.get("name", "")
    pid = int(pokemon_data.get("id")) if isinstance(pokemon_data.get("id"), int) else None
    if not name_slug or pid is None:
        return None
    species_path = species_dir / f"{pid}.json"
    if not species_path.exists():
        # Some caches use name-based files; try name
        alt = species_dir / f"{name_slug}.json"
        if alt.exists():
            species_path = alt
        else:
            species_path = None
    species_data: Dict[str, Any] = {}
    if species_path and species_path.exists():
        try:
            species_data = read_json(species_path)
        except Exception:
            species_data = {}

    # Per-field mapping with reasonable fallbacks
    types = map_types(pokemon_data)
    base_stats = map_base_stats(pokemon_data)
    ev_yield = map_ev_yield(pokemon_data)
    abilities = map_abilities(pokemon_data)

    capture_rate = (species_data.get("capture_rate") if species_data else None) or 45
    base_happiness = (species_data.get("base_happiness") if species_data else None) or 70
    gender_rate = (species_data.get("gender_rate") if species_data else None)
    base_experience_yield = pokemon_data.get("base_experience", 64)

    height_m = round(float(pokemon_data.get("height", 1.0)) / 10.0, 2)
    weight_kg = round(float(pokemon_data.get("weight", 10.0)) / 10.0, 2)

    egg_groups = [to_kebab(eg.get("name", "")) for eg in species_data.get("egg_groups", [])] if species_data else []
    growth_rate_slug = (species_data.get("growth_rate", {}) or {}).get("name") if species_data else None
    growth_rate = to_kebab(growth_rate_slug) if growth_rate_slug else "medium-fast"

    evolution_line_id = extract_evolution_chain_id(species_data) if species_data else None

    moves = map_moves_sword_shield(pokemon_data)

    name_readable = map_name_readable(species_data, name_slug)

    payload: Dict[str, Any] = {
        "name": name_slug,
        "name_readable": name_readable,
        "pokedex_number": pid,
        "types": types,
        "base_stats": base_stats,
        "ev_yield": ev_yield,
        "capture_rate": capture_rate,
        "base_experience_yield": base_experience_yield,
        "base_happiness": base_happiness,
        "gender_rate": gender_rate if gender_rate is not None else 4,
        "abilities": abilities,
        "height_m": height_m,
        "weight_kg": weight_kg,
        "egg_groups": egg_groups,
        "growth_rate": growth_rate,
        "moves": moves,
        "evolution_line_id": evolution_line_id,
    }
    folder_name = f"{zero_pad_id(pid)}-{name_slug}"
    return folder_name, payload


def write_payload(out_dir: Path, folder_name: str, payload: Dict[str, Any], overwrite: bool) -> Path:
    target_dir = out_dir / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / "base_pokemon.json"
    if target_file.exists() and not overwrite:
        return target_file
    with target_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)
    return target_file


def run(source: Path, out: Path, overwrite: bool, limit: Optional[int]) -> None:
    pokemon_dir = source / "pokemon"
    species_dir = source / "pokemon-species"

    written = 0
    for p in sorted(pokemon_dir.glob("*.json")):
        built = build_pokemon_payload(p, species_dir)
        if not built:
            continue
        fname, payload = built
        write_payload(out, fname, payload, overwrite)
        written += 1
        if limit and written >= limit:
            break

    print(f"Wrote {written} Pokémon base files to {out}")


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Generate Pokémon base data from cached PokeAPI JSON")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Source pokeapi_database directory")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output data/pokemon directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing base_pokemon.json files")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of Pokémon to process")

    args = parser.parse_args(argv)
    run(args.source, args.out, args.overwrite, args.limit)


if __name__ == "__main__":
    main()
