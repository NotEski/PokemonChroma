from typing import Optional, TYPE_CHECKING
from enum import Enum
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from shared.pokemon.pokemon import BattleMon
    from shared.pokemon.move import BaseMove


class Ability(BaseModel):
    model_config = ConfigDict(extra='allow')

    name: str
    display_name: str
    description: str

    # Stat modifiers
    stat_attack_mod: float = 1.0  # Multiplier for stat modifications
    stat_defense_mod: float = 1.0
    stat_speed_mod: float = 1.0
    stat_special_attack_mod: float = 1.0
    stat_special_defense_mod: float = 1.0


    def __hash__(self):
        return hash(self.name)
    
    def on_before_move(self, pokemon: "BattleMon", move: "BaseMove", target: "BattleMon") -> Optional[bool]:
        """Called before the Pokémon uses a move."""
        return None
    
    def on_escape_attempt(self, pokemon: "BattleMon") -> Optional[bool]:
        """Called when the Pokémon attempts to escape from battle. for Eevee Run Away ability"""
        return None
    
    def on_enemy_escape_attempt(self, pokemon: "BattleMon") -> Optional[bool]:
        """Called when an enemy Pokémon attempts to escape from battle."""
        return None

    def on_switch_in(self, pokemon: "BattleMon") -> None:
        """Called when the Pokémon switches in."""
        pass

    def on_switch_out(self, pokemon: "BattleMon") -> None:
        """Called when the Pokémon switches out."""
        pass

    def on_faint(self, pokemon: "BattleMon") -> None:
        """Called when the Pokémon faints."""
        pass

    def on_damage_taken(self, pokemon: "BattleMon", damage: int) -> Optional[int]:
        """Called when the Pokémon takes damage."""
        return None
    
    def on_contact(self, pokemon: "BattleMon", attacker: "BattleMon") -> None:
        """Called when the Pokémon is hit by a contact move."""
        pass

    def accuracy_modifier(self, user: "BattleMon", opponent: "BattleMon", move: "BaseMove") -> float:
        """Modify the accuracy of moves used by the Pokémon."""
        return 1.0
    


class AbilitySlot(Enum):
    PRIMARY = 1
    SECONDARY = 2
    HIDDEN = 3

class PokemonBaseAbility(BaseModel):
    ability: Ability
    is_hidden: bool = False
    slot: AbilitySlot

# TODO, abliity management system need to be updated cause a list doesnt make sense for ability slot to have one
class PokemonAbilities(BaseModel):
    abilities: dict[Ability, bool] = {
    }
    slots: dict[AbilitySlot, Optional[Ability]] = {
        AbilitySlot.PRIMARY: None,
        AbilitySlot.SECONDARY: None,
        AbilitySlot.HIDDEN: None
    }
    
    def list_abilities_by_slot(self) -> dict[AbilitySlot, Ability|None]:
        return {
            AbilitySlot.PRIMARY: self.primary,
            AbilitySlot.SECONDARY: self.secondary,
            AbilitySlot.HIDDEN: self.hidden
        }

    def reset_ability_active_states(self):
        if self.primary:
            self.abilities[self.primary] = True
        if self.secondary:
            self.abilities[self.secondary] = True
        if self.hidden:
            self.abilities[self.hidden] = True

    def activate_ability(self, slot: AbilitySlot):
        if slot == AbilitySlot.PRIMARY and self.primary:
            self.abilities[self.primary] = True
        elif slot == AbilitySlot.SECONDARY and self.secondary:
            self.abilities[self.secondary] = True
        elif slot == AbilitySlot.HIDDEN and self.hidden:
            self.abilities[self.hidden] = True
        
    def deactivate_ability(self, slot: AbilitySlot):
        if slot == AbilitySlot.PRIMARY and self.primary:
            self.abilities[self.primary] = False
        elif slot == AbilitySlot.SECONDARY and self.secondary:
            self.abilities[self.secondary] = False
        elif slot == AbilitySlot.HIDDEN and self.hidden:
            self.abilities[self.hidden] = False

    def get_ability_by_slot(self, slot: AbilitySlot) -> Optional[Ability]:
        return self.slots.get(slot)

    def get_all_abilities(self) -> list[Ability]:
        return list(self.abilities.keys())

    def get_all_active_abilities(self) -> list[Ability]:
        active_abilities: list[Ability] = []
        for ability, is_active in self.abilities.items():
            if is_active:
                active_abilities.append(ability)
        return active_abilities

    def has_ability(self, ability_name: str) -> bool:
        abilities = self.list_abilities_by_slot().values()
        for ability in abilities:
            if not ability: continue
            if ability.name.lower() == ability_name.lower():
                return True
        return False

    def has_active_ability(self, ability_name: str) -> bool:
        abilities = self.list_abilities_by_slot().values()
        for ability in abilities:
            if not ability: continue
            if ability.name.lower() == ability_name.lower():
                if self.abilities.get(ability):
                    return True
        return False

    def has_any_ability(self, ability_names: list[str]) -> bool:
        for ability in ability_names:
            if self.has_ability(ability):
                return True
        return False

    @property
    def primary(self) -> Optional[Ability]:
        return self.slots.get(AbilitySlot.PRIMARY)
    
    @primary.setter
    def primary(self, value: Optional[Ability]):
        if self.primary:
            del self.abilities[self.primary]
        if value is None:
            self.slots[AbilitySlot.PRIMARY] = None
            return
        self.slots[AbilitySlot.PRIMARY] = value
        self.abilities[value] = True
        
    
    @property
    def secondary(self) -> Optional[Ability]:
        return self.slots.get(AbilitySlot.SECONDARY)
    
    @secondary.setter
    def secondary(self, value: Optional[Ability]):
        if self.secondary:
            del self.abilities[self.secondary]
        if value is None:
            self.slots[AbilitySlot.SECONDARY] = None
            return
        self.slots[AbilitySlot.SECONDARY] = value
        self.abilities[value] = True
    
    @property
    def hidden(self) -> Optional[Ability]:
        return self.slots.get(AbilitySlot.HIDDEN)
    
    @hidden.setter
    def hidden(self, value: Optional[Ability]):
        if self.hidden:
            del self.abilities[self.hidden]
        if value is None:
            self.slots[AbilitySlot.HIDDEN] = None
            return
        self.slots[AbilitySlot.HIDDEN] = value
        self.abilities[value] = True