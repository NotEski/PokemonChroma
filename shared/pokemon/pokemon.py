from random import randint
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Protocol
from enum import Enum

from .types import PokemonType
from .move import MoveSet, Move, MoveTarget
from .genders import Gender, GenderRate
from .natures import Nature
from .abilities import PokemonBaseAbility, PokemonAbilities
from .stats import BaseStats, IndividualValues, EffortValues, EffortYield, Stat
from .status_conditions import StatusCondition
from shared.items.pokeball import Pokeball
from shared.items.items import Item
from shared.battle.battle_positions import BattlePosition

class GrowthRate(Enum):
    FAST_THEN_VERY_SLOW = "fast_then_very_slow"
    SLOW = "slow"
    MEDIUM_SLOW = "medium_slow"
    MEDIUM = "medium"
    MEDIUM_FAST = "medium_fast"
    FAST = "fast"
    SLOW_THEN_VERY_FAST = "slow_then_very_fast"
    

class EggGroup(Enum):
    BUG = "bug"
    DITTO = "ditto"
    DRAGON = "dragon"
    FAIRY = "fairy"
    FLYING = "flying"
    GROUND = "ground"
    HUMANSHAPE = "humanshape"
    INDETERMINATE = "indeterminate"
    MINERAL = "mineral"
    MONSTER = "monster"
    NO_EGGS = "no_eggs"
    PLANT = "plant"
    WATER1 = "water1"
    WATER2 = "water2"
    WATER3 = "water3"



class PokemonBase(BaseModel):
    name: str
    name_readable: str = Field(default="")
    types: List[PokemonType]
    base_stats: BaseStats
    pokedex_number: int
    ev_yield: EffortYield = Field(default_factory=EffortYield)
    abilities: list[PokemonBaseAbility] = Field(default_factory=list)

    base_experience_yield: int = Field(default=64)
    gender_rate: GenderRate = Field(default=GenderRate.EQUAL)
    capture_rate: int = Field(ge=0, le=255, default=45)
    base_happiness: int = Field(ge=0, le=255, default=70)
    growth_rate: GrowthRate = Field(default=GrowthRate.MEDIUM)
    egg_groups: List[EggGroup] = Field(default_factory=list)

    height: float = Field(ge=0.0, default=1.0)  # in meters
    weight: float = Field(ge=0.0, default=1.0)  # in kilograms

class PokemonBattleState(BaseModel):
    attack_stat_stage: int = Field(default=0)
    defense_stat_stage: int = Field(default=0)
    special_attack_stat_stage: int = Field(default=0)
    special_defense_stat_stage: int = Field(default=0)
    speed_stat_stage: int = Field(default=0)
    accuracy_stage: int = Field(default=0)
    evasion_stage: int = Field(default=0)
    critical_hit_stage: int = Field(default=0)

    non_volatile_status_conditions: List[StatusCondition] = Field(default_factory=list)



class Pokemon(BaseModel):
    pokemon: PokemonBase
    nickname: str = Field(default="")
    personality_value: int = Field(default_factory=lambda: randint(0, 2**32 - 1))
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
    move_set: MoveSet = Field(default_factory=MoveSet)
    abilities: PokemonAbilities = Field(default_factory=PokemonAbilities)
    friendship: int = Field(ge=0, le=255, default=70)
    experience: int = Field(ge=0, default=0)
    held_item: Optional[Item] = Field(default=None)


    pokemon_battle_state: PokemonBattleState = Field(default_factory=PokemonBattleState)

    @model_validator(mode="after")
    def __post_init__(self):

        # calc values based on personality value
        self._calc_gender()
        self._calc_nature()
        self._calc_individual_values()
        self._calc_shiny()

        self.max_hp = self.calculate_stat(Stat.HP)
        self.current_hp = self.max_hp
        self.nickname = self.pokemon.name
        self.terra_type = self.pokemon.types[0]  # Default tera type to first type

        return self
   
    def _calc_shiny(self):
        # Simplified shiny calculation
        # In actual games, shiny determination is more complex
        self.shiny = (self.personality_value % 8192) < 1 # 1 in 8192 chance

    def _calc_gender(self):
        rate = self.pokemon.gender_rate
        if rate == GenderRate.GENDERLESS:
            self.gender = Gender.NONE
            return
        self.gender = Gender.MALE if (self.personality_value % 8) <= rate.value else Gender.FEMALE

    def _calc_nature(self):
        nature_index = self.personality_value % 25
        self.nature = Nature(list(Nature)[nature_index])

    def _calc_individual_values(self):
        self.individual_values.hp = self.personality_value & 0x1F
        self.individual_values.attack = (self.personality_value >> 5) & 0x1F
        self.individual_values.defense = (self.personality_value >> 10) & 0x1F
        self.individual_values.speed = (self.personality_value >> 15) & 0x1F
        self.individual_values.special_attack = (self.personality_value >> 20) & 0x1F
        self.individual_values.special_defense = (self.personality_value >> 25) & 0x1F
    
    def calculate_max_hp(self) -> int:
        return (((self.individual_values.hp + 2 * self.pokemon.base_stats.hp +((self.effort_values.hp)/4)+100) * self.level)/100)+10
 
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
            return round(self.calculate_max_hp())
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
    
    def get_base_stat(self, stat_name: str) -> int:
        return getattr(self.pokemon.base_stats, stat_name)
        

    @property
    def is_fainted(self) -> bool:
        return self.current_hp <= 0
    
    


class BattleActionExecutor(Protocol):
    def use_move(self, move: str|int|Move, target: Optional[BattlePosition]) -> None:
        # BattlePosition is only required for moves that target other Pokemon
        
        pass

    def use_item(self, item: Item) -> None:
        pass

    def use_escape(self) -> None:
        pass

    def use_pokeball(self, pokeball: Pokeball, target: Optional[BattlePosition]) -> None:
        pass


class PokemonTeam(BaseModel):
    pokemons: List[Pokemon] = Field(min_items=1, max_items=6)

    def get_all_pokemons(self) -> List[Pokemon]:
        return self.pokemons