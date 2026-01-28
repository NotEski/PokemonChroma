from __future__ import annotations

from random import randint
import uuid
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from enum import Enum

from .pokemon_types import PokemonType
from .move import MoveSet, BaseMove, LearnSet
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
    name: str = Field(default="none")
    display_name: str = Field(default="None")
    types: List[PokemonType] = []
    base_stats: BaseStats
    pokedex_number: int
    ev_yield: EffortYield = Field(default_factory=EffortYield)
    abilities: list[PokemonBaseAbility] = []

    base_experience_yield: int = Field(default=64)
    gender_rate: GenderRate = Field(default=GenderRate.EQUAL)
    capture_rate: int = Field(ge=0, le=255, default=45)
    base_happiness: int = Field(ge=0, le=255, default=70)
    growth_rate: GrowthRate = Field(default=GrowthRate.MEDIUM)
    egg_groups: List[EggGroup] = []

    height: float = Field(ge=0.0, default=1.0)  # in meters
    weight: float = Field(ge=0.0, default=1.0)  # in kilograms

    mega_evolutions: List[MegaEvolution] = []

    learnset: LearnSet = Field(default_factory=LearnSet)

    model_config = {"frozen": True}


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
    
    @property
    def total(self) -> int:
        return (
            self.attack_stat_stage +
            self.defense_stat_stage +
            self.special_attack_stat_stage +
            self.special_defense_stat_stage +
            self.speed_stat_stage +
            self.accuracy_stage +
            self.evasion_stage +
            self.critical_hit_stage
        )
    
    @property
    def to_dict(self) -> Dict[str, int]:
        return {
            "attack": self.attack_stat_stage,
            "defense": self.defense_stat_stage,
            "special_attack": self.special_attack_stat_stage,
            "special_defense": self.special_defense_stat_stage,
            "speed": self.speed_stat_stage,
            "accuracy": self.accuracy_stage,
            "evasion": self.evasion_stage,
            "critical_hit": self.critical_hit_stage,
        }


class BattleMonBattleState(BaseModel):
    # Stat Stages
    stat_stages: StatStages = Field(default_factory=StatStages)
    
    # Status Conditions
    status_conditions: dict[StatusCondition, dict[str, Any]] = {}  # e.g., "burn", "poison", etc. with turns present

    # Extra and Excluded Types added from moves, items, abilities, etc.
    extra_types: List[PokemonType] = []
    excluded_types: List[PokemonType] = []

    # Turns in battle
    turns_in_battle: int = Field(ge=0, default=0)

    # Flinch next turn
    flinch_next_turn: bool = Field(default=False)

    # Disabled Moves
    disabled_moves: Dict[int, int] = {}  # list of move indices that are disabled and the remaining turns they are disabled for

    # Previously Used Moves
    last_used_moves: List[BaseMove] = []

    damage_taken_this_turn: int = Field(ge=0, default=0)
    last_damage_taken: int = Field(ge=0, default=0)


