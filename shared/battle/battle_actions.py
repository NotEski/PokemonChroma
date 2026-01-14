from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from shared.battle.position import BattlePosition


class ActionType(Enum):
    MOVE = "move"
    SWITCH = "switch"
    USE_ITEM = "use_item"
    ESCAPE = "escape"
    SKIP = "skip"
    UNDEFINED = "undefined"

class BattleAction(BaseModel):
    position: BattlePosition
    action_type: ActionType = ActionType.UNDEFINED

class MoveAction(BattleAction):
    action_type: ActionType = Field(default=ActionType.MOVE)
    move_index: int
    target_position: BattlePosition

class SwitchAction(BattleAction):
    action_type: ActionType = Field(default=ActionType.SWITCH)
    switch_in_pokemon_index: int

class UseItemAction(BattleAction):
    action_type: ActionType = Field(default=ActionType.USE_ITEM)
    item_name: str
    target_position: Optional[BattlePosition] = None

class EscapeAction(BattleAction):
    action_type: ActionType = Field(default=ActionType.ESCAPE)
    escape_attempts: int = 0

class SkipTurnAction(BattleAction):
    action_type: ActionType = Field(default=ActionType.SKIP)