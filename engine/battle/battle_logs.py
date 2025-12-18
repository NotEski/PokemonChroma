from pydantic import BaseModel, Field
from abc import abstractmethod
from typing import Dict, List, Optional
from enum import Enum, auto

from shared.pokemon.pokemon import Pokemon
from shared.pokemon.types import StatusCondition
from shared.pokemon.move import BaseMove
from .battle_positions import BattlePosition
from .battle_header import BattleTrainer



class BattleLogType(Enum):
    BATTLE_START = "battle_start"
    TURN_START = "turn_start"
    POKEMON_SWITCH_IN = "pokemon_switch_in"
    MOVE_USED = "move_used"
    DAMAGE_DEALT = "damage_dealt"
    STATUS_APPLIED = "status_applied"
    POKEMON_FAINTED = "pokemon_fainted"
    BATTLE_END = "battle_end"


class EffectivenessLevel(Enum):
    NO_EFFECT = 0
    NOT_EFFECTIVE = 1
    NORMAL_EFFECTIVE = 2
    SUPER_EFFECTIVE = 3

class BattleLogEntry(BaseModel):
    """
    Docstring for BattleLogEntry needs to contain everything that happened in a turn. so it could be replicated later perfectly if needed.
    """
    turn_number: int
    log_type: BattleLogType
    description: str # Console log of the event


class BattleLogMoveUsed(BattleLogEntry):
    move_name: BaseMove
    user_pokemon: Pokemon
    target_pokemon: List[Pokemon] = Field(default_factory=list)
    damage_dealt: int = Field(default=0)
    is_critical: bool = Field(default=False)
    status_condition_applied: Optional[StatusCondition]  # e.g., "burn", "paralysis", etc.
    move_effectiveness: EffectivenessLevel = Field(default=EffectivenessLevel.NORMAL_EFFECTIVE)


class BattleLogPokemonFainted(BattleLogEntry):
    fainted_pokemon: Pokemon
    pokemon_position: BattlePosition
    trainer: BattleTrainer

class BattleLogPokemonSwitchIn(BattleLogEntry):
    switched_in_pokemon: Pokemon
    posistion: BattlePosition
    trainer: BattleTrainer

class BattleLogBattleStart(BattleLogEntry):
    trainers: List[BattleTrainer]

class BattleLogTurnStart(BattleLogEntry):
    turn_number: int

class BattleLogBattleEnd(BattleLogEntry):
    winning_trainer: Optional[BattleTrainer]