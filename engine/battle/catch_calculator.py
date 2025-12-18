from shared.pokemon.pokemon import Pokemon, StatusCondition
from shared.pokemon.pokeball import Pokeball
from random import randint

import time

status_condition_big_bonus = [
    StatusCondition.SLEEP,
    StatusCondition.FROZEN,
]
status_condition_small_bonus = [
    StatusCondition.PARALYZED,
    StatusCondition.BURNED,
    StatusCondition.POISONED,
]

def calculate_catch_probability(pokemon: Pokemon, pokeball: Pokeball) -> float:

    if pokeball.name == "Master Ball":
        return 65537  # Guaranteed catch (above max shake chance)

    hp_max_x_3 = 3 * pokemon.max_hp
    hp_current_x_2 = 2 * pokemon.current_hp

    dark_grass = 1.0  # Placeholder for Dark Grass effect


    bonus_level = max((30-pokemon.level)//10, 1)

    if pokemon.status_condition in status_condition_big_bonus:
        bonus_status = 2.0
    elif pokemon.status_condition in status_condition_small_bonus:
        bonus_status = 1.5

    rate_modified =  pokemon.pokemon.capture_rate * pokeball.catch_rate_modifier

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

def catch_attempt(pokemon: Pokemon, pokeball: Pokeball) -> bool:
    shake_chance = calculate_catch_probability(pokemon, pokeball)

    for _ in range(4):
        if not calculate_shake(shake_chance):
            print ("Oh no! The Pokémon broke free!")
            return False
        if _ < 3:
            print ("Shake!")
        time.sleep(0.5)  # Simulate time between shakes
    print ("Caught!")
    return True