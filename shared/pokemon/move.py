from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional, Type, TYPE_CHECKING

from .types import PokemonType
from .move_tags import *
from math import floor

if TYPE_CHECKING:
    from shared.pokemon.pokemon import BattleMon
    from shared.battle.battle_header import BattleState


class DamageClass(Enum):
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"

class MoveCategory(Enum):
    DAMAGE = "damage"
    STATUS = "status"
    DAMAGE_STATUS = "damage_status"
    DAMAGE_HEAL = "damage_heal"
    DAMAGE_LOWER = "damage_lower"
    DAMAGE_RAISE = "damage_raise"
    FIELD_EFFECT = "field_effect"
    FORCE_SWITCH = "force_switch"
    HEAL = "heal"
    NET_GOOD_STATS = "net_good_stats"
    OHKO = "ohko"
    SWAGGER = "swagger"
    UNIQUE = "unique"
    WHOLE_FIELD_EFFECT = "whole_field_effect"

class MoveCategoryCategories:
    DAMAGE_MOVES = [
            MoveCategory.DAMAGE,
            MoveCategory.DAMAGE_STATUS,
            MoveCategory.DAMAGE_HEAL,
            MoveCategory.DAMAGE_LOWER,
            MoveCategory.DAMAGE_RAISE
        ]
    STATUS_MOVES = [
        MoveCategory.STATUS
    ]
    STAT_CHANGE_MOVES = [
            MoveCategory.DAMAGE_LOWER,
            MoveCategory.DAMAGE_RAISE,
            MoveCategory.NET_GOOD_STATS
        ]
    FIELD_EFFECT_MOVES = [
        MoveCategory.FIELD_EFFECT,
        MoveCategory.WHOLE_FIELD_EFFECT
    ]

class MoveTarget(Enum):
    ALL_ALLIES = "all_allies"
    ALL_OPPONENTS = "all_opponents"
    ALL_OTHER_POKEMON = "all_other_pokemon"
    ALL_POKEMON = "all_pokemon"
    ALLY = "ally"
    ENTIRE_FIELD = "entire_field"
    FAINTING_POKEMON = "fainting_pokemon"
    OPPONENTS_FIELD = "opponents_field"
    RANDOM_OPPONENT = "random_opponent"
    SELECTED_POKEMON_ME_FIRST = "selected_pokemon_me_first"
    SELECTED_POKEMON = "selected_pokemon"
    SPECIFIC_MOVE = "specific_move"
    USER_AND_ALLIES = "user_and_allies"
    USER_OR_ALLY = "user_or_ally"
    USER = "user"
    USERS_FIELD = "users_field"

class MoveTargetCategories:
    USER_AND_ALLIES: list[MoveTarget] = [
        MoveTarget.USER,
        MoveTarget.ALLY,
        MoveTarget.USER_AND_ALLIES,
        MoveTarget.USERS_FIELD
    ]

class OnUseReturns(Enum):
    SUCCESS = "success"
    FAIL = "fail"
    NO_EFFECT = "no_effect"

