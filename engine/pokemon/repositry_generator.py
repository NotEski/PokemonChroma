# Generate Repository from json files

import ast
import json
import builtins
from random import randint
import os
from shared.pokemon.genders import GenderRate
from shared.pokemon.move import BaseMove, MoveTarget, DamageClass, MoveCategory, StatChange
from shared.pokemon.status_conditions import StatusCondition
from shared.pokemon.pokemon import PokemonBase, GrowthRate, EggGroup
from shared.pokemon.abilities import Ability, AbilitySlot, PokemonBaseAbility
from engine.pokemon.repository import pokemon_repository, ability_repository, move_repository, item_repository, status_repository
from shared.pokemon.types import PokemonType
from shared.pokemon.stats import BaseStats, EffortYield
from shared.items.items import Item, ItemCategory, ItemAttribute, ItemFlingEffect, ItemPocket




class DSLParseError(Exception):
    pass


def move(move_name: str):
    def decorator(dsl_cls):
        dsl_cls.meta = dsl_cls.__dict__.get("meta", {})

        # Display Name
        display_name = get_field(dsl_cls.meta, "display_name", str, required=False, default=move_name.capitalize())
        # Index
        index = get_field(dsl_cls.meta, "index", int)
        # Type
        move_type = get_field(dsl_cls.meta, "type", PokemonType)
        # Damage Class
        damage_class = get_field(dsl_cls.meta, "damage_class", DamageClass)
        # Category
        category = get_field(dsl_cls.meta, "category", MoveCategory)
        # Accuracy
        accuracy = get_field(dsl_cls.meta, "accuracy", int, required=False, default=None)
        # Power
        power = get_field(dsl_cls.meta, "power", int, required=False, default=None)
        # PP
        pp = get_field(dsl_cls.meta, "pp", int, required=False, default=15)
        # Target
        target = get_field(dsl_cls.meta, "target", MoveTarget, required=False, default=MoveTarget.SELECTED_POKEMON)
        # Priority
        priority = get_field(dsl_cls.meta, "priority", int, required=False, default=0)

        # Status Condition and chance
        # Needs to be looked into further as these might be becoming a part of on hit effects so they can be more dynamic
        # but for now we will keep them here for simplicity
        if "status_condition" in dsl_cls.meta and dsl_cls.meta.get("status_condition") is not None:
            status_condition = status_repository.get(dsl_cls.meta.get("status_condition"))
        else:
            status_condition = None

        status_condition_chance = get_field(dsl_cls.meta, "status_condition_chance", int, required=False, default=0)
        # Critical Hit Rate
        critical_hit_rate = get_field(dsl_cls.meta, "critical_hit_rate", int, required=False, default=0)
        # Flinch Chance
        flinch_chance = get_field(dsl_cls.meta, "flinch_chance", int, required=False, default=0)
        # Drain
        drain = get_field(dsl_cls.meta, "drain", int, required=False, default=0)
        # Healing
        healing = get_field(dsl_cls.meta, "healing", int, required=False, default=0)
        # Stat Changes Inflicted
        stat_changes_inflicted = []
        if "stat_changes_inflicted" in dsl_cls.meta and dsl_cls.meta.get("stat_changes_inflicted") is not None:
            for sc in dsl_cls.meta.get("stat_changes_inflicted", []):
                stat_change = StatChange(**sc)
                stat_changes_inflicted.append(stat_change)
        # Stat Changes Received
        stat_changes_recieved = []
        if "stat_changes_recieved" in dsl_cls.meta and dsl_cls.meta.get("stat_changes_recieved") is not None:
            for sc in dsl_cls.meta.get("stat_changes_recieved", []):
                stat_change = StatChange(**sc)
                stat_changes_recieved.append(stat_change)

        base_move = BaseMove(
            name=move_name,
            display_name=display_name,
            index=index,
            type=move_type,
            damage_class=damage_class,
            category=category,
            accuracy=accuracy,
            power=power,
            pp=pp,
            target=target,
            priority=priority,
            status_condition=status_condition,
            status_condition_chance=status_condition_chance,
            critical_hit_rate=critical_hit_rate,
            flinch_chance=flinch_chance,
            drain=drain,
            healing=healing,
            stat_changes_inflicted=stat_changes_inflicted,
            stat_changes_recieved=stat_changes_recieved,
        )

        if hasattr(dsl_cls, "on_use"):
            dsl_method = dsl_cls.on_use
            base_move.on_use = lambda attacker, defender, battle_state: dsl_method(base_move, attacker, defender, battle_state)
        if hasattr(dsl_cls, "on_hit"):
            dsl_method = dsl_cls.on_hit
            base_move.on_hit = lambda: dsl_method(base_move)
        if hasattr(dsl_cls, "before_use"):
            dsl_method = dsl_cls.before_use
            base_move.before_use = lambda: dsl_method(base_move)
        if hasattr(dsl_cls, "damage_calculation"):
            dsl_method = dsl_cls.damage_calculation
            base_move.damage_calculation = lambda attacker, defender: dsl_method(base_move, attacker, defender)

        move_repository.create(base_move)
        return dsl_cls
    return decorator

