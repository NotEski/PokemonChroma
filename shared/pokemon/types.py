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

class StatusCondition(Enum):
    NONE = "none"
    PARALYZED = "paralyzed"
    POISONED = "poisoned"
    BURNED = "burned"
    FROZEN = "frozen"
    SLEEP = "sleep"

class LevelingRate(Enum):
    FAST = "fast"
    MEDIUM_FAST = "medium_fast"
    MEDIUM_SLOW = "medium_slow"
    SLOW = "slow"
