# Opponent script

from pydantic import BaseModel, ConfigDict
from abc import abstractmethod
from typing import List

from shared.pokemon.pokemon import Pokemon
from ..trainer.trainer import Trainer
from .battle_header import *


class Opponent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    escape_attempts: int = 0

    battlemons: List[BattleMon] = []

    def __init__(self, **data):
        super().__init__(**data)
        self.generate_battlemons()

    @abstractmethod
    def get_all_pokemons(self) -> List[Pokemon]:
        pass

    def get_all_battlemons(self) -> List[BattleMon]:
        return self.battlemons

    def generate_battlemons(self) -> List[BattleMon]:
        self.battlemons = [pokemon.generate_battlemon() for pokemon in self.get_all_pokemons()]
        return self.battlemons

    def _has_viable_pokemons(self) -> bool:
        return any(not pokemon.is_fainted for pokemon in self.get_all_pokemons())

    def get_active_battlemon(self) -> BattleMon:
        if not self._has_viable_pokemons():
            raise ValueError("No viable Pokémons available for this opponent.")
        for battlemon in self.get_all_battlemons():
            if not battlemon.is_fainted:
                return battlemon

class TrainerOpponent(Opponent):
    trainer: Trainer

    def get_all_pokemons(self) -> List[Pokemon]:
        return self.trainer.team.get_all_pokemons()
    
class WildPokemonOpponent(Opponent):
    pokemon: Pokemon

    def get_all_pokemons(self) -> List[Pokemon]:
        return [self.pokemon]