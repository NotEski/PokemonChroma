from pydantic import BaseModel, Field
from typing import List, Optional, TypedDict, Unpack, NotRequired
from enum import Enum

from shared.battle.opponent import Opponent
from shared.pokemon.pokemon import BattleMon
from shared.pokemon.status_conditions import StatusCondition
from shared.pokemon.move import BaseMove
from shared.battle.type_effectiveness import EffectivenessLevel
from shared.battle.position_manager import BattlePosition



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
    move_name: Optional[BaseMove] = Field(default=None)
    user_pokemon: BattleMon
    target_pokemon: Optional[List[BattleMon]] = []
    damage_dealt: int = Field(default=0)
    is_critical: bool = Field(default=False)
    status_condition_applied: Optional[StatusCondition] = Field(default=None)  # e.g., "burn", "paralysis", etc.
    log_type: BattleLogType = BattleLogType.MOVE_USED

class BattleLogMoveUsedData(TypedDict):
    move_name: BaseMove
    user_pokemon: BattleMon
    target_pokemon: NotRequired[List[BattleMon]]
    damage_dealt: NotRequired[int]
    is_critical: NotRequired[bool]
    status_condition_applied: NotRequired[StatusCondition]
    move_effectiveness: NotRequired[EffectivenessLevel]
    description: NotRequired[str]

class BattleLogPokemonFainted(BattleLogEntry):
    fainted_pokemon: BattleMon
    pokemon_position: BattlePosition
    opponent: Opponent
    log_type: BattleLogType = BattleLogType.POKEMON_FAINTED

class BattleLogPokemonFaintedData(TypedDict):
    fainted_pokemon: BattleMon
    pokemon_position: BattlePosition
    opponent: Opponent
    description: NotRequired[str]


class BattleLogPokemonSwitchIn(BattleLogEntry):
    switched_in_pokemon: BattleMon
    posistion: BattlePosition
    opponent: Opponent
    log_type: BattleLogType = BattleLogType.POKEMON_SWITCH_IN

class BattleLogPokemonSwitchInData(TypedDict):
    switched_in_pokemon: BattleMon
    posistion: BattlePosition
    opponent: Opponent
    description: NotRequired[str]

class BattleLogBattleStart(BattleLogEntry):
    opponents: List[Opponent]
    log_type: BattleLogType = BattleLogType.BATTLE_START
    
class BattleLogBattleStartData(TypedDict):
    opponents: List[Opponent]
    description: NotRequired[str]

class BattleLogTurnStart(BattleLogEntry):
    turn_number: int
    log_type: BattleLogType = BattleLogType.TURN_START

class BattleLogTurnStartData(TypedDict):
    turn_number: int
    description: NotRequired[str]

class BattleLogBattleEnd(BattleLogEntry):
    winning_trainer: Optional[Opponent]
    log_type: BattleLogType = BattleLogType.BATTLE_END

class BattleLogBattleEndData(TypedDict):
    winning_trainer: NotRequired[Opponent]
    description: NotRequired[str]


class BattleLogManager(BaseModel):
    logs: List['BattleLogEntry'] = []

    def add_log(self, log_entry: 'BattleLogEntry'):
        self.logs.append(log_entry)
    
    def clear_logs(self):
        self.logs.clear()

    def print_log(self):
        for log in self.logs:
            print(f"[{log.log_type.value}]\n{log.description}")

    def misc(self, description: str):
        log = BattleLogEntry(
            log_type=BattleLogType.UNDEFINED,
            description=description
        )
        self.add_log(log)

    def move_used(self, **data: Unpack[BattleLogMoveUsedData]):
        log = BattleLogMoveUsed(**data) # type: ignore
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

    def weather_end(self, description: str):
        log = BattleLogEntry(
            log_type=BattleLogType.UNDEFINED,
            description=description
        )
        self.add_log(log)
    
    def status_condition_damage(self, description: str):
        log = BattleLogEntry(
            log_type=BattleLogType.DAMAGE_DEALT,
            description=description
        )
        self.add_log(log)