class BattleMon(BaseModel):
    """
    The BattleMon class represents a Pokémon's state during battle.
    Including almost everything that can change during battle. including BasePokemon reference for mega evolutions etc.
    """

    pokemon_reference: Pokemon  # reference to the original Pokemon object outside of battle
    pokemon_base: PokemonBase # editable during battle to allow for mega evolutions, terastallization, etc.

    move_set: MoveSet = Field(default_factory=MoveSet)
    current_hp: int = Field(ge=0, default=0)
    max_hp: int = Field(ge=1, default=0)

    battle_state: BattleMonBattleState = Field(default_factory=BattleMonBattleState)
    
    # Battle Postion
    current_position: Optional[BattlePosition] = None  # (team_id, pokemon_index)

    # Pokemon Battled for experience tracking
    pokemon_battled: List[BattleMon] = []

    def __post_init__(self, pokemon_base: PokemonBase = None, **data): # type: ignore
        super().__init__(**data)

        # Initialize base_pokemon from pokemon_reference if not provided
        if not pokemon_base:
            self.pokemon_base = self.pokemon_reference.pokemon_base
        else:
            self.pokemon_base = pokemon_base

        # Initialize move_set from pokemon_reference if not provided
        if not self.move_set.moves:
            self.move_set = self.pokemon_reference.move_set
        # Initialize max_hp and current_hp if not provided
        if self.max_hp == 0:
            self.max_hp = self.pokemon_reference.max_hp
        if self.current_hp == 0:
            self.current_hp = self.max_hp


    def mutual_exclusive_status_conditions(self) -> List[StatusCondition]:
        return [status for status in self.status_conditions.keys() if status.mutual_exclusive]

    def add_status_condition(self, status: StatusCondition, status_data: dict[str, Any]):
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

    def add_extra_type(self, pokemon_type: PokemonType):
        if pokemon_type not in self.extra_types:
            self.extra_types.append(pokemon_type)

    def remove_type(self, pokemon_type: PokemonType):
        if pokemon_type in self.extra_types:
            self.extra_types.remove(pokemon_type)
        elif pokemon_type not in self.excluded_types:
            self.excluded_types.append(pokemon_type)

    def disable_move(self, move_index: int, turns: int):
        self.disabled_moves[move_index] = turns

    def add_previous_move_used(self, move: BaseMove):
        self.battle_state.last_used_moves.append(move)

    def get_move_slot(self, move: BaseMove) -> Optional[int]:
        for index, m in enumerate(self.move_set.moves):
            if m == move:
                return index
        return None

    def has_type(self, pokemon_type: str | PokemonType) -> bool:
        return pokemon_type in self.types
    
    def has_ability(self, ability_name: str) -> bool:
        for ability in self.abilities.abilities:
            if ability.name.lower() == ability_name.lower():
                return True
        return False
    
    def apply_status(self, status_condition: StatusCondition):
        # logic to apply status condition to the pokemon
        if status_condition in self.status_conditions:
            return  # Already has the status condition
        self.add_status_condition(status_condition, status_condition.default_data_factory())

    def take_damage(self, damage: int):
        self.current_hp = max(0, self.current_hp - damage)

        

#region BattleState Proxy Properties
    @property
    def stat_stages(self) -> StatStages:
        return self.battle_state.stat_stages
    @stat_stages.setter
    def stat_stages(self, value: StatStages):
        self.battle_state.stat_stages = value
    @property
    def status_conditions(self) -> dict[StatusCondition, dict[str, Any]]:
        return self.battle_state.status_conditions
    @property
    def extra_types(self) -> List[PokemonType]:
        return self.battle_state.extra_types
    @property
    def excluded_types(self) -> List[PokemonType]:
        return self.battle_state.excluded_types
    @property
    def turns_in_battle(self) -> int:
        return self.battle_state.turns_in_battle
    @turns_in_battle.setter
    def turns_in_battle(self, value: int):
        self.battle_state.turns_in_battle = value
    @property
    def flinch_next_turn(self) -> bool:
        return self.battle_state.flinch_next_turn
    @flinch_next_turn.setter
    def flinch_next_turn(self, value: bool):
        self.battle_state.flinch_next_turn = value
    @property
    def previous_move_used(self) -> Optional[BaseMove]:
        return self.battle_state.last_used_moves[-1] if self.battle_state.last_used_moves else None
    @previous_move_used.setter
    def previous_move_used(self, value: BaseMove):
        self.battle_state.last_used_moves.append(value)
    @property
    def last_damage_taken(self) -> int:
        return self.battle_state.last_damage_taken
    @last_damage_taken.setter
    def last_damage_taken(self, value: int):
        self.battle_state.last_damage_taken = value
    @property
    def disabled_moves(self) -> dict[int, int]:
        return self.battle_state.disabled_moves
    @disabled_moves.setter
    def disabled_moves(self, value: dict[int, int]):
        self.battle_state.disabled_moves = value
#endregion

#region Pokemon Base Proxy Properties
    @property
    def types(self) -> List[PokemonType]:
        all_types: list[PokemonType] = []

        all_types.extend(self.pokemon_base.types)
        all_types.extend(self.extra_types)
        for excluded_type in self.excluded_types:
            if excluded_type in all_types:
                all_types.remove(excluded_type)
        return all_types
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
    def id(self) -> uuid.UUID:
        return self.pokemon_reference.id

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
    @held_item.setter
    def held_item(self, value: Optional[Item]):
        self.pokemon_reference.held_item = value
    
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
    def terra_type(self) -> PokemonType:
        # This will need to be updated to be changeable to the specific pokemon from the use of
        # terra shards to change the terra type of the pokemon and will need to be stored in the Pokemon class
        return self.pokemon_reference.terra_type
#endregion


