"""Consolidate Pokemon files plugin with GUI support."""

from __future__ import annotations

import shutil
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase


def consolidate_pokemon_files(source_dir: Path) -> None:
    """Move .pkmn files up one level and clean up subdirectories."""
    if not source_dir.exists():
        print(f"Error: {source_dir} does not exist")
        return

    pokemon_dirs = sorted([d for d in source_dir.iterdir() if d.is_dir()])

    moved = 0
    deleted_json = 0
    deleted_dirs = 0

    for pokemon_dir in pokemon_dirs:
        pokemon_name = pokemon_dir.name

        pkmn_file = pokemon_dir / f"{pokemon_name}.pkmn"
        if not pkmn_file.exists():
            print(f"Skipping {pokemon_name} - no .pkmn file found")
            continue

        target_file = source_dir / f"{pokemon_name}.pkmn"

        # Move the .pkmn file
        shutil.move(str(pkmn_file), str(target_file))
        print(f"Moved: {pokemon_name}.pkmn")
        moved += 1

        # Delete JSON files in the directory
        json_files = list(pokemon_dir.glob("*.json"))
        for json_file in json_files:
            json_file.unlink()
            deleted_json += 1

        # Remove the now-empty directory
        try:
            remaining_files = list(pokemon_dir.iterdir())
            if not remaining_files:
                pokemon_dir.rmdir()
                deleted_dirs += 1
            else:
                print(
                    f"Warning: {pokemon_dir} not empty, contains: {[f.name for f in remaining_files]}"
                )
        except Exception as e:
            print(f"Error removing {pokemon_dir}: {e}")

    print(f"\nConsolidation complete:")
    print(f"  Moved: {moved} .pkmn files")
    print(f"  Deleted: {deleted_json} JSON files")
    print(f"  Removed: {deleted_dirs} directories")


class Plugin(ToolPluginBase):
    """Plugin for consolidating Pokemon data files."""

    name = "consolidate_files"
    version = "1.0.0"
    description = "Consolidate Pokemon files into a single directory"
    default_config: Dict[str, str] = {
        "source": "data/pokemon",
        "output": "data/pokemon_consolidated",
    }

    def setup(self, toolbox: Any) -> None:
        """Initialize the plugin."""
        # No external script needed - logic is embedded

    def get_form_fields(self) -> List[FormFieldSpec]:
        """Get form field specifications."""
        return [
            FormFieldSpec(
                name="source",
                label="Source Directory",
                field_type="directory",
                default=self.default_config["source"],
                required=True,
                help_text="Directory with distributed Pokemon files",
            ),
            FormFieldSpec(
                name="output",
                label="Output Directory",
                field_type="directory",
                default=self.default_config["output"],
                required=True,
                help_text="Consolidated output directory",
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
            button_frame, text="Consolidate Files", command=on_execute, width=20
        )
        run_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(
            button_frame, text="Clear Form", command=self.form_builder.clear, width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        return frame

    def execute(self, form_data: Dict[str, Any]) -> None:
        """Execute consolidation with embedded business logic."""
        source = form_data.get("source", "data/pokemon")
        source_dir = Path(source)
        consolidate_pokemon_files(source_dir)
