from pydantic import BaseModel, ConfigDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shared.pokemon.pokemon import BattleMon

class EntryHazard(BaseModel):
    model_config = ConfigDict(extra='allow')

    name: str
    display_name: str

    def __hash__(self):
        return hash(f"entry_hazard_{self.name}")

    def on_entry(self, pokemon: "BattleMon", layer_count: int):
        # Implement hazard effects on the entering Pokémon on this position
        pass