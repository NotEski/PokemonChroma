from enum import Enum, auto

class BattlePosition(Enum):
    pass

class SinglesBattlePosition(BattlePosition):
    Team1_Pokemon1 = auto()
    Team2_Pokemon1 = auto()

class DoublesBattlePosition(BattlePosition):
    Team1_Pokemon1 = auto()
    Team1_Pokemon2 = auto()
    Team2_Pokemon1 = auto()
    Team2_Pokemon2 = auto()