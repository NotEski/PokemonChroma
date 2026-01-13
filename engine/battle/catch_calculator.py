from shared.pokemon.pokemon import BattleMon
from shared.items.pokeball import Pokeball
from engine.repositories.repository import status_repository
from random import randint

status_condition_big_bonus = [
    status_repository.get("sleep"),
    status_repository.get("freeze"),
]
status_condition_small_bonus = [
    status_repository.get("paralysis"),
    status_repository.get("burn"),
    status_repository.get("poison"),
]

def calculate_catch_probability(pokemon: BattleMon, pokeball: Pokeball) -> int:

    if pokeball.name == "Master Ball":
        return 65537  # Guaranteed catch (above max shake chance)

    hp_max_x_3 = 3 * pokemon.max_hp
    hp_current_x_2 = 2 * pokemon.current_hp

    dark_grass = 1.0  # Placeholder for Dark Grass effect


    bonus_level = max((30-pokemon.level)//10, 1)

    bonus_status = 1.0  # Default no bonus

    for status_condition in pokemon.status_conditions:
        if status_condition in status_condition_big_bonus:
            bonus_status = 2.0
        elif status_condition in status_condition_small_bonus:
            bonus_status = 1.5
        if bonus_status != 1.0:
            break

    rate_modified =  pokemon.pokemon_base.capture_rate * pokeball.catch_rate_modifier

    if rate_modified < 1:
        rate_modified = 1
    elif rate_modified > 255:
        rate_modified = 255


    a  = ((( hp_max_x_3 - hp_current_x_2) / hp_max_x_3) * 4096 * dark_grass * rate_modified) * bonus_level * bonus_status

    # shake proabability
    b = round(65536 * (a / 1044480) ** 0.1875)

    return b




def calculate_shake(shake_chance: int) -> bool:
    roll = randint(0, 65535)
    return roll < shake_chance

def catch_attempt(pokemon: BattleMon, pokeball: Pokeball) -> bool:
    shake_chance = calculate_catch_probability(pokemon, pokeball)

    for _ in range(4):
        if not calculate_shake(shake_chance):
            # send call outs here for shakes, caught and fail
            return False
    return True