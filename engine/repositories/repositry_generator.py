# Generate Repository from json files

import ast
import json
import builtins
from random import randint
import os
from typing import Any, Optional, List, TypeVar, Callable
from shared.battle.type_effectiveness import get_attack_multiplier
from shared.pokemon.genders import GenderRate
from shared.pokemon.hazard import EntryHazard
from shared.battle.field_effect import FieldEffect
from shared.pokemon.move import BaseMove, MoveTarget, DamageClass, MoveCategory, LearnSet
from shared.pokemon.move_tags import *
from shared.pokemon.status_conditions import StatusCondition
from shared.pokemon.pokemon import PokemonBase, BattleMon, GrowthRate, EggGroup
from shared.pokemon.abilities import Ability, AbilitySlot, PokemonBaseAbility
from engine.repositories.repository import (
    type_repository,
    pokemon_repository,
    ability_repository,
    move_repository,
    item_repository,
    status_repository,
    hazard_repository,
    field_effect_repository
)
from shared.pokemon.pokemon_types import PokemonTypeData, PokemonType
from shared.pokemon.stats import BaseStats, Stat, EffortYield
from shared.items.items import Item, ItemCategory, ItemAttribute, ItemFlingEffect, ItemPocket
from shared.battle.weather import BattleWeather
from shared.battle.battle_header import BattleState


# TypeVar for class decorators
T = TypeVar('T', bound=type)


class DSLParseError(Exception):
    pass


def pokemon_type(type_id: str):
    def decorator(dsl_cls: T) -> T:
        name_default = type_id.replace("_", " ").capitalize()
        name = dsl_cls.__dict__.get("name", name_default)
        icon_bytes = dsl_cls.__dict__.get("icon", b"")
        effectiveness = dsl_cls.__dict__.get("effectiveness", {})
        pkmn_type = PokemonTypeData(
            name=name,
            id=type_id,
            icon=icon_bytes,
            effectiveness=effectiveness
        )
        type_repository.create(pkmn_type)
        return dsl_cls
    return decorator

