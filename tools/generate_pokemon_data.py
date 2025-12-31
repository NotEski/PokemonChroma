"""
Generate Pokémon base data, move files, item files, and ability files from cached PokeAPI JSON.

Outputs:
- data/pokemon/NNNN-name/base_pokemon.json aligned to PokemonBase fields
- data/moves/NNNN-move-name.pkmn generated from pokeapi_database/move
- data/items/NNNN-item-name.json copied from pokeapi_database/item
- data/abilities/ability-name.pkmn generated from pokeapi_database/ability

Rules:
- Moveset source: sword-shield version-group only (no fallback for moves)
- Per-field fallback for Pokémon attributes when needed
- Types, growth_rate, egg_groups: lower_snake
- Abilities: kebab-case slug names
- Height/weight: dm→meters, hg→kilograms (÷10)

Usage:
    python -m tools.generate_pokemon_data --overwrite
    python -m tools.generate_pokemon_data --skip-pokemon --overwrite  # only moves, items, abilities
    python -m tools.generate_pokemon_data --skip-pokemon --skip-moves --skip-items --overwrite  # only abilities
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = WORKSPACE_ROOT / "pokeapi_database"
DEFAULT_OUT_POKEMON = WORKSPACE_ROOT / "data" / "pokemon"
DEFAULT_OUT_MOVES = WORKSPACE_ROOT / "data" / "moves"
DEFAULT_OUT_ITEMS = WORKSPACE_ROOT / "data" / "items"
DEFAULT_OUT_ABILITIES = WORKSPACE_ROOT / "data" / "abilities"


# ------------------------- Helpers -------------------------
def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def to_upper_snake(s: str) -> str:
    s = s.strip().replace("-", "_").replace(" ", "_")
    return s.upper()


def to_lower_snake(s: str) -> str:
    normalized = re.sub(r"[\s-]+", "_", s.strip().lower())
    return re.sub(r"_+", "_", normalized)


def to_kebab(s: str) -> str:
    normalized = re.sub(r"[ _]+", "-", s.strip().lower())
    return re.sub(r"-+", "-", normalized)


def to_title_spaces(s: str) -> str:
    parts = re.split(r"[-_ ]+", s)
    parts = [p.capitalize() for p in parts if p]
    return " ".join(parts)


def zero_pad_id(num: int, width: int = 4) -> str:
    return str(num).zfill(width)


# ------------------------- Field mappers -------------------------
def map_base_stats(pokemon_data: Dict[str, Any]) -> Dict[str, int]:
    stats = {"hp": 0, "attack": 0, "defense": 0, "special_attack": 0, "special_defense": 0, "speed": 0}
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
            types.append(to_lower_snake(tname))
    return types


def map_abilities(pokemon_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    mapped: List[Dict[str, Any]] = []
    for entry in sorted(pokemon_data.get("abilities", []), key=lambda e: e.get("slot", 0)):
        aname = entry.get("ability", {}).get("name", "")
        slot = entry.get("slot", 0)
        hidden = bool(entry.get("is_hidden", False))
        if aname:
            mapped.append({"ability": to_lower_snake(aname), "slot": slot, "is_hidden": hidden})
    return mapped


def map_moves_sword_shield(pokemon_data: Dict[str, Any]) -> Dict[str, Any]:
    moves = {"level": {}, "machine": [], "tutor": [], "egg_moves": []}
    target_vg = "sword-shield"
    for m in pokemon_data.get("moves", []):
        mname = m.get("move", {}).get("name")
        if not mname:
            continue
        mslug = to_lower_snake(mname)
        vg_entries = [d for d in m.get("version_group_details", []) if d.get("version_group", {}).get("name") == target_vg]
        if not vg_entries:
            continue
        for d in vg_entries:
            method = (d.get("move_learn_method", {}) or {}).get("name")
            level = d.get("level_learned_at", 0)
            if method == "level-up":
                key = str(level)
                moves["level"].setdefault(key, [])
                moves["level"][key].append(mslug)
            elif method == "machine":
                moves["machine"].append(mslug)
            elif method == "tutor":
                moves["tutor"].append(mslug)
            elif method == "egg":
                moves["egg_moves"].append(mslug)
    # Dedup/sort
    moves["machine"] = sorted(set(moves["machine"]))
    moves["tutor"] = sorted(set(moves["tutor"]))
    moves["egg_moves"] = sorted(set(moves["egg_moves"]))
    for lvl in list(moves["level"].keys()):
        moves["level"][lvl] = sorted(set(moves["level"][lvl]))
    return moves


def map_display_name(species_data: Dict[str, Any], fallback_slug: str) -> str:
    for entry in species_data.get("names", []):
        lang = (entry.get("language", {}) or {}).get("name")
        if lang == "en":
            nm = entry.get("name")
            if nm:
                return nm
    return to_title_spaces(fallback_slug)


def map_move_display_name(move_data: Dict[str, Any], fallback_slug: str) -> str:
    for entry in move_data.get("names", []):
        lang = (entry.get("language", {}) or {}).get("name")
        if lang == "en":
            nm = entry.get("name")
            if nm:
                return nm
    return to_title_spaces(fallback_slug)


def map_item_display_name(item_data: Dict[str, Any], fallback_slug: str) -> str:
    for entry in item_data.get("names", []):
        lang = (entry.get("language", {}) or {}).get("name")
        if lang == "en":
            nm = entry.get("name")
            if nm:
                return nm
    return to_title_spaces(fallback_slug)


def map_item_description(item_data: Dict[str, Any]) -> str:
    for entry in item_data.get("effect_entries", []):
        lang = (entry.get("language", {}) or {}).get("name")
        if lang == "en":
            text = entry.get("short_effect") or entry.get("effect")
            if text:
                return " ".join(text.replace("\n", " ").split())
    for entry in item_data.get("flavor_text_entries", []):
        lang = (entry.get("language", {}) or {}).get("name")
        if lang == "en":
            text = entry.get("text")
            if text:
                return " ".join(text.replace("\n", " ").split())
    return ""


def map_baby_trigger_id(item_data: Dict[str, Any]) -> Optional[int]:
    url = (item_data.get("baby_trigger_for", {}) or {}).get("url")
    if not url:
        return None
    match = re.search(r"/evolution-chain/(\d+)/", url)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


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


# ------------------------- Pokémon payload -------------------------
def build_pokemon_payload(pokemon_path: Path, species_dir: Path) -> Optional[Tuple[str, Dict[str, Any]]]:
    try:
        pokemon_data = read_json(pokemon_path)
    except Exception:
        return None
    name_slug = to_lower_snake(pokemon_data.get("name", ""))
    pid = int(pokemon_data.get("id")) if isinstance(pokemon_data.get("id"), int) else None
    if not name_slug or pid is None:
        return None
    species_path = species_dir / f"{pid}.json"
    if not species_path.exists():
        alt = species_dir / f"{name_slug}.json"
        species_path = alt if alt.exists() else None
    species_data: Dict[str, Any] = {}
    if species_path and species_path.exists():
        try:
            species_data = read_json(species_path)
        except Exception:
            species_data = {}

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

    egg_groups = [to_lower_snake(eg.get("name", "")) for eg in species_data.get("egg_groups", [])] if species_data else []
    growth_rate_slug = (species_data.get("growth_rate", {}) or {}).get("name") if species_data else None
    growth_rate = to_lower_snake(growth_rate_slug) if growth_rate_slug else "medium_fast"

    evolution_line_id = extract_evolution_chain_id(species_data) if species_data else None
    moves = map_moves_sword_shield(pokemon_data)
    display_name = map_display_name(species_data, name_slug)

    payload: Dict[str, Any] = {
        "name": name_slug,
        "display_name": display_name,
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
    folder_name = f"{name_slug}"
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


# ------------------------- Item files -------------------------

def build_item_payload(item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    iid = item_data.get("id")
    iname = item_data.get("name")
    if not isinstance(iid, int) or not isinstance(iname, str) or not iname:
        return None

    name_slug = to_lower_snake(iname)
    display_name = map_item_display_name(item_data, name_slug)

    attributes = [to_lower_snake(attr.get("name", "")) for attr in item_data.get("attributes", []) if attr.get("name")]
    attributes = sorted(set(a for a in attributes if a))

    category_raw = (item_data.get("category", {}) or {}).get("name", "")
    category = to_lower_snake(category_raw) if category_raw else None

    fling_effect_raw = (item_data.get("fling_effect", {}) or {}).get("name", "") if isinstance(item_data.get("fling_effect"), dict) else None
    fling_effect = to_lower_snake(fling_effect_raw) if fling_effect_raw else None

    held_by_pokemon = []
    for entry in item_data.get("held_by_pokemon", []):
        pname = (entry.get("pokemon", {}) or {}).get("name")
        if pname:
            held_by_pokemon.append(to_lower_snake(pname))
    held_by_pokemon = sorted(set(held_by_pokemon))

    payload: Dict[str, Any] = {
        "name": name_slug,
        "display_name": display_name,
        "index": iid,
        "description": map_item_description(item_data),
        "cost": item_data.get("cost", 0) or 0,
        "attributes": attributes,
        "fling_effect": fling_effect,
        "fling_power": item_data.get("fling_power") if item_data.get("fling_power") is not None else 0,
        "baby_trigger_for": map_baby_trigger_id(item_data),
        "category": category,
        "held_by_pokemon": held_by_pokemon,
    }
    return payload


def generate_items(source: Path, out_items: Path, overwrite: bool, limit: Optional[int]) -> int:
    item_dir = source / "item"
    if not item_dir.exists():
        return 0
    out_items.mkdir(parents=True, exist_ok=True)
    written = 0
    for p in sorted(item_dir.glob("*.json")):
        try:
            data = read_json(p)
        except Exception:
            continue
        payload = build_item_payload(data)
        if not payload:
            continue
        iname = payload.get("name")
        fname = f"{iname}.json"
        target_file = out_items / fname
        if target_file.exists() and not overwrite:
            written += 1
            if limit and written >= limit:
                break
            continue
        with target_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
        written += 1
        if limit and written >= limit:
            break
    return written


# ------------------------- Move files -------------------------
def build_move_payload(move_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract and normalize move data to BaseMove schema.
    Maps PokeAPI fields to BaseMove fields with enum conversions.
    """
    mid = move_data.get("id")
    mname = move_data.get("name")
    if not isinstance(mid, int) or not isinstance(mname, str) or not mname:
        return None

    mslug = to_lower_snake(mname)
    if not mslug:
        return None
    display_name = map_move_display_name(move_data, mslug)

    # Core fields
    mtype = to_lower_snake(move_data.get("type", {}).get("name", "normal"))
    if mtype == "shadow":
        return None  # Skip Shadow-type moves
    damage_class_name = move_data.get("damage_class", {}).get("name", "physical")
    damage_class = to_lower_snake(damage_class_name)  # physical, special, status
    
    # Category: map from PokeAPI category if present, else infer from type/damage_class
    category_name = move_data.get("category", {}).get("name", "damage") if isinstance(move_data.get("category"), dict) else "damage"
    category = to_lower_snake(category_name)  # damage, status, etc
    
    accuracy = move_data.get("accuracy")
    power = move_data.get("power")
    pp = move_data.get("pp", 15)
    priority = move_data.get("priority", 0)
    
    # Target
    target_name = move_data.get("target", {}).get("name", "selected-pokemon")
    target = to_lower_snake(target_name)  # all_opponents, selected_pokemon, etc
    
    # Status condition (extract from effect_entries if needed, or meta if present)
    status_condition = "none"
    status_condition_chance = 0
    meta = move_data.get("meta", {})
    if meta:
        ailment = meta.get("ailment", {})
        ailment_name = ailment.get("name") if isinstance(ailment, dict) else None
        if ailment_name:
            status_condition = to_lower_snake(ailment_name)
            status_condition_chance = meta.get("ailment_chance", 0)
    
    # Move effects
    critical_hit_rate = (meta.get("crit_rate", 0) * 8) if meta else 0  # Normalize to stages
    flinch_chance = meta.get("flinch_chance", 0) if meta else 0
    
    # Drain: list [numerator, denominator] or single int
    drain_data = meta.get("drain", [0, 1]) if meta else [0, 1]
    if isinstance(drain_data, list) and len(drain_data) >= 2:
        drain = (drain_data[0] * 100 // drain_data[1]) if drain_data[1] != 0 else 0
    else:
        drain = drain_data if isinstance(drain_data, int) else 0
    
    # Healing: list [numerator, denominator] or single int
    healing_data = meta.get("healing", [0, 1]) if meta else [0, 1]
    if isinstance(healing_data, list) and len(healing_data) >= 2:
        healing = (healing_data[0] * 100 // healing_data[1]) if healing_data[1] != 0 else 0
    else:
        healing = healing_data if isinstance(healing_data, int) else 0
    
    # Multi-hit/multi-turn (from meta if present)
    min_hits = meta.get("min_hits") if meta else None
    max_hits = meta.get("max_hits") if meta else None
    min_turns = meta.get("min_turns") if meta else None
    max_turns = meta.get("max_turns") if meta else None
    
    # Stat changes - categorize based on target
    stat_changes_raw = move_data.get("stat_changes", [])
    stat_chance = meta.get("stat_chance", 0) if meta else 0
    # If stat_chance is 0 and there are stat changes, it means guaranteed (100%)
    if stat_chance == 0 and stat_changes_raw:
        stat_chance = 100
    
    parsed_stat_changes = []
    if stat_changes_raw and isinstance(stat_changes_raw, list):
        for sc in stat_changes_raw:
            stat_name = sc.get("stat", {}).get("name")
            change = sc.get("change")
            if stat_name and change is not None:
                    parsed_stat_changes.append({
                        "stat": to_lower_snake(stat_name),
                    "change": change,
                    "chance": stat_chance
                })
    
    # Determine if stat changes affect user or target based on move target
    user_targets = {"user", "user-and-allies", "user-or-allies", "users-field", "ally", "all-allies"}
    stat_changes_inflicted = None
    stat_changes_recieved = None
    
    if parsed_stat_changes:
        # If target affects user/allies, stat changes are received by user
        if target in user_targets:
            stat_changes_recieved = parsed_stat_changes
        else:
            # Otherwise, stat changes are inflicted on opponents
            stat_changes_inflicted = parsed_stat_changes
    
    payload: Dict[str, Any] = {
        "name": mslug,
        "display_name": display_name,
        "index": mid,
        "type": mtype,
        "damage_class": damage_class,
        "category": category,
        "accuracy": accuracy,
        "power": power,
        "pp": pp,
        "target": target,
        "priority": priority,
        "status_condition": status_condition,
        "status_condition_chance": status_condition_chance,
        "critical_hit_rate": critical_hit_rate,
        "flinch_chance": flinch_chance,
        "drain": drain,
        "healing": healing,
        "min_hits": min_hits,
        "max_hits": max_hits,
        "min_turns": min_turns,
        "max_turns": max_turns,
        "stat_changes_inflicted": stat_changes_inflicted,
        "stat_changes_recieved": stat_changes_recieved,
    }
    return payload


def generate_move_pkmn_file(payload: Dict[str, Any]) -> str:
    """Generate .pkmn file content from move payload."""
    move_id = payload.get("name")
    class_name = "_" + "".join(word.capitalize() for word in move_id.split("_"))
    
    # Build meta dict
    meta_lines = [
        "    meta = {",
        f'        "display_name": "{payload.get("display_name")}",',
        f'        "type": "{payload.get("type")}",',
        f'        "index": {payload.get("index")},',
        f'        "damage_class": "{payload.get("damage_class")}",',
        f'        "category": "{payload.get("category")}",',
    ]
    
    # Handle None values properly
    accuracy = payload.get("accuracy")
    power = payload.get("power")
    meta_lines.append(f'        "accuracy": {accuracy if accuracy is not None else "None"},')
    meta_lines.append(f'        "power": {power if power is not None else "None"},')
    meta_lines.append(f'        "pp": {payload.get("pp")},')
    meta_lines.append(f'        "target": "{payload.get("target")}",')
    
    # Optional fields with defaults
    priority = payload.get("priority", 0)
    if priority != 0:
        meta_lines.append(f'        "priority": {priority},')
    
    status_condition = payload.get("status_condition", "none")
    if status_condition != "none":
        meta_lines.append(f'        "status_condition": "{status_condition}",')
        status_chance = payload.get("status_condition_chance", 0)
        meta_lines.append(f'        "status_condition_chance": {status_chance},')
    
    crit_rate = payload.get("critical_hit_rate", 0)
    if crit_rate != 0:
        meta_lines.append(f'        "critical_hit_rate": {crit_rate},')
    
    flinch = payload.get("flinch_chance", 0)
    if flinch != 0:
        meta_lines.append(f'        "flinch_chance": {flinch},')
    
    drain = payload.get("drain", 0)
    if drain != 0:
        meta_lines.append(f'        "drain": {drain},')
    
    healing = payload.get("healing", 0)
    if healing != 0:
        meta_lines.append(f'        "healing": {healing},')
    
    # Stat changes
    stat_changes_inflicted = payload.get("stat_changes_inflicted")
    if stat_changes_inflicted:
        meta_lines.append(f'        "stat_changes_inflicted": {json.dumps(stat_changes_inflicted)},')
    
    stat_changes_recieved = payload.get("stat_changes_recieved")
    if stat_changes_recieved:
        meta_lines.append(f'        "stat_changes_recieved": {json.dumps(stat_changes_recieved)},')
    
    meta_lines.append("    }")
    
    # Build the full file content
    lines = [
        f'@move("{move_id}")  # type: ignore',
        f'class {class_name}:',
    ] + meta_lines
    
    return "\n".join(lines) + "\n"


def generate_moves(source: Path, out_moves: Path, overwrite: bool, limit: Optional[int]) -> int:
    move_dir = source / "move"
    if not move_dir.exists():
        return 0
    out_moves.mkdir(parents=True, exist_ok=True)
    written = 0
    for p in sorted(move_dir.glob("*.json")):
        try:
            data = read_json(p)
        except Exception:
            continue
        payload = build_move_payload(data)
        if not payload:
            continue
        mid = payload.get("index")
        mname = payload.get("name")
        fname = f"{mname}.pkmn"
        target_file = out_moves / fname
        if target_file.exists() and not overwrite:
            written += 1
            if limit and written >= limit:
                break
            continue
        pkmn_content = generate_move_pkmn_file(payload)
        with target_file.open("w", encoding="utf-8") as f:
            f.write(pkmn_content)
        written += 1
        if limit and written >= limit:
            break
    return written


# ------------------------- Ability files -------------------------
def build_ability_payload(ability_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract and normalize ability data to BaseAbility schema.
    Maps PokeAPI fields to BaseAbility fields.
    """
    aid = ability_data.get("id")
    aname = ability_data.get("name")
    if not isinstance(aid, int) or not isinstance(aname, str) or not aname:
        return None

    aslug = to_lower_snake(aname)
    if not aslug:
        return None
    
    display_name = map_ability_display_name(ability_data, aslug)
    description = map_ability_description(ability_data)
    
    payload: Dict[str, Any] = {
        "name": aslug,
        "display_name": display_name,
        "index": aid,
        "description": description,
    }
    return payload


def map_ability_display_name(ability_data: Dict[str, Any], fallback_slug: str) -> str:
    for entry in ability_data.get("names", []):
        lang = (entry.get("language", {}) or {}).get("name")
        if lang == "en":
            nm = entry.get("name")
            if nm:
                return nm
    return to_title_spaces(fallback_slug)


def map_ability_description(ability_data: Dict[str, Any]) -> str:
    for entry in ability_data.get("effect_entries", []):
        lang = (entry.get("language", {}) or {}).get("name")
        if lang == "en":
            text = entry.get("short_effect") or entry.get("effect")
            if text:
                return " ".join(text.replace("\n", " ").split())
    return ""


def generate_ability_pkmn_file(payload: Dict[str, Any]) -> str:
    """Generate .pkmn file content from ability payload."""
    ability_id = payload.get("name")
    class_name = "_" + "".join(word.capitalize() for word in ability_id.split("_"))
    
    # Build meta dict
    meta_lines = [
        "    meta = {",
        f'        "display_name": "{payload.get("display_name")}",',
        f'        "description": "{payload.get("description")}",',
        f'        "index": {payload.get("index")},',
        "    }",
    ]
    
    # Build the full file content
    lines = [
        f'@ability("{ability_id}")  # type: ignore',
        f'class {class_name}:',
    ] + meta_lines
    
    return "\n".join(lines) + "\n"


def generate_abilities(source: Path, out_abilities: Path, overwrite: bool, limit: Optional[int]) -> int:
    ability_dir = source / "ability"
    if not ability_dir.exists():
        return 0
    out_abilities.mkdir(parents=True, exist_ok=True)
    written = 0
    for p in sorted(ability_dir.glob("*.json")):
        try:
            data = read_json(p)
        except Exception:
            continue
        payload = build_ability_payload(data)
        if not payload:
            continue
        aname = payload.get("name")
        fname = f"{aname}.pkmn"
        target_file = out_abilities / fname
        if target_file.exists() and not overwrite:
            written += 1
            if limit and written >= limit:
                break
            continue
        pkmn_content = generate_ability_pkmn_file(payload)
        with target_file.open("w", encoding="utf-8") as f:
            f.write(pkmn_content)
        written += 1
        if limit and written >= limit:
            break
    return written


# ------------------------- Orchestration -------------------------
def run(
    source: Path,
    out_pokemon: Path,
    out_moves: Path,
    out_items: Path,
    out_abilities: Path,
    overwrite: bool,
    limit: Optional[int],
    include_pokemon: bool,
    include_moves: bool,
    include_items: bool,
    include_abilities: bool,
) -> None:
    pokemon_dir = source / "pokemon"
    species_dir = source / "pokemon-species"

    total_pokemon = 0
    if include_pokemon:
        for p in sorted(pokemon_dir.glob("*.json")):
            built = build_pokemon_payload(p, species_dir)
            if not built:
                continue
            fname, payload = built
            write_payload(out_pokemon, fname, payload, overwrite)
            total_pokemon += 1
            if limit and total_pokemon >= limit:
                break

    total_moves = 0
    if include_moves:
        total_moves = generate_moves(source, out_moves, overwrite, limit)

    total_items = 0
    if include_items:
        total_items = generate_items(source, out_items, overwrite, limit)

    total_abilities = 0
    if include_abilities:
        total_abilities = generate_abilities(source, out_abilities, overwrite, limit)

    if include_pokemon:
        print(f"Wrote {total_pokemon} Pokémon base files to {out_pokemon}")
    if include_moves:
        print(f"Wrote {total_moves} move files to {out_moves}")
    if include_items:
        print(f"Wrote {total_items} item files to {out_items}")
    if include_abilities:
        print(f"Wrote {total_abilities} ability files to {out_abilities}")


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Generate Pokémon base data, move data, item data, and ability data from cached PokeAPI JSON")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Source pokeapi_database directory")
    parser.add_argument("--out-pokemon", type=Path, default=DEFAULT_OUT_POKEMON, help="Output data/pokemon directory")
    parser.add_argument("--out-moves", type=Path, default=DEFAULT_OUT_MOVES, help="Output data/moves directory")
    parser.add_argument("--out-items", type=Path, default=DEFAULT_OUT_ITEMS, help="Output data/items directory")
    parser.add_argument("--out-abilities", type=Path, default=DEFAULT_OUT_ABILITIES, help="Output data/abilities directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of entries to process (separately for pokemon, moves, items, and abilities)")
    parser.add_argument("--skip-pokemon", action="store_true", help="Skip generating Pokémon data")
    parser.add_argument("--skip-moves", action="store_true", help="Skip generating moves data")
    parser.add_argument("--skip-items", action="store_true", help="Skip generating item data")
    parser.add_argument("--skip-abilities", action="store_true", help="Skip generating ability data")

    args = parser.parse_args(argv)
    run(
        source=args.source,
        out_pokemon=args.out_pokemon,
        out_moves=args.out_moves,
        out_items=args.out_items,
        out_abilities=args.out_abilities,
        overwrite=args.overwrite,
        limit=args.limit,
        include_pokemon=not args.skip_pokemon,
        include_moves=not args.skip_moves,
        include_items=not args.skip_items,
        include_abilities=not args.skip_abilities,
    )


if __name__ == "__main__":
    main()
