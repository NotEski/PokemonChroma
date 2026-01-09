from typing import Optional
from pydantic import BaseModel, Field

from .status_conditions import StatusCondition
from .stats import Stat
from ..battle.weather import BattleWeather
from ..battle.terrain import BattleTerrain
from .hazard import EntryHazard
from ..battle.field_effect import FieldEffect


class MoveTag(BaseModel):
    pass


class AuthenticMove(MoveTag):
    pass


class BallisticsMove(MoveTag):
    pass


class BiteMove(MoveTag):
    pass


class ChargeMove(MoveTag):
    pass


class ContactMove(MoveTag):
    pass


class CriticalHitMove(MoveTag):
    critical_hit_rate_increase: int  # Additional stages to critical hit rate


class DefrostMove(MoveTag):
    pass


class DistanceMove(MoveTag):
    pass


class DrainMove(MoveTag):
    drain_percentage: int = Field(ge=-100, le=100, default=0)  # Percentage of damage dealt to heal the user. If negative, recoiled damage.

    @property
    def is_recoil(self) -> bool:
        return self.drain_percentage < 0


class FlinchMove(MoveTag):
    chance: int  # Percentage chance to flinch the target

class FieldEffectMove(MoveTag):
    field_effect: FieldEffect
    turns: int  # Number of turns the field effect will last

class GravityMove(MoveTag):
    pass


class EntryHazardMove(MoveTag):
    entry_hazard: EntryHazard
    layers: int  # Number of layers to set up


class HealMove(MoveTag):
    heal_percentage: int  # Percentage of max HP to heal


class MentalMove(MoveTag):
    pass


class MirrorMove(MoveTag):
    pass


class MultiHitMove(MoveTag):
    hits: dict[int, int]  # Dictionary with 'hit_amount' and 'weight' for multi-hit moves e.g. {2: 35, 3: 35, 4: 15, 5: 15} for moves that hit 2-5 times


class MultiTurnMove(MoveTag):
    min_turns: int
    max_turns: int


class NonSkyBattleMove(MoveTag):
    pass


class PivotMove(MoveTag):
    pass


class PowderMove(MoveTag):
    pass


class ProtectMove(MoveTag):
    pass


class PulseMove(MoveTag):
    pass


class PunchMove(MoveTag):
    pass


class RechargeMove(MoveTag):
    pass


class ReflectableMove(MoveTag):
    pass


class ScreenMove(MoveTag):
    screen_type: str  # e.g., "Reflect", "Light Screen" # this will likely need to be an Enum later
    duration_turns: int  # Number of turns the screen will last


class SnatchMove(MoveTag):
    pass


class SoundMove(MoveTag):
    pass


class StatChangeMove(MoveTag):
    stat: Stat
    change: int  # Positive for increase, negative for decrease
    chance: int = Field(default=100)  # Percentage chance to apply the stat change


class StatChangeInflictedMove(StatChangeMove):
    pass

class StatChangeReceivedMove(StatChangeMove):
    pass

class StatusConditionMove(MoveTag):
    status_condition: StatusCondition
    chance: int  # Percentage chance to inflict the status condition. If 0 or less, always inflicts.


class TerrainMove(MoveTag):
    terrain: BattleTerrain
    duration_turns: int  # Number of turns the terrain will last


class WeatherMove(MoveTag):
    weather: BattleWeather