from pydantic import BaseModel, Field, model_validator, field_validator
from typing import List
from .types import *
from .move import MoveSet

class PokemonBase(BaseModel):
    name: str
    types: List[PokemonType]
    base_stats: BaseStats
    pokedex_number: int
    catch_rate: int = Field(ge=1, le=255, default=45)
    ev_yield: EffortYield = Field(default_factory=EffortYield)

class PokemonBattleState(BaseModel):
    attack_stat_stage: int = Field(default=0)
    defense_stat_stage: int = Field(default=0)
    special_attack_stat_stage: int = Field(default=0)
    special_defense_stat_stage: int = Field(default=0)
    speed_stat_stage: int = Field(default=0)
    accuracy_stage: int = Field(default=0)
    evasion_stage: int = Field(default=0)
    critical_hit_stage: int = Field(default=0)

    is_protected: bool = Field(default=False)
    confusion_turns: int = Field(default=0)
    is_bound: bool = Field(default=False)
    is_flinching: bool = Field(default=False)

class Pokemon(BaseModel):
    pokemon: PokemonBase
    nickname: str = Field(default="")
    level: int = Field(ge=1, le=100, default=1)
    current_hp: int = Field(ge=0, default=0)
    max_hp: int = Field(ge=1, default=0)
    status_condition: StatusCondition = Field(default=StatusCondition.NONE)
    shiny: bool = Field(default=False)
    gender: Gender = Field(default=Gender.MALE)
    individual_values: IndividualValues = Field(default_factory=IndividualValues)
    effort_values: EffortValues = Field(default_factory=EffortValues)
    terra_type: PokemonType = Field(default=None)
    nature: Nature = Field(default=Nature.HARDY)
    pokemon_battle_state: PokemonBattleState = Field(default_factory=PokemonBattleState)

    move_set: MoveSet = Field(default_factory=MoveSet)

    @model_validator(mode="after")
    def __post_init__(self):
        self.max_hp = self.calculate_stat(Stat.HP)
        self.current_hp = self.max_hp
        self.nickname = self.pokemon.name
        self.terra_type = self.pokemon.types[0]  # Default tera type to first type
        return self

    def calculate_max_hp(self) -> int:
        # Simplified HP calculation formula
        return ((2 * self.pokemon.base_stats.hp + self.individual_values.hp + (self.effort_values.hp // 4)) * self.level) // 100 + self.level + 10
    
    def calculate_stat(self, stat: Stat) -> int:
        base = getattr(self.pokemon.base_stats, stat.value)
        iv = getattr(self.individual_values, stat.value)
        ev = getattr(self.effort_values, stat.value)
        
        
        if self.nature.increased_stat == stat:
            nature = 1.1
        elif self.nature.decreased_stat == stat:
            nature = 0.9
        else:
            nature = 1.0

        if stat.value == "hp":
            return self.calculate_max_hp()
        else:
            return round(((((2 * base + iv + (ev / 4)) * self.level) / 100) + 5) * nature)

    def get_attack_stat(self) -> int:
        return self.calculate_stat(Stat.ATTACK)
    
    def get_defense_stat(self) -> int:
        return self.calculate_stat(Stat.DEFENSE)
    
    def get_special_attack_stat(self) -> int:
        return self.calculate_stat(Stat.SPECIAL_ATTACK)

    def get_special_defense_stat(self) -> int:
        return self.calculate_stat(Stat.SPECIAL_DEFENSE)
    
    def get_speed_stat(self) -> int:
        return self.calculate_stat(Stat.SPEED)
    
    @property
    def is_fainted(self) -> bool:
        return self.current_hp <= 0