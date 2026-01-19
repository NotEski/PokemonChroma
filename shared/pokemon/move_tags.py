from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .status_conditions import StatusCondition
    from .stats import Stat
    from ..battle.weather import BattleWeather
    from ..battle.terrain import BattleTerrain
    from .hazard import EntryHazard
    from ..battle.field_effect import FieldEffect
    from .types import PokemonType
    from .move import MoveTarget



class MoveTag(BaseModel):
    pass

class AddTypingMove(MoveTag):
    typing_to_add: PokemonType  # Type to be added to the target
    alt_target: Optional[MoveTarget] = None # Alternative target if needed otherwise uses the move's target

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

class HazardMove(MoveTag):
    entry_hazard: EntryHazard
    layers: int  # Number of layers to set up

class HazardRemovalMove(MoveTag):
    entry_hazard: Optional[EntryHazard] # if None, removes all hazards

class HealMove(MoveTag):
    heal_percentage: int  # Percentage of max HP to heal

class MentalMove(MoveTag):
    pass

class MirrorMove(MoveTag):
    pass

class MultiHitMove(MoveTag):
    hits: dict[int, int] = { 2: 35, 3: 35, 4: 15, 5: 15 } # Dictionary with 'hit_amount' and 'weight' for multi-hit moves e.g. {2: 35, 3: 35, 4: 15, 5: 15} for moves that hit 2-5 times

class MultiTurnMove(MoveTag):
    min_turns: int
    max_turns: int

class NonSkyBattleMove(MoveTag):
    pass

class PivotMove(MoveTag):
    pass

class PowderMove(MoveTag):
    pass

class PokemonTypeRequirementMove(MoveTag):
    required_type: PokemonType  # Type required to use the move otherwise fails

class ProtectMove(MoveTag):
    # blocks incoming moves for the turn on target
    # side effects
    success_rate: Optional[dict[int, float]] = Field({1: 100, 2: 50, 3: 25, 4: 12.5}, description="Success rate per consecutive use if None always succeeds")
    stats_inflicted_on_attacker: Optional[dict[Stat, int]] = Field(None, description="Stats to inflict on attacker if they use a damaging move against the protected target")
    status_condition_inflicted_on_attacker: Optional[StatusCondition] = Field(None, description="Status condition to inflict on attacker if they use a damaging move against the protected target")
    damage_inflicted_on_attacker_damage_percentage: Optional[int] = Field(None, description="Damage to inflict on attacker based on damage that would have been inflicted if they use a damaging move against the protected target")
    damage_inflicted_on_attacker_health_percentage: Optional[int] = Field(None, description="Damage to inflict on attacker based on their max health if they use a damaging move against the protected target")

    full_protect: bool = Field(default=True, description="If true, protects as normal. If false, only protects from certain move types (e.g., status moves)")

    survive_on_one_hp: bool = Field(default=False, description="If true, the target will survive with 1 HP if the move would have knocked it out. Only applies if full_protect is true.")
    # add more side effects as needed

class ProtectAgainstMove(MoveTag):
    pass

class PriorityMove(MoveTag):
    priority: int # Priority level of the move

class PulseMove(MoveTag):
    pass

class PunchMove(MoveTag):
    pass

class RechargeMove(MoveTag):
    pass

class ReflectableMove(MoveTag):
    pass

class RemoveTypingMove(MoveTag):
    typing_to_remove: PokemonType  # Type to be removed from the target
    alt_target: Optional[MoveTarget] = None # Alternative target if needed otherwise uses the move's target
                                            # e.g for burn up which damages the target but removes fire typing from the user

class ScreenMove(MoveTag):
    screen_type: str  # e.g., "Reflect", "Light Screen" # this will likely need to be an Enum later
    duration_turns: int  # Number of turns the screen will last

class SetupMove(MoveTag): # Speceial tag for AI to identify setup moves
    stat_changes_received: list['StatChangeReceivedMove'] = []
    stat_changes_inflicted: list['StatChangeInflictedMove'] = []
    damages_user: bool = Field(default=False)  # Whether the move also damages the user
    damages_opponent: bool = Field(default=False)  # Whether the move also damages the opponent
    trap_user: bool = Field(default=False)  # Whether the move traps the user
    trap_opponent: bool = Field(default=False)  # Whether the move traps the opponent
    recoil_percentage: Optional[int] = Field(default=None)  # Percentage of damage dealt to recoil to the user
    secondary_effects: Optional[list[MoveTag]] = Field(default=None)  # List of additional MoveTags that represent secondary effects of the move

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

class SupportMove(MoveTag):
    pass

class SwitchOutMove(MoveTag):
    pass

class TerrainMove(MoveTag):
    terrain: BattleTerrain

class TrapUserMove(MoveTag):
    pass

class TrapTargetMove(MoveTag):
    pass

class WeatherMove(MoveTag):
    weather: BattleWeather

class WeatherAffectedMove(MoveTag):
    weather: BattleWeather
    multiplier: float  # Effectiveness multiplier under the specified weather might need to be changed

class WeatherDependentMove(MoveTag):
    weather: BattleWeather