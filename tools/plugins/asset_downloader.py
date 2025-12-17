from pathlib import Path
from typing import Dict, List, Any

from plugin_base import ToolPluginBase


class Plugin(ToolPluginBase):
    name = "asset_downloader"
    version = "1.0.0"
    description = "Download and manage Pokemon asset images and metadata"
    default_config: Dict[str, str] = {
        "output_dir": "assets",
        "concurrency": "4",
    }

    def setup(self, toolbox: Any) -> None:
        # Set path to underlying script
        # tools/download_assets.py
        from pathlib import Path
        import sys
        # Compute path relative to this file: ../../download_assets.py
        base = Path(__file__).resolve().parents[1]
        self.set_script_path(base / "download_assets.py")

    # Inherit run() which forwards args to underlying script
