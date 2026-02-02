from __future__ import annotations

from enum import Enum
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, Field


if TYPE_CHECKING:
    from .status_conditions import StatusCondition
    from .stats import Stat
    from .pokemon_types import PokemonType
    from ..battle.weather import BattleWeather
    from ..battle.terrain import BattleTerrain
    from .hazard import EntryHazard
    from ..battle.field_effect import FieldEffect
    from .move import MoveTarget
    from .abilities import Ability

class AbilityModify(Enum):
    COPY = "copy"
    SUPPRESS = "suppress"
    SWAP = "swap"
    SET = "set"

class DamageScalingVariable(Enum):
    TARGET_CURRENT_HP = "target_current_hp"
    TARGET_MAX_HP = "target_max_hp"
    TARGET_LEVEL = "target_level"
    TARGET_WEIGHT = "target_weight"
    TARGET_HEIGHT = "target_height"
    TARGET_LAST_DAMAGE = "target_last_damage"

    USER_CURRENT_HP = "user_current_hp"
    USER_MAX_HP = "user_max_hp"
    USER_LEVEL = "user_level"
    USER_WEIGHT = "user_weight"
    USER_HEIGHT = "user_height"
    USER_LAST_DAMAGE = "user_last_damage"

class ItemInteraction(Enum):
    STEAL = "steal"
    GIVE = "give"
    TAKE = "take"
    SWAP = "swap"
    FLING = "fling"


class MoveTag(BaseModel):
    pass

class AbilityModifyMove(MoveTag):
    modify_type: AbilityModify
    ability_set: Optional[Ability] = None  # Ability to set if modify_type is SET
    duration: Optional[int] = None  # Duration in turns for which the ability modification lasts, if applicable

class AddTypingMove(MoveTag):
    typing_to_add: PokemonType  # Type to be added to the target
    alt_target: Optional[MoveTarget] = None # Alternative target if needed otherwise uses the move's target

class AuthenticMove(MoveTag):
    pass

class BallisticsMove(MoveTag):
    pass

class BlockedByProtectMove(MoveTag):
    pass

class BiteMove(MoveTag):
    pass

class BypassSubstituteMove(MoveTag):
    pass

class ChargeMove(MoveTag):
    pass

class ContactMove(MoveTag):
    pass

class CriticalHitMove(MoveTag):
    critical_hit_rate_increase: int  # Additional stages to critical hit rate

class DamageScaleMove(MoveTag):
    variable_scaled_against: DamageScalingVariable  # e.g., "target_current_hp", "user_max_hp", "target_weight" etc

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

class FirstTurnOutMove(MoveTag):
    pass

class GravityMove(MoveTag):
    pass

class HazardMove(MoveTag):
    entry_hazard: EntryHazard
    layers: int  # Number of layers to set up

class HazardRemovalMove(MoveTag):
    entry_hazard: Optional[EntryHazard] # if None, removes all hazards

class HPDependentMove(MoveTag):
    check_user: bool  # if True, checks user's HP instead of target's HP
    above_hp_threshold: bool  # True if move is more effective above threshold, False if below
    hp_threshold_percentage: int  # HP percentage threshold

class ItemDependentMove(MoveTag):
    check_user: bool  # True if checking user's item, False if checking target's
    item_name: Optional[str] = None  # Name of the item to check for. i.e. "Leftovers", "Choice Band" etc.
    item_catagory: Optional[str] = None  # Category of the item to check for. i.e. "berries", "hold_items", "gem" etc.
    requires_item: bool  # True if move requires the item to be present, False if it requires the item to be absent

class ItemInteractionMove(MoveTag):
    interaction: ItemInteraction

class HealMove(MoveTag):
    heal_percentage: int  # Percentage of max HP to heal

class MentalMove(MoveTag):
    pass

class MirrorMove(MoveTag):
    pass

