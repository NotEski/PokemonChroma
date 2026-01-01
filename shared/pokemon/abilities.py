from typing import Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict

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
    
    def on_before_move(self, pokemon, move, target) -> Optional[bool]:
        """Called before the Pokémon uses a move."""
        return None
    
    def on_escape_attempt(self, pokemon) -> Optional[bool]:
        """Called when the Pokémon attempts to escape from battle. for Eevee Run Away ability"""
        return None
    
    def on_enemy_escape_attempt(self, pokemon) -> Optional[bool]:
        """Called when an enemy Pokémon attempts to escape from battle."""
        return None

    def on_switch_in(self, pokemon) -> None:
        """Called when the Pokémon switches in."""
        pass

    def on_switch_out(self, pokemon) -> None:
        """Called when the Pokémon switches out."""
        pass

    def on_faint(self, pokemon) -> None:
        """Called when the Pokémon faints."""
        pass

    def on_damage_taken(self, pokemon, damage) -> Optional[int]:
        """Called when the Pokémon takes damage."""
        return None
    
    def on_contact(self, pokemon, attacker) -> None:
        """Called when the Pokémon is hit by a contact move."""
        pass

    def accuracy_modifier(self, user, opponent, move) -> float:
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

class PokemonAbilities(BaseModel):
    primary: Optional[list[Ability, bool]] = None
    secondary: Optional[list[Ability, bool]] = None
    hidden: Optional[list[Ability, bool]] = None

    def update_ability_slot(self, slot: AbilitySlot, ability: Ability, active: bool = True):
        if slot == AbilitySlot.PRIMARY:
            self.primary = [ability, active]
        elif slot == AbilitySlot.SECONDARY:
            self.secondary = [ability, active]
        elif slot == AbilitySlot.HIDDEN:
            self.hidden = [ability, active]
        else:
            raise ValueError(f"Invalid ability slot: {slot}")
    
    def reset_ability_active_states(self):
        if self.primary:
            self.primary[1] = True
        if self.secondary:
            self.secondary[1] = True
        if self.hidden:
            self.hidden[1] = True

    def activate_ability(self, slot: AbilitySlot):
        if slot == AbilitySlot.PRIMARY and self.primary:
            self.primary[1] = True
        elif slot == AbilitySlot.SECONDARY and self.secondary:
            self.secondary[1] = True
        elif slot == AbilitySlot.HIDDEN and self.hidden:
            self.hidden[1] = True
        
    def deactivate_ability(self, slot: AbilitySlot):
        if slot == AbilitySlot.PRIMARY and self.primary:
            self.primary[1] = False
        elif slot == AbilitySlot.SECONDARY and self.secondary:
            self.secondary[1] = False
        elif slot == AbilitySlot.HIDDEN and self.hidden:
            self.hidden[1] = False

    def get_ability_by_slot(self, slot: AbilitySlot) -> Optional[Ability]:
        if slot == AbilitySlot.PRIMARY:
            return self.primary[0]
        elif slot == AbilitySlot.SECONDARY:
            return self.secondary[0]
        elif slot == AbilitySlot.HIDDEN:
            return self.hidden[0]
        else:
            return None

    def get_all_abilities(self) -> list[Ability]:
        all_abilities = []
        for ability in self.list_abilities_by_slot().values():
            if ability:
                all_abilities.append(ability[0])
        return all_abilities

    def get_all_active_abilities(self) -> list[Ability]:
        active_abilities = []
        for ability in self.list_abilities_by_slot().values():
            if ability and ability[1]:  # Check if ability is active
                active_abilities.append(ability[0])
        return active_abilities

    def list_abilities_by_slot(self) -> dict:
        return {
            AbilitySlot.PRIMARY: self.primary,
            AbilitySlot.SECONDARY: self.secondary,
            AbilitySlot.HIDDEN: self.hidden
        }

    def has_ability(self, ability_name: str) -> bool:
        for ability in self.list_abilities_by_slot().values():
            if ability and ability[0].name.lower() == ability_name.lower():
                return True
        return False

    def has_active_ability(self, ability_name: str) -> bool:
        for ability in self.list_abilities_by_slot().values():
            if ability and ability[0].name.lower() == ability_name.lower() and ability[1]:
                return True
        return False

    def has_any_ability(self, ability_names: list[str]) -> bool:
        for ability in ability_names:
            if self.has_ability(ability):
                return True

    @property
    def primary_ability(self) -> Optional[Ability]:
        if self.primary:
            return self.primary[0]
        return None
    
    @property
    def secondary_ability(self) -> Optional[Ability]:
        if self.secondary:
            return self.secondary[0]
        return None
    
    @property
    def hidden_ability(self) -> Optional[Ability]:
        if self.hidden:
            return self.hidden[0]
        return None