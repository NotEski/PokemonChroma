import random
from shared.pokemon.move import Move
from shared.pokemon.pokemon import Pokemon
from shared.pokemon.types import PokemonType, StatusCondition
from shared.pokemon.move import MoveCategory
from engine.battle.battle_header import BattleState, BattleWeather
from engine.battle.type_effectiveness import get_attack_multiplier

def calculate_damage(attacking_pokemon: Pokemon, defending_pokemon: Pokemon, move: Move, critical_hit: bool, battle_state: BattleState) -> int:
    # Simplified damage calculation formula for demonstration purposes
    # Will need to pull in if this move hits multiple targets

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
    modified_damage = round(modified_damage * _get_weather_modifier(move.base_move.type, battle_state.weather_turns.weather))
    modified_damage = round(modified_damage * _get_glaive_rush_modifier(glaive_rush))
    modified_damage = round(modified_damage * _get_critical_modifier(critical_hit))
    modified_damage = round(modified_damage * _get_random_factor())
    modified_damage = round(modified_damage * _get_stab_modifier(attacking_pokemon, move))
    modified_damage = round(modified_damage * _get_type_effectiveness_modifier(move, defending_pokemon))
    modified_damage = round(modified_damage * _get_burn_modifier(attacking_pokemon, move))
    modified_damage = round(modified_damage * _get_other_modifiers())

    return max(1, modified_damage)  # Ensure at least 1 damage is dealt

def _get_level_modifier(level: int) -> float:
    return (2 * level) / 5 + 2

def _get_power_modifier(move) -> float:
    return move.base_move.power if move.base_move.power is not None else 0

def _get_attack_stat_modifier(attacking_pokemon: Pokemon, move: Move) -> int:
    if move.base_move.category == MoveCategory.PHYSICAL:
        attack_stat = attacking_pokemon.get_attack_stat()

        return attack_stat
    else:
        attack_stat = attacking_pokemon.get_special_attack_stat()

        return attack_stat

def _get_defence_stat_modifier(defending_pokemon: Pokemon, move: Move) -> int:
    flip_defence = False  # Placeholder for moves that flip defense and special defense
    if move.base_move.category == MoveCategory.PHYSICAL and not flip_defence:
        defence_stat = defending_pokemon.get_defense_stat()
        
        return defence_stat
    else:
        defence_stat = defending_pokemon.get_special_defense_stat()

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

def _get_critical_modifier(is_critical_hit) -> float:
    if is_critical_hit:
        return 1.5
    return 1.0

def _get_random_factor() -> float:
    return random.uniform(0.85, 1.0)

def _get_stab_modifier(attacking_pokemon: Pokemon, move: Move) -> float:
    if move.base_move.type in attacking_pokemon.pokemon.types:
        return 1.5
    return 1.0

def _get_type_effectiveness_modifier(move: Move, defending_pokemon: Pokemon) -> float:
    multiplier = get_attack_multiplier(move.base_move.type, defending_pokemon.pokemon.types)
    return multiplier if multiplier > 0 else 0.0

def _get_burn_modifier(attacking_pokemon: Pokemon, move: Move) -> float:
    if move.base_move.category == MoveCategory.PHYSICAL and attacking_pokemon.status_condition == StatusCondition.BURNED:
        # TODO Check if the Pokémon has the Guts ability to return 1.0 instead
        # if attacking_pokemon.ability
        return 0.5
    return 1.0

def _get_other_modifiers() -> float:
    # Placeholder for other miscellaneous modifiers
    return 1.0



def calculate_critical_hit(attacking_pokemon: Pokemon) -> bool:
    is_critical = False
    if attacking_pokemon.pokemon_battle_state.critical_hit_stage == 0:
        chance = 1/24
        if random.random() < chance:
            is_critical = True
    elif attacking_pokemon.pokemon_battle_state.critical_hit_stage == 1:
        chance = 1/8
        if random.random() < chance:
            is_critical = True
    elif attacking_pokemon.pokemon_battle_state.critical_hit_stage == 2:
        chance = 1/2
        if random.random() < chance:
            is_critical = True
    elif attacking_pokemon.pokemon_battle_state.critical_hit_stage >= 3:
        is_critical = True
    return is_critical