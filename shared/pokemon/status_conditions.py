from pydantic import BaseModel, ConfigDict, Field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from shared.pokemon.pokemon import BattleMon


class StatusCondition(BaseModel):
    model_config = ConfigDict(extra='allow')

    name: str
    display_name: str = Field(default="")
    mutual_exclusive: bool = Field(default=False) # whether this status condition is mutually exclusive with others also marked as such
    default_data: dict[str, Any] = Field(default_factory=dict)  # Default data associated with the status condition

    def __hash__(self):
        return hash(self.name)

    def on_inflicted(self, pokemon: "BattleMon"):
        """Called when the status condition is inflicted on a Pokémon."""
        pass

    def on_turn_start(self, pokemon: "BattleMon"):
        """Called at the start of the Pokémon's turn."""
        pass

    def on_turn_end(self, pokemon: "BattleMon"):
        """Called at the end of the Pokémon's turn."""
        pass
    
    def on_switch_out(self, pokemon: "BattleMon"):
        """Called when the Pokémon switches out."""
        pass

    def can_move(self, pokemon: "BattleMon") -> bool:
        """Determine if the Pokémon can move this turn with this status condition."""
        return True