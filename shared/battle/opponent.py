# Opponent script

from pydantic import BaseModel, ConfigDict
from abc import abstractmethod
from typing import List
from ..trainer.trainer import Trainer
from .battle_header import *


class Opponent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    escape_attempts: int = 0

    @abstractmethod
    def get_all_pokemons(self) -> List[Pokemon]:
        pass

    def _has_viable_pokemons(self) -> bool:
        return any(not pokemon.is_fainted for pokemon in self.get_all_pokemons())

    def get_active_pokemon(self) -> Pokemon:
        if not self._has_viable_pokemons():
            raise ValueError("No viable Pokémons available for this opponent.")
        for pokemon in self.get_all_pokemons():
            if not pokemon.is_fainted:
                return pokemon

class TrainerOpponent(Opponent):
    trainer: Trainer

    def get_all_pokemons(self) -> List[Pokemon]:
        return self.trainer.team.get_all_pokemons()
    
class WildPokemonOpponent(Opponent):
    pokemon: Pokemon

    def get_all_pokemons(self) -> List[Pokemon]:
        return [self.pokemon]
