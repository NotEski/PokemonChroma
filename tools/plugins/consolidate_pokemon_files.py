"""
Pokemon File Consolidator Plugin

Consolidates Pokemon data files by moving .pkmn files to parent directory
and cleaning up JSON files and subdirectories.
"""

import shutil
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase


class PokemonConsolidator:
    """Consolidates Pokemon file structure."""
    
    def __init__(self, pokemon_dir: Path):
        self.pokemon_dir = Path(pokemon_dir)
        self.stats = {
            'moved': 0,
            'deleted_json': 0,
            'deleted_dirs': 0,
            'skipped': 0,
            'errors': [],
        }
    
    def consolidate(self, dry_run: bool = False) -> Dict[str, Any]:
        """Move .pkmn files up one level and clean up subdirectories."""
        
        if not self.pokemon_dir.exists():
            raise ValueError(f"Pokemon directory not found: {self.pokemon_dir}")
        
        pokemon_dirs = sorted([d for d in self.pokemon_dir.iterdir() if d.is_dir()])
        
        for pokemon_dir in pokemon_dirs:
            pokemon_name = pokemon_dir.name
            
            # Look for the .pkmn file
            pkmn_file = pokemon_dir / f"{pokemon_name}.pkmn"
            if not pkmn_file.exists():
                self.stats['skipped'] += 1
                continue
            
            # Target location (parent directory)
            target_file = self.pokemon_dir / f"{pokemon_name}.pkmn"
            
            if not dry_run:
                try:
                    # Move the .pkmn file
                    shutil.move(str(pkmn_file), str(target_file))
                    self.stats['moved'] += 1
                    print(f"Moved: {pokemon_name}.pkmn")
                except Exception as e:
                    self.stats['errors'].append(f"Error moving {pokemon_name}: {e}")
                    continue
            
            # Delete JSON files in the directory
            json_files = list(pokemon_dir.glob("*.json"))
            for json_file in json_files:
                if not dry_run:
                    try:
                        json_file.unlink()
                        self.stats['deleted_json'] += 1
                    except Exception as e:
                        self.stats['errors'].append(f"Error deleting {json_file}: {e}")
            
            # Remove the now-empty directory
            if not dry_run:
                try:
                    remaining_files = list(pokemon_dir.iterdir())
                    if not remaining_files:
                        pokemon_dir.rmdir()
                        self.stats['deleted_dirs'] += 1
                except Exception as e:
                    self.stats['errors'].append(f"Error removing {pokemon_dir}: {e}")
        
        return self.stats


class Plugin(ToolPluginBase):
    """Pokemon File Consolidator plugin."""
    
    name = "consolidate_pokemon_files"
    version = "1.0.0"
    description = "Consolidate Pokemon files by moving .pkmn files to parent directory"
    default_config: Dict[str, str] = {
        "pokemon_dir": "data/pokemon",
        "dry_run": "true",
    }
    
    def get_form_fields(self) -> List[FormFieldSpec]:
        """Define form fields for this plugin."""
        return [
            FormFieldSpec(
                name="pokemon_dir",
                label="Pokemon Directory",
                field_type="directory",
                required=True,
                default=self.default_config["pokemon_dir"],
                help_text="Path to data/pokemon directory with Pokemon subdirectories"
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
            text="This plugin consolidates your Pokemon data structure:\n"
                 "• Moves .pkmn files from subdirectories to parent directory\n"
                 "• Deletes JSON files in subdirectories\n"
                 "• Removes empty subdirectories\n\n"
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
            text="⚠ WARNING: This operation modifies your data directory.\n"
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
            height=10,
            width=80,
            font=("Courier New", 9),
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
        """Execute the consolidation."""
        pokemon_dir = Path(form_data.get("pokemon_dir", self.default_config["pokemon_dir"]))
        dry_run = form_data.get("dry_run", True)
        
        if not pokemon_dir.exists():
            raise ValueError(f"Pokemon directory not found: {pokemon_dir}")
        
        output_lines = []
        
        if dry_run:
            output_lines.append("=" * 80)
            output_lines.append("DRY RUN MODE - No files will be modified")
            output_lines.append("=" * 80)
        else:
            output_lines.append("=" * 80)
            output_lines.append("CONSOLIDATION IN PROGRESS")
            output_lines.append("=" * 80)
        
        output_lines.append(f"Pokemon Directory: {pokemon_dir}")
        output_lines.append("")
        
        print(f"Consolidating Pokemon files in {pokemon_dir}...")
        
        consolidator = PokemonConsolidator(pokemon_dir)
        stats = consolidator.consolidate(dry_run=dry_run)
        
        output_lines.append("RESULTS:")
        output_lines.append(f"  Files moved: {stats['moved']}")
        output_lines.append(f"  JSON files deleted: {stats['deleted_json']}")
        output_lines.append(f"  Directories removed: {stats['deleted_dirs']}")
        output_lines.append(f"  Files skipped: {stats['skipped']}")
        
        if stats['errors']:
            output_lines.append("")
            output_lines.append("ERRORS:")
            for error in stats['errors']:
                output_lines.append(f"  • {error}")
        
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
