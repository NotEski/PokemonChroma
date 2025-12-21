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