def move(move_name: str):
    def decorator(dsl_cls: T) -> T:

        name = move_name.lower()

        meta: dict[str, Any] = dsl_cls.__dict__.get("meta", {})

        # Display Name
        display_name: str = get_field(meta, "display_name", str, required=False, default=move_name.capitalize())
        # Index
        index: int = get_field(meta, "index", int)
        # Type
        move_type: PokemonType = get_field(meta, "type", PokemonType)
        if not type_repository.get(move_type):
            raise ValueError(f"Move '{move_name}' has unknown type '{move_type}'.")
        # Damage Class
        damage_class: DamageClass = get_field(meta, "damage_class", DamageClass)
        # Category
        category: MoveCategory = get_field(meta, "category", MoveCategory)
        # Accuracy
        accuracy: Optional[int] = get_field(meta, "accuracy", int, required=False, default=None)
        # Power
        power: Optional[int] = get_field(meta, "power", int, required=False, default=None)
        # PP
        pp: int = get_field(meta, "pp", int, required=False, default=15)
        # Target
        target: MoveTarget = get_field(meta, "target", MoveTarget, required=False, default=MoveTarget.SELECTED_POKEMON)

        # Below are MoveTags specific fields

        move_tags: List[MoveTag] = []
        healing_flag = None
        heal_exception = False
        flags: List[str] = dsl_cls.__dict__.get("flags", [])
        for flag in flags:
            match flag:
                case "authentic":
                    move_tags.append(AuthenticMove())
                case "ballistics":
                    move_tags.append(BallisticsMove())
                case "bite":
                    move_tags.append(BiteMove())
                case "charge":
                    move_tags.append(ChargeMove())
                case "contact":
                    move_tags.append(ContactMove())
                case "defrost":
                    move_tags.append(DefrostMove())
                case "distance":
                    move_tags.append(DistanceMove())
                case "gravity":
                    move_tags.append(GravityMove())
                case "heal":
                    # Set a value that needs to be true by the end of decorator
                    # This will be set by healing or positive drain
                    healing_flag = False
                case "heal_exception":
                    heal_exception = True
                case "mirror":
                    move_tags.append(MirrorMove())
                case "mental":
                    move_tags.append(MentalMove())
                case "non_sky_battle":
                    move_tags.append(NonSkyBattleMove())
                case "pivot":
                    move_tags.append(PivotMove())
                case "powder":
                    move_tags.append(PowderMove())
                case "protect":
                    move_tags.append(BlockedByProtectMove())
                case "pulse":
                    move_tags.append(PulseMove())
                case "punch":
                    move_tags.append(PunchMove())
                case "recharge":
                    move_tags.append(RechargeMove())
                case "reflectable":
                    move_tags.append(ReflectableMove())
                case "snatch":
                    move_tags.append(SnatchMove())
                case "sound":
                    move_tags.append(SoundMove())
                case "trap_target":
                    move_tags.append(TrapTargetMove())
                case "trap_user":
                    move_tags.append(TrapUserMove())
                case _:
                    raise ValueError(f"Move '{move_name}' has unknown flag '{flag}'.")

        # Add Typing
        add_typing: Optional[List[dict[str, str]] | dict[str, str]] = dsl_cls.__dict__.get("add_typing", None)
        if add_typing is not None:
            if isinstance(add_typing, dict):
                add_typing = [add_typing]
            for type_name in add_typing:
                move_tags.append(AddTypingMove(typing_to_add=PokemonType(type_name["typing_to_add"]), alt_target=MoveTarget(type_name["alt_target"]) if "alt_target" in type_name else None))

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

        # Field Effect
        field_effect: Optional[dict[str, int|Any]] = dsl_cls.__dict__.get("field_effect", None)
        if field_effect is not None:
            for field_effect_name, field_effect_turns in field_effect.items():
                field_effect_obj = field_effect_repository.get(field_effect_name)
                if field_effect_obj is None:
                    raise ValueError(f"Move '{move_name}' field effect '{field_effect_name}' not found in repository.")
                if field_effect_turns is None:
                    field_effect_turns = field_effect_obj.default_duration
                move_tags.append(FieldEffectMove(field_effect=field_effect_obj, turns=field_effect_turns))

        # Flinch Chance
        flinch_chance = dsl_cls.__dict__.get("flinch_chance", None)
        if flinch_chance is not None:
            move_tags.append(FlinchMove(chance=flinch_chance))

        # Hazard
        hazard: Optional[dict[str, int]] = dsl_cls.__dict__.get("hazard", None)
        if hazard is not None:
            for hazard_name, layers_added in hazard.items():
                hazard_obj = hazard_repository.get(hazard_name)
                if hazard_obj is None:
                    raise ValueError(f"Move '{move_name}' hazard '{hazard_name}' not found in repository.")
                move_tags.append(HazardMove(entry_hazard=hazard_obj, layers=layers_added))

        # Healing
        healing = dsl_cls.__dict__.get("healing", None)
        if healing is not None:
            if healing_flag is False and healing > 0:
                healing_flag = True
            if healing != 0:
                move_tags.append(HealMove(heal_percentage=healing))

        # Multi-hit
        multi_hit: Optional[dict[int, int|float]|tuple[int, int]|bool] = dsl_cls.__dict__.get("multi_hit", None)
        if multi_hit is not None:
            if isinstance(multi_hit, tuple):
                # Convert list to dict with equal weights
                min_hit = min(multi_hit)
                max_hit = max(multi_hit)
                for _ in range(min_hit, max_hit + 1):
                    multi_hit = {i: 1 for i in range(min_hit, max_hit + 1)}
            elif isinstance(multi_hit, bool) and multi_hit is True:
                move_tags.append(MultiHitMove()) # Use default weights if just true

            if not isinstance(multi_hit, bool): # If not just True, as the default weights will be used and the custom weights have now been processed
                 move_tags.append(MultiHitMove(hits=multi_hit)) # type: ignore

        # Pokemon Type Requirement
        pokemon_type_requirement = dsl_cls.__dict__.get("pokemon_type_requirement", None)
        if pokemon_type_requirement is not None:
            move_tags.append(PokemonTypeRequirementMove(required_type=PokemonType(pokemon_type_requirement)))

        # Priority
        priority_value = dsl_cls.__dict__.get("priority", None)
        if priority_value is not None:
            move_tags.append(PriorityMove(priority=priority_value))

        # Protect
        protect: Optional[dict[str, Any]] = dsl_cls.__dict__.get("protect", None)
        if protect is not None:
            if "status_condition_inflicted_on_attacker" in protect:
                sc_name = protect["status_condition_inflicted_on_attacker"]
                status_condition_obj = get_status_condition(sc_name)
                protect["status_condition_inflicted_on_attacker"] = status_condition_obj
            move_tags.append(ProtectMove.model_validate(protect))

        # Remove Typing
        remove_typing: Optional[List[dict[str, str]] | dict[str, str]] = dsl_cls.__dict__.get("remove_typing", None)
        if remove_typing is not None:
            if isinstance(remove_typing, dict):
                remove_typing = [remove_typing]
            for type_name in remove_typing:
                move_tags.append(RemoveTypingMove(
                    typing_to_remove=PokemonType(type_name["typing_to_remove"]),
                    alt_target=MoveTarget(type_name["alt_target"]) if "alt_target" in type_name else None
                    ))

        # Screen
        screen: Optional[dict[str, Any]] = dsl_cls.__dict__.get("screen", None)
        if screen is not None:
            move_tags.append(ScreenMove.model_validate(screen))

        # Stat Changes
        stat_changes: Optional[dict[str, list[dict[str, str | int]]]] = dsl_cls.__dict__.get("stat_changes", None)
        if stat_changes is not None:
            if "stat_changes_inflicted" in stat_changes:
                for sc in stat_changes["stat_changes_inflicted"]:
                    move_tags.append(StatChangeInflictedMove(
                        stat=Stat(sc["stat"]),
                        change=int(sc["change"]),
                        chance=int(sc.get("chance", 100))
                        ))
            if "stat_changes_received" in stat_changes:
                for sc in stat_changes["stat_changes_received"]:
                    move_tags.append(StatChangeReceivedMove(
                        stat=Stat(sc["stat"]),
                        change=int(sc["change"]),
                        chance=int(sc.get("chance", 100))
                        ))

        # Status Condition and chance
        status_condition: Optional[dict[str, int]] = dsl_cls.__dict__.get("status_condition", None)
        if status_condition is not None:
            for sc_name, sc_chance in status_condition.items():
                move_tags.append(StatusConditionMove(
                    status_condition=get_status_condition(sc_name),
                    chance=sc_chance
                ))

        # Terrain
        if "terrain" in dsl_cls.__dict__:
            terrain: BattleTerrain = BattleTerrain(dsl_cls.__dict__.get("terrain", None))
            move_tags.append(TerrainMove(terrain=terrain))

        # Weather
        if "weather" in dsl_cls.__dict__:
            weather: BattleWeather = BattleWeather(dsl_cls.__dict__.get("weather", None))
            move_tags.append(WeatherMove(weather=weather))

        # Weather Affected
        if "weather_affected" in dsl_cls.__dict__:
            weather_info: dict[str, Any] = dsl_cls.__dict__.get("weather_affected", {})
            weather: BattleWeather = BattleWeather(weather_info.get("weather", None))
            multiplier: float = float(weather_info.get("multiplier", 1.0))
            move_tags.append(WeatherAffectedMove(weather=weather, multiplier=multiplier))

        # Weather Dependent
        if "weather_dependent" in dsl_cls.__dict__:
            weather: BattleWeather = BattleWeather(dsl_cls.__dict__.get("weather_dependent", None))
            move_tags.append(WeatherDependentMove(weather=weather))


        if healing_flag is not None and healing_flag is False and not heal_exception:
            raise ValueError(f"Move '{move_name}' has 'heal' flag but no healing or drain defined.")

        # Generate BaseMove
        base_move = BaseMove(
            name=name,
            display_name=display_name,
            index=index,
            type=move_type,
            damage_class=damage_class,
            category=category,
            accuracy=accuracy,
            power=power,
            base_pp=pp,
            target=target,
            move_tags=move_tags
        )

        if hasattr(dsl_cls, "on_use"):
            dsl_method: Callable[[BaseMove, BattleMon, BattleMon, BattleState], None] = dsl_cls.on_use # type: ignore
            base_move.on_use = lambda attacker, defender, battle_state: dsl_method(dsl_cls, attacker, defender, battle_state) # type: ignore
        if hasattr(dsl_cls, "on_hit"):
            dsl_method: Callable[[BaseMove], None] = dsl_cls.on_hit # type: ignore
            base_move.on_hit = lambda: dsl_method(dsl_cls) # type: ignore
        if hasattr(dsl_cls, "before_use"):
            dsl_method: Callable[[BaseMove], None] = dsl_cls.before_use # type: ignore
            base_move.before_use = lambda: dsl_method(dsl_cls) # type: ignore
        if hasattr(dsl_cls, "damage_calculation"):
            dsl_method: Callable[[BaseMove, BattleMon, BattleMon], int] = dsl_cls.damage_calculation # type: ignore
            base_move.damage_calculation = lambda attacker, defender: dsl_method(dsl_cls, attacker, defender) # type: ignore

        move_repository.create(base_move)
        return dsl_cls
    return decorator

