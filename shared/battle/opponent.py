# Opponent script

from abc import ABC, abstractmethod
from pydantic import ConfigDict
from typing import List

from shared.pokemon.pokemon import Pokemon
from ..trainer.trainer import Trainer
from .battle_header import *


# TODO : Combine them into the one class theres no reason to have separate ones

class Opponent(ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    escape_attempts: int = 0

    battlemons: List[BattleMon] = []

    def __init__(self, **data): # type: ignore
        super().__init__(**data)
        self.generate_battlemons()

    def get_all_pokemons(self) -> List[Pokemon]:
        pokemon: List[Pokemon] = []
        for battlemon in self.battlemons:
            pokemon_ref = battlemon.pokemon_reference
            if not pokemon_ref: continue
            pokemon.append(pokemon_ref)
        return pokemon

    def get_battlemon_by_index(self, index: int) -> BattleMon:
        return self.battlemons[index]

    def get_all_battlemons(self) -> List[BattleMon]:
        return self.battlemons

    def generate_battlemons(self) -> List[BattleMon]:
        self.battlemons = [pokemon.generate_battlemon() for pokemon in self.get_all_pokemons()]
        return self.battlemons

    def has_viable_pokemons(self) -> bool:
        if self.get_viable_battlemons() == []:
            return False
        return True
    
    def get_viable_battlemons(self) -> List[BattleMon]:
        return [battlemon for battlemon in self.get_all_battlemons() if not battlemon.is_fainted]

    def get_active_battlemon(self) -> Optional[BattleMon]:
        if not self.has_viable_pokemons():
            raise ValueError("No viable Pokémons available for this opponent.")
        for battlemon in self.get_all_battlemons():
            if not battlemon.is_fainted:
                return battlemon
        return None

    @abstractmethod
    def get_trainer(self) -> Trainer:
        pass

class TrainerOpponent(Opponent):
    trainer: Trainer
    
    def get_trainer(self) -> Trainer:
        return self.trainer
    
class WildPokemonOpponent(Opponent):
    pokemon: Pokemon

    def get_trainer(self) -> Trainer:
        raise NotImplementedError("Wild Pokémon opponents do not have a trainer.")