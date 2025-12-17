from pathlib import Path
from typing import Dict, List, Optional, Any

from run_script import run_script


class ToolPluginBase:
    name: str = "unnamed"
    version: str = "0.0.0"
    description: str = ""
    default_config: Dict[str, str] = {}

    def __init__(self) -> None:
        self._script_path: Optional[Path] = None

    def setup(self, toolbox: Any) -> None:
        # Optional initialization hook
        pass

    @property
    def script_path(self) -> Optional[Path]:
        return self._script_path

    def set_script_path(self, p: Path) -> None:
        self._script_path = p

    def run(self, args: List[str], config: Dict[str, str], toolbox: Any) -> int:
        if not self._script_path:
            raise RuntimeError("Plugin has no script path set")
        return int(run_script(self._script_path, args))
