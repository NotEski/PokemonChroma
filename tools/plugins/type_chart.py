"""Type chart generator plugin with GUI support."""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase


def load_type_jsons(type_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Load all type JSON files."""
    types: Dict[str, Dict[str, Any]] = {}
    for p in type_dir.glob("*.json"):
        if p.name in {"_index.json", "summary.json"}:
            continue
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
                types[p.stem] = data
        except json.JSONDecodeError:
            continue
    return types


def format_type_name(name: str) -> str:
    """Convert type name to lowercase with underscores."""
    return name.replace("-", "_").lower()


def format_class_name(name: str) -> str:
    """Convert type name to class name."""
    return "".join(word.capitalize() for word in name.replace("-", " ").split()) + "Type"


def format_display_name(name: str) -> str:
    """Convert type name to display name."""
    return name.replace("-", " ").title()


def build_type_data(type_dir: Path) -> Dict[str, Dict[str, float]]:
    """Build type effectiveness data."""
    type_data: Dict[str, Dict[str, float]] = {}
    types = load_type_jsons(type_dir)

    for type_name, data in types.items():
        rel = data.get("damage_relations", {})
        effectiveness = {}

        for defender in rel.get("double_damage_to", []):
            defender_name = format_type_name(defender["name"])
            effectiveness[defender_name] = 2.0
        for defender in rel.get("half_damage_to", []):
            defender_name = format_type_name(defender["name"])
            effectiveness[defender_name] = 0.5
        for defender in rel.get("no_damage_to", []):
            defender_name = format_type_name(defender["name"])
            effectiveness[defender_name] = 0.0

        type_data[type_name] = effectiveness

    return type_data


def emit_pkmn_file(type_name: str, effectiveness: Dict[str, float]) -> str:
    """Generate .pkmn file content for a type."""
    formatted_name = format_type_name(type_name)
    class_name = format_class_name(type_name)
    display_name = format_display_name(type_name)

    lines = [
        f'@pokemon_type("{formatted_name}")\n',
        f"class {class_name}:\n",
        f'    name = "{display_name}"\n',
        f'    icon = b""  # Placeholder for icon bytes\n',
        f"    effectiveness = {{\n",
    ]

    for defender, mult in sorted(effectiveness.items()):
        lines.append(f'        "{defender}": {mult},\n')

    lines.append("    }\n")

    return "".join(lines)


class Plugin(ToolPluginBase):
    """Plugin for generating type effectiveness charts."""

    name = "type_chart"
    version = "1.0.0"
    description = "Generate type effectiveness chart"
    default_config: Dict[str, str] = {
        "output": "engine/type_chart.json",
    }

    def setup(self, toolbox: Any) -> None:
        """Initialize the plugin."""
        # No external script needed - logic is embedded

    def get_form_fields(self) -> List[FormFieldSpec]:
        """Get form field specifications."""
        return [
            FormFieldSpec(
                name="output",
                label="Output File",
                field_type="file",
                default=self.default_config["output"],
                required=True,
                help_text="Path for type_chart.json",
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
            button_frame, text="Generate Type Chart", command=on_execute, width=20
        )
        run_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(
            button_frame, text="Clear Form", command=self.form_builder.clear, width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        return frame

    def execute(self, form_data: Dict[str, Any]) -> None:
        """Generate type chart with embedded business logic."""
        workspace_root = Path(__file__).resolve().parents[2]
        type_dir = workspace_root / "pokeapi_database" / "type"
        output_path = Path(form_data.get("output", "engine/type_chart.json"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Building type data from {type_dir}...")
        type_data = build_type_data(type_dir)

        print(f"Generated data for {len(type_data)} types")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(type_data, f, indent=2)

        print(f"Wrote type chart to {output_path}")
