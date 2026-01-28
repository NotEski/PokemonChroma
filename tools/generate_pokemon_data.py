"""
Generate Pokémon base data, move files, item files, and ability files from cached PokeAPI JSON.

Outputs:
- data/pokemon/NNNN-name/base_pokemon.json aligned to PokemonBase fields
- data/moves/NNNN-move-name.pkmn generated from pokeapi_database/move
- data/items/NNNN-item-name.json copied from pokeapi_database/item
- data/abilities/ability-name.pkmn generated from pokeapi_database/ability
- data/status/status-name.pkmn generated from SQLite move ailments

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
    python -m tools.generate_pokemon_data --sqlite-db database_download/veekun-pokedex.sqlite/veekun-pokedex.sqlite --overwrite  # use SQLite for moves/status
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = WORKSPACE_ROOT / "pokeapi_database"
DEFAULT_OUT_POKEMON = WORKSPACE_ROOT / "data" / "pokemon"
DEFAULT_OUT_MOVES = WORKSPACE_ROOT / "data" / "moves"
DEFAULT_OUT_ITEMS = WORKSPACE_ROOT / "data" / "items"
DEFAULT_OUT_ABILITIES = WORKSPACE_ROOT / "data" / "abilities"
DEFAULT_OUT_STATUS = WORKSPACE_ROOT / "data" / "status"
DEFAULT_SQLITE_DB = WORKSPACE_ROOT / "database_download" / "veekun-pokedex.sqlite" / "veekun-pokedex.sqlite"


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


def load_table_names(conn: sqlite3.Connection) -> Set[str]:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return {row[0] for row in cur.fetchall()}


def pick_table(existing: Set[str], *candidates: str) -> Optional[str]:
    for name in candidates:
        if name in existing:
            return name
    return None


def normalize_move_category(category_raw: str) -> str:
    """
    Normalize move category from database format to enum format.
    Maps database identifiers (with hyphens and plus signs) to snake_case enum values.
    """
    category_map = {
        "damage": "damage",
        "ailment": "status",
        "damage+ailment": "damage_status",
        "damage+heal": "damage_heal",
        "damage+lower": "damage_lower",
        "damage+raise": "damage_raise",
        "field-effect": "field_effect",
        "force-switch": "force_switch",
        "heal": "heal",
        "net-good-stats": "net_good_stats",
        "ohko": "ohko",
        "swagger": "swagger",
        "unique": "unique",
        "whole-field-effect": "whole_field_effect",
    }
    return category_map.get(category_raw, to_lower_snake(category_raw))


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
    category = normalize_move_category(category_name)
    
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
        "flags": [],
    }
    return payload


def generate_move_pkmn_file(payload: Dict[str, Any]) -> str:
    """Generate .pkmn file content from move payload using MoveMetaData."""
    move_id = payload.get("name")
    class_name = "_" + "".join(word.capitalize() for word in move_id.split("_"))
    
    # Build MoveMetaData
    meta_lines = [
        "    meta = MoveMetaData(",
        f'        display_name="{payload.get("display_name")}",',
        f'        index={payload.get("index")},',
        f'        type=PokemonType("{payload.get("type")}"),',
    ]
    
    # Convert damage_class to enum format
    damage_class_raw = payload.get("damage_class", "physical")
    damage_class_map = {
        "physical": "DamageClass.PHYSICAL",
        "special": "DamageClass.SPECIAL",
        "status": "DamageClass.STATUS",
    }
    damage_class = damage_class_map.get(damage_class_raw, f'DamageClass("{damage_class_raw}")')
    meta_lines.append(f'        damage_class={damage_class},')
    
    # Convert category to enum format
    category_raw = payload.get("category", "damage")
    category_map = {
        "damage": "MoveCategory.DAMAGE",
        "status": "MoveCategory.STATUS",
        "damage_status": "MoveCategory.DAMAGE_STATUS",
    }
    category = category_map.get(category_raw, f'MoveCategory("{category_raw}")')
    meta_lines.append(f'        category={category},')
    
    # Handle optional fields
    accuracy = payload.get("accuracy")
    power = payload.get("power")
    
    if accuracy is not None:
        meta_lines.append(f'        accuracy={accuracy},')
    if power is not None:
        meta_lines.append(f'        power={power},')
    
    meta_lines.append(f'        pp={payload.get("pp", 15)},')
    
    # Convert target to enum format
    target_raw = payload.get("target", "selected_pokemon")
    target_map = {
        "selected_pokemon": "MoveTarget.SELECTED_POKEMON",
        "user": "MoveTarget.USER",
        "all_opponents": "MoveTarget.ALL_OPPONENTS",
        "all_allies": "MoveTarget.ALL_ALLIES",
        "all_others": "MoveTarget.ALL_OTHERS",
        "all": "MoveTarget.ALL",
    }
    target = target_map.get(target_raw, f'MoveTarget("{target_raw}")')
    meta_lines.append(f'        target={target},')
    meta_lines.append("    )")
    
    # Build the full file content
    lines = [
        "from pkmn_imports import *",
        "",
        f'@move("{move_id}")',
        f'class {class_name}:',
    ] + meta_lines

    flags = payload.get("flags") or []
    if flags:
        lines.append(f"    flags = {json.dumps(flags)}")

    # Priority as separate top-level attribute
    priority = payload.get("priority", 0)
    if priority != 0:
        lines.append(f"    priority = {priority}")

    stat_changes_inflicted = payload.get("stat_changes_inflicted")
    stat_changes_recieved = payload.get("stat_changes_recieved")
    if stat_changes_inflicted or stat_changes_recieved:
        lines.append("    stat_changes = {")
        if stat_changes_inflicted:
            lines.append(f'        "stat_changes_inflicted": {json.dumps(stat_changes_inflicted)},')
        if stat_changes_recieved:
            lines.append(f'        "stat_changes_recieved": {json.dumps(stat_changes_recieved)},')
        lines.append("    }")

    status_condition = payload.get("status_condition", "none")
    status_condition_chance = payload.get("status_condition_chance", 0)
    if status_condition and status_condition != "none":
        lines.append("    status_condition = {")
        lines.append(f'        "{status_condition}": {status_condition_chance},')
        lines.append("    }")

    crit_rate = payload.get("critical_hit_rate", 0)
    if crit_rate:
        lines.append(f"    critical_hit_rate = {crit_rate}")

    flinch = payload.get("flinch_chance", 0)
    if flinch:
        lines.append(f"    flinch_chance = {flinch}")

    drain = payload.get("drain", 0)
    if drain:
        lines.append(f"    drain = {drain}")
    healing = payload.get("healing", 0)
    if healing:
        lines.append(f"    healing = {healing}")

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


def fetch_english_name(
    cur: sqlite3.Cursor,
    table: Optional[str],
    id_col: str,
    value_col: str,
    target_id: int,
    language_table: Optional[str],
    language_identifier_field: str = "identifier",
    language_value: str = "en",
    language_id_col: str = "local_language_id",
) -> Optional[str]:
    if not table or not language_table:
        return None
    try:
        row = cur.execute(
            f"""
            SELECT n.{value_col}
            FROM {table} n
            JOIN {language_table} l ON l.id = n.{language_id_col}
            WHERE l.{language_identifier_field} = ? AND n.{id_col} = ?
            LIMIT 1
            """,
            (language_value, target_id),
        ).fetchone()
        if row and row[0]:
            return str(row[0])
    except Exception:
        return None
    return None


def generate_moves_from_sqlite(db_path: Path, out_moves: Path, overwrite: bool, limit: Optional[int]) -> int:
    if not db_path.exists() or db_path.stat().st_size == 0:
        print(f"SQLite database {db_path} missing or empty; skipping move generation")
        return 0

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    tables = load_table_names(conn)

    moves_table = pick_table(tables, "moves", "move")
    type_table = pick_table(tables, "types", "type")
    damage_class_table = pick_table(tables, "move_damage_classes", "move_damage_class")
    meta_table = pick_table(tables, "move_meta")
    meta_category_table = pick_table(tables, "move_meta_categories", "move_category", "move_categories")
    target_table = pick_table(tables, "move_targets", "move_target")
    ailment_table = pick_table(tables, "move_meta_ailments", "move_ailments")
    flag_table = pick_table(tables, "move_flags", "move_flag")
    flag_map_table = pick_table(tables, "move_flag_map", "move_flag_maps")
    stat_change_table = pick_table(tables, "move_meta_stat_changes", "move_stat_changes")
    stat_table = pick_table(tables, "stats", "stat")
    move_names_table = pick_table(tables, "move_names")
    language_table = pick_table(tables, "languages", "language")

    required = [moves_table, type_table, damage_class_table, target_table, meta_table]
    if any(t is None for t in required):
        print("SQLite move generation skipped: required tables missing (moves/types/damage_class/target)")
        return 0

    category_select = "mc.identifier AS category" if meta_category_table else "NULL AS category"
    category_join = f"LEFT JOIN {meta_category_table} mc ON mc.id = mm.meta_category_id" if meta_category_table else ""

    ailment_select = "ma.identifier AS ailment" if ailment_table else "NULL AS ailment"
    ailment_join = f"LEFT JOIN {ailment_table} ma ON ma.id = mm.meta_ailment_id" if ailment_table else ""

    meta_join = f"LEFT JOIN {meta_table} mm ON mm.move_id = m.id" if meta_table else ""

    query = f"""
    SELECT
        m.id,
        m.identifier AS name,
        t.identifier AS type,
        dc.identifier AS damage_class,
        {category_select},
        m.accuracy,
        m.power,
        m.pp,
        m.priority,
        mt.identifier AS target,
        mm.min_hits AS min_hits,
        mm.max_hits AS max_hits,
        mm.min_turns AS min_turns,
        mm.max_turns AS max_turns,
        mm.drain AS drain,
        mm.healing AS healing,
        mm.crit_rate AS crit_rate,
        mm.ailment_chance AS ailment_chance,
        mm.flinch_chance AS flinch_chance,
        mm.stat_chance AS stat_chance,
        {ailment_select}
    FROM {moves_table} m
    LEFT JOIN {type_table} t ON t.id = m.type_id
    LEFT JOIN {damage_class_table} dc ON dc.id = m.damage_class_id
    {meta_join}
    {category_join}
    LEFT JOIN {target_table} mt ON mt.id = m.target_id
    {ailment_join}
    ORDER BY m.id
    """

    params: Tuple[Any, ...] = ()
    if limit:
        query += " LIMIT ?"
        params = (limit,)

    out_moves.mkdir(parents=True, exist_ok=True)
    written = 0

    rows = cur.execute(query, params).fetchall()

    for row in rows:
        row_dict = dict(row)
        mname = row_dict.get("name")
        if not mname:
            continue
        # Skip shadow-type moves
        mtype = to_lower_snake(row_dict.get("type")) if row_dict.get("type") else "normal"
        if mtype == "shadow":
            continue
        mslug = to_lower_snake(str(mname))
        display_name = fetch_english_name(
            cur,
            move_names_table,
            id_col="move_id",
            value_col="name",
            target_id=row_dict.get("id", 0),
            language_table=language_table,
            language_id_col="local_language_id",
        ) or to_title_spaces(mslug)

        flags: List[str] = []
        if flag_table and flag_map_table:
            try:
                flag_rows = conn.execute(
                    f"""
                    SELECT mf.identifier
                    FROM {flag_map_table} mfm
                    JOIN {flag_table} mf ON mf.id = mfm.move_flag_id
                    WHERE mfm.move_id = ?
                    """,
                    (row_dict.get("id", 0),),
                ).fetchall()
                flags = [to_lower_snake(fr[0]) for fr in flag_rows if fr and fr[0]]
            except Exception:
                flags = []

        stat_changes_inflicted = None
        stat_changes_recieved = None
        if stat_change_table and stat_table:
            try:
                stat_rows = conn.execute(
                    f"""
                    SELECT s.identifier, msc.change
                    FROM {stat_change_table} msc
                    JOIN {stat_table} s ON s.id = msc.stat_id
                    WHERE msc.move_id = ?
                    """,
                    (row_dict.get("id", 0),),
                ).fetchall()
                stat_list = []
                stat_chance = row_dict.get("stat_chance", 0)
                if stat_chance == 0 and stat_rows:
                    stat_chance = 100
                for sr in stat_rows:
                    stat_identifier = sr[0]
                    change_val = sr[1]
                    if stat_identifier is None or change_val is None:
                        continue
                    stat_list.append({
                        "stat": to_lower_snake(str(stat_identifier)),
                        "change": change_val,
                        "chance": stat_chance,
                    })

                if stat_list:
                    target_slug = to_lower_snake(row_dict.get("target")) if row_dict.get("target") else "selected_pokemon"
                    user_targets = {"user", "user_and_allies", "user_or_allies", "users_field", "ally", "all_allies"}
                    if target_slug in user_targets:
                        stat_changes_recieved = stat_list
                    else:
                        stat_changes_inflicted = stat_list
            except Exception:
                stat_changes_inflicted = None
                stat_changes_recieved = None

        status_condition = to_lower_snake(row_dict.get("ailment")) if row_dict.get("ailment") else "none"
        if status_condition == "none" or status_condition == "unknown":
            status_condition = "none"

        payload: Dict[str, Any] = {
            "name": mslug,
            "display_name": display_name,
            "index": int(row_dict.get("id", 0)),
            "type": to_lower_snake(row_dict.get("type")) if row_dict.get("type") else "normal",
            "damage_class": to_lower_snake(row_dict.get("damage_class")) if row_dict.get("damage_class") else "physical",
            "category": normalize_move_category(row_dict.get("category")) if row_dict.get("category") else "damage",
            "accuracy": row_dict.get("accuracy"),
            "power": row_dict.get("power"),
            "pp": row_dict.get("pp"),
            "target": to_lower_snake(row_dict.get("target")) if row_dict.get("target") else "selected_pokemon",
            "priority": row_dict.get("priority") or 0,
            "status_condition": status_condition,
            "status_condition_chance": row_dict.get("ailment_chance", 0) or 0,
            "critical_hit_rate": ((row_dict.get("crit_rate", 0) or 0) * 8),
            "flinch_chance": row_dict.get("flinch_chance", 0) or 0,
            "drain": row_dict.get("drain", 0) or 0,
            "healing": row_dict.get("healing", 0) or 0,
            "min_hits": row_dict.get("min_hits"),
            "max_hits": row_dict.get("max_hits"),
            "min_turns": row_dict.get("min_turns"),
            "max_turns": row_dict.get("max_turns"),
            "stat_changes_inflicted": stat_changes_inflicted,
            "stat_changes_recieved": stat_changes_recieved,
            "flags": flags,
        }

        target_file = out_moves / f"{mslug}.pkmn"
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

    conn.close()
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


def generate_statuses_from_sqlite(db_path: Path, out_status: Path, overwrite: bool, limit: Optional[int]) -> int:
    if not db_path.exists() or db_path.stat().st_size == 0:
        print(f"SQLite database {db_path} missing or empty; skipping status generation")
        return 0

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    tables = load_table_names(conn)

    ailment_table = pick_table(tables, "move_meta_ailments", "move_ailments")
    ailment_names_table = pick_table(tables, "move_meta_ailment_names", "move_ailment_names")
    language_table = pick_table(tables, "languages", "language")

    english_language_id: Optional[int] = None
    if language_table:
        try:
            row = cur.execute(f"SELECT id FROM {language_table} WHERE identifier = 'en'").fetchone()
            if row:
                english_language_id = int(row[0])
        except Exception:
            english_language_id = None

    if not ailment_table:
        print("Status generation skipped: move_meta_ailments table missing")
        return 0

    params: Tuple[Any, ...] = ()
    if ailment_names_table and language_table and english_language_id:
        query = f"""
        SELECT ma.id, ma.identifier, man.name AS display_name
        FROM {ailment_table} ma
        LEFT JOIN {ailment_names_table} man ON man.move_meta_ailment_id = ma.id AND man.local_language_id = ?
        ORDER BY ma.id
        """
        if limit:
            query += " LIMIT ?"
            params = (english_language_id, limit)
        else:
            params = (english_language_id,)
    else:
        query = f"SELECT ma.id, ma.identifier, NULL AS display_name FROM {ailment_table} ma ORDER BY ma.id"
        if limit:
            query += " LIMIT ?"
            params = (limit,)

    out_status.mkdir(parents=True, exist_ok=True)
    written = 0

    for row in cur.execute(query, params):
        row_dict = dict(row)
        slug = to_lower_snake(row_dict.get("identifier", ""))
        if not slug or slug == "none":
            continue
        display_name = row_dict.get("display_name") or to_title_spaces(slug)
        class_name = "_" + "".join(word.capitalize() for word in slug.split("_")) + "Status"

        lines = [
            f'@status("{slug}")  # type: ignore',
            f'class {class_name}:',
            "    meta = {",
            f'        "display_name": "{display_name}",',
            f'        "mutual_exclusive": {"True" if slug != "none" else "False"},',
            "    }",
        ]

        target_file = out_status / f"{slug}.pkmn"
        if target_file.exists() and not overwrite:
            written += 1
            if limit and written >= limit:
                break
            continue

        with target_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        written += 1
        if limit and written >= limit:
            break

    conn.close()
    return written


# ------------------------- Orchestration -------------------------
def run(
    source: Path,
    sqlite_db: Optional[Path],
    out_pokemon: Path,
    out_moves: Path,
    out_items: Path,
    out_abilities: Path,
    out_status: Path,
    overwrite: bool,
    limit: Optional[int],
    include_pokemon: bool,
    include_moves: bool,
    include_items: bool,
    include_abilities: bool,
    include_status: bool,
) -> None:
    pokemon_dir = source / "pokemon"
    species_dir = source / "pokemon-species"

    use_sqlite = bool(sqlite_db and sqlite_db.exists() and sqlite_db.stat().st_size > 0)

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
        if use_sqlite:
            total_moves = generate_moves_from_sqlite(sqlite_db, out_moves, overwrite, limit)
        else:
            total_moves = generate_moves(source, out_moves, overwrite, limit)

    total_items = 0
    if include_items:
        total_items = generate_items(source, out_items, overwrite, limit)

    total_abilities = 0
    if include_abilities:
        total_abilities = generate_abilities(source, out_abilities, overwrite, limit)

    total_status = 0
    if include_status:
        if use_sqlite:
            total_status = generate_statuses_from_sqlite(sqlite_db, out_status, overwrite, limit)
        else:
            print("Status generation requires SQLite; skipping status files")

    if include_pokemon:
        print(f"Wrote {total_pokemon} Pokémon base files to {out_pokemon}")
    if include_moves:
        print(f"Wrote {total_moves} move files to {out_moves}")
    if include_items:
        print(f"Wrote {total_items} item files to {out_items}")
    if include_abilities:
        print(f"Wrote {total_abilities} ability files to {out_abilities}")
    if include_status:
        print(f"Wrote {total_status} status files to {out_status}")


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Generate Pokémon base data, move data, item data, and ability data from cached PokeAPI JSON")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Source pokeapi_database directory")
    parser.add_argument("--sqlite-db", type=Path, default=DEFAULT_SQLITE_DB, help="Optional SQLite source (uses flags/stat changes from DB when present)")
    parser.add_argument("--out-pokemon", type=Path, default=DEFAULT_OUT_POKEMON, help="Output data/pokemon directory")
    parser.add_argument("--out-moves", type=Path, default=DEFAULT_OUT_MOVES, help="Output data/moves directory")
    parser.add_argument("--out-items", type=Path, default=DEFAULT_OUT_ITEMS, help="Output data/items directory")
    parser.add_argument("--out-abilities", type=Path, default=DEFAULT_OUT_ABILITIES, help="Output data/abilities directory")
    parser.add_argument("--out-status", type=Path, default=DEFAULT_OUT_STATUS, help="Output data/status directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of entries to process (separately for pokemon, moves, items, and abilities)")
    parser.add_argument("--skip-pokemon", action="store_true", help="Skip generating Pokémon data")
    parser.add_argument("--skip-moves", action="store_true", help="Skip generating moves data")
    parser.add_argument("--skip-items", action="store_true", help="Skip generating item data")
    parser.add_argument("--skip-abilities", action="store_true", help="Skip generating ability data")
    parser.add_argument("--skip-status", action="store_true", help="Skip generating status data")

    args = parser.parse_args(argv)
    run(
        source=args.source,
        sqlite_db=args.sqlite_db,
        out_pokemon=args.out_pokemon,
        out_moves=args.out_moves,
        out_items=args.out_items,
        out_abilities=args.out_abilities,
        out_status=args.out_status,
        overwrite=args.overwrite,
        limit=args.limit,
        include_pokemon=not args.skip_pokemon,
        include_moves=not args.skip_moves,
        include_items=not args.skip_items,
        include_abilities=not args.skip_abilities,
        include_status=not args.skip_status,
    )


if __name__ == "__main__":
    main()
