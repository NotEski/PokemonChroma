# Generate Repository from json files


import json
from shared.pokemon.genders import GenderRate
from shared.pokemon.pokemon import PokemonBase, GrowthRate, EggGroup
from shared.pokemon.abilities import PokemonAbilities
from engine.pokemon.repository import pokemon_repository
from shared.pokemon.types import PokemonType
from shared.pokemon.stats import BaseStats, EffortYield
import pathlib

# pull data from json files and populate the repository

def json_to_pokemon_base(json_data: dict) -> PokemonBase:
    if json_data.get("base_experience_yield", 64) is None:
        json_data["base_experience_yield"] = 64
    return PokemonBase(
        name=json_data["name"],
        name_readable=json_data["name_readable"],
        pokedex_number=json_data["pokedex_number"],
        types=[PokemonType(type_str) for type_str in json_data["types"]],
        base_stats=BaseStats(**json_data["base_stats"]),
        ev_yield=EffortYield(**json_data.get("ev_yield", {})),
        capture_rate=json_data["capture_rate"],
        base_experience_yield=json_data.get("base_experience_yield", 64),
        base_happiness=json_data.get("base_happiness", 70),
        gender_rate=GenderRate(json_data.get("gender_rate", "4")),

        #abilities=[AbilitySlot(**ability) for ability in json_data.get("abilities", [])],
        height=json_data.get("height_m", 1.0),
        weight=json_data.get("weight_kg", 1.0),

        egg_groups=[EggGroup(egg_group) for egg_group in json_data.get("egg_groups", "no-eggs")],

        growth_rate=GrowthRate(json_data.get("growth_rate", "medium")),
        # Moves


    )

def load_pokemon_from_json_file(file_path: str) -> PokemonBase:
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    return json_to_pokemon_base(json_data)

def generate_pokemon_repository_from_json(file_paths: list[str]):
    for file_path in file_paths:
        pokemon_base = load_pokemon_from_json_file(file_path)
        pokemon_repository.create_pokemon(pokemon_base)


def generate_abilities_repository_from_json(file_paths: list[str]):
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            json_data = json.load(f)
            ability = PokemonAbilities(
                name=json_data["name"],
                name_readable=json_data["name_readable"],
                description=json_data["description"]
            )
            #ability_repository.create_ability(ability)