def status(status_name: str):
    def decorator(dsl_cls: T) -> T:
        meta = dsl_cls.__dict__.get("meta", {})
        dsl_cls.default_data = dsl_cls.__dict__.get("default_data", {})
        status_condition = StatusCondition(
            name=status_name,
            display_name=meta.get("display_name", status_name.capitalize()),
            mutual_exclusive=meta.get("mutual_exclusive", False),
            default_data=dsl_cls.default_data
            )

        if hasattr(dsl_cls, "on_inflicted"):
            dsl_method: Callable[[StatusCondition, BattleMon], None] = dsl_cls.on_inflicted # type: ignore
            status_condition.on_inflicted = lambda pokemon, method=dsl_method: method(dsl_cls, pokemon) # type: ignore

        if hasattr(dsl_cls, "on_turn_start"):
            dsl_method: Callable[[StatusCondition, BattleMon], None] = dsl_cls.on_turn_start # type: ignore
            status_condition.on_turn_start = lambda pokemon, method=dsl_method: method(dsl_cls, pokemon) # type: ignore

        if hasattr(dsl_cls, "on_turn_end"):
            dsl_method: Callable[[StatusCondition, BattleMon], None] = dsl_cls.on_turn_end # type: ignore
            status_condition.on_turn_end = lambda pokemon, method=dsl_method: method(dsl_cls, pokemon) # type: ignore
            
        if hasattr(dsl_cls, "on_switch_out"):
            dsl_method: Callable[[StatusCondition, BattleMon], None] = dsl_cls.on_switch_out # type: ignore
            status_condition.on_switch_out = lambda pokemon, method=dsl_method: method(dsl_cls, pokemon) # type: ignore

        if hasattr(dsl_cls, "can_move"):
            dsl_method: Callable[[StatusCondition, BattleMon], bool] = dsl_cls.can_move # type: ignore
            status_condition.can_move = lambda pokemon, method=dsl_method: method(dsl_cls, pokemon) # type: ignore
        

        status_repository.create(status_condition)
        return dsl_cls
    return decorator

