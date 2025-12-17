from pydantic import BaseModel, Field, model_validator
from typing import Dict

from shared.pokemon.pokemon import PokemonBase
from shared.pokemon.pokemon import PokemonAbility


class PokemonRepository(BaseModel):
    pokemons: Dict[str, 'PokemonBase'] = Field(default_factory=dict)


    def create_pokemon(self, pokemon: 'PokemonBase', force: bool = False):
        key = pokemon.name.lower()
        if key in self.pokemons and not force:
            raise ValueError(f"Pokemon with name '{pokemon.name}' already exists.")

        self.pokemons[key] = pokemon

    def get_pokemon(self, key: str) -> 'PokemonBase':
        return self.pokemons.get(key.lower())
    
    def list_pokemons(self) -> Dict[str, 'PokemonBase']:
        return self.pokemons

class PokemonRepositorySingleton:
    _instance: PokemonRepository = None

    @classmethod
    def get_instance(cls) -> PokemonRepository:
        if cls._instance is None:
            cls._instance = PokemonRepository()
        return cls._instance


class PokemonAbilityRepository(BaseModel):
    abilities: Dict[str, 'PokemonAbility'] = Field(default_factory=dict)


    def create_ability(self, ability: 'PokemonAbility', force: bool = False):
        key = ability.name.lower()
        if key in self.abilities and not force:
            raise ValueError(f"Ability with name '{ability.name}' already exists.")

        self.abilities[key] = ability

    def get_ability(self, key: str) -> 'PokemonAbility':
        return self.abilities.get(key.lower())
    
    def list_abilities(self) -> Dict[str, 'PokemonAbility']:
        return self.abilities

class PokemonAbilityRepositorySingleton:
    _instance: PokemonAbilityRepository = None

    @classmethod
    def get_instance(cls) -> PokemonAbilityRepository:
        if cls._instance is None:
            cls._instance = PokemonAbilityRepository()
        return cls._instance





pokemon_repository = PokemonRepositorySingleton.get_instance()
ability_repository = PokemonAbilityRepositorySingleton.get_instance()