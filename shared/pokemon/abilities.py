from typing import Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict

class Ability(BaseModel):
    model_config = ConfigDict(extra='allow')

    name: str
    display_name: str
    description: str

    def __hash__(self):
        return hash(self.name)
    
    def on_modify_attack(self, pokemon, move, target) -> Optional[int]:
        """Modify the attack stat of the Pokémon."""
        return None
    
    def on_modify_defense(self, pokemon, move, target) -> Optional[int]:
        """Modify the defense stat of the Pokémon."""
        return None
    
    def on_modify_speed(self, pokemon, move, target) -> Optional[int]:
        """Modify the speed stat of the Pokémon."""
        return None
    
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
    


class AbilitySlot(Enum):
    PRIMARY = 1
    SECONDARY = 2
    HIDDEN = 3

class PokemonBaseAbility(BaseModel):
    ability: Ability
    is_hidden: bool = False
    slot: AbilitySlot

class PokemonAbilities(BaseModel):
    primary: Optional[Ability] = None
    secondary: Optional[Ability] = None
    hidden: Optional[Ability] = None

    def update_ability_slot(self, slot: AbilitySlot, ability: Ability):
        if slot == AbilitySlot.PRIMARY:
            self.primary = ability
        elif slot == AbilitySlot.SECONDARY:
            self.secondary = ability
        elif slot == AbilitySlot.HIDDEN:
            self.hidden = ability
        else:
            raise ValueError(f"Invalid ability slot: {slot}")
    
    def get_ability_by_slot(self, slot: AbilitySlot) -> Optional[Ability]:
        if slot == AbilitySlot.PRIMARY:
            return self.primary
        elif slot == AbilitySlot.SECONDARY:
            return self.secondary
        elif slot == AbilitySlot.HIDDEN:
            return self.hidden
        else:
            return None
    
    def list_abilities(self) -> dict:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "hidden": self.hidden
        }
    
    def has_ability(self, ability_name: str) -> bool:
        for ability in self.list_abilities().values():
            if ability and ability.name.lower() == ability_name.lower():
                return True
        return False
    
    def has_any_ability(self, ability_names: list[str]) -> bool:
        for ability in ability_names:
            if self.has_ability(ability):
                return True