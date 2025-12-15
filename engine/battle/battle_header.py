from pydantic import BaseModel, Field
from abc import abstractmethod
from typing import List, Optional
from enum import Enum, auto
from shared.pokemon.pokemon import Pokemon
from shared.pokemon.trainer import BattleTrainer
from shared.pokemon.move import Move

class UnfinishedTurnException(Exception):
    pass

class BattleType(Enum):
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    ROTATION = "rotation"
    HORDE = "horde"

class ActionType(Enum):
    MOVE = "move"
    SWITCH = "switch"
    USE_ITEM = "use_item"
    FLEE = "flee"

class Action(BaseModel):
    action_type: ActionType

class ActionMove(Action):
    action_type: ActionType = Field(default=ActionType.MOVE)
    move: Move
    target_position: Optional['BattlePosition'] = None

class ActionSwitch(Action):
    action_type: ActionType = Field(default=ActionType.SWITCH)
    switch_in_pokemon: Pokemon

class ActionUseItem(Action):
    action_type: ActionType = Field(default=ActionType.USE_ITEM)
    item_name: str
    target_position: Optional['BattlePosition'] # specicially for when using pokeballs on wild pokemon

class ActionFlee(Action):
    action_type: ActionType = Field(default=ActionType.FLEE)

class BattleLogType(Enum):
    BATTLE_START = "battle_start"
    TURN_START = "turn_start"
    POKEMON_SWITCH_IN = "pokemon_switch_in"
    MOVE_USED = "move_used"
    DAMAGE_DEALT = "damage_dealt"
    STATUS_APPLIED = "status_applied"
    POKEMON_FAINTED = "pokemon_fainted"
    BATTLE_END = "battle_end"

class BattleWeather(Enum):
    HARSH_SUNLIGHT = "harsh_sunlight"
    RAIN = "rain"
    SANDSTORM = "sandstorm"
    HAIL = "hail"
    SNOW = "snow"
    FOG = "fog"
    EXTREMELY_HARSH_SUNLIGHT = "extremely_harsh_sunlight"
    HEAVY_RAIN = "heavy_rain"
    STRONG_WIND = "strong_wind"
    SHADOWY_AURA = "shadowy_aura"
    NONE = None

class BattleLogEntry(BaseModel):
    """
    Docstring for BattleLogEntry needs to contain everything that happened in a turn. so it could be replicated later perfectly if needed.
    """
    turn_number: int
    log_type: BattleLogType
    description: str # TODO this will need to be more complex later. For now, just a string.

class BattleConfig(BaseModel):
    is_wild: bool = Field(default=False)
    can_flee: bool = Field(default=True)
    terrain: Optional[str] = None  # e.g., "grassy", "electric", etc.

class BattleState(BaseModel):
    turn_number: int = Field(default=0)
    weather: BattleWeather = Field(default=None)
    terrain: Optional[str] = None  # e.g., "grassy", "electric", etc.
    field_effects: List[str] = Field(default_factory=list)  # e.g., "reflect", "light screen", etc.
    battle_log: List[BattleLogEntry] = Field(default_factory=list)  # Log of battle events


class Opponent(BaseModel):
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

class BattlePosition(Enum):
    pass

class SinglesBattlePosition(BattlePosition):
    Team1_Pokemon1 = auto()
    Team2_Pokemon1 = auto()

class DoublesBattlePosition(BattlePosition):
    Team1_Pokemon1 = auto()
    Team1_Pokemon2 = auto()
    Team2_Pokemon1 = auto()
    Team2_Pokemon2 = auto()