def hazard(hazard_name: str):
    def decorator(dsl_cls: T) -> T:
        meta = dsl_cls.__dict__.get("meta", {})
        display_name = get_field(meta, "display_name", str, required=False, default=hazard_name.capitalize())
        hazard = EntryHazard(name=hazard_name, display_name=display_name)
        if hasattr(dsl_cls, "on_entry"):
            dsl_method: Callable[[EntryHazard, BattleMon, int], None] = dsl_cls.on_entry # type: ignore
            hazard.on_entry = lambda pokemon, layer_count, method=dsl_method: method(dsl_cls, pokemon, layer_count) # type: ignore
        try:
            hazard_repository.create(hazard)
        except ValueError:
            pass  # Ignore if already exists
        return dsl_cls
    return decorator

def field_effect(field_effect_name: str):
    def decorator(dsl_cls: T) -> T:
        meta = dsl_cls.__dict__.get("meta", {})
        display_name = get_field(meta, "display_name", str, required=False, default=field_effect_name.capitalize())
        duration = get_field(meta, "default_duration", int, required=True)

        field_effect = FieldEffect(
            name=field_effect_name,
            display_name=display_name,
            default_duration=duration
        )

        if hasattr(dsl_cls, "on_apply"):
            dsl_method: Callable[[FieldEffect, int], None] = dsl_cls.on_apply # type: ignore
            field_effect.on_apply = lambda position, method=dsl_method: method(dsl_cls, position) # type: ignore

        if hasattr(dsl_cls, "on_remove"):
            dsl_method: Callable[[FieldEffect, int], None] = dsl_cls.on_remove # type: ignore
            field_effect.on_remove = lambda position, method=dsl_method: method(dsl_cls, position) # type: ignore

        if hasattr(dsl_cls, "on_stat_calculation"):
            dsl_method: Callable[[FieldEffect, BattleMon, str], None] = dsl_cls.on_stat_calculation # type: ignore
            field_effect.on_stat_calculation = lambda pokemon, stat, method=dsl_method: method(dsl_cls, pokemon, stat) # type: ignore

        field_effect_repository.create(field_effect)
        return dsl_cls
    return decorator

