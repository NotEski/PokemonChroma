from pathlib import Path
from typing import Dict, Any

from plugin_base import ToolPluginBase


class Plugin(ToolPluginBase):
    name = "pokeapi_downloader"
    version = "1.0.0"
    description = "Download and cache data from the PokeAPI"
    default_config: Dict[str, str] = {
        "database_dir": "pokeapi_database",
    }

    def setup(self, toolbox: Any) -> None:
        base = Path(__file__).resolve().parents[1]
        self.set_script_path(base / "download_pokeapi.py")
