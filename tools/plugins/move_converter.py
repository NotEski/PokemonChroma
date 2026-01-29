"""Move metadata converter plugin with GUI support."""

from __future__ import annotations

import re
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase


def parse_move_file(content: str) -> Optional[Dict[str, Any]]:
    """Parse a .pkmn move file and extract its components."""
    decorator_match = re.search(
        r'^@move\("([^"]+)"\)\s*(?:#\s*type:\s*ignore)?\s*\nclass\s+(\w+):',
        content,
        re.MULTILINE,
    )
    if not decorator_match:
        return None

    move_name = decorator_match.group(1)
    class_name = decorator_match.group(2)

    meta_match = re.search(
        r"meta\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}", content, re.DOTALL
    )
    if not meta_match:
        return None

    meta_dict = {}
    meta_content = meta_match.group(1)

    for line in meta_content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        match = re.match(r'"([^"]+)":\s*(.+?),?\s*$', line)
        if match:
            key = match.group(1)
            value = match.group(2).rstrip(",").strip()
            meta_dict[key] = value

    other_attrs = {}
    attr_pattern = r"^\s{4}(\w+)\s*=\s*(.+?)(?=\n\s{4}\w+\s*=|\Z)"
    for match in re.finditer(attr_pattern, content[meta_match.end() :], re.MULTILINE | re.DOTALL):
        attr_name = match.group(1)
        if attr_name != "meta":
            attr_value = match.group(2).strip()
            other_attrs[attr_name] = attr_value

    return {
        "move_name": move_name,
        "class_name": class_name,
        "meta_dict": meta_dict,
        "other_attrs": other_attrs,
    }


def convert_move_to_metadata_format(parsed: Dict[str, Any]) -> str:
    """Convert parsed move data to MoveMetaData format."""
    lines = [
        "from pkmn_imports import *",
        "",
        f'@move("{parsed["move_name"]}")',
        f'class {parsed["class_name"]}:',
    ]

    meta_dict = parsed["meta_dict"]
    meta_lines = ["    meta = MoveMetaData("]

    if "display_name" in meta_dict:
        meta_lines.append(f'        display_name={meta_dict["display_name"]},')

    if "index" in meta_dict:
        meta_lines.append(f'        index={meta_dict["index"]},')

    if "type" in meta_dict:
        type_val = meta_dict["type"]
        meta_lines.append(f"        type=PokemonType({type_val}),")

    if "damage_class" in meta_dict:
        damage_class_val = meta_dict["damage_class"]
        damage_class_map = {
            '"physical"': "DamageClass.PHYSICAL",
            '"special"': "DamageClass.SPECIAL",
            '"status"': "DamageClass.STATUS",
        }
        damage_class = damage_class_map.get(
            damage_class_val, f"DamageClass({damage_class_val})"
        )
        meta_lines.append(f"        damage_class={damage_class},")

    if "category" in meta_dict:
        category_val = meta_dict["category"]
        category_map = {
            '"damage"': "MoveCategory.DAMAGE",
            '"status"': "MoveCategory.STATUS",
            '"damage_status"': "MoveCategory.DAMAGE_STATUS",
        }
        category = category_map.get(category_val, f"MoveCategory({category_val})")
        meta_lines.append(f"        category={category},")

    if "accuracy" in meta_dict:
        meta_lines.append(f'        accuracy={meta_dict["accuracy"]},')

    if "power" in meta_dict:
        meta_lines.append(f'        power={meta_dict["power"]},')

    if "pp" in meta_dict:
        meta_lines.append(f'        pp={meta_dict["pp"]},')

    if "target" in meta_dict:
        target_val = meta_dict["target"]
        target_map = {
            '"selected_pokemon"': "MoveTarget.SELECTED_POKEMON",
            '"user"': "MoveTarget.USER",
            '"all_opponents"': "MoveTarget.ALL_OPPONENTS",
            '"all_allies"': "MoveTarget.ALL_ALLIES",
            '"all_others"': "MoveTarget.ALL_OTHERS",
            '"all"': "MoveTarget.ALL",
        }
        target = target_map.get(target_val, f"MoveTarget({target_val})")
        meta_lines.append(f"        target={target},")

    meta_lines.append("    )")
    lines.extend(meta_lines)

    for attr_name, attr_value in parsed["other_attrs"].items():
        lines.append(f"    {attr_name} = {attr_value}")

    return "\n".join(lines) + "\n"


def convert_moves(directory: str) -> None:
    """Convert all move files in the specified directory."""
    moves_dir = Path(directory)
    if not moves_dir.exists():
        print(f"Moves directory not found: {moves_dir}")
        return

    move_files = sorted(moves_dir.glob("*.pkmn"))
    converted = 0
    failed = 0

    print(f"Found {len(move_files)} move files to convert...\n")

    for move_file in move_files:
        try:
            with open(move_file, "r", encoding="utf-8") as f:
                content = f.read()

            if content.startswith("from pkmn_imports import *"):
                print(f"[OK] {move_file.name} - Already converted")
                continue

            parsed = parse_move_file(content)
            if not parsed:
                print(f"[FAIL] {move_file.name} - Failed to parse")
                failed += 1
                continue

            converted_content = convert_move_to_metadata_format(parsed)

            with open(move_file, "w", encoding="utf-8") as f:
                f.write(converted_content)
            print(f"[DONE] {move_file.name} - Converted")

            converted += 1
        except Exception as e:
            print(f"[FAIL] {move_file.name} - Error: {e}")
            failed += 1

    print(f"\nConversion complete:")
    print(f"  Converted: {converted}")
    print(f"  Failed: {failed}")


class Plugin(ToolPluginBase):
    """Plugin for converting moves to metadata format."""

    name = "move_converter"
    version = "1.0.0"
    description = "Convert move files to MoveMetaData format"
    default_config: Dict[str, str] = {
        "directory": "data/moves",
    }

    def setup(self, toolbox: Any) -> None:
        """Initialize the plugin."""
        # No external script needed - logic is embedded

    def get_form_fields(self) -> List[FormFieldSpec]:
        """Get form field specifications."""
        return [
            FormFieldSpec(
                name="directory",
                label="Moves Directory",
                field_type="directory",
                default=self.default_config["directory"],
                required=True,
                help_text="Directory containing move .pkmn files",
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
            button_frame, text="Convert Moves", command=on_execute, width=20
        )
        run_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(
            button_frame, text="Clear Form", command=self.form_builder.clear, width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        return frame

    def execute(self, form_data: Dict[str, Any]) -> None:
        """Execute move conversion with embedded business logic."""
        directory = form_data.get("directory", "data/moves")
        convert_moves(directory)