def status(status_name: str):
    def decorator(dsl_cls):
        dsl_cls.meta = dsl_cls.__dict__.get("meta", {})
        status_condition = StatusCondition(name=status_name, display_name=dsl_cls.meta.get("display_name", status_name.capitalize()), mutual_exclusive=dsl_cls.meta.get("mutual_exclusive", False))

        if hasattr(dsl_cls, "on_inflicted"):
            dsl_method = dsl_cls.on_inflicted
            status_condition.on_inflicted = lambda pokemon, method=dsl_method: method(dsl_cls, pokemon)

        if hasattr(dsl_cls, "on_turn_start"):
            dsl_method = dsl_cls.on_turn_start
            status_condition.on_turn_start = lambda pokemon, method=dsl_method: method(dsl_cls, pokemon)

        if hasattr(dsl_cls, "on_turn_end"):
            dsl_method = dsl_cls.on_turn_end
            status_condition.on_turn_end = lambda pokemon, method=dsl_method: method(dsl_cls, pokemon)
            
        if hasattr(dsl_cls, "on_switch_out"):
            dsl_method = dsl_cls.on_switch_out
            status_condition.on_switch_out = lambda pokemon, method=dsl_method: method(dsl_cls, pokemon)

        if hasattr(dsl_cls, "can_move"):
            dsl_method = dsl_cls.can_move
            status_condition.can_move = lambda pokemon, method=dsl_method: method(dsl_cls, pokemon)
        

        status_repository.create(status_condition)
        return dsl_cls
    return decorator

def item(item_name: str):
    def decorator(dsl_cls):
        # Code goes here for registering items
        return dsl_cls
    return decorator

def ability(ability_name: str):
    def decorator(dsl_cls):
        dsl_cls.meta = dsl_cls.__dict__.get("meta", {})
        ability = Ability(
            name=ability_name,
            display_name=dsl_cls.meta.get("display_name", ability_name.capitalize()),
            description=dsl_cls.meta.get("description", ""),
        )
        ability_repository.create(ability)
        return dsl_cls
    return decorator

def get_status_condition(status_name: str) -> StatusCondition:
    status_condition = status_repository.get(status_name.lower())
    if status_condition is None:
        raise ValueError(f"Status Condition '{status_name}' not found in status repository.")
    return status_condition

def get_move(move_name: str) -> BaseMove:
    move = move_repository.get(move_name.lower())
    if move is None:
        raise ValueError(f"Move '{move_name}' not found in move repository.")
    return move

def get_ability(ability_name: str) -> Ability:
    ability = ability_repository.get(ability_name.lower())
    if ability is None:
        raise ValueError(f"Ability '{ability_name}' not found in ability repository.")
    return ability

def get_item(item_name: str) -> Item:
    item = item_repository.get(item_name.lower())
    if item is None:
        raise ValueError(f"Item '{item_name}' not found in item repository.")
    return item

safe_namespace = {
        "__builtins__": {
            "__build_class__": builtins.__build_class__,
            "__name__": str,
            "dict": dict,
            "list": list,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "None": None,
            "True": True,
            "False": False,
            "print": print, # for debugging purposes only will be removed later
            "max": max,
            "min": min,
            "len": len,
            "randint": randint,
        },
        "move": move,
        "status": status,
        "item": item,
        "ability": ability,

        "get_status_condition": get_status_condition,
        "get_move": get_move,
        "get_ability": get_ability,
        "get_item": get_item,
    }

