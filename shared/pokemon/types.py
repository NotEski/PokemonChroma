from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, model_validator

class PokemonType(Enum):
    NORMAL = "normal"
    FIRE = "fire"
    WATER = "water"
    ELECTRIC = "electric"
    GRASS = "grass"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DRAGON = "dragon"
    DARK = "dark"
    STEEL = "steel"
    FAIRY = "fairy"

class Stat(Enum):
    HP = "hp"
    ATTACK = "attack"
    DEFENSE = "defense"
    SPECIAL_ATTACK = "special_attack"
    SPECIAL_DEFENSE = "special_defense"
    SPEED = "speed"

class StatusCondition(Enum):
    NONE = "none"
    PARALYZED = "paralyzed"
    POISONED = "poisoned"
    BURNED = "burned"
    FROZEN = "frozen"
    ASLEEP = "asleep"

class BaseStats(BaseModel):
    hp: int = Field(ge=1, le=255)
    attack: int = Field(ge=1, le=255)
    defense: int = Field(ge=1, le=255)
    special_attack: int = Field(ge=1, le=255)
    special_defense: int = Field(ge=1, le=255)
    speed: int = Field(ge=1, le=255)

class IndividualValues(BaseModel):
    hp: int = Field(ge=0, le=31, default=0)
    attack: int = Field(ge=0, le=31, default=0)
    defense: int = Field(ge=0, le=31, default=0)
    special_attack: int = Field(ge=0, le=31, default=0)
    special_defense: int = Field(ge=0, le=31, default=0)
    speed: int = Field(ge=0, le=31, default=0)

class EffortValues(BaseModel):
    hp: int = Field(ge=0, le=252, default=0)
    attack: int = Field(ge=0, le=252, default=0)
    defense: int = Field(ge=0, le=252, default=0)
    special_attack: int = Field(ge=0, le=252, default=0)
    special_defense: int = Field(ge=0, le=252, default=0)
    speed: int = Field(ge=0, le=252, default=0)

    @model_validator(mode="after")
    def validate_total_evs(self) -> bool:
        total = sum([self.hp, self.attack, self.defense, self.special_attack, self.special_defense, self.speed])
        if total > 510:
            raise ValueError("Total EVs cannot exceed 510.")
        return self

class EffortYield(BaseModel):
    hp: int = Field(ge=0, default=0)
    attack: int = Field(ge=0, default=0)
    defense: int = Field(ge=0, default=0)
    special_attack: int = Field(ge=0, default=0)
    special_defense: int = Field(ge=0, default=0)
    speed: int = Field(ge=0, default=0)

class Nature(Enum):
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

class LevelingRate(Enum):
    FAST = "fast"
    MEDIUM_FAST = "medium_fast"
    MEDIUM_SLOW = "medium_slow"
    SLOW = "slow"

class MoveCategory(Enum):
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NONE = "none"

class Ability(BaseModel):
    name: str
    name_readable: str
    description: str

class AbilitySlot(BaseModel):
    ability: Ability
    is_hidden: bool = Field(default=False)
    slot: int = Field(ge=1)

class GenderRate(Enum):
    GENDERLESS = -1
    ALWAYS_FEMALE = 0
    MOSTLY_FEMALE = 1
    MAJORITY_FEMALE = 2
    LIKELY_FEMALE = 3
    EQUAL = 4
    LIKELY_MALE = 5
    MAJORITY_MALE = 6
    MOSTLY_MALE = 7
    ALWAYS_MALE = 8