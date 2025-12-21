from pydantic import BaseModel, Field, model_validator
from typing import Dict

from shared.pokemon.pokemon import PokemonBase
from shared.pokemon.abilities import Ability
from shared.pokemon.move import BaseMove


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
    
    def reset_instance(cls):
        cls._instance = None


class MoveRepository(BaseModel):
    moves: Dict[str, 'BaseMove'] = Field(default_factory=dict)
    def create_move(self, move: 'BaseMove', force: bool = False):
        key = move.name.lower()
        if key in self.moves and not force:
            raise ValueError(f"Move with name '{move.name}' already exists.")

        self.moves[key] = move

    def get_move(self, key: str) -> 'BaseMove':
        return self.moves.get(key.lower())
    
    def list_moves(self) -> Dict[str, 'BaseMove']:
        return self.moves

class MoveRepositorySingleton:
    _instance: MoveRepository = None

    @classmethod
    def get_instance(cls) -> MoveRepository:
        if cls._instance is None:
            cls._instance = MoveRepository()
        return cls._instance





class PokemonAbilityRepository(BaseModel):
    abilities: Dict[str, 'Ability'] = Field(default_factory=dict)


    def create_ability(self, ability: 'Ability', force: bool = False):
        key = ability.name.lower()
        if key in self.abilities and not force:
            raise ValueError(f"Ability with name '{ability.name}' already exists.")

        self.abilities[key] = ability

    def get_ability(self, key: str) -> 'Ability':
        return self.abilities.get(key.lower())

    def list_abilities(self) -> Dict[str, 'Ability']:
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
move_repository = MoveRepositorySingleton.get_instance()