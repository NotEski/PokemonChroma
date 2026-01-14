# Opponent script

from pydantic import ConfigDict, BaseModel
from typing import List

from shared.pokemon.pokemon import Pokemon, BattleMon
from ..trainer.trainer import Trainer
from .battle_header import *


class Opponent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    escape_attempts: int = 0

    pokemon_team: list[Pokemon] = []

    battlemons: List[BattleMon] = []

    def __init__(self, **data): # type: ignore
        super().__init__(**data)
        self.generate_pokemon_team()

    def has_viable_pokemons(self) -> bool:
        if self.get_viable_battlemons() == []:
            return False
        return True
    
    def get_viable_battlemons(self) -> List[BattleMon]:
        return [battlemon for battlemon in self.battlemons if not battlemon.is_fainted]

    def get_active_battlemon(self) -> Optional[BattleMon]:
        if not self.has_viable_pokemons():
            raise ValueError("No viable Pokémons available for this opponent.")
        for battlemon in self.battlemons:
            if not battlemon.is_fainted:
                return battlemon
        return None

    def get_trainer(self) -> Trainer:
        return Trainer(
            name="Wild Pokémon",
            team=[],
        )
    
    def generate_pokemon_team(self) -> list[Pokemon]:
        return self.pokemon_team

class TrainerOpponent(Opponent):
    trainer: Trainer
    
    def generate_pokemon_team(self) -> list[Pokemon]:
        for pokemon in self.trainer.team.pokemons:
            self.pokemon_team.append(pokemon)
        self.battlemons = [pokemon.generate_battlemon() for pokemon in self.pokemon_team]
        return self.pokemon_team

    def get_trainer(self) -> Trainer:
        return self.trainer
    
class WildPokemonOpponent(Opponent):
    pokemon: Pokemon

    def generate_pokemon_team(self) -> list[Pokemon]:
        self.pokemon_team.append(self.pokemon)
        self.battlemons = [pokemon.generate_battlemon() for pokemon in self.pokemon_team]
        return self.pokemon_team