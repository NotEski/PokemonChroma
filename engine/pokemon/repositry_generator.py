# Generate Repository from json files

import ast
import json
import builtins
from random import randint
import os
from shared.pokemon.genders import GenderRate
from shared.pokemon.hazard import EntryHazard
from shared.battle.field_effect import FieldEffect
from shared.pokemon.move import BaseMove, MoveTarget, DamageClass, MoveCategory
from shared.pokemon.move_tags import *
from shared.pokemon.status_conditions import StatusCondition
from shared.pokemon.pokemon import PokemonBase, GrowthRate, EggGroup
from shared.pokemon.abilities import Ability, AbilitySlot, PokemonBaseAbility
from engine.pokemon.repository import (
    pokemon_repository,
    ability_repository,
    move_repository,
    item_repository,
    status_repository,
    hazard_repository,
    field_effect_repository
)
from shared.pokemon.types import PokemonType
from shared.pokemon.stats import BaseStats, EffortYield
from shared.items.items import Item, ItemCategory, ItemAttribute, ItemFlingEffect, ItemPocket
from shared.battle.weather import BattleWeather




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

        # Below are MoveTags specific fields

        move_tags = []
        healing_flag = None
        heal_exception = False
        dsl_cls.flags = dsl_cls.__dict__.get("flags", None)
        if dsl_cls.flags is not None:
            for flag in dsl_cls.flags:
                match flag:
                    case "contact":
                        move_tags.append(ContactMove())
                    case "charge":
                        move_tags.append(ChargeMove())
                    case "recharge":
                        move_tags.append(RechargeMove())
                    case "protect":
                        move_tags.append(ProtectMove())
                    case "reflectable":
                        move_tags.append(ReflectableMove())
                    case "snatch":
                        move_tags.append(SnatchMove())
                    case "mirror":
                        move_tags.append(MirrorMove())
                    case "punch":
                        move_tags.append(PunchMove())
                    case "sound":
                        move_tags.append(SoundMove())
                    case "gravity":
                        move_tags.append(GravityMove())
                    case "defrost":
                        move_tags.append(DefrostMove())
                    case "distance":
                        move_tags.append(DistanceMove())
                    case "heal":
                        # Set a value that needs to be true by the end of decorator
                        # This will be set by healing or positive drain
                        healing_flag = False
                    case "authentic":
                        move_tags.append(AuthenticMove())
                    case "powder":
                        move_tags.append(PowderMove())
                    case "bite":
                        move_tags.append(BiteMove())
                    case "pulse":
                        move_tags.append(PulseMove())
                    case "ballistics":
                        move_tags.append(BallisticsMove())
                    case "mental":
                        move_tags.append(MentalMove())
                    case "non-sky-battle":
                        move_tags.append(NonSkyBattleMove())
                    case "pivot":
                        move_tags.append(PivotMove())
                    case "heal_exception":
                        heal_exception = True

        # Critical Hit Rate
        critical_hit_rate = dsl_cls.__dict__.get("critical_hit_rate", None)
        if critical_hit_rate is not None:
            move_tags.append(CriticalHitMove(critical_hit_rate_increase=critical_hit_rate))

        # Drain
        drain = dsl_cls.__dict__.get("drain", None)
        if drain is not None and drain != 0:
            if healing_flag is False and drain > 0:
                healing_flag = True
            move_tags.append(DrainMove(drain_percentage=drain))

        # Flinch Chance
        flinch_chance = dsl_cls.__dict__.get("flinch_chance", None)
        if flinch_chance is not None:
            move_tags.append(FlinchMove(chance=flinch_chance))

        # Status Condition and chance
        status_condition = dsl_cls.__dict__.get("status_condition", None)
        if status_condition is not None:
            if isinstance(status_condition, dict):
                for sc_name, sc_chance in status_condition.items():
                    status_condition_obj = get_status_condition(sc_name)
                    move_tags.append(StatusConditionMove(
                        status_condition=status_condition_obj,
                        chance=sc_chance
                    ))
            else:
                raise ValueError(f"Move '{move_name}' has invalid status_condition definition. {type(status_condition)} found, dict expected.")
        
        # Healing
        healing = dsl_cls.__dict__.get("healing", None)
        if healing is not None:
            if healing_flag is False and healing > 0:
                healing_flag = True
            if healing != 0:
                move_tags.append(HealMove(heal_percentage=healing))

        # Stat Changes
        stat_changes = dsl_cls.__dict__.get("stat_changes", None)
        if stat_changes is not None:
            if "stat_changes_inflicted" in stat_changes:
                for sc in stat_changes["stat_changes_inflicted"]:
                    stat_change = StatChangeInflictedMove(**sc)
                    move_tags.append(stat_change)
            if "stat_changes_received" in stat_changes:
                for sc in stat_changes["stat_changes_received"]:
                    stat_change = StatChangeReceivedMove(**sc)
                    move_tags.append(stat_change)

        # Hazard
        hazard: dict = dsl_cls.__dict__.get("hazard", None)
        if hazard is not None:
            for hazard_name, layers_added in hazard.items():
                harard_obj = hazard_repository.get(hazard_name)
                move_tags.append(EntryHazardMove(entry_hazard=harard_obj, layers=layers_added))

        if healing_flag is not None and healing_flag is False and not heal_exception:
            raise ValueError(f"Move '{move_name}' has 'heal' flag but no healing or drain defined.")
        
        # Field Effect
        field_effect: dict = dsl_cls.__dict__.get("field_effect", None)
        if field_effect is not None:
            for field_effect_name, field_effect_turns in field_effect.items():
                field_effect_obj = field_effect_repository.get(field_effect_name)
                if field_effect_obj is None:
                    raise ValueError(f"Move '{move_name}' field effect '{field_effect_name}' not found in repository.")
                if field_effect_turns is None:
                    field_effect_turns = field_effect_obj.default_duration
                move_tags.append(FieldEffectMove(field_effect=field_effect_obj, turns=field_effect_turns))

        # Multi-hit
        multi_hit: dict|tuple|bool = dsl_cls.__dict__.get("multi_hit", None)
        if multi_hit is not None:
            if isinstance(multi_hit, tuple):
                # Convert list to dict with equal weights
                min_hit = min(multi_hit)
                max_hit = max(multi_hit)
                for i in range(min_hit, max_hit + 1):
                    multi_hit = {i: 1 for i in range(min_hit, max_hit + 1)}
            elif isinstance(multi_hit, bool) and multi_hit is True:
                move_tags.append(MultiHitMove()) # Use default weights if just true

            if not isinstance(multi_hit, bool): # If not just True, as the default weights will be used and the custom weights have now been processed
                    move_tags.append(MultiHitMove(hits=multi_hit))
                


        # Weather
        if "weather" in dsl_cls.__dict__:
            weather: BattleWeather = BattleWeather(dsl_cls.__dict__.get("weather", None))
            move_tags.append(WeatherMove(weather=weather))
            

        # Generate BaseMove
        base_move = BaseMove(
            name=move_name,
            display_name=display_name,
            index=index,
            type=move_type,
            damage_class=damage_class,
            category=category,
            accuracy=accuracy,
            power=power,
            base_pp=pp,
            target=target,
            priority=priority,
            move_tags=move_tags
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
        dsl_cls.default_data = dsl_cls.__dict__.get("default_data", {})
        status_condition = StatusCondition(
            name=status_name,
            display_name=dsl_cls.meta.get("display_name", status_name.capitalize()),
            mutual_exclusive=dsl_cls.meta.get("mutual_exclusive", False),
            default_data=dsl_cls.default_data
            )

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

def hazard(hazard_name: str):
    def decorator(dsl_cls):
        dsl_cls.meta = dsl_cls.__dict__.get("meta", {})
        display_name = get_field(dsl_cls.meta, "display_name", str, required=False, default=hazard_name.capitalize())
        hazard = EntryHazard(name=hazard_name, display_name=display_name)
        if hasattr(dsl_cls, "on_entry"):
            dsl_method = dsl_cls.on_entry
            hazard.on_entry = lambda pokemon, layer_count, method=dsl_method: method(dsl_cls, pokemon, layer_count)
        try:
            hazard_repository.create(hazard)
        except ValueError:
            pass  # Ignore if already exists
        return dsl_cls
    return decorator

def field_effect(field_effect_name: str):
    def decorator(dsl_cls):
        dsl_cls.meta = dsl_cls.__dict__.get("meta", {})
        display_name = get_field(dsl_cls.meta, "display_name", str, required=False, default=field_effect_name.capitalize())
        duration = get_field(dsl_cls.meta, "default_duration", int, required=True)

        field_effect = FieldEffect(
            name=field_effect_name,
            display_name=display_name,
            default_duration=duration
        )

        if hasattr(dsl_cls, "on_apply"):
            dsl_method = dsl_cls.on_apply
            field_effect.on_apply = lambda position, method=dsl_method: method(dsl_cls, position)

        if hasattr(dsl_cls, "on_remove"):
            dsl_method = dsl_cls.on_remove
            field_effect.on_remove = lambda position, method=dsl_method: method(dsl_cls, position)

        if hasattr(dsl_cls, "on_stat_calculation"):
            dsl_method = dsl_cls.on_stat_calculation
            field_effect.on_stat_calculation = lambda pokemon, stat, method=dsl_method: method(dsl_cls, pokemon, stat)

        field_effect_repository.create(field_effect)
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
        "hazard": hazard,
        "field_effect": field_effect,

        "get_status_condition": get_status_condition,
        "get_move": get_move,
        "get_ability": get_ability,
        "get_item": get_item,
        "get_type": PokemonType,
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
            print (f"Loading Ability Repo      - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            load_dsl_files_from_directory(file_path)
    print()

    # Generate Status Condition Repository
    status_conditions_folder_path = os.path.join(application_root_path, "data/status")
    for subdir, _, files in os.walk(status_conditions_folder_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.pkmn')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print (f"Loading Status Repo       - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            load_dsl_files_from_directory(file_path)
    print()

    # Generate Entry Hazard Repository
    hazards_folder_path = os.path.join(application_root_path, "data/hazards")
    for subdir, _, files in os.walk(hazards_folder_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.pkmn')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print (f"Loading Hazard Repo       - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            load_dsl_files_from_directory(file_path)
    print()

    # Generate Field Effect Repository
    field_effects_folder_path = os.path.join(application_root_path, "data/field_effects")
    for subdir, _, files in os.walk(field_effects_folder_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.pkmn')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print (f"Loading Field Effect Repo - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            load_dsl_files_from_directory(file_path)
    print()

    # Generate Moves Repository
    moves_folder_path = os.path.join(application_root_path, "data/moves")
    for subdir, _, files in os.walk(moves_folder_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.pkmn')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print (f"Loading Move Repo         - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            load_dsl_files_from_directory(file_path)
    print()

    # Generate Pokemon Repository
    pokemon_folder_path = os.path.join(application_root_path, "data/pokemon")
    for subdir, _, files in os.walk(pokemon_folder_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.json')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print(f"Loading Pokemon Repo      - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            generate_pokemon_repository_from_json(file_path)
    print()

    # Generate Item Repository
    items_folder_path = os.path.join(application_root_path, "data/items")
    for subdir, _, files in os.walk(items_folder_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.json')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print (f"Loading Item Repo         - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            generate_item_repository_from_json(file_path)
    print()

