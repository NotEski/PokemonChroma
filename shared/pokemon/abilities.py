from typing import Optional
from enum import Enum
from pydantic import BaseModel

class Ability(BaseModel):
    name: str
    name_readable: str
    description: str

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