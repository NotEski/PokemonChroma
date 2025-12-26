from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from .types import PokemonType
from .status_conditions import StatusCondition
from .stats import Stat


class DamageClass(Enum):
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"

class MoveCategory(Enum):
    DAMAGE = "damage"
    STATUS = "status"
    DAMAGE_AND_STATUS = "damage_status"
    DAMAGE_AND_HEAL = "damage_heal"
    DAMAGE_AND_LOWER = "damage_lower"
    DAMAGE_AND_RAISE = "damage_raise"
    FIELD_EFFECT = "field_effect"
    FORCE_SWITCH = "force_switch"
    HEAL = "heal"
    NET_GOOD_STATS = "net_good_stats"
    OHKO = "ohko"
    SWAGGER = "swagger"
    UNIQUE = "unique"
    WHOLE_FIELD_EFFECT = "whole_field_effect"

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


class BaseMove(BaseModel):
    name: str
    name_readable: str = Field(default="")
    index: int

    type: PokemonType
    damage_class: DamageClass = Field(default=DamageClass.PHYSICAL)
    category: MoveCategory = Field(default=MoveCategory.DAMAGE)

    accuracy: Optional[int] = 100
    power: Optional[int] = 100
    pp: int = Field(ge=1, le=40, default=15)

    target: MoveTarget = Field(default=MoveTarget.SELECTED_POKEMON)

    priority: int = Field(default=0)  # Move priority
    
    status_condition: StatusCondition = StatusCondition.NONE # Status condition inflicted by the move
    status_condition_chance: int = 0  # Percentage chance to inflict status condition

    critical_hit_rate: int = Field(default=0)  # Additional stages to critical hit rate
    flinch_chance: int = Field(default=0)  # Percentage chance to flinch the target

    drain: int = Field(default=0)  # Percentage of in percentage of damage dealt healed, recoiled damage if negative
    healing: int = Field(default=0)  # Percentage of max HP healed

    min_hits: Optional[int] = None  # For multi-hit moves
    max_hits: Optional[int] = None  # For multi-hit moves

    min_turns: Optional[int] = None  # For moves that last multiple turns
    max_turns: Optional[int] = None  # For moves that last multiple turns
    
    stat_changes: Optional[List['StatChange']] = None  # List of stat changes inflicted by the move
    stat_chance: int = Field(default=0)  # Percentage chance to apply stat changes
    
    stat_changes_inflicted: Optional[List['StatChange']] = None  # List of stat changes inflicted by the move
    stat_changes_recieved: Optional[List['StatChange']] = None  # List of stat changes received by the user of the move


class Move(BaseModel):
    current_pp: int
    base_move: BaseMove

class StatChange(BaseModel):
    stat: Stat
    change: int  # Positive for increase, negative for decrease
    chance: int = Field(default=100)  # Percentage chance to apply the stat change

class MoveSet(BaseModel):
    # this will store move objects in a dict of the move index, and then the move and its current pp
    moves: dict[int, Move] = Field(default_factory=dict)

    def __init__(self, moves: Optional[List[BaseMove]] = None, **data):
        super().__init__(**data)
        
        if not isinstance(moves, list):
            if moves is None: moves = []
            else:             moves = [moves]
        for move in moves:
            if not (isinstance(move, BaseMove)):
                raise ValueError("Each move must be a BaseMove object.")
            self.moves[move.index] = Move(current_pp=move.pp, base_move=move)

    def get_move_by_name(self, name: str) -> Optional[Move]:
        for move in self.moves.values():
            if move.base_move.name == name:
                return move
        return None
    
    def get_move_by_index(self, index: int) -> Optional[Move]:
        return self.moves.get(index, None)
            

    @model_validator(mode="after")
    def _validate_move_count(self):
        if len(self.moves) > 4:
            raise ValueError("A Pokémon can only know up to 4 moves.")
        return self

    def add_move(self, move: Move):
        if len(self.moves) < 4:
            self.moves.append(move)
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