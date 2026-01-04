from __future__ import annotations

from random import randint
from pydantic import BaseModel, Field
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

class MegaEvolution(BaseModel):
    mega_evolved_form: PokemonBase
    required_item: Optional[Item] = None

class PokemonBase(BaseModel):
    name: str
    display_name: str = Field(default="")
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

    mega_evolutions: Optional[List[MegaEvolution]] = Field(default=None)


class StatStages(BaseModel):
    # Stat Stages range from -6 to +6
    attack_stat_stage: int = Field(ge=-6, le=6, default=0)
    defense_stat_stage: int = Field(ge=-6, le=6, default=0)
    special_attack_stat_stage: int = Field(ge=-6, le=6, default=0)
    special_defense_stat_stage: int = Field(ge=-6, le=6, default=0)
    speed_stat_stage: int = Field(ge=-6, le=6, default=0)
    accuracy_stage: int = Field(ge=-6, le=6, default=0)
    evasion_stage: int = Field(ge=-6, le=6, default=0)
    critical_hit_stage: int = Field(ge=-6, le=6, default=0)

    def adjust_stat_stage(self, stat: Stat, stages: int):
        if stat == Stat.ATTACK:
            self.attack_stat_stage = max(-6, min(6, self.attack_stat_stage + stages))
        elif stat == Stat.DEFENSE:
            self.defense_stat_stage = max(-6, min(6, self.defense_stat_stage + stages))
        elif stat == Stat.SPECIAL_ATTACK:
            self.special_attack_stat_stage = max(-6, min(6, self.special_attack_stat_stage + stages))
        elif stat == Stat.SPECIAL_DEFENSE:
            self.special_defense_stat_stage = max(-6, min(6, self.special_defense_stat_stage + stages))
        elif stat == Stat.SPEED:
            self.speed_stat_stage = max(-6, min(6, self.speed_stat_stage + stages))
        elif stat == Stat.ACCURACY:
            self.accuracy_stage = max(-6, min(6, self.accuracy_stage + stages))
        elif stat == Stat.EVASION:
            self.evasion_stage = max(-6, min(6, self.evasion_stage + stages))
        elif stat == Stat.CRITICAL_HIT:
            self.critical_hit_stage = max(-6, min(6, self.critical_hit_stage + stages))


class BattleMon(BaseModel):
    """
    The BattleMon class represents a Pokémon's state during battle.
    Including almost everything that can change during battle. including BasePokemon reference for mega evolutions etc.
    """

    pokemon_reference: Optional[Pokemon] = Field(default=None)  # reference to the original Pokemon object outside of battle
    pokemon_base: Optional[PokemonBase] = Field(default=None) # editable during battle to allow for mega evolutions, terastallization, etc.

    move_set: MoveSet = Field(default_factory=MoveSet)
    current_hp: int = Field(ge=0, default=0)
    max_hp: int = Field(ge=1, default=0)

    stat_stages: StatStages = Field(default_factory=StatStages)

    
    # Battle Postion
    current_position: Optional[BattlePosition] = Field(default=None)  # (team_id, pokemon_index)

    # Status Conditions
    status_conditions: dict[StatusCondition, dict] = Field(default_factory=dict)  # e.g., "burn", "poison", etc. with turns present


    # Pokemon Battled for experience tracking
    pokemon_battled: List[BattleMon] = Field(default_factory=list)

    def __post_init__(self, **data):
        super().__init__(**data)

        # Initialize base_pokemon from pokemon_reference if not provided
        if self.pokemon_base is None and self.pokemon_reference is not None:
            self.pokemon_base = self.pokemon_reference.pokemon_base
        # Initialize move_set from pokemon_reference if not provided
        if not self.move_set.moves and self.pokemon_reference is not None:
            self.move_set = self.pokemon_reference.move_set
        # Initialize max_hp and current_hp if not provided
        if self.max_hp == 0 and self.pokemon_reference is not None:
            self.max_hp = self.pokemon_reference.max_hp
        if self.current_hp == 0:
            self.current_hp = self.max_hp


    def mutual_exclusive_status_conditions(self) -> List[StatusCondition]:
        return [status for status in self.status_conditions.keys() if status.mutual_exclusive]

    def add_status_condition(self, status: StatusCondition, status_data: dict):
        if status in self.status_conditions:
            return  # Status condition already present

        # Check for mutual exclusivity
        for mutual_status in self.mutual_exclusive_status_conditions():
            if status.name == mutual_status.name:
                return  # Do not add if a mutually exclusive status is already present
        # Add the new status condition
        new_status = status
        self.status_conditions[new_status] = status_data

    def remove_status_condition(self, status_name: str):
        status_to_remove = None
        for status in self.status_conditions.keys():
            if status.name == status_name:
                status_to_remove = status
                break
        if status_to_remove:
            del self.status_conditions[status_to_remove]

    

    def set_position(self, position: BattlePosition):
        self.current_position = position

    def calculate_max_hp(self) -> int:
        return generic_calculate_max_hp(self.pokemon_base, self.individual_values, self.effort_values, self.level)
    
    def calculate_stat(self, stat: Stat) -> int:
        return generic_calculate_stat(self.pokemon_base, self.effort_values, self.individual_values, self.nature, self.level, stat)
    
    def can_mega_evolve(self) -> bool:
        # logic to determine if the pokemon can mega evolve
        if self.pokemon_base.mega_evolutions not in (None, []) and self.pokemon_reference:
            for mega_evo in self.pokemon_base.mega_evolutions:
                if mega_evo.required_item is None:
                    return True
                if self.pokemon_reference.held_item == mega_evo.required_item:
                    return True
        return False

    def mega_evolve(self):
        if not self.can_mega_evolve():
            raise ValueError("This Pokémon cannot mega evolve at this time.")
        for mega_evo in self.pokemon_base.mega_evolutions:
            if mega_evo.required_item is None:
                self.pokemon_base = mega_evo.mega_evolved_form
            elif self.pokemon_reference.held_item == mega_evo.required_item:
                self.pokemon_base = mega_evo.mega_evolved_form
    
    def modify_stat_stage(self, stat: Stat, stages: int):
        self.stat_stages.adjust_stat_stage(stat, stages)

    def add_pokemon_battled(self, pokemon: BattleMon):
        if pokemon not in self.pokemon_battled:
            self.pokemon_battled.append(pokemon)



