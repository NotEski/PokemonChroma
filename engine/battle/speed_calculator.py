# Speed Processing
from pydantic import BaseModel
from shared.pokemon.pokemon import BattleMon
def calculate_speed(pokemon: BattleMon) -> int:

    # Start with the Pokemon's raw, untouched speed stat
    pokemon_speed = pokemon.stat_speed

    # if boost rank (R) > 0, multiply speed by (2+R), truncate to 16 bits, divide by 2 and round down
    boost_rank = pokemon.speed_stat_stage
    if boost_rank > 0:
        pokemon_speed = (pokemon_speed * (2 + boost_rank)) // 2

    # otherwise, multiply speed by 2, truncate to 16 bits, divide by (2-R) and round down
    elif boost_rank < 0:
        pokemon_speed = (pokemon_speed * 2) // (2 - boost_rank)

    # set the default speed modifier to 4096
    default_modifier = 4096
    modifier = default_modifier

    # if ability is activated Swift Swim, Chlorophyll, Slush Rush, Sand Rush, Surge Surfer, or Unburden, multiply modifier by 8192/4096


    # if ability is activated Quick Feet, multiply modifier by 6144/4096


    # if ability is Slow Start and has not expired yet, multiply modifier by 2048/4096


    # if item is Quick Powder and species is Ditto (not transformed), multiply modifier by 8192/4096


    # if item is Choice Scarf, multiply modifier by 6144/4096


    # if item is Iron Ball, Macho Brace, or a Power EV item, multiply modifier by 2048/4096


    # if Tailwind is in effect on this side, multiply modifier by 8192/4096


    # if pledge swamp is in effect on this side, multiply modifier by 1024/4096


    # multiply speed (last used in step 3) by modifier, divide by 4096, and round to nearest but ties round DOWN
    pokemon_speed = (pokemon_speed * modifier) // 4096

    # if paralyzed and not Quick Feet, multiply speed by 2048/4096 (G7) or 1024/4096 (G5-6), and round down


    # if speed > 10000, set speed to 10000
    if pokemon_speed > 10000:
        pokemon_speed = 10000

    # if Trick Room is active, set speed to (10000 - speed)


    # if speed > 8191, set speed to (speed - 8192)
    if pokemon_speed > 8191:
        pokemon_speed = pokemon_speed - 8192

    return pokemon_speed
