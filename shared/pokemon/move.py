from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from .types import PokemonType, MoveCategory, StatusCondition, Stat


class BaseMove(BaseModel):
    name: str
    type: PokemonType
    power: Optional[int] = 100
    accuracy: Optional[int] = 100
    pp: int = Field(ge=1, le=40, default=10)
    category: MoveCategory = Field(default=MoveCategory.PHYSICAL)
    status_condition: StatusCondition = StatusCondition.NONE
    stat_changes_inflicted: Optional[List['StatChange']] = None  # List of stat changes inflicted by the move
    stat_changes_recieved: Optional[List['StatChange']] = None  # List of stat changes received by the user of the move

class Move(BaseModel):
    current_pp: int
    base_move: BaseMove

    

class StatChange(BaseModel):
    stat: Stat
    change: int  # Positive for increase, negative for decrease


class MoveSet(BaseModel):
    # this will store move objects in a dict of the move index, and then the move and its current pp
    moves: dict[int, Move] = Field(default_factory=dict)

    def __init__(self, moves: Optional[List[BaseMove]] = None, **data):
        super().__init__(**data)
        
        if moves:
            self.moves = {index: Move(base_move=move, current_pp=move.pp) for index, move in enumerate(moves)}

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