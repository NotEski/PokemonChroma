from __future__ import annotations

from random import randint
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from enum import Enum

from .types import PokemonType
from .move import MoveSet
from .genders import Gender, GenderRate
from .natures import Nature
from .abilities import PokemonBaseAbility, PokemonAbilities
from .stats import BaseStats, IndividualValues, EffortValues, EffortYield, Stat
from .status_conditions import StatusCondition
from shared.items.items import Item

from shared.battle.battle_actions import MoveAction, SwitchAction, UseItemAction
from shared.battle.position import BattlePosition


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

    current_position: BattlePosition = Field(default_factory=BattlePosition)  # (team_id, pokemon_index)

    status_conditions: dict = Field(default_factory=dict[StatusCondition, int])  # e.g., "burn", "poison", etc. with turns present

    pokemon_enhancement_used: bool = Field(default=False)  # e.g., Mega Evolution, Terastallization, Z-Move

    def non_volatile_status_condition_check(self) -> List[StatusCondition]:
        non_volatile_conditions = [status for status in self.status_conditions.keys() if status.is_non_volatile()]
        if len(non_volatile_conditions) > 1:
            print ("Warning: More than one non-volatile status condition present.")
        return non_volatile_conditions



class Pokemon(BaseModel):
    pokemon: PokemonBase
    nickname: str = Field(default="")
    level: int = Field(ge=1, le=100, default=1)
    current_hp: int = Field(ge=0, default=0)
    max_hp: int = Field(ge=1, default=0)
    shiny: bool = Field(default=None)
    gender: Gender = Field(default=None)
    individual_values: IndividualValues = Field(default=None)
    effort_values: EffortValues = Field(default_factory=EffortValues)
    terra_type: PokemonType = Field(default=None)
    nature: Nature = Field(default=None)
    move_set: MoveSet = Field(default_factory=MoveSet)
    abilities: PokemonAbilities = Field(default_factory=PokemonAbilities)
    friendship: int = Field(ge=0, le=255, default=70)
    experience: int = Field(ge=0, default=0)
    held_item: Optional[Item] = Field(default=None)
    


    # NOTE FOR OUTSIDE OF BATTLE ONLY
    # for all battle related status conditions, they should be stored in PokemonBattleState
    external_status_condition: StatusCondition = Field(default=StatusCondition.NONE) 


    pokemon_battle_state: PokemonBattleState = Field(default_factory=PokemonBattleState)

    def __init__(self, **data):
        super().__init__(**data)
        # calc values based on personality value
        if hasattr(self, "_initialized"):
            return
        self._calc_gender()
        self._calc_nature()
        self._calc_individual_values()
        self._calc_shiny()

        self.max_hp = self.calculate_stat(Stat.HP)
        self.current_hp = self.max_hp
        self.nickname = self.pokemon.name
        self.terra_type = self.pokemon.types[0]  # Default tera type to first type
        self._initialized = True


    def _calc_shiny(self):
        if self.shiny is not None:
            return
        self.shiny = (randint(0, 8191) < 1) # 1 in 8192 chance

    def _calc_gender(self):
        if self.gender is not None:
            return
        rate = self.pokemon.gender_rate
        if rate == GenderRate.GENDERLESS:
            self.gender = Gender.NONE
            return
        self.gender = Gender.MALE if randint(0, 7) <= rate.value else Gender.FEMALE

    def _calc_nature(self):
        if self.nature is not None:
            return
        nature_index = randint(0, 24)
        self.nature = Nature(list(Nature)[nature_index])

    def _calc_individual_values(self):
        if self.individual_values:
            return
        self.individual_values = IndividualValues()

        self.individual_values.hp = randint(0, 31)
        self.individual_values.attack = randint(0, 31)
        self.individual_values.defense = randint(0, 31)
        self.individual_values.speed = randint(0, 31)
        self.individual_values.special_attack = randint(0, 31)
        self.individual_values.special_defense = randint(0, 31)
    
    def calculate_max_hp(self) -> int:
        return round((((self.individual_values.hp + 2 * self.pokemon.base_stats.hp +((self.effort_values.hp)/4)+100) * self.level)/100)+10)
 
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
        
    def set_position(self, position: BattlePosition):
        self.pokemon_battle_state.current_position = position

    def _get_current_position(self) -> BattlePosition:
        return self.pokemon_battle_state.current_position

    def create_move_action(self, move: str, target_position: BattlePosition = None) -> MoveAction:
        current_position = self._get_current_position()        
        # get the move object from the pokemon with name or index provided
        
            
        if not isinstance(move, str):
            raise ValueError("Move must be a the name as string")

        move_obj = self.move_set.get_move_by_name(move)
        if move_obj is None:
            raise ValueError(f"Move with name {move} not found in move set.")
        move_index = move_obj.base_move.index

        if target_position is None:
            return MoveAction(position=current_position, move_index=move_index)
        return MoveAction(position=current_position, move_index=move_index, target_position=target_position)

    def create_item_action(self, item: Item) -> UseItemAction:
        current_position = self._get_current_position()
        return UseItemAction(position=current_position, item=item)
    
    def create_switch_action(self, switch_position: BattlePosition) -> SwitchAction:
        current_position = self._get_current_position()
        return SwitchAction(position=current_position, switch_position=switch_position)

    def get_base_stat(self, stat_name: str) -> int:
        return getattr(self.pokemon.base_stats, stat_name)

    def faint_check(self) -> bool:
        return self.current_hp <= 0
    
    def force_faint(self):
        self.current_hp = 0

    def faint(self):
        # logic behind once a pokemon faints what needs to be done to it, clearing the battle state etc
        pass

    @property
    def stat_attack(self) -> int:
        return self.calculate_stat(Stat.ATTACK)
    
    @property
    def stat_defense(self) -> int:
        return self.calculate_stat(Stat.DEFENSE)
    
    @property
    def stat_special_attack(self) -> int:
        return self.calculate_stat(Stat.SPECIAL_ATTACK)

    @property
    def stat_special_defense(self) -> int:
        return self.calculate_stat(Stat.SPECIAL_DEFENSE)
    
    @property
    def stat_speed(self) -> int:
        return self.calculate_stat(Stat.SPEED)

    @property
    def is_fainted(self) -> bool:
        return self.current_hp <= 0



class PokemonTeam(BaseModel):
    pokemons: List[Pokemon] = Field(min_items=1, max_items=6)

    def get_all_pokemons(self) -> List[Pokemon]:
        return self.pokemons
    
    def get_usable_pokemons(self) -> List[Pokemon]:
        return [pokemon for pokemon in self.pokemons if not pokemon.is_fainted]
    
    def has_usable_pokemons(self) -> bool:
        return any(not pokemon.is_fainted for pokemon in self.pokemons)