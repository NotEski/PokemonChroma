import random
from shared.pokemon.move import BaseMove
from shared.pokemon.pokemon import BattleMon
from shared.pokemon.types import PokemonType
from engine.pokemon.repository import status_repository
from shared.pokemon.move import DamageClass
from shared.battle.battle_header import BattleState, BattleWeather
from shared.battle.type_effectiveness import get_attack_multiplier

def calculate_damage(attacking_pokemon: BattleMon, defending_pokemon: BattleMon, move: BaseMove, critical_hit: bool, battle_state: BattleState) -> int:
    # Simplified damage calculation formula for demonstration purposes
    # Will need to pull in if this move hits multiple targets

    if move.power is None or move.power == 0:
        return 0

    # Placeholder values
    targets = 1
    pb_second_strike = False
    glaive_rush = False


    # Base damage calculation

    level_modifier        = _get_level_modifier(attacking_pokemon.level)
    power_modifier        = _get_power_modifier(move)
    attack_stat_modifier  = _get_attack_stat_modifier(attacking_pokemon, move)
    defence_stat_modifier = _get_defence_stat_modifier(defending_pokemon, move)

    initial_damage = ((level_modifier * power_modifier * attack_stat_modifier / defence_stat_modifier) / 50 + 2)

    # Apply modifiers

    modified_damage = round(initial_damage  * _get_targets_modifier(targets))
    modified_damage = round(modified_damage * _get_pb_modifier(pb_second_strike))
    modified_damage = round(modified_damage * _get_weather_modifier(move.type, battle_state.weather_turns.weather))
    modified_damage = round(modified_damage * _get_glaive_rush_modifier(glaive_rush))
    modified_damage = round(modified_damage * _get_critical_modifier(critical_hit))
    modified_damage = round(modified_damage * _get_random_factor())
    modified_damage = round(modified_damage * _get_stab_modifier(attacking_pokemon, move))
    modified_damage = round(modified_damage * _get_type_effectiveness_modifier(move, defending_pokemon))
    modified_damage = round(modified_damage * _get_burn_modifier(attacking_pokemon, move))
    modified_damage = round(modified_damage * _get_other_modifiers())

    if modified_damage <= 0:
        return 0

    return max(1, modified_damage)  # Ensure at least 1 damage is dealt

def _get_level_modifier(level: int) -> float:
    return (2 * level) / 5 + 2

def _get_power_modifier(move: BaseMove) -> float:
    return move.power if move.power is not None else 0

def _get_attack_stat_modifier(attacking_pokemon: BattleMon, move: BaseMove) -> int:
    if move.damage_class == DamageClass.PHYSICAL:
        attack_stat = attacking_pokemon.stat_attack

        return attack_stat
    else:
        attack_stat = attacking_pokemon.stat_special_attack

        return attack_stat

def _get_defence_stat_modifier(defending_pokemon: BattleMon, move: BaseMove) -> int:
    flip_defence = False  # Placeholder for moves that flip defense and special defense
    if move.damage_class == DamageClass.PHYSICAL and not flip_defence:
        defence_stat = defending_pokemon.stat_defense
        
        return defence_stat
    else:
        defence_stat = defending_pokemon.stat_special_defense

        return defence_stat

def _get_targets_modifier(num_targets: int) -> float:
    if num_targets > 1:
        return 0.75
    return 1.0

def _get_pb_modifier(is_second_strike: bool) -> float:
    if is_second_strike:
        return 0.25
    return 1.0

def _get_weather_modifier(move_type: PokemonType, weather: BattleWeather) -> float:
    if weather == BattleWeather.HARSH_SUNLIGHT:
        if move_type == PokemonType.FIRE:
            return 1.5
        elif move_type == PokemonType.WATER:
            return 0.5
    elif weather == BattleWeather.RAIN:
        if move_type == PokemonType.WATER:
            return 1.5
        elif move_type == PokemonType.FIRE:
            return 0.5
    elif weather == BattleWeather.EXTREMELY_HARSH_SUNLIGHT:
        if move_type == PokemonType.FIRE:
            return 1.5
        elif move_type == PokemonType.WATER:
            return 0
    elif weather == BattleWeather.HEAVY_RAIN:
        if move_type == PokemonType.WATER:
            return 1.5
        elif move_type == PokemonType.FIRE:
            return 0
    return 1.0

def _get_glaive_rush_modifier(is_under_effect: bool) -> float:
    if is_under_effect:
        return 2.0
    return 1.0

def _get_critical_modifier(is_critical_hit: bool) -> float:
    if is_critical_hit:
        return 1.5
    return 1.0

def _get_random_factor() -> float:
    return random.uniform(0.85, 1.0)

def _get_stab_modifier(attacking_pokemon: BattleMon, move: BaseMove) -> float:
    if move.type in attacking_pokemon.pokemon_base.types:
        return 1.5
    return 1.0

def _get_type_effectiveness_modifier(move: BaseMove, defending_pokemon: BattleMon) -> float:
    multiplier = get_attack_multiplier(move.type, defending_pokemon.pokemon_base.types)
    return multiplier if multiplier > 0 else 0.0

def _get_burn_modifier(attacking_pokemon: BattleMon, move: BaseMove) -> float:
    if move.damage_class == DamageClass.PHYSICAL and status_repository.get("burn") in attacking_pokemon.status_conditions.keys():
        # TODO Check if the Pokémon has the Guts ability to return 1.0 instead
        # if attacking_pokemon.ability
        return 0.5
    return 1.0

def _get_other_modifiers() -> float:
    # Placeholder for other miscellaneous modifiers
    return 1.0

def calculate_critical_hit(attacking_pokemon: BattleMon, move: BaseMove) -> bool:
    is_critical = False

    critical_hit_stage = attacking_pokemon.critical_hit_stage + move.critical_hit_rate_stage_increase

    if critical_hit_stage == 0:
        chance = 1/24
        if random.random() < chance:
            is_critical = True
    elif critical_hit_stage == 1:
        chance = 1/8
        if random.random() < chance:
            is_critical = True
    elif critical_hit_stage == 2:
        chance = 1/2
        if random.random() < chance:
            is_critical = True
    elif critical_hit_stage >= 3:
        is_critical = True
    return is_critical

