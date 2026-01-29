"""Asset downloader plugin with GUI support."""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import requests

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase

# Sprite types to download from Generation V Black/White
GEN5_SPRITE_TYPES = [
    "front_default",
    "back_default",
    "front_shiny",
    "back_shiny",
    "front_female",
    "back_female",
    "front_shiny_female",
    "back_shiny_female",
]


class PokemonAssetDownloader:
    """Downloads Pokemon sprites, animations, and cries from PokeAPI data."""

    def __init__(
        self,
        pokeapi_dir: Union[str, Path] = "pokeapi_database/pokemon",
        output_dir: Union[str, Path] = "assets",
        verbose: bool = True,
    ):
        self.pokeapi_dir = Path(pokeapi_dir)
        self.output_dir = Path(output_dir)
        self.pokemon_root = (
            self.output_dir
            if self.output_dir.name.lower() == "pokemon"
            else self.output_dir / "pokemon"
        )
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Pokemon-Asset-Downloader/1.0"})

    def _print(self, message: str) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(message)

    def _get_pokemon_data(self, pokemon_file: Path) -> Optional[Dict[str, Any]]:
        """Load Pokemon data from JSON file."""
        try:
            with open(pokemon_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self._print(f"Error loading {pokemon_file.name}: {e}")
            return None

    def _download_file(self, url: str, output_path: Path) -> bool:
        """Download a file from URL to output path."""
        try:
            if output_path.exists():
                return True

            output_path.parent.mkdir(parents=True, exist_ok=True)

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

            return True
        except Exception as e:
            self._print(f"  Error downloading {url}: {e}")
            return False

    def _extract_sprite_urls(self, pokemon_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract Generation V sprite URLs from Pokemon data."""
        sprites: Dict[str, str] = {}
        sprite_data = pokemon_data.get("sprites", {})

        versions = sprite_data.get("versions", {})
        gen5 = versions.get("generation-v", {})
        black_white = gen5.get("black-white", {})

        animated = black_white.get("animated", {})
        for sprite_type in GEN5_SPRITE_TYPES:
            url = animated.get(sprite_type)
            if url:
                sprite_name = f"animated_{sprite_type}"
                sprites[sprite_name] = url

        return sprites

    def _extract_cry_urls(self, pokemon_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract cry URLs from Pokemon data."""
        cries: Dict[str, str] = {}
        cry_data = pokemon_data.get("cries", {})

        for cry_type, url in cry_data.items():
            if url:
                cries[cry_type] = url

        return cries

    def _get_pokemon_identifier(
        self, pokemon_data: Dict[str, Any]
    ) -> Tuple[int, str]:
        """Get Pokemon ID and name from data."""
        pokemon_id = pokemon_data.get("id", 0)
        pokemon_name = pokemon_data.get("name", "unknown")
        return pokemon_id, pokemon_name

    def download_pokemon_assets(
        self, pokemon_file: Path, skip_existing: bool = True
    ) -> Dict[str, int]:
        """Download all assets for a single Pokemon."""
        stats = {
            "sprites_downloaded": 0,
            "sprites_failed": 0,
            "cries_downloaded": 0,
            "cries_failed": 0,
        }

        pokemon_data = self._get_pokemon_data(pokemon_file)
        if not pokemon_data:
            return stats

        pokemon_id, pokemon_name = self._get_pokemon_identifier(pokemon_data)

        pokemon_dir = self.pokemon_root / f"{pokemon_id:04d}-{pokemon_name.capitalize()}"

        self._print(f"Processing: {pokemon_id:04d} - {pokemon_name.capitalize()}")

        sprite_urls = self._extract_sprite_urls(pokemon_data)
        cry_urls = self._extract_cry_urls(pokemon_data)

        for sprite_name, url in sprite_urls.items():
            sprite_path = pokemon_dir / f"{sprite_name}.png"
            if self._download_file(url, sprite_path):
                stats["sprites_downloaded"] += 1
            else:
                stats["sprites_failed"] += 1

        for cry_name, url in cry_urls.items():
            cry_path = pokemon_dir / f"cry_{cry_name}.ogg"
            if self._download_file(url, cry_path):
                stats["cries_downloaded"] += 1
            else:
                stats["cries_failed"] += 1

        return stats

    def download_range(self, start_id: int, end_id: int) -> None:
        """Download assets for a range of Pokemon."""
        self._print(f"Downloading assets for Pokemon {start_id}-{end_id}")

        for pokemon_id in range(start_id, end_id + 1):
            for pokemon_file in self.pokeapi_dir.glob(f"{pokemon_id:04d}-*.json"):
                self.download_pokemon_assets(pokemon_file)

        self._print("Download complete!")

    def download_all(self) -> None:
        """Download assets for all Pokemon."""
        self._print("Downloading assets for all Pokemon")

        pokemon_files = sorted(self.pokeapi_dir.glob("*.json"))
        for pokemon_file in pokemon_files:
            self.download_pokemon_assets(pokemon_file)

        self._print("Download complete!")

    def download_by_names(self, names: List[str]) -> None:
        """Download assets for specific Pokemon by name."""
        self._print(f"Downloading assets for: {', '.join(names)}")

        for name in names:
            for pokemon_file in self.pokeapi_dir.glob(f"*-{name}.json"):
                self.download_pokemon_assets(pokemon_file)

        self._print("Download complete!")


class Plugin(ToolPluginBase):
    """Plugin for downloading Pokemon sprites and cries."""

    name = "asset_downloader"
    version = "1.0.0"
    description = "Download and manage Pokemon asset images and metadata"
    default_config: Dict[str, str] = {
        "output_dir": "assets",
        "concurrency": "4",
    }

    def setup(self, toolbox: Any) -> None:
        """Initialize the plugin."""
        # No external script needed - logic is embedded

    def get_form_fields(self) -> List[FormFieldSpec]:
        """Get form field specifications."""
        return [
            FormFieldSpec(
                name="mode",
                label="Download Mode",
                field_type="combobox",
                choices=["Range", "Names", "All"],
                default="Range",
                required=True,
                help_text="How to select Pokemon to download",
            ),
            FormFieldSpec(
                name="start_id",
                label="Start ID",
                field_type="spinbox",
                default="1",
                help_text="Starting Pokemon ID (for Range mode)",
            ),
            FormFieldSpec(
                name="end_id",
                label="End ID",
                field_type="spinbox",
                default="151",
                help_text="Ending Pokemon ID (for Range mode)",
            ),
            FormFieldSpec(
                name="names",
                label="Pokemon Names",
                field_type="text",
                default="",
                help_text="Comma-separated names (for Names mode)",
            ),
            FormFieldSpec(
                name="output_dir",
                label="Output Directory",
                field_type="directory",
                default=self.default_config["output_dir"],
                required=True,
            ),
            FormFieldSpec(
                name="quiet",
                label="Quiet Mode",
                field_type="checkbox",
                default=False,
                help_text="Suppress progress output",
            ),
        ]

    def create_ui(
        self, parent: tk.Frame, config: Dict[str, str], on_execute: Callable[[], None]
    ) -> tk.Frame:
        """Create the plugin's GUI interface."""
        frame = tk.Frame(parent)
        
        # Description
        desc = ttk.Label(
            frame,
            text=self.description,
            wraplength=700,
            font=("TkDefaultFont", 10, "bold"),
        )
        desc.pack(pady=10)
        
        # Form
        form_frame = tk.Frame(frame)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        form_frame.columnconfigure(1, weight=1)
        
        self.form_builder = FormBuilder(form_frame)
        
        for field_spec in self.get_form_fields():
            # Set defaults from config if available
            if field_spec.name in config:
                field_spec.default = config[field_spec.name]
            self.form_builder.add_field(field_spec)
        
        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)
        
        run_btn = ttk.Button(
            button_frame, text="Download Assets", command=on_execute, width=20
        )
        run_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(
            button_frame, text="Clear Form", command=self.form_builder.clear, width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        return frame

    def execute(self, form_data: Dict[str, Any]) -> None:
        """Execute the asset download with embedded business logic."""
        output_dir = form_data.get("output_dir", "assets")
        verbose = not form_data.get("quiet", False)
        pokeapi_dir = Path("pokeapi_database/pokemon")

        downloader = PokemonAssetDownloader(
            pokeapi_dir=pokeapi_dir, output_dir=output_dir, verbose=verbose
        )

        mode = form_data.get("mode", "Range")

        if mode == "All":
            downloader.download_all()
        elif mode == "Range":
            start_id = int(form_data.get("start_id", 1))
            end_id = int(form_data.get("end_id", 151))
            downloader.download_range(start_id, end_id)
        elif mode == "Names":
            names_str = form_data.get("names", "")
            if names_str:
                names = [n.strip().lower() for n in names_str.split(",") if n.strip()]
                downloader.download_by_names(names)
