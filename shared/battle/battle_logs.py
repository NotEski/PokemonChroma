from pydantic import BaseModel, Field
from abc import abstractmethod
from typing import List, Literal, Optional, TypedDict, Unpack, NotRequired
from enum import Enum

from shared.pokemon.pokemon import Pokemon
from shared.pokemon.status_conditions import StatusCondition
from shared.pokemon.move import BaseMove
from shared.trainer.trainer import Trainer
from shared.battle.type_effectiveness import EffectivenessLevel
from .battle_positions import BattlePosition



class BattleLogType(Enum):
    BATTLE_START = "battle_start"
    TURN_START = "turn_start"
    POKEMON_SWITCH_IN = "pokemon_switch_in"
    MOVE_USED = "move_used"
    DAMAGE_DEALT = "damage_dealt"
    STATUS_APPLIED = "status_applied"
    POKEMON_FAINTED = "pokemon_fainted"
    BATTLE_END = "battle_end"
    UNDEFINED = "undefined"


class BattleLogEntry(BaseModel):
    """
    Docstring for BattleLogEntry needs to contain everything that happened in a turn. so it could be replicated later perfectly if needed.
    """
    log_type: BattleLogType = Field(default=BattleLogType.UNDEFINED)
    description: str = Field(default="")


class BattleLogMoveUsed(BattleLogEntry):
    move_name: BaseMove
    user_pokemon: Pokemon
    target_pokemon: Optional[List[Pokemon]] = Field(default_factory=list)
    damage_dealt: int = Field(default=0)
    is_critical: bool = Field(default=False)
    status_condition_applied: Optional[StatusCondition] = Field(default=None)  # e.g., "burn", "paralysis", etc.
    move_effectiveness: EffectivenessLevel = Field(default=EffectivenessLevel.NORMAL_EFFECTIVE)
    log_type: Literal[BattleLogType.MOVE_USED] = BattleLogType.MOVE_USED

class BattleLogMoveUsedData(TypedDict):
    move_name: BaseMove
    user_pokemon: Pokemon
    target_pokemon: NotRequired[List[Pokemon]]
    damage_dealt: NotRequired[int]
    is_critical: NotRequired[bool]
    status_condition_applied: NotRequired[StatusCondition]
    move_effectiveness: NotRequired[EffectivenessLevel]
    description: NotRequired[str]


class BattleLogPokemonFainted(BattleLogEntry):
    fainted_pokemon: Pokemon
    pokemon_position: BattlePosition
    trainer: Trainer
    log_type: Literal[BattleLogType.POKEMON_FAINTED] = BattleLogType.POKEMON_FAINTED

class BattleLogPokemonFaintedData(TypedDict):
    fainted_pokemon: Pokemon
    pokemon_position: BattlePosition
    trainer: Trainer
    description: NotRequired[str]


class BattleLogPokemonSwitchIn(BattleLogEntry):
    switched_in_pokemon: Pokemon
    posistion: BattlePosition
    trainer: Trainer
    log_type: Literal[BattleLogType.POKEMON_SWITCH_IN] = BattleLogType.POKEMON_SWITCH_IN

class BattleLogPokemonSwitchInData(TypedDict):
    switched_in_pokemon: Pokemon
    posistion: BattlePosition
    trainer: Trainer
    description: NotRequired[str]

class BattleLogBattleStart(BattleLogEntry):
    trainers: List[Trainer]
    log_type: Literal[BattleLogType.BATTLE_START] = BattleLogType.BATTLE_START
    
class BattleLogBattleStartData(TypedDict):
    trainers: List[Trainer]
    description: NotRequired[str]

class BattleLogTurnStart(BattleLogEntry):
    turn_number: int
    log_type: Literal[BattleLogType.TURN_START] = BattleLogType.TURN_START

class BattleLogTurnStartData(TypedDict):
    turn_number: int
    description: NotRequired[str]


class BattleLogBattleEnd(BattleLogEntry):
    winning_trainer: Optional[Trainer]
    log_type: Literal[BattleLogType.BATTLE_END] = BattleLogType.BATTLE_END

class BattleLogBattleEndData(TypedDict):
    winning_trainer: NotRequired[Trainer]
    description: NotRequired[str]


class BattleLogManager(BaseModel):
    logs: List['BattleLogEntry'] = Field(default_factory=list)

    def add_log(self, log_entry: 'BattleLogEntry'):
        self.logs.append(log_entry)

    def print_log(self):
        for log in self.logs:
            print(f"[{log.log_type.value}] {log.description}")

    def move_used(self, **data: Unpack[BattleLogMoveUsedData]):
        log = BattleLogMoveUsed(**data)
        self.add_log(log)

    def pokemon_fainted(self, **data: Unpack[BattleLogPokemonFaintedData]):
        log = BattleLogPokemonFainted(**data)
        self.add_log(log)
    
    def pokemon_switch_in(self, **data: Unpack[BattleLogPokemonSwitchInData]):
        log = BattleLogPokemonSwitchIn(**data)
        self.add_log(log)

    def battle_start(self, **data: Unpack[BattleLogBattleStartData]):
        log = BattleLogBattleStart(**data)
        self.add_log(log)
    
    def turn_start(self, **data: Unpack[BattleLogTurnStartData]):
        log = BattleLogTurnStart(**data)
        self.add_log(log)

    def battle_end(self, **data: Unpack[BattleLogBattleEndData]):
        log = BattleLogBattleEnd(**data)
        self.add_log(log)

    