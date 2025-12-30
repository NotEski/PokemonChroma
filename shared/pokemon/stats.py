from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Stat(Enum):
    HP = "hp"
    ATTACK = "attack"
    DEFENSE = "defense"
    SPECIAL_ATTACK = "special_attack"
    SPECIAL_DEFENSE = "special_defense"
    SPEED = "speed"
    ACCURACY = "accuracy"
    EVASION = "evasion"
    CRITICAL_HIT = "critical_hit"

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