def item(item_name: str):
    def decorator(dsl_cls: T) -> T:
        # Code goes here for registering items
        return dsl_cls
    return decorator

def ability(ability_name: str):
    def decorator(dsl_cls: T) -> T:
        meta = dsl_cls.__dict__.get("meta", {})
        ability = Ability(
            name=ability_name,
            display_name=meta.get("display_name", ability_name.capitalize()),
            description=meta.get("description", ""),
        )
        ability_repository.create(ability)
        return dsl_cls
    return decorator

def pokemon(pokemon_name: str):
    def decorator(dsl_cls: T) -> T:
        pokedex_number = dsl_cls.__dict__.get("id", None)
        if pokedex_number is None:
            raise ValueError(f"Pokemon '{pokemon_name}' must have an 'id' attribute defined.")
        display_name = dsl_cls.__dict__.get("display_name", pokemon_name.capitalize())
        types_str = dsl_cls.__dict__.get("types", [])
        if types_str == []:
            raise ValueError(f"Pokemon '{pokemon_name}' must have at least one type defined.")
        types: list[PokemonType] = [PokemonType(type_str) for type_str in types_str]
        base_stats: BaseStats = dsl_cls.__dict__.get("base_stats", BaseStats())
        ev_yield: EffortYield = dsl_cls.__dict__.get("ev_yield", EffortYield())
        catch_rate: int = dsl_cls.__dict__.get("catch_rate", 45)
        base_experience_yield: int = dsl_cls.__dict__.get("base_experience_yield", 64)
        base_happiness: int = dsl_cls.__dict__.get("base_happiness", 70)
        gender_rate_int: int = dsl_cls.__dict__.get("gender_rate", 4)
        gender_rate = GenderRate(gender_rate_int)
        abilities_str: list[dict[str, str|int|bool]] = dsl_cls.__dict__.get("abilities", [])

        abilities: list[PokemonBaseAbility] = []
        for ability_info in abilities_str:
            ability_name: str = ability_info["ability"] # type: ignore
            ability_obj = get_ability(ability_name)
            ability_slot = AbilitySlot(ability_info["slot"])
            is_hidden: bool = ability_info.get("is_hidden", False) # type: ignore
            pkmn_ability = PokemonBaseAbility(
                ability=ability_obj,
                slot=ability_slot,
                is_hidden=is_hidden
            )
            abilities.append(pkmn_ability)

        height_m: float = dsl_cls.__dict__.get("height_m", 1.0)
        weight_kg: float = dsl_cls.__dict__.get("weight_kg", 10.0)
        egg_groups_str: list[str] = dsl_cls.__dict__.get("egg_groups", [])
        egg_groups: list[EggGroup] = [EggGroup(egg_group_str) for egg_group_str in egg_groups_str]
        growth_rate_str: str = dsl_cls.__dict__.get("growth_rate", "medium_fast")
        growth_rate: GrowthRate = GrowthRate(growth_rate_str)
        level_up_moves: dict[int, List[BaseMove]] = {}
        level_moves_dict: dict[int, list[str]] = dsl_cls.__dict__.get("level_moves", {})
        for level, move_names in level_moves_dict.items():
            move_list: List[BaseMove] = []
            for move_name in move_names:
                move_obj = get_move(move_name)
                move_list.append(move_obj)
            level_up_moves[level] = move_list
        
        machine_moves: List[BaseMove] = []
        machine_move_names: List[str] = dsl_cls.__dict__.get("machine_moves", [])
        for move_name in machine_move_names:
            move_obj = get_move(move_name)
            machine_moves.append(move_obj)

        tutor_moves: List[BaseMove] = []
        tutor_move_names: List[str] = dsl_cls.__dict__.get("tutor_moves", [])
        for move_name in tutor_move_names:
            move_obj = get_move(move_name)
            tutor_moves.append(move_obj)

        egg_moves: List[BaseMove] = []
        egg_move_names: List[str] = dsl_cls.__dict__.get("egg_moves", [])
        for move_name in egg_move_names:
            move_obj = get_move(move_name)
            egg_moves.append(move_obj)

        learn_set = LearnSet(
            level_up_moves=level_up_moves,
            machine_moves=machine_moves,
            tutor_moves=tutor_moves,
            egg_moves=egg_moves
        )
        
        pokemon_base = PokemonBase(
            name=pokemon_name,
            display_name=display_name,
            pokedex_number=pokedex_number,
            types=types,
            base_stats=base_stats,
            ev_yield=ev_yield,
            abilities=abilities,
            capture_rate=catch_rate,
            base_experience_yield=base_experience_yield,
            gender_rate=gender_rate,
            base_happiness=base_happiness,
            growth_rate=growth_rate,
            egg_groups=egg_groups,
            height=height_m,
            weight=weight_kg,
            mega_evolutions=[],
            learnset=learn_set
        )
        pokemon_repository.create(pokemon_base)

        return dsl_cls
    return decorator

