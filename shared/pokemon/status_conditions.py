from pydantic import BaseModel, ConfigDict, Field


class StatusCondition(BaseModel):
    model_config = ConfigDict(extra='allow')

    name: str
    display_name: str = Field(default="")
    mutual_exclusive: bool = Field(default=False) # whether this status condition is mutually exclusive with others also marked as such

    def __hash__(self):
        return hash(self.name)

    def on_inflicted(self, pokemon):
        """Called when the status condition is inflicted on a Pokémon."""
        pass

    def on_turn_start(self, pokemon):
        """Called at the start of the Pokémon's turn."""
        pass

    def on_turn_end(self, pokemon):
        """Called at the end of the Pokémon's turn."""
        pass
    
    def on_switch_out(self, pokemon):
        """Called when the Pokémon switches out."""
        pass

    def can_move(self, pokemon) -> bool:
        """Determine if the Pokémon can move this turn with this status condition."""
        return True