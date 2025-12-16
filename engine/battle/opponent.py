# Opponent script

from pydantic import BaseModel, ConfigDict
from abc import abstractmethod
from typing import Callable, Protocol, List, Optional, runtime_checkable
from .battle_header import *


class Opponent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    escape_attempts: int = 0

    @abstractmethod
    def get_all_pokemons(self) -> List[Pokemon]:
        pass

class TrainerOpponent(Opponent):
    trainer: BattleTrainer

    def get_all_pokemons(self) -> List[Pokemon]:
        return self.trainer.team.get_all_pokemons()
    
class WildPokemonOpponent(Opponent):
    pokemon: Pokemon

    def get_all_pokemons(self) -> List[Pokemon]:
        return [self.pokemon]