#region Pokemon Base Proxy Properties
    @property
    def types(self) -> List[PokemonType]:
        return self.pokemon_base.types
#endregion

#region Pokemon stats Proxy Properties
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
#endregion

#region Stat Stage Proxy Properties
    @property
    def attack_stat_stage(self) -> int:
        return self.stat_stages.attack_stat_stage
    @property
    def defense_stat_stage(self) -> int:
        return self.stat_stages.defense_stat_stage
    @property
    def special_attack_stat_stage(self) -> int:
        return self.stat_stages.special_attack_stat_stage
    @property
    def special_defense_stat_stage(self) -> int:
        return self.stat_stages.special_defense_stat_stage
    @property
    def speed_stat_stage(self) -> int:
        return self.stat_stages.speed_stat_stage
    @property
    def accuracy_stage(self) -> int:
        return self.stat_stages.accuracy_stage
    @property
    def evasion_stage(self) -> int:
        return self.stat_stages.evasion_stage
    @property
    def critical_hit_stage(self) -> int:
        return self.stat_stages.critical_hit_stage
#endregion

#region Proxy Properties to Pokemon Reference
    @property
    def abilities(self) -> PokemonAbilities:
        return self.pokemon_reference.abilities
    
    @property
    def effort_values(self) -> EffortValues:
        return self.pokemon_reference.effort_values
    
    @property
    def experience(self) -> int:
        return self.pokemon_reference.experience
    
    @property
    def friendship(self) -> int:
        return self.pokemon_reference.friendship
    
    @property
    def gender(self) -> Gender:
        return self.pokemon_reference.gender
    
    @property
    def held_item(self) -> Optional[Item]:
        return self.pokemon_reference.held_item
    
    @property
    def held_item_str(self) -> str:
        if self.held_item is None:
            return "none"
        return self.held_item.name
    
    @property
    def individual_values(self) -> IndividualValues:
        return self.pokemon_reference.individual_values
    
    @property
    def level(self) -> int:
        return self.pokemon_reference.level
    
    @property
    def nature(self) -> Nature:
        return self.pokemon_reference.nature
    
    @property
    def nickname(self) -> str:
        return self.pokemon_reference.nickname
    
    @property
    def shiny(self) -> bool:
        return self.pokemon_reference.shiny
    
    @property
    def tera_type(self) -> PokemonType:
        return self.pokemon_reference.terra_type
#endregion


