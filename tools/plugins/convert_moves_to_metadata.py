"""
Move Metadata Converter Plugin

Converts move .pkmn files from meta dict format to MoveMetaData format.
"""

import re
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase


class MoveConverter:
    """Converts move files to MoveMetaData format."""
    
    def __init__(self, moves_dir: Path):
        self.moves_dir = Path(moves_dir)
        self.stats: Dict[str, Any] = {
            'converted': 0,
            'already_converted': 0,
            'failed': 0,
            'errors': [],
        }
    
    def parse_move_file(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse a .pkmn move file and extract its components."""
        # Extract decorator and class definition
        decorator_match = re.search(
            r'^@move\("([^"]+)"\)\s*(?:#\s*type:\s*ignore)?\s*\nclass\s+(\w+):',
            content, re.MULTILINE
        )
        if not decorator_match:
            return None
        
        move_name = decorator_match.group(1)
        class_name = decorator_match.group(2)
        
        # Extract meta dict
        meta_match = re.search(r'meta\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', content, re.DOTALL)
        if not meta_match:
            return None
        
        meta_dict = {}
        meta_content = meta_match.group(1)
        
        # Parse key-value pairs from meta dict
        for line in meta_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Match "key": value patterns
            match = re.match(r'"([^"]+)":\s*(.+?),?\s*$', line)
            if match:
                key = match.group(1)
                value = match.group(2).rstrip(',').strip()
                meta_dict[key] = value
        
        # Extract all other attributes
        other_attrs = {}
        attr_pattern = r'^\s{4}(\w+)\s*=\s*(.+?)(?=\n\s{4}\w+\s*=|\Z)'
        for match in re.finditer(attr_pattern, content[meta_match.end():], re.MULTILINE | re.DOTALL):
            attr_name = match.group(1)
            if attr_name != 'meta':
                attr_value = match.group(2).strip()
                other_attrs[attr_name] = attr_value
        
        return {
            'move_name': move_name,
            'class_name': class_name,
            'meta_dict': meta_dict,
            'other_attrs': other_attrs,
        }
    
    def convert_move_to_metadata_format(self, parsed: Dict[str, Any]) -> str:
        """Convert parsed move data to MoveMetaData format."""
        lines = [
            "from pkmn_imports import *",
            "",
            f'@move("{parsed["move_name"]}")',
            f'class {parsed["class_name"]}:',
        ]
        
        # Build MoveMetaData
        meta_dict = parsed['meta_dict']
        meta_lines = ["    meta = MoveMetaData("]
        
        # Required fields in order
        if 'display_name' in meta_dict:
            meta_lines.append(f'        display_name={meta_dict["display_name"]},')
        
        if 'index' in meta_dict:
            meta_lines.append(f'        index={meta_dict["index"]},')
        
        if 'type' in meta_dict:
            type_val = meta_dict['type']
            meta_lines.append(f'        type=PokemonType({type_val}),')
        
        if 'damage_class' in meta_dict:
            damage_class_val = meta_dict['damage_class']
            damage_class_map = {
                '"physical"': 'DamageClass.PHYSICAL',
                '"special"': 'DamageClass.SPECIAL',
                '"status"': 'DamageClass.STATUS',
            }
            damage_class = damage_class_map.get(damage_class_val, f'DamageClass({damage_class_val})')
            meta_lines.append(f'        damage_class={damage_class},')
        
        if 'category' in meta_dict:
            category_val = meta_dict['category']
            category_map = {
                '"damage"': 'MoveCategory.DAMAGE',
                '"status"': 'MoveCategory.STATUS',
                '"damage_status"': 'MoveCategory.DAMAGE_STATUS',
            }
            category = category_map.get(category_val, f'MoveCategory({category_val})')
            meta_lines.append(f'        category={category},')
        
        if 'accuracy' in meta_dict:
            meta_lines.append(f'        accuracy={meta_dict["accuracy"]},')
        
        if 'power' in meta_dict:
            meta_lines.append(f'        power={meta_dict["power"]},')
        
        if 'pp' in meta_dict:
            meta_lines.append(f'        pp={meta_dict["pp"]},')
        
        if 'target' in meta_dict:
            target_val = meta_dict['target']
            target_map = {
                '"selected_pokemon"': 'MoveTarget.SELECTED_POKEMON',
                '"user"': 'MoveTarget.USER',
                '"all_opponents"': 'MoveTarget.ALL_OPPONENTS',
                '"all_allies"': 'MoveTarget.ALL_ALLIES',
                '"all_others"': 'MoveTarget.ALL_OTHERS',
                '"all"': 'MoveTarget.ALL',
            }
            target = target_map.get(target_val, f'MoveTarget({target_val})')
            meta_lines.append(f'        target={target},')
        
        meta_lines.append("    )")
        lines.extend(meta_lines)
        
        # Add other attributes
        for attr_name, attr_value in parsed['other_attrs'].items():
            lines.append(f"    {attr_name} = {attr_value}")
        
        return "\n".join(lines) + "\n"
    
    def convert(self, dry_run: bool = False) -> Dict[str, Any]:
        """Convert all move files in the moves directory."""
        if not self.moves_dir.exists():
            raise ValueError(f"Moves directory not found: {self.moves_dir}")
        
        move_files = sorted(self.moves_dir.glob("*.pkmn"))
        
        for move_file in move_files:
            try:
                with open(move_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip if already converted
                if content.startswith("from pkmn_imports import *"):
                    self.stats['already_converted'] += 1
                    print(f"[OK] {move_file.name} - Already converted")
                    continue
                
                parsed = self.parse_move_file(content)
                if not parsed:
                    self.stats['failed'] += 1
                    self.stats['errors'].append(f"{move_file.name}: Failed to parse")
                    print(f"[FAIL] {move_file.name} - Failed to parse")
                    continue
                
                converted_content = self.convert_move_to_metadata_format(parsed)
                
                if not dry_run:
                    with open(move_file, 'w', encoding='utf-8') as f:
                        f.write(converted_content)
                    print(f"[DONE] {move_file.name} - Converted")
                else:
                    print(f"[DRY RUN] {move_file.name} - Would convert")
                
                self.stats['converted'] += 1
            except Exception as e:
                self.stats['failed'] += 1
                self.stats['errors'].append(f"{move_file.name}: {str(e)}")
                print(f"[FAIL] {move_file.name} - Error: {e}")
        
        return self.stats


class Plugin(ToolPluginBase):
    """Move Metadata Converter plugin."""
    
    name = "convert_moves_to_metadata"
    version = "1.0.0"
    description = "Convert move files to MoveMetaData format"
    default_config: Dict[str, str] = {
        "moves_dir": "data/moves",
        "dry_run": "true",
    }
    
    def get_form_fields(self) -> List[FormFieldSpec]:
        """Define form fields for this plugin."""
        return [
            FormFieldSpec(
                name="moves_dir",
                label="Moves Directory",
                field_type="directory",
                required=True,
                default=self.default_config["moves_dir"],
                help_text="Path to data/moves directory containing .pkmn files"
            ),
            FormFieldSpec(
                name="dry_run",
                label="Dry Run (Preview Changes)",
                field_type="checkbox",
                default=True,
                help_text="Check to preview changes without modifying files"
            ),
        ]
    
    def create_ui(
        self, parent: tk.Frame, config: Dict[str, str], on_execute: Callable[[], None]
    ) -> tk.Frame:
        """Create the plugin's GUI."""
        frame = tk.Frame(parent)
        
        # Description
        desc = ttk.Label(
            frame,
            text=self.description,
            wraplength=700,
            font=("TkDefaultFont", 10, "bold"),
        )
        desc.pack(pady=10)
        
        # Info text
        info = ttk.Label(
            frame,
            text="Converts move files from meta dict format to MoveMetaData format:\n"
                 "• Adds 'from pkmn_imports import *' import\n"
                 "• Converts meta dict to MoveMetaData constructor\n"
                 "• Preserves all other class attributes\n\n"
                 "Use Dry Run first to preview changes!",
            wraplength=700,
            font=("TkDefaultFont", 9),
            foreground="gray60",
        )
        info.pack(pady=5)
        
        # Warning box
        warning_frame = tk.Frame(frame, bg="#fff3cd", relief=tk.SOLID, bd=1)
        warning_frame.pack(fill=tk.X, padx=10, pady=10)
        
        warning_label = ttk.Label(
            warning_frame,
            text="⚠ WARNING: This operation modifies your move files.\n"
                 "Always run Dry Run first to preview changes!",
            foreground="#856404",
            background="#fff3cd",
            wraplength=680,
        )
        warning_label.pack(padx=8, pady=8)
        
        # Form
        form_frame = tk.Frame(frame)
        form_frame.pack(fill=tk.BOTH, expand=False, pady=10)
        form_frame.columnconfigure(1, weight=1)
        
        self.form_builder = FormBuilder(form_frame)
        for field_spec in self.get_form_fields():
            if field_spec.name in config:
                field_spec.default = config[field_spec.name]
            self.form_builder.add_field(field_spec)
        
        # Output area
        output_label = ttk.Label(frame, text="Results:", font=("TkDefaultFont", 10, "bold"))
        output_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.output_text = tk.Text(
            frame,
            height=12,
            width=80,
            font=("Courier New", 8),
            wrap=tk.WORD,
            bg="white",
            fg="black",
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.output_text, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)
        
        run_btn = ttk.Button(
            button_frame, text="Execute", command=on_execute, width=20
        )
        run_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(
            button_frame, text="Clear Results", command=self._clear_output, width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def _clear_output(self) -> None:
        """Clear the output text area."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def execute(self, form_data: Dict[str, Any]) -> None:
        """Execute the conversion."""
        moves_dir = Path(form_data.get("moves_dir", self.default_config["moves_dir"]))
        dry_run = form_data.get("dry_run", True)
        
        if not moves_dir.exists():
            raise ValueError(f"Moves directory not found: {moves_dir}")
        
        output_lines: List[str] = []
        
        if dry_run:
            output_lines.append("=" * 80)
            output_lines.append("DRY RUN MODE - No files will be modified")
            output_lines.append("=" * 80)
        else:
            output_lines.append("=" * 80)
            output_lines.append("CONVERSION IN PROGRESS")
            output_lines.append("=" * 80)
        
        output_lines.append(f"Moves Directory: {moves_dir}")
        output_lines.append("")
        
        print(f"Converting moves in {moves_dir}...")
        
        converter = MoveConverter(moves_dir)
        stats = converter.convert(dry_run=dry_run)
        
        output_lines.append("RESULTS:")
        output_lines.append(f"  Files converted: {stats['converted']}")
        output_lines.append(f"  Already converted: {stats['already_converted']}")
        output_lines.append(f"  Failed: {stats['failed']}")
        
        if stats['errors']:
            output_lines.append("")
            output_lines.append("ERRORS:")
            for error in stats['errors'][:10]:  # Show first 10 errors
                output_lines.append(f"  • {error}")
            if len(stats['errors']) > 10:
                output_lines.append(f"  ... and {len(stats['errors']) - 10} more")
        
        if dry_run:
            output_lines.append("")
            output_lines.append("This was a dry run. Uncheck 'Dry Run' to apply changes.")
        
        output = "\n".join(output_lines)
        
        # Display in output area if it exists
        if hasattr(self, 'output_text'):
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, output)
            self.output_text.config(state=tk.DISABLED)
        
        print(output)