class Pokemon(BaseModel):
    pokemon_base: PokemonBase
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    nickname: str = Field(default="")
    level: int = Field(ge=1, le=100, default=1)
    current_hp: int = Field(ge=0, default=0)
    max_hp: int = Field(ge=1, default=0)
    shiny: bool = Field(default=False)
    gender: Gender = Field(default=Gender.NONE)
    individual_values: IndividualValues = Field(default_factory=IndividualValues)
    effort_values: EffortValues = Field(default_factory=EffortValues)
    terra_type: PokemonType = Field(default=PokemonType("normal"))
    nature: Nature = Field(default=Nature.HARDY)
    move_set: MoveSet = Field(default_factory=MoveSet)
    abilities: PokemonAbilities = Field(default_factory=PokemonAbilities)
    friendship: int = Field(ge=0, le=255, default=70)
    experience: int = Field(ge=0, default=0)
    held_item: Optional[Item] = Field(default=None)


    # NOTE FOR OUTSIDE OF BATTLE ONLY
    # for all battle related status conditions, they should be stored in BattleMon
    external_status_condition: Optional[StatusCondition] = Field(default=None)

    battlemon: Optional[BattleMon] = Field(default=None)

    def __init__(self, generate=True, **data): # type: ignore
        super().__init__(**data)
        # calc values based on personality value
        if hasattr(self, "_initialized"):
            return
        if generate:
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
        rate = self.pokemon_base.gender_rate
        if rate == GenderRate.GENDERLESS:
            self.gender = Gender.NONE
            return
        self.gender = Gender.MALE if randint(0, 7) <= rate.value else Gender.FEMALE

    def _calc_nature(self):
        nature_index = randint(0, 24)
        self.nature = Nature(list(Nature)[nature_index])

    def _calc_individual_values(self):
        self.individual_values = IndividualValues()

        self.individual_values.hp = randint(0, 31)
        self.individual_values.attack = randint(0, 31)
        self.individual_values.defense = randint(0, 31)
        self.individual_values.speed = randint(0, 31)
        self.individual_values.special_attack = randint(0, 31)
        self.individual_values.special_defense = randint(0, 31)

    def _calc_shiny(self):
        self.shiny = (randint(0, 8191) < 1) # 1 in 8192 chance


    def get_current_position(self) -> Optional[BattlePosition]:
        if self.battlemon is None:
            return None
        return self.battlemon.current_position


    def calculate_max_hp(self) -> int:
        return generic_calculate_max_hp(self.pokemon_base, self.individual_values, self.effort_values, self.level)
    
    def calculate_stat(self, stat: Stat) -> int:
        return generic_calculate_stat(self.pokemon_base, self.effort_values, self.individual_values, self.nature, self.level, stat)


    def create_move_action(self, move: str, target_position: Optional[BattlePosition] = None) -> MoveAction:
        current_position = self.get_current_position()
        if current_position is None:
            raise ValueError("Pokemon is not currently in a battle position.")
        # get the move object from the pokemon with name or index provided

        if not isinstance(move, str): # type: ignore - Sanity check
            raise ValueError("Move must be a the name as string")

        move_obj = self.move_set.get_move_by_name(move)
        if move_obj is None:
            raise ValueError(f"Move with name {move} not found in move set.")
        move_index = move_obj.index

        if target_position is None:
            raise ValueError("Target position must be provided for move action.")
            # return MoveAction(position=current_position, move_index=move_index)
        return MoveAction(position=current_position, move_index=move_index, target_position=target_position)

    def create_item_action(self, item: Item) -> UseItemAction:
        current_position = self.get_current_position()
        if current_position is None:
            raise ValueError("Pokemon is not currently in a battle position.")
        return UseItemAction(position=current_position, item_name=item.name)

    def create_switch_action(self, switch_position: BattlePosition) -> SwitchAction:
        current_position = self.get_current_position()
        if current_position is None:
            raise ValueError("Pokemon is not currently in a battle position.")
        return SwitchAction(position=current_position, switch_in_pokemon_index=switch_position.pokemon_index)

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

    @property
    def name(self) -> str:
        return self.nickname if self.nickname else self.pokemon_base.name

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
    def get_terra_type(self) -> PokemonType:
        return self.terra_type

    @property
    def is_fainted(self) -> bool:
        return self.current_hp <= 0
    #endregion



class PokemonTeam(BaseModel):
    pokemons: List[Pokemon] = Field(min_items=1, max_items=6, default=[]) # pyright: ignore

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