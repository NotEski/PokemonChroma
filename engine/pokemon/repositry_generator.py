# Generate Repository from json files

import json
from shared.pokemon.genders import GenderRate
from shared.pokemon.move import BaseMove, MoveTarget, DamageClass, MoveCategory, StatChange
from shared.pokemon.status_conditions import StatusCondition
from shared.pokemon.pokemon import PokemonBase, GrowthRate, EggGroup
from shared.pokemon.abilities import Ability, AbilitySlot, PokemonBaseAbility
from engine.pokemon.repository import pokemon_repository, ability_repository, move_repository
from shared.pokemon.types import PokemonType
from shared.pokemon.stats import BaseStats, EffortYield


# ============================================================================
# Pokemon
# ============================================================================

def json_to_pokemon_base(json_data: dict) -> PokemonBase:
    if json_data.get("base_experience_yield", 64) is None:
        json_data["base_experience_yield"] = 64

    compiled_abilities = []
    for ability_entry in json_data.get("abilities", []):
        ability_name = ability_entry["ability"]
        ability_slot_str = ability_entry.get("slot", 1)
        ability_slot = AbilitySlot(ability_slot_str)
        is_hidden = ability_entry.get("is_hidden", False)

        ability = ability_repository.get(ability_name.lower())
        if ability is None:
            raise ValueError(f"Ability '{ability_name}' not found in ability repository.")
        compiled_abilities.append(PokemonBaseAbility(
            ability=ability,
            is_hidden=is_hidden,
            slot=ability_slot
        ))

    return PokemonBase(
        name=json_data["name"],
        name_readable=json_data["name_readable"],
        pokedex_number=json_data["pokedex_number"],
        types=[PokemonType(type_str) for type_str in json_data["types"]],
        base_stats=BaseStats(**json_data["base_stats"]),
        ev_yield=EffortYield(**json_data.get("ev_yield", {})),
        capture_rate=json_data["capture_rate"],
        base_experience_yield=json_data.get("base_experience_yield", 64),
        base_happiness=json_data.get("base_happiness", 70),
        gender_rate=GenderRate(json_data.get("gender_rate", "4")),
        abilities=compiled_abilities,
        height=json_data.get("height_m", 1.0),
        weight=json_data.get("weight_kg", 1.0),
        egg_groups=[EggGroup(egg_group) for egg_group in json_data.get("egg_groups", "no-eggs")],
        growth_rate=GrowthRate(json_data.get("growth_rate", "medium")),
    )

def load_pokemon_from_json_file(file_path: str) -> PokemonBase:
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    return json_to_pokemon_base(json_data)

def generate_pokemon_repository_from_json(file_path: str):
    pokemon_base = load_pokemon_from_json_file(file_path)
    pokemon_repository.create(pokemon_base)


# ============================================================================
# Ability
# ============================================================================

def json_to_ability(json_data: dict) -> Ability:
    return Ability(
        name=json_data["name"],
        name_readable=json_data["name_readable"],
        description=json_data["description"]
    )

def load_ability_from_json_file(file_path: str) -> Ability:
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    return json_to_ability(json_data)

def generate_abilities_repository_from_json(file_path: str):
    with open(file_path, 'r') as f:
        json_data = json.load(f)
        for ability_name, ability_data in json_data.items():
            pokemon_ability = Ability(
                name=ability_name,
                name_readable=ability_data["name_readable"],
                description=ability_data["description"]
            )
            ability_repository.create(pokemon_ability)


# ============================================================================
# Move
# ============================================================================

def json_to_move(json_data: dict) -> BaseMove:
    stat_changes_inflicted = []
    if "stat_changes_inflicted" in json_data:
        if isinstance(json_data["stat_changes_inflicted"], list):
            for sc in json_data["stat_changes_inflicted"]:
                stat_changes_inflicted.append(StatChange(**sc))
    
    stat_changes_recieved = []
    if "stat_changes_recieved" in json_data:
        if isinstance(json_data["stat_changes_recieved"], list):
            for sc in json_data["stat_changes_recieved"]:
                stat_changes_recieved.append(StatChange(**sc))
    

    return BaseMove(
        name=json_data["name"],
        name_readable=json_data.get("name_readable", json_data["name"]),
        index=json_data["index"],
        type=PokemonType(json_data["type"]),
        damage_class=DamageClass(json_data["damage_class"]),
        category=MoveCategory(json_data["category"]),
        accuracy=json_data.get("accuracy"),
        power=json_data.get("power"),
        pp=json_data.get("pp", 10),
        target=MoveTarget(json_data.get("target", "selected_pokemon")),
        priority=json_data.get("priority", 0),
        status_condition=StatusCondition(json_data.get("status_condition", "none")),
        status_condition_chance=json_data.get("status_condition_chance", 0),
        critical_hit_rate=json_data.get("critical_hit_rate", 0),
        flinch_chance=json_data.get("flinch_chance", 0),
        drain=json_data.get("drain", 0),
        healing=json_data.get("healing", 0),
        min_hits=json_data.get("min_hits"),
        max_hits=json_data.get("max_hits"),
        min_turns=json_data.get("min_turns"),
        max_turns=json_data.get("max_turns"),
        stat_changes_inflicted=stat_changes_inflicted,
        stat_changes_recieved=stat_changes_recieved,
    )

def load_move_from_json_file(file_path: str) -> BaseMove:
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    return json_to_move(json_data)

def generate_move_repository_from_json(file_path: str):
    move = load_move_from_json_file(file_path)
    move_repository.create(move)