class MultiHitMove(MoveTag):
    hits: dict[int, int] = Field(default_factory=lambda: { 2: 35, 3: 35, 4: 15, 5: 15 }) # Dictionary with 'hit_amount' and 'weight' for multi-hit moves e.g. {2: 35, 3: 35, 4: 15, 5: 15} for moves that hit 2-5 times

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
    success_rate: Optional[dict[int, float]] = Field(default_factory=lambda: {1: 100, 2: 50, 3: 25, 4: 12.5}, description="Success rate per consecutive use if None always succeeds")
    stats_inflicted_on_attacker: Optional[dict[Stat, int]] = Field(default=None, description="Stats to inflict on attacker if they use a damaging move against the protected target")
    status_condition_inflicted_on_attacker: Optional[StatusCondition] = Field(default=None, description="Status condition to inflict on attacker if they use a damaging move against the protected target")
    damage_inflicted_on_attacker_damage_percentage: Optional[int] = Field(default=None, description="Damage to inflict on attacker based on damage that would have been inflicted if they use a damaging move against the protected target")
    damage_inflicted_on_attacker_health_percentage: Optional[int] = Field(default=None, description="Damage to inflict on attacker based on their max health if they use a damaging move against the protected target")

    full_protect: bool = Field(default=True, description="If true, protects as normal. If false, only protects from certain move types (e.g., status moves)")

    survive_on_one_hp: bool = Field(default=False, description="If true, the target will survive with 1 HP if the move would have knocked it out. Only applies if full_protect is true.")
    # add more side effects as needed

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
    stat_changes_received: list['StatChangeReceivedMove'] = Field(default_factory=list) # type:ignore
    stat_changes_inflicted: list['StatChangeInflictedMove'] = Field(default_factory=list) # type:ignore
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

class StatusConditionDependentMove(MoveTag):
    check_user: bool  # True if checking user's status condition, False if checking target's
    status_condition: StatusCondition
    requires_condition: bool  # True if move requires the condition to be present, False if it requires the condition to be absent

class StatSwapMove(MoveTag):
    stats_to_swap: dict[Stat, Stat]  # Dictionary mapping stats to be swapped from {User: Target} e.g. {Stat.ATTACK: Stat.DEFENSE}
                                     # Set up like this to allow for moves that swap stats with itself

class StatStageSwapMove(MoveTag):
    stats_to_swap: dict[Stat, Stat]  # Dictionary mapping stats to be swapped from {User: Target} e.g. {Stat.ATTACK: Stat.DEFENSE}
                                     # Set up like this to allow for moves that swap stats with itself like Power Swap

class SubstituteMove(MoveTag):
    hp_cost_percentage: int  # Percentage of max HP to use for the substitute

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


def rebuild_models():
    # This function is used to rebuild models to resolve forward references post definition and import into Move to avoid circular imports
    # First import all models that MoveTags use
    from .status_conditions import StatusCondition  # pyright: ignore[reportUnusedImport] #
    from .stats import Stat                         # pyright: ignore[reportUnusedImport] #
    from .pokemon_types import PokemonType          # pyright: ignore[reportUnusedImport] #
    from ..battle.weather import BattleWeather      # pyright: ignore[reportUnusedImport] #
    from ..battle.terrain import BattleTerrain      # pyright: ignore[reportUnusedImport] #
    from .hazard import EntryHazard                 # pyright: ignore[reportUnusedImport] #
    from ..battle.field_effect import FieldEffect   # pyright: ignore[reportUnusedImport] #
    from .move import MoveTarget                    # pyright: ignore[reportUnusedImport] #
    from .abilities import Ability                  # pyright: ignore[reportUnusedImport] #

    # Now rebuild all models
    AbilityModifyMove.model_rebuild()
    AddTypingMove.model_rebuild()
    CriticalHitMove.model_rebuild()
    DamageScaleMove.model_rebuild()
    DrainMove.model_rebuild()
    FlinchMove.model_rebuild()
    FieldEffectMove.model_rebuild()
    HazardMove.model_rebuild()
    HazardRemovalMove.model_rebuild()
    ItemInteractionMove.model_rebuild()
    HealMove.model_rebuild()
    MultiHitMove.model_rebuild()
    MultiTurnMove.model_rebuild()
    PokemonTypeRequirementMove.model_rebuild()
    ProtectMove.model_rebuild()
    PriorityMove.model_rebuild()
    StatChangeMove.model_rebuild()
    StatChangeInflictedMove.model_rebuild()
    StatChangeReceivedMove.model_rebuild()
    StatusConditionMove.model_rebuild()
    StatSwapMove.model_rebuild()
    StatStageSwapMove.model_rebuild()
    TerrainMove.model_rebuild()
    WeatherMove.model_rebuild()
    WeatherAffectedMove.model_rebuild()
    WeatherDependentMove.model_rebuild()