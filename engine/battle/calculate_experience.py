from shared.pokemon.pokemon import BattleMon


def calculate_experience(defeated_pokemon: BattleMon, victorious_pokemon: BattleMon) -> int:

    a = 1.5 # if its a trainer battle else 1
    base_experience = defeated_pokemon.pokemon_base.base_experience_yield # base experience yield of defeated pokemon
    defeated_pokemon_level = defeated_pokemon.level # level of defeated pokemon
    victorious_pokemon_level = victorious_pokemon.level # level of pokemon receiving experience
    point_power_booster = 1 # Exp Point Power Booster (1 for no booster, 1.5 for exp charm)
    traded_pokemon_multiplier = 1 # 1.5 if pokemon is traded else 1

    delta_experience = ((base_experience * defeated_pokemon_level) / 5) * a * (1/5) * (((2 * defeated_pokemon_level + 10) ** 0.5) * ((2 * defeated_pokemon_level + 10) ** 2) / (((defeated_pokemon_level + victorious_pokemon_level + 10) ** 0.5) * ((defeated_pokemon_level + victorious_pokemon_level + 10) ** 2)) + 1) * traded_pokemon_multiplier * point_power_booster
    rounded_experience = round(delta_experience)
    return rounded_experience