from pydantic import BaseModel, Field


class StatusCondition(BaseModel):
    name: str
    display_name: str = Field(default="")
    mutual_exclusive: bool = Field(default=False) # whether this status condition is mutually exclusive with others also marked as such

    def on_turn_end(self):
        """Called at the end of the Pokémon's turn."""
        return None
    
    def on_switch_out(self):
        """Called when the Pokémon switches out."""
        return None