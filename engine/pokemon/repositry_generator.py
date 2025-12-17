# Generate Repository from json files


import json
from shared.pokemon.pokemon import PokemonBase, PokemonAbility
from engine.pokemon.repository import ability_repository, pokemon_repository
from shared.pokemon.types import PokemonType
import pathlib

# pull data from json files and populate the repository

def json_to_pokemon_base(json_data: dict) -> PokemonBase:
    return PokemonBase(
        name=json_data["name"],
        types=[PokemonType[type_str] for type_str in json_data["types"]],
        base_stats=json_data["base_stats"],
        pokedex_number=json_data["pokedex_number"],
        catch_rate=json_data["catch_rate"]
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
            ability = PokemonAbility(
                name=json_data["name"],
                name_readable=json_data["name_readable"],
                description=json_data["description"]
            )
            ability_repository.create_ability(ability)

