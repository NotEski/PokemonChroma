"""JSON to PKMN converter plugin with GUI support."""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase


def convert_json_to_pkmn(json_data: Dict[str, Any], pokemon_name: str) -> str:
    """Convert a JSON pokemon definition to a .pkmn Python file format."""
    lines: List[str] = []
    lines.append("from shared.pokemon.stats import BaseStats, EffortYield")
    lines.append("")
    lines.append("")

    # Check if this is a mega evolution
    is_mega = (
        json_data.get("moves", {}).get("level", {}) == {}
        and json_data.get("moves", {}).get("machine", []) == []
        and json_data.get("pokedex_number", 0) > 10000
    )

    moves_data = json_data.get("moves", {})
    level_moves = moves_data.get("level", {})
    machine_moves = moves_data.get("machine", [])
    tutor_moves = moves_data.get("tutor", [])
    egg_moves = moves_data.get("egg_moves", [])

    if is_mega:
        base_name = json_data.get("name", pokemon_name).replace("_mega", "").replace("_gmax", "")
        class_name = "".join(word.capitalize() for word in base_name.split("_"))
        mega_form = json_data.get("name", pokemon_name)

        lines.append(f'@mega_evolution("{mega_form}")')
        lines.append(f"class Mega{class_name}:")
        lines.append(f'    display_name = "{json_data.get("display_name", class_name)}"')
        lines.append(f'    id = {json_data.get("pokedex_number", 0)}')
    else:
        class_name = "".join(word.capitalize() for word in pokemon_name.split("_"))

        lines.append(f'@pokemon("{pokemon_name}")')
        lines.append(f"class {class_name}:")
        lines.append(f'    display_name = "{json_data.get("display_name", class_name)}"')
        lines.append(f'    id = {json_data.get("pokedex_number", 0)}')

        types = json_data.get("types", [])
        if types:
            lines.append(f"    types = {types}")

    # Base stats
    base_stats = json_data.get("base_stats", {})
    lines.append("    base_stats = BaseStats(")
    lines.append(f"        hp={base_stats.get('hp', 0)},")
    lines.append(f"        attack={base_stats.get('attack', 0)},")
    lines.append(f"        defense={base_stats.get('defense', 0)},")
    lines.append(f"        special_attack={base_stats.get('special_attack', 0)},")
    lines.append(f"        special_defense={base_stats.get('special_defense', 0)},")
    lines.append(f"        speed={base_stats.get('speed', 0)}")
    lines.append("    )")

    if not is_mega:
        ev_yield = json_data.get("ev_yield", {})
        lines.append("    ev_yield = EffortYield(")
        lines.append(f"        hp={ev_yield.get('hp', 0)},")
        lines.append(f"        attack={ev_yield.get('attack', 0)},")
        lines.append(f"        defense={ev_yield.get('defense', 0)},")
        lines.append(f"        special_attack={ev_yield.get('special_attack', 0)},")
        lines.append(f"        special_defense={ev_yield.get('special_defense', 0)},")
        lines.append(f"        speed={ev_yield.get('speed', 0)}")
        lines.append("    )")

        lines.append(f'    catch_rate = {json_data.get("capture_rate", 45)}')
        lines.append(f'    base_experience_yield = {json_data.get("base_experience_yield", 64)}')
        lines.append(f'    base_happiness = {json_data.get("base_happiness", 70)}')
        lines.append(f'    gender_rate = {json_data.get("gender_rate", 4)}')

        abilities = json_data.get("abilities", [])
        if abilities:
            lines.append("    abilities: list[dict[str, str|int|bool]] = [")
            for ability in abilities:
                lines.append("        {")
                lines.append(f'            "ability": "{ability.get("ability", "")}",')
                lines.append(f'            "slot": {ability.get("slot", 1)},')
                lines.append(f'            "is_hidden": {str(ability.get("is_hidden", False))}')
                lines.append("        },")
            lines.append("    ]")

        lines.append(f'    height_m = {json_data.get("height_m", 1.0)}')
        lines.append(f'    weight_kg = {json_data.get("weight_kg", 1.0)}')

        egg_groups = json_data.get("egg_groups", [])
        if egg_groups:
            lines.append(f'    egg_groups = {egg_groups}')

        lines.append(f'    growth_rate = "{json_data.get("growth_rate", "medium")}"')

        if level_moves:
            lines.append("    level_moves: dict[int, list[str]] = {")
            for level, moves in sorted((int(k), v) for k, v in level_moves.items()):
                lines.append(f"            {level}: [")
                for move in moves:
                    lines.append(f'                "{move}",')
                lines.append("            ],")
            lines.append("        }")

        if machine_moves:
            lines.append("    machine_moves = [")
            for move in machine_moves:
                lines.append(f'        "{move}",')
            lines.append("    ]")

        if tutor_moves:
            lines.append("    tutor_moves = [")
            for move in tutor_moves:
                lines.append(f'        "{move}",')
            lines.append("    ]")

        if egg_moves:
            lines.append("    egg_moves = [")
            for move in egg_moves:
                lines.append(f'        "{move}",')
            lines.append("    ]")
        else:
            lines.append("    egg_moves = []")
    else:
        lines.append(f'    mega_evolution_item = "{json_data.get("mega_evolution_item", "")}"')
        lines.append(f'    base_experience_yield = {json_data.get("base_experience_yield", 64)}')
        lines.append(f'    height_m = {json_data.get("height_m", 1.0)}')
        lines.append(f'    weight_kg = {json_data.get("weight_kg", 1.0)}')

    return "\n".join(lines)


