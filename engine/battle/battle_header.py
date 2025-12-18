from pydantic import BaseModel, Field
from abc import abstractmethod
from typing import Dict, List, Optional
from enum import Enum, auto
from shared.pokemon.pokemon import Pokemon
from shared.pokemon.trainer import BattleTrainer
from shared.pokemon.move import Move
from .battle_logs import BattleLogEntry
from .battle_positions import *

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
    ESCAPE = "escape"

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

class ActionEscape(Action):
    action_type: ActionType = Field(default=ActionType.ESCAPE)
    escape_attempts: int = Field(default=0)


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

class WeatherTurns(BaseModel):
    weather: BattleWeather
    remaining_turns: int


class BattleConfig(BaseModel):
    is_wild: bool = Field(default=False)
    can_escape: bool = Field(default=True)
    terrain: Optional[str] = None  # e.g., "grassy", "electric", etc.

class BattleState(BaseModel):
    turn_number: int = Field(default=0)
    weather_turns: WeatherTurns = Field(default_factory=lambda: WeatherTurns(weather=BattleWeather.NONE, remaining_turns=0))  # e.g., (BattleWeather.RAIN, 5) means rain for 5 more turns
    terrain: Optional[str] = None  # e.g., "grassy", "electric", etc.
    field_effects: List[str] = Field(default_factory=list)  # e.g., "reflect", "light screen", etc.
    battle_log: List[BattleLogEntry] = Field(default_factory=list)  # Log of battle events