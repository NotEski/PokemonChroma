from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from .battle_logs import BattleLogEntry
from .position_manager import *
from .weather import *
from .terrain import *

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

class BattleSwitchType(Enum):
    SET = "set"
    SWITCH = "switch"

class BattleConfig(BaseModel):
    battle_type: BattleType = Field(default=BattleType.SINGLE)
    battle_switch_type: BattleSwitchType = Field(default=BattleSwitchType.SET)
    is_wild: bool = Field(default=False)
    can_escape: bool = Field(default=False)
    terrain: BattleTerrain = None  # e.g., "grassy", "electric", etc.
    grant_exp: bool = Field(default=True)

class BattleState(BaseModel):
    turn_number: int = Field(default=0)

    switch_turn: bool = Field(default=False)  # Indicates if the current turn is a switch turn

    weather_turns: WeatherTurns = Field(default_factory=lambda: WeatherTurns(weather=BattleWeather.NONE, remaining_turns=-1))  # e.g., (BattleWeather.RAIN, 5) means rain for 5 more turns
    terrain: BattleTerrain = None  # e.g., "grassy", "electric", etc.

    position_manager_ref: Optional[BattlePositionManager] = None  # Reference to the PositionManager managing the battle positions

    battle_log: List[BattleLogEntry] = Field(default_factory=list)  # Log of battle events

    def set_weather(self, weather: BattleWeather, turns: int = 5):
        self.weather_turns.weather = weather
        self.weather_turns.remaining_turns = turns

    def decrement_weather(self):
        if self.weather_turns.remaining_turns > 0:
            self.weather_turns.remaining_turns -= 1
            if self.weather_turns.remaining_turns == 0:
                self.weather_turns.weather = BattleWeather.NONE
                self.weather_turns.remaining_turns = -1
    
    def get_all_active_pokemon(self) -> List[BattleMon]:
        if self.position_manager_ref is None:
            raise ValueError("Position manager reference is not set in BattleState.")
        active_pokemon = []
        for position in self.position_manager_ref.get_valid_positions():
            pokemon = self.position_manager_ref.get_pokemon_at_position(position)
            if pokemon is not None and not pokemon.is_fainted:
                active_pokemon.append(pokemon)
        return active_pokemon