def process_pokemon_directory(pokemon_dir: Path, overwrite: bool = False) -> bool:
    """Process a single pokemon directory. Returns True if a .pkmn file was created."""
    json_file = pokemon_dir / "base_pokemon.json"
    if not json_file.exists():
        return False

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading {json_file}: {e}")
        return False

    pokemon_name = json_data.get("name", pokemon_dir.name)
    pkmn_file = pokemon_dir / f"{pokemon_name}.pkmn"

    if pkmn_file.exists() and not overwrite:
        print(f"Skipping {pokemon_name} - .pkmn file already exists")
        return False

    try:
        pkmn_content = convert_json_to_pkmn(json_data, pokemon_name)
        with open(pkmn_file, "w", encoding="utf-8") as f:
            f.write(pkmn_content)
        print(f"Created {pkmn_file}")
        return True
    except Exception as e:
        print(f"Error creating .pkmn for {pokemon_name}: {e}")
        return False


def convert_pokemon_json_files(input_dir: str, overwrite: bool = False) -> None:
    """Convert all pokemon JSON files to .pkmn files."""
    pokemon_data_dir = Path(input_dir)

    if not pokemon_data_dir.exists():
        print(f"Error: {pokemon_data_dir} does not exist")
        return

    pokemon_dirs = sorted([d for d in pokemon_data_dir.iterdir() if d.is_dir()])

    created = 0
    skipped = 0

    for pokemon_dir in pokemon_dirs:
        if process_pokemon_directory(pokemon_dir, overwrite=overwrite):
            created += 1
        else:
            skipped += 1

    print(f"\nConversion complete: {created} created, {skipped} skipped")


class Plugin(ToolPluginBase):
    """Plugin for converting JSON files to PKMN format."""

    name = "json_converter"
    version = "1.0.0"
    description = "Convert Pokemon JSON files to .pkmn format"
    default_config: Dict[str, str] = {
        "input": "data/pokemon",
        "output": "data/pokemon_pkmn",
    }

    def setup(self, toolbox: Any) -> None:
        """Initialize the plugin."""
        # No external script needed - logic is embedded

    def get_form_fields(self) -> List[FormFieldSpec]:
        """Get form field specifications."""
        return [
            FormFieldSpec(
                name="input",
                label="Pokemon Directory",
                field_type="directory",
                default=self.default_config["input"],
                required=True,
                help_text="Directory containing Pokemon subdirectories with base_pokemon.json files",
            ),
            FormFieldSpec(
                name="overwrite",
                label="Overwrite Existing",
                field_type="checkbox",
                default=False,
                help_text="Overwrite existing .pkmn files",
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
            button_frame, text="Convert Files", command=on_execute, width=20
        )
        run_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(
            button_frame, text="Clear Form", command=self.form_builder.clear, width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        return frame

    def execute(self, form_data: Dict[str, Any]) -> None:
        """Execute JSON conversion with embedded business logic."""
        input_dir = form_data.get("input", "data/pokemon")
        overwrite = form_data.get("overwrite", False)
        convert_pokemon_json_files(input_dir, overwrite=bool(overwrite))
