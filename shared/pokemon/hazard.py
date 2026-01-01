from pydantic import BaseModel, ConfigDict

class EntryHazard(BaseModel):
    model_config = ConfigDict(extra='allow')

    name: str
    display_name: str

    def __hash__(self):
        return hash(f"entry_hazard_{self.name}")

    def on_entry(self, pokemon, layer_count: int):
        # Implement hazard effects on the entering Pokémon on this position
        pass