def validate_dsl_code_strict(source: str, filename: str):
    tree = ast.parse(source, filename=filename)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise DSLParseError(
                f"Imports not allowed in {filename}. "
                f"Move definitions must be self-contained."
            )
        
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                blocked_calls = {
                    "open", "exec", "eval", "__import__",
                    "compile", "globals", "locals", "vars"
                }
                if node.func.id in blocked_calls:
                    raise DSLParseError(
                        f"Use of '{node.func.id}' is not allowed in {filename}."
                    )
            # Block os.*, sys.*, subprocess.*
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    blocked_modules = {"os", "sys", "subprocess", "pathlib", "importlib"}
                    if node.func.value.id in blocked_modules:
                        raise DSLParseError(
                            f"Access to '{node.func.value.id}' not allowed in {filename}"
                        )
    return True

def load_dsl_files_from_directory(file_path: str):   

    try:
        with open(file_path) as f:
            source = f.read()
        
        # Validate first
        validate_dsl_code_strict(source, str(file_path))
        
        # Execute with safe namespace only
        exec(compile(source, file_path, 'exec'), safe_namespace)

    except DSLParseError as e:
        print(f"Error loading {file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error loading {file_path}: {e}")

def get_field(meta: dict, field_name: str, field_type, required: bool = True, default=None):
    if field_name not in meta:
        if required:
            raise ValueError(f"Field '{field_name}' is required in meta.")
        else:
            return default
        
    value = meta.get(field_name)
    if value is None:
        return None
    if isinstance(value, field_type):
        return value
    return field_type(value)




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
        display_name=json_data["display_name"],
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
# Item
# ============================================================================

def json_to_item(json_data: dict) -> Item:
    return Item(
        name=json_data["name"],
        display_name=json_data["display_name"],
        index=json_data["index"],
        description=json_data["description"],
        cost=json_data.get("cost", 0),
        attributes=[ItemAttribute(attr) for attr in json_data.get("attributes", [])],
        fling_effect=ItemFlingEffect(json_data.get("fling_effect")) if json_data.get("fling_effect") else None,
        fling_power=json_data.get("fling_power", None),
        baby_trigger_for=json_data.get("baby_trigger_for", None),
        category=ItemCategory(json_data["category"]),
        held_by_pokemon=json_data.get("held_by_pokemon", []),
        pocket=ItemPocket(json_data["pocket"]) if json_data.get("pocket") else None,
    )

def load_item_from_json_file(file_path: str) -> Item:
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    return json_to_item(json_data)

def generate_item_repository_from_json(file_path: str):
    item = load_item_from_json_file(file_path)
    item_repository.create(item)



# ============================================================================
# Initialize All Repositories
# ============================================================================

def initialize_repositories(application_root_path: str):

    loading_bar_length = 50
    loading_bar_increment_length = 100 / loading_bar_length

    # Generate Ability Repository
    abilities_folder_path = os.path.join(application_root_path, "data/abilities")
    for subdir, _, files in os.walk(abilities_folder_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.pkmn')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print (f"Loading Ability Repo   - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            load_dsl_files_from_directory(file_path)
    print()

    # Generate Status Condition Repository
    status_conditions_folder_path = os.path.join(application_root_path, "data/status")
    for subdir, _, files in os.walk(status_conditions_folder_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.pkmn')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print (f"Loading Status Repo    - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            load_dsl_files_from_directory(file_path)
    print()

    # Generate Moves Repository
    moves_folder_path = os.path.join(application_root_path, "data/moves")
    for subdir, _, files in os.walk(moves_folder_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.pkmn')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print (f"Loading Move Repo      - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            load_dsl_files_from_directory(file_path)
    print()

    # Generate Pokemon Repository
    pokemon_folder_path = os.path.join(application_root_path, "data/pokemon")
    for subdir, _, files in os.walk(pokemon_folder_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.json')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print(f"Loading Pokemon Repo   - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            generate_pokemon_repository_from_json(file_path)
    print()

    # Generate Item Repository
    items_folder_path = os.path.join(application_root_path, "data/items")
    for subdir, _, files in os.walk(items_folder_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.json')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print (f"Loading Item Repo      - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            generate_item_repository_from_json(file_path)
    print()

