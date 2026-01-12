from enum import Enum
from .stats import Stat
from typing import Optional

class Nature(Enum):
    NONE = ("none", None, None)
    HARDY = ("hardy", None, None)
    LONELY = ("lonely", Stat.ATTACK, Stat.DEFENSE)
    BRAVE = ("brave", Stat.ATTACK, Stat.SPEED)
    ADAMANT = ("adamant", Stat.ATTACK, Stat.SPECIAL_ATTACK)
    NAUGHTY = ("naughty", Stat.ATTACK, Stat.SPECIAL_DEFENSE)
    BOLD = ("bold", Stat.DEFENSE, Stat.ATTACK)
    DOCILE = ("docile", None, None)
    RELAXED = ("relaxed", Stat.DEFENSE, Stat.SPEED)
    IMPISH = ("impish", Stat.DEFENSE, Stat.SPECIAL_ATTACK)
    LAX = ("lax", Stat.DEFENSE, Stat.SPECIAL_DEFENSE)
    TIMID = ("timid", Stat.SPEED, Stat.ATTACK)
    HASTY = ("hasty", Stat.SPEED, Stat.DEFENSE)
    SERIOUS = ("serious", None, None)
    JOLLY = ("jolly", Stat.SPEED, Stat.SPECIAL_ATTACK)
    NAIVE = ("naive", Stat.SPEED, Stat.SPECIAL_DEFENSE)
    MODEST = ("modest", Stat.SPECIAL_ATTACK, Stat.ATTACK)
    MILD = ("mild", Stat.SPECIAL_ATTACK, Stat.DEFENSE)
    QUIET = ("quiet", Stat.SPECIAL_ATTACK, Stat.SPEED)
    BASHFUL = ("bashful", None, None)
    RASH = ("rash", Stat.SPECIAL_ATTACK, Stat.SPECIAL_DEFENSE)
    CALM = ("calm", Stat.SPECIAL_DEFENSE, Stat.ATTACK)
    GENTLE = ("gentle", Stat.SPECIAL_DEFENSE, Stat.DEFENSE)
    SASSY = ("sassy", Stat.SPECIAL_DEFENSE, Stat.SPEED)
    CAREFUL = ("careful", Stat.SPECIAL_DEFENSE, Stat.SPECIAL_ATTACK)
    QUIRKY = ("quirky", None, None)

    def __init__(self, name: str, increased_stat: Optional[Stat], decreased_stat: Optional[Stat]):
        self._name = name
        self.increased_stat = increased_stat
        self.decreased_stat = decreased_stat