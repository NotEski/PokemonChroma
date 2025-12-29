from pathlib import Path
from typing import Dict, Any

from plugin_base import ToolPluginBase  # type: ignore


class Plugin(ToolPluginBase):
    name = "pokemon_data"
    version = "1.0.0"
    description = "Generate Pokemon, move, and item data from cached PokeAPI JSON"
    default_config: Dict[str, str] = {
        "source": "pokeapi_database",
        "out_pokemon": "data/pokemon",
        "out_moves": "data/moves",
        "out_items": "data/items",
    }

    def setup(self, toolbox: Any) -> None:
        base = Path(__file__).resolve().parents[1]
        self.set_script_path(base / "generate_pokemon_data.py")