class BaseMove(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    name: str
    display_name: str = ""
    index: int

    type: PokemonType
    damage_class: DamageClass = DamageClass.PHYSICAL
    category: MoveCategory = MoveCategory.DAMAGE

    accuracy: Optional[int] = 100
    power: Optional[int] = 100
    base_pp: int = 15
    max_pp_inc_one: int = 0
    max_pp_inc_two: int = 0
    max_pp_inc_three: int = 0

    target: MoveTarget = Field(default=MoveTarget.SELECTED_POKEMON)

    move_tags: List[MoveTag] = [] # Additional tags for the move
    
    def __init__(self, **data): # type: ignore
        super().__init__(**data)
        if self.display_name == "":
            self.display_name = self.name.replace("-", " ").title()

        self.max_pp_inc_one = floor(self.base_pp * 1.2)
        self.max_pp_inc_two = floor(self.base_pp * 1.4)
        self.max_pp_inc_three = floor(self.base_pp * 1.6)

    def __hash__(self):
        return hash(self.index)
        
    def on_use(self, attacker: "BattleMon", defender: "BattleMon", battle_state: "BattleState") -> Optional[bool]:
        """Called when the move is used."""
        return None

    def on_hit(self):
        """Called when the move hits the target."""
        return None

    def before_use(self):
        """Called before the move is used."""
        return None

    def damage_calculation(self, attacker: "BattleMon", defender: "BattleMon") -> Optional[int]:
        """Calculate damage dealt by the move instead of using standard formula. e.g. 50% of target's max HP
        Returns the damage amount as an integer.
        """
        return None
    
    def move_factory(self):
        """Creates a new instance of the move."""
        return Move(current_pp=self.base_pp, base_move=self)
    
    def has_tag(self, tag_type: Type[MoveTag]) -> bool:
        if self.move_tags == []:
            return False
        for tag in self.move_tags:
            if isinstance(tag, tag_type):
                return True
        return False
    
    def has_tags(self, tag_types: List[Type[MoveTag]]) -> bool:
        if self.move_tags == []:
            return False
        for tag_type in tag_types:
            if not self.has_tag(tag_type):
                return False
        return True
    
    def has_any_tag(self, tag_types: List[Type[MoveTag]]) -> bool:
        if self.move_tags == []:
            return False
        for tag_type in tag_types:
            if self.has_tag(tag_type):
                return True
        return False

    def get_tag(self, tag_type: Type[MoveTag]) -> Optional[MoveTag]:
        if self.move_tags == []:
            return None
        if isinstance(tag_type, StatChangeMove):
            raise ValueError("For StatChangeMove use get_stat_change_tag() instead.")
        for tag in self.move_tags:
            if isinstance(tag, tag_type):
               return tag
        return None
    
    def get_stat_change_tags(self, tag_type: Type[StatChangeMove]) -> List[StatChangeMove]:
        if self.move_tags == []:
            return []
        stat_change_tags: List[StatChangeMove] = []
        for tag in self.move_tags:
            if isinstance(tag, tag_type):
                stat_change_tags.append(tag)
        return stat_change_tags
    
    def add_tag(self, tag: MoveTag):
        if self.move_tags == []:
            self.move_tags = []
        self.move_tags.append(tag)
    
    def remove_tag(self, tag_type: Type[MoveTag]):
        if self.move_tags == []:
            return
        self.move_tags = [tag for tag in self.move_tags if not isinstance(tag, tag_type)]

    #region Move property getters
    @property
    def physical(self) -> bool:
        return self.damage_class == DamageClass.PHYSICAL
    @property
    def special(self) -> bool:
        return self.damage_class == DamageClass.SPECIAL
    @property
    def status(self) -> bool:
        return self.damage_class == DamageClass.STATUS
    @property
    def priority(self) -> int:
        priority_tag = self.get_tag(PriorityMove)
        if isinstance(priority_tag, PriorityMove):
            return priority_tag.priority
        return 0

    @property
    def requires_charge(self) -> bool:
        return self.has_tag(ChargeMove)
    @property
    def critical_hit_rate_stage_increase(self) -> int:
        crit_tag = self.get_tag(CriticalHitMove)
        if isinstance(crit_tag, CriticalHitMove):
            return crit_tag.critical_hit_rate_increase
        return 0
    @property
    def high_critical_hit(self) -> bool:
        crit_tag = self.get_tag(CriticalHitMove)
        if isinstance(crit_tag, CriticalHitMove):
            return crit_tag.critical_hit_rate_increase >= 2
        return False
    @property
    def always_critical_hit(self) -> bool:
        crit_tag = self.get_tag(CriticalHitMove)
        if isinstance(crit_tag, CriticalHitMove):
            return crit_tag.critical_hit_rate_increase >= 3
        return False
    @property
    def drain_percentage(self) -> int:
        drain_tag = self.get_tag(DrainMove)
        if isinstance(drain_tag, DrainMove):
            return drain_tag.drain_percentage
        return 0
    @property
    def is_recoil(self) -> bool:
        drain_tag = self.get_tag(DrainMove)
        if isinstance(drain_tag, DrainMove):
            return drain_tag.is_recoil
        return False
    @property
    def flinch_chance(self) -> int:
        flinch_tag = self.get_tag(FlinchMove)
        if isinstance(flinch_tag, FlinchMove):
            return flinch_tag.chance
        return 0
    @property
    def is_hazard(self) -> bool:
        return self.has_tag(HazardMove)
    @property
    def heal_percentage(self) -> int:
        heal_tag = self.get_tag(HealMove)
        if isinstance(heal_tag, HealMove):
            return heal_tag.heal_percentage
        return 0
    @property
    def is_multi_hit(self) -> bool:
        return self.has_tag(MultiHitMove)
    @property
    def is_multi_turn(self) -> bool:
        return self.has_tag(MultiTurnMove)
    @property
    def is_ohko(self) -> bool:
        return self.category == MoveCategory.OHKO
    @property
    def is_protect_move(self) -> bool:
        return self.has_tag(ProtectMove)
    @property
    def is_pivot_move(self) -> bool:
        return self.has_tag(PivotMove)
    @property
    def is_screen_move(self) -> bool:
        return self.has_tag(ScreenMove)
    @property
    def screen_move(self) -> Optional[ScreenMove]:
        return self.get_tag(ScreenMove) # type: ignore
    @property
    def is_stat_change_move(self) -> bool:
        return self.has_tag(StatChangeMove)
    @property
    def is_status_condition_move(self) -> bool:
        return self.has_tag(StatusConditionMove)    
    @property
    def is_terrain_move(self) -> bool:
        return self.has_tag(TerrainMove)
    @property
    def is_weather_move(self) -> bool:
        return self.has_tag(WeatherMove)
    #endregion

class Move(BaseModel):
    """

    Args:
        current_pp: int: Current PP of the move
        max_pp: int: Maximum PP of the move
        base_move: BaseMove: The base move data
    """
    current_pp: int
    max_pp: int = Field(default=0)
    base_move: BaseMove

    pp_incremented_amount: int = 0
    
    def __init__(self, **data): # type: ignore
        super().__init__(**data)
        if self.max_pp == 0:
            self.max_pp = self.base_move.base_pp
        if self.current_pp > self.max_pp:
            self.current_pp = self.max_pp

    def increment_pp(self) -> None:
        if self.pp_incremented_amount >= 3:
            return  # Cannot increase PP further
        self.pp_incremented_amount += 1
        if self.pp_incremented_amount == 1:
            self.max_pp = self.base_move.max_pp_inc_one
        elif self.pp_incremented_amount == 2:
            self.max_pp = self.base_move.max_pp_inc_two
        elif self.pp_incremented_amount == 3:
            self.max_pp = self.base_move.max_pp_inc_three

        # Ensure current PP does not exceed new max PP
        if self.current_pp > self.max_pp:
            self.current_pp = self.max_pp
    def maximize_pp(self) -> None:
        self.pp_incremented_amount = 3
        self.max_pp = self.base_move.max_pp_inc_three
        if self.current_pp > self.max_pp:
            self.current_pp = self.max_pp
    
    def has_tag(self, tag_type: Type[MoveTag]) -> bool:
        return self.base_move.has_tag(tag_type)
    
    def get_tag(self, tag_type: Type[MoveTag]) -> Optional[MoveTag]:
        return self.base_move.get_tag(tag_type)

#region Move property getters
    @property
    def type(self) -> PokemonType:
        return self.base_move.type
    @property
    def name(self) -> str:
        return self.base_move.name
    @property
    def index(self) -> int:
        return self.base_move.index
    @property
    def damage_class(self) -> DamageClass:
        return self.base_move.damage_class
    @property
    def category(self) -> MoveCategory:
        return self.base_move.category
    @property
    def power(self) -> Optional[int]:
        return self.base_move.power
    @property
    def accuracy(self) -> Optional[int]:
        return self.base_move.accuracy
    @property
    def base_pp(self) -> int:
        return self.base_move.base_pp
    @property
    def target(self) -> MoveTarget:
        return self.base_move.target
    @property
    def priority(self) -> int:
        return self.base_move.priority
    @property
    def makes_contact(self) -> bool:
        return self.base_move.has_tag(ContactMove)
    @property
    def is_multi_hit(self) -> bool:
        return self.base_move.is_multi_hit
    @property
    def min_hits(self) -> int:
        multi_hit_tag: Optional[MultiHitMove] = self.base_move.get_tag(MultiHitMove) # type: ignore
        if multi_hit_tag:
            return min(multi_hit_tag.hits.keys())
        return 1
    @property
    def max_hits(self) -> int:
        multi_hit_tag: Optional[MultiHitMove] = self.base_move.get_tag(MultiHitMove) # type: ignore
        if multi_hit_tag:
            return max(multi_hit_tag.hits.keys())
        return 1
    
    
    
#endregion

class MoveSet(BaseModel):
    # this will store move objects in a dict of the move index, and then the move and its current pp
    moves: dict[int, Move] = {}
    moveset_order: List[int] = []

    def __init__(self, moves: Optional[List[BaseMove]] = None, **data): # type: ignore
        super().__init__(**data)
        
        if not isinstance(moves, list):
            if moves is None: moves = []
            else:             moves = [moves]
        for move in moves:
            if not isinstance(move, BaseMove): # type: ignore - Sanity check
                raise ValueError("Each move must be a BaseMove object.")
            self.moves[move.index] = Move(current_pp=move.base_pp, base_move=move) # type: ignore

        self._set_initial_move_order()

    def _set_initial_move_order(self):
        self.moveset_order = list(self.moves.keys())[:4]

    def get_move_by_move_order_index(self, index: int) -> Optional[Move]:
        if 0 <= index < len(self.moveset_order):
            move_index = self.moveset_order[index]
            return self.moves.get(move_index, None)
        return None

    def get_move_by_name(self, name: str) -> Optional[Move]:
        for move in self.moves.values():
            if move.base_move.name == name:
                return move
        return None
    
    def get_move_by_index(self, index: int) -> Optional[Move]:
        return self.moves.get(index, None)
    
    def list_moves(self) -> List[Move]:
        move_list: List[Move] = []
        for move_index in self.moveset_order:
            move = self.moves.get(move_index, None)
            if move:
                move_list.append(move)
        return move_list
            

    @model_validator(mode="after")
    def _validate_move_count(self):
        if len(self.moves) > 4:
            raise ValueError("A Pokémon can only know up to 4 moves.")
        return self

    def add_move(self, move: Move):
        if len(self.moves) < 4:
            self.moves[move.base_move.index] = move
        else:
            raise ValueError("A Pokémon can only know up to 4 moves.")
    
    def replace_move(self, index: int, move: Move):
        if 0 <= index < len(self.moves):
            self.moves[index] = move
        else:
            raise IndexError("Move index out of range.")
    
    def _get_move_by_name(self, name: str) -> Optional[Move]:
        for move in self.moves.values():
            if move.base_move.name == name:
                return move
        return None
    
    def restore_all_pp(self):
        for move in self.moves.values():
            move.current_pp = move.max_pp

rebuild_models()