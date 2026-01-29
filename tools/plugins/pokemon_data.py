"""Pokemon data generator plugin with GUI support."""

from __future__ import annotations

import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase


class Plugin(ToolPluginBase):
    """Plugin for generating Pokemon game data."""

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
        """Initialize the plugin."""
        base = Path(__file__).resolve().parents[1]
        self.set_script_path(base / "generate_pokemon_data.py")

    def get_form_fields(self) -> List[FormFieldSpec]:
        """Get form field specifications."""
        return [
            FormFieldSpec(
                name="source",
                label="Source Directory",
                field_type="directory",
                default=self.default_config["source"],
                required=True,
                help_text="Directory containing PokeAPI data",
            ),
            FormFieldSpec(
                name="out_pokemon",
                label="Pokemon Output",
                field_type="directory",
                default=self.default_config["out_pokemon"],
                required=True,
            ),
            FormFieldSpec(
                name="out_moves",
                label="Moves Output",
                field_type="directory",
                default=self.default_config["out_moves"],
                required=True,
            ),
            FormFieldSpec(
                name="out_items",
                label="Items Output",
                field_type="directory",
                default=self.default_config["out_items"],
                required=True,
            ),
            FormFieldSpec(
                name="overwrite",
                label="Overwrite Existing",
                field_type="checkbox",
                default=False,
                help_text="Overwrite existing files",
            ),
        ]

    def create_ui(
        self, parent: tk.Frame, config: Dict[str, str], on_execute: Callable[[], None]
    ) -> tk.Frame:
        """Create the plugin's GUI interface."""
        frame = tk.Frame(parent)

        desc = ttk.Label(
            frame,
            text=self.description,
            wraplength=700,
            font=("TkDefaultFont", 10, "bold"),
        )
        desc.pack(pady=10)

        form_frame = tk.Frame(frame)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        form_frame.columnconfigure(1, weight=1)

        self.form_builder = FormBuilder(form_frame)

        for field_spec in self.get_form_fields():
            if field_spec.name in config:
                field_spec.default = config[field_spec.name]
            self.form_builder.add_field(field_spec)

        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)

        run_btn = ttk.Button(
            button_frame, text="Generate Data", command=on_execute, width=20
        )
        run_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(
            button_frame, text="Clear Form", command=self.form_builder.clear, width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        return frame

    def execute(self, form_data: Dict[str, Any]) -> None:
        """Execute data generation by calling the underlying script."""
        if not self._script_path:
            raise RuntimeError("Plugin has no script path set")

        args: List[str] = []

        source = form_data.get("source")
        if source:
            args.extend(["--source", str(source)])

        out_pokemon = form_data.get("out_pokemon")
        if out_pokemon:
            args.extend(["--out-pokemon", str(out_pokemon)])

        out_moves = form_data.get("out_moves")
        if out_moves:
            args.extend(["--out-moves", str(out_moves)])

        out_items = form_data.get("out_items")
        if out_items:
            args.extend(["--out-items", str(out_items)])

        if form_data.get("overwrite"):
            args.append("--overwrite")

        subprocess.run(["python", str(self._script_path)] + args, check=False)
