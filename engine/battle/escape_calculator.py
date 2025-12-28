# Calculate if you can successfully flee from a wild battle.


# A=Speed of pokemon trying to run away.

# B=Speed of opponent's pokemon, divided by four.

# C=Number of times you tried to run away.


# If your F value is over 255, then you will successfully run away;
# if it is 255 or less, then the game will generate a random number over the interval [0,255].
# 
# If the number is greater than F, then you escape.
# If not, then you "can't escape" and wasted a turn.

from shared.pokemon.pokemon import BattleMon
import random

def calculate_escape_success(escaping_pokemon: BattleMon, opponent_pokemon: BattleMon, escape_attempts: int) -> bool:
    escaping_pokemon_speed = escaping_pokemon.stat_speed
    opponent_pokemon_speed = opponent_pokemon.stat_speed
    
    if escaping_pokemon_speed > opponent_pokemon_speed:
        return True

    odds_escape = (escaping_pokemon_speed * 32) // (opponent_pokemon_speed // 4) + (30 * escape_attempts)

    random_number = random.randint(0, 255)
    return random_number < odds_escape