class Pokemon(BaseModel):
    pokemon_base: PokemonBase
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
    # for all battle related status conditions, they should be stored in BattleMon
    external_status_condition: Optional[StatusCondition] = Field(default=None)


    battlemon: Optional[BattleMon] = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        # calc values based on personality value
        if hasattr(self, "_initialized"):
            return
        self._calc_gender()
        self._calc_nature()
        self._calc_individual_values()
        self._calc_shiny()

        self.max_hp = generic_calculate_stat(self.pokemon_base, self.effort_values, self.individual_values, self.nature, self.level, Stat.HP)
        self.current_hp = self.max_hp
        self.nickname = self.pokemon_base.name
        self.terra_type = self.pokemon_base.types[0]  # Default tera type to first type
        self._initialized = True

    def _calc_gender(self):
        if self.gender is not None:
            return
        rate = self.pokemon_base.gender_rate
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

    def _calc_shiny(self):
        if self.shiny is not None:
            return
        self.shiny = (randint(0, 8191) < 1) # 1 in 8192 chance


    def _get_current_position(self) -> BattlePosition:
        return self.battlemon.current_position


    def calculate_max_hp(self) -> int:
        return generic_calculate_max_hp(self.pokemon_base, self.individual_values, self.effort_values, self.level)
    
    def calculate_stat(self, stat: Stat) -> int:
        return generic_calculate_stat(self.pokemon_base, self.effort_values, self.individual_values, self.nature, self.level, stat)


    def create_move_action(self, move: str, target_position: BattlePosition = None) -> MoveAction:
        current_position = self._get_current_position()        
        # get the move object from the pokemon with name or index provided

        if not isinstance(move, str):
            raise ValueError("Move must be a the name as string")

        move_obj = self.move_set.get_move_by_name(move)
        if move_obj is None:
            raise ValueError(f"Move with name {move} not found in move set.")
        move_index = move_obj.index

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
        return getattr(self.pokemon_base.base_stats, stat_name)

    def faint_check(self) -> bool:
        return self.current_hp <= 0

    def force_faint(self):
        self.current_hp = 0

    def faint(self):
        # logic behind once a pokemon faints what needs to be done to it, clearing the battle state etc
        pass

    def generate_battlemon(self) -> BattleMon:
        battlemon = BattleMon(
            pokemon_reference=self,
            pokemon_base=self.pokemon_base,
            move_set=self.move_set,
            current_hp=self.current_hp,
            max_hp=self.max_hp
        )
        self.battlemon = battlemon
        return battlemon

    def level_up(self, levels: int = 1):
        self.level += levels
        self.recalculate_health()
    
    def evolve_pokemon(self, new_base_pokemon: PokemonBase):
        self.pokemon_base = new_base_pokemon
        self.recalculate_health()

    def recalculate_health(self):
        past_max_hp = self.max_hp

        # Recalculate max HP based on new base stats
        self.max_hp = round((((self.individual_values.hp + 2 * self.pokemon_base.base_stats.hp +((self.effort_values.hp)/4)+100) * self.level)/100)+10)

        # Adjust current HP proportionally
        self.current_hp = round((self.current_hp / past_max_hp) * self.max_hp)
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        # Other stats are already recalculated as needed

    def heal_full(self):
        self.current_hp = self.max_hp
        self.move_set.restore_all_pp()

    #region Pokemon stats Proxy Properties
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
    #endregion



class PokemonTeam(BaseModel):
    pokemons: List[Pokemon] = Field(min_items=1, max_items=6)

    def get_all_pokemons(self) -> List[Pokemon]:
        return self.pokemons
    
    def get_usable_pokemons(self) -> List[Pokemon]:
        return [pokemon for pokemon in self.pokemons if not pokemon.is_fainted]
    
    def has_usable_pokemons(self) -> bool:
        return any(not pokemon.is_fainted for pokemon in self.pokemons)
    


def generic_calculate_max_hp(pokemon_base: PokemonBase, individual_values: IndividualValues, effort_values: EffortValues, level: int) -> int:
    return round((((individual_values.hp + 2 * pokemon_base.base_stats.hp + ((effort_values.hp)/4)+100) * level)/100)+10)

def generic_calculate_stat(pokemon_base: PokemonBase, effort_values: EffortValues, individual_values: IndividualValues, nature: Nature, level: int, stat: Stat) -> int:
    base = getattr(pokemon_base.base_stats, stat.value)
    iv = getattr(individual_values, stat.value)
    ev = getattr(effort_values, stat.value)

    if nature.increased_stat == stat:
        nature_mult = 1.1
    elif nature.decreased_stat == stat:
        nature_mult = 0.9
    else:
        nature_mult = 1.0

    if stat.value == "hp":
        return generic_calculate_max_hp(pokemon_base, individual_values, effort_values, level)
    else:
        return round(((((2 * base + iv + (ev / 4)) * level) / 100) + 5) * nature_mult)