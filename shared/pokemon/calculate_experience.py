from pokemon import BattleMon, PokemonBase


def calculate_experience(defeated_pokemon: PokemonBase, victorious_pokemon: PokemonBase) -> int:


    a = 1.5 # if its a trainer battle else 1
    base_experience = defeated_pokemon.base_experience # base experience yield of defeated pokemon
    defeated_pokemon_level = defeated_pokemon.level # level of defeated pokemon
    victorious_pokemon_level = victorious_pokemon.level # level of pokemon receiving experience
    point_power_booster = 1 # Exp Point Power Booster (1 for no booster, 1.5 for exp charm)
    traded_pokemon_multiplier = 1 # 1.5 if pokemon is traded else 1

    delta_experience = ((base_experience * defeated_pokemon_level) / 5) * a * (1/5) * (((2 * defeated_pokemon_level + 10) ** 0.5) * ((2 * defeated_pokemon_level + 10) ** 2) / (((defeated_pokemon_level + victorious_pokemon_level + 10) ** 0.5) * ((defeated_pokemon_level + victorious_pokemon_level + 10) ** 2)) + 1) * traded_pokemon_multiplier * point_power_booster
    rounded_experience = round(delta_experience)
    return rounded_experience


def calculate_experience_distributed(base_pokemon: PokemonBase, recieveing_pokemons: list[BattleMon]) -> dict[BattleMon, int]:

    experience_distribution = {}
    for pokemon in recieveing_pokemons:
        holding_lucky_egg_multiplier = 1.5 if pokemon.held_item_str == "lucky_egg" else 1
        experience_distribution[pokemon] = calculate_experience(base_pokemon, pokemon) // len(recieveing_pokemons) * holding_lucky_egg_multiplier
    return experience_distribution