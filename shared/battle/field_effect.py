from pydantic import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shared.battle.position import BattlePosition
    from shared.pokemon.pokemon import BattleMon
    from shared.pokemon.stats import Stat

class FieldEffect(BaseModel):
    name: str
    display_name: str
    default_duration: int  # Duration in turns

    def __hash__(self):
        return hash(f"field_effect_{self.name}")

    def on_apply(self, position: "BattlePosition"):
        """Called when the field effect is applied to a position."""
        pass

    def on_remove(self, position: "BattlePosition"):
        """Called when the field effect is removed from a position."""
        pass

    def on_stat_calculation(self, pokemon: "BattleMon", stat: "Stat"):
        """Modify stat calculation for Pokémon on this position.
        i.e Trick Room effect reversing speed calculations but keeping priority intact
        """
        pass