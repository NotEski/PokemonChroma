# Opponent script

from pydantic import BaseModel, ConfigDict
from abc import abstractmethod
from typing import Callable, Protocol, List, Optional, runtime_checkable
from .battle_header import *


@runtime_checkable
class ActionExecutor(Protocol):
    def execute_escape(self):
        pass

    def execute_move(self, move_index: int, target_position: 'BattlePosition'):
        pass

    def execute_switch(self, switch_in_pokemon: Pokemon):
        pass

    def execute_use_item(self, item_name: str, target_position: 'BattlePosition' = None):
        pass


class Opponent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    action_executor: Optional[ActionExecutor] = None

    escape_attempts: int = 0

    @abstractmethod
    def get_all_pokemons(self) -> List[Pokemon]:
        pass

    def use_escape(self):
        if self.action_executor is None:
            raise Exception("Action executor not set for opponent.")
        self.action_executor.execute_escape()

    def use_move(self, move_index: int, target_position: 'BattlePosition'):
        if self.action_executor is None:
            raise Exception("Action executor not set for opponent.")
        self.action_executor.execute_move(move_index, target_position)

    def use_switch(self, switch_in_pokemon: Pokemon):
        if self.action_executor is None:
            raise Exception("Action executor not set for opponent.")
        self.action_executor.execute_switch(switch_in_pokemon)

class TrainerOpponent(Opponent):
    trainer: BattleTrainer

    def get_all_pokemons(self) -> List[Pokemon]:
        return self.trainer.team.get_all_pokemons()
    

class WildPokemonOpponent(Opponent):
    pokemon: Pokemon

    def get_all_pokemons(self) -> List[Pokemon]:
        return [self.pokemon]
