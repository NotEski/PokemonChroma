from pathlib import Path
from typing import Dict, Any

from plugin_base import ToolPluginBase #type: ignore


class Plugin(ToolPluginBase):
    name = "type_chart"
    version = "1.0.0"
    description = "Generate type effectiveness chart"
    default_config: Dict[str, str] = {
        "output": "engine/type_chart.json",
    }

    def setup(self, toolbox: Any) -> None:
        base = Path(__file__).resolve().parents[1]
        self.set_script_path(base / "generate_type_chart.py")
