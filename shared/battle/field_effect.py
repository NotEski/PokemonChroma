from pydantic import BaseModel, Field

class FieldEffect(BaseModel):
    name: str
    display_name: str
    default_duration: int  # Duration in turns

    def __hash__(self):
        return hash(f"field_effect_{self.name}")

    def on_apply(self, position):
        """Called when the field effect is applied to a position."""
        pass

    def on_remove(self, position):
        """Called when the field effect is removed from a position."""
        pass

    def on_stat_calculation(self, pokemon, stat):
        """Modify stat calculation for Pokémon on this position.
        i.e Trick Room effect reversing speed calculations but keeping priority intact
        """
        pass