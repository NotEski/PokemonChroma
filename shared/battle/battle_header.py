from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from shared.pokemon.pokemon import Pokemon
from shared.pokemon.move import Move
from .battle_logs import BattleLogEntry
from .position_manager import *

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

class BattleTerrain(Enum):
    GRASSY = "grassy"
    ELECTRIC = "electric"
    MISTY = "misty"
    PSYCHIC = "psychic"
    NONE = None

class FieldEffects(Enum):
    TRICK_ROOM = "trick_room"
    MAGIC_ROOM = "magic_room"
    WONDER_ROOM = "wonder_room"
    NONE = None


class WeatherTurns(BaseModel):
    weather: BattleWeather
    remaining_turns: int

class BattleConfig(BaseModel):
    is_wild: bool = Field(default=False)
    can_escape: bool = Field(default=True)
    terrain: BattleTerrain = None  # e.g., "grassy", "electric", etc.

class BattleState(BaseModel):
    turn_number: int = Field(default=0)
    weather_turns: WeatherTurns = Field(default_factory=lambda: WeatherTurns(weather=BattleWeather.NONE, remaining_turns=-1))  # e.g., (BattleWeather.RAIN, 5) means rain for 5 more turns
    terrain: BattleTerrain = None  # e.g., "grassy", "electric", etc.
    field_effects: List[FieldEffects] = Field(default_factory=list)  # e.g., "reflect", "light screen", etc.
    
    battle_log: List[BattleLogEntry] = Field(default_factory=list)  # Log of battle events