def mega_evolution(mega_evolution_name: str):
    def decorator(dsl_cls: T) -> T:
        # Code goes here for registering mega evolutions
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

safe_namespace: dict[str, Any|dict[str, Any]] = {
        "__builtins__": {
            "__build_class__": builtins.__build_class__,
            "__import__": builtins.__import__,
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
        "pokemon_type": pokemon_type,
        "move": move,
        "status": status,
        "item": item,
        "ability": ability,
        "hazard": hazard,
        "field_effect": field_effect,
        "pokemon": pokemon,
        "mega_evolution": mega_evolution,

        "get_status_condition": get_status_condition,
        "get_move": get_move,
        "get_ability": get_ability,
        "get_item": get_item,
        "get_attack_multiplier": get_attack_multiplier,

        # imports
        "BaseStats": BaseStats,
        "EffortYield": EffortYield,
        "PokemonType": PokemonType,
        "Stat": Stat,
    }

def validate_dsl_code_strict(source: str, filename: str):
    tree = ast.parse(source, filename=filename)

    ALLOWED_IMPORT_MODULES = (
        "pkmn_imports",
    )

    BLOCKED_CALLS = {
        "open", "exec", "eval",
        "compile", "globals", "locals", "vars"
        }
    BLOCKED_MODULES = {
        "os", "sys", "subprocess", "pathlib",
        "importlib"
        }

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if node.module: # type: ignore
                if not any(node.module.startswith(allowed) for allowed in ALLOWED_IMPORT_MODULES): # type: ignore
                    raise DSLParseError(
                        f"Imports not allowed in {filename}. "
                        f"Move definitions must be self-contained."
                    )
        
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in BLOCKED_CALLS:
                    raise DSLParseError(
                        f"Use of '{node.func.id}' is not allowed in {filename}."
                    )
            # Block os.*, sys.*, subprocess.*
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id in BLOCKED_MODULES:
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

def get_field(meta: dict[str, Any], field_name: str, field_type: Any, required: bool = True, default: Optional[Any] = None) -> Any:
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
# DSL Loader
# ============================================================================

def load_dsl_files(application_root_path: str, loading_bar_length: int = 50, loading_bar_increment_length: float = 2.0,
                                  directory_path: str = "data/dsl", loading_text: str = "DSL Files"):
    
    # Make the loading text at most 20 characters and pad with spaces
    loading_text = loading_text[:20].ljust(20)
    for subdir, _, files in os.walk(directory_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.pkmn')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print (f"Loading {loading_text} - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            load_dsl_files_from_directory(file_path)
    print()


# ============================================================================
# Item
# ============================================================================

def json_to_item(json_data: dict[str, Any]) -> Item:
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

def initialize_repositories(app_path: str):

    loading_bar_length = 50
    loading_bar_increment_length = 100 / loading_bar_length

    # Generate Pokemon Type Repository
    load_dsl_files(app_path, loading_bar_length, loading_bar_increment_length, directory_path="data/types", loading_text="Pokemon Types")

    # Generate Ability Repository
    load_dsl_files(app_path, loading_bar_length, loading_bar_increment_length, directory_path="data/abilities", loading_text="Abilities")

    # Generate Status Condition Repository
    load_dsl_files(app_path, loading_bar_length, loading_bar_increment_length, directory_path="data/status", loading_text="Status Conditions")

    # Generate Entry Hazard Repository
    load_dsl_files(app_path, loading_bar_length, loading_bar_increment_length, directory_path="data/hazards", loading_text="Hazards")

    # Generate Field Effect Repository
    load_dsl_files(app_path, loading_bar_length, loading_bar_increment_length, directory_path="data/field_effects", loading_text="Field Effects")

    # Generate Moves Repository
    load_dsl_files(app_path, loading_bar_length, loading_bar_increment_length, directory_path="data/moves", loading_text="Moves")
    move_repository.refresh_categories()

    # Generate Pokemon Repository
    load_dsl_files(app_path, loading_bar_length, loading_bar_increment_length, directory_path="data/pokemon", loading_text="Pokemon")

    # Generate Item Repository
    items_folder_path = os.path.join(app_path, "data/items")
    for subdir, _, files in os.walk(items_folder_path):
        file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.json')]
        for file_path in file_paths:
            # Loading bar
            progress_percent = (file_paths.index(file_path) + 1) / len(file_paths) * 100
            print (f"Loading Item Repo         - [{'=' * int(progress_percent // loading_bar_increment_length)}{'-' * (loading_bar_length - int(progress_percent // loading_bar_increment_length))}] {progress_percent:.2f}%", end="\r")
            generate_item_repository_from_json(file_path)
    print()
