"""
Field Effects Analyzer Plugin

Analyzes and categorizes field effects in move data, excluding weather and terrain.
"""

import json
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase


class FieldEffectsAnalyzer:
    """Analyzes field effects in moves."""
    
    def __init__(self, moves_dir: Path):
        self.moves_dir = Path(moves_dir)
        self.field_effect_moves = []
        self.effect_groups = {}
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze field effects in moves database."""
        # Track all moves that mention "field" or specific effects
        field_effect_moves = []
        all_effects = set()
        
        # Exclude weather and terrain related phrases
        exclude_phrases = [
            'weather', 'electric terrain', 'grassy terrain', 'misty terrain', 'psychic terrain',
            'rain', 'sunny', 'hail', 'sandstorm', 'snow'
        ]
        
        for move_file in sorted(self.moves_dir.glob("*.json")):
            if move_file.name == "_index.json":
                continue
                
            try:
                data = json.load(open(move_file, 'r', encoding='utf-8'))
                move_name = data.get('name', move_file.stem)
                
                effect_entries = data.get('effect_entries', [])
                if not effect_entries:
                    continue
                    
                short_effect = effect_entries[0].get('short_effect', '')
                short_effect_lower = short_effect.lower()
                
                # Skip if it's a weather or terrain move
                is_excluded = any(phrase in short_effect_lower for phrase in exclude_phrases)
                if is_excluded:
                    continue
                
                # Check for field-related effects
                if 'field' in short_effect_lower or \
                   'room' in short_effect_lower or \
                   'spikes' in short_effect_lower or \
                   'stealth rock' in short_effect_lower or \
                   'sticky web' in short_effect_lower or \
                   'reflect' in short_effect_lower or \
                   'light screen' in short_effect_lower or \
                   'aurora veil' in short_effect_lower or \
                   'safeguard' in short_effect_lower or \
                   'mist' in short_effect_lower or \
                   'tailwind' in short_effect_lower or \
                   'g-max' in short_effect_lower:
                    field_effect_moves.append({
                        'name': move_name,
                        'effect': short_effect
                    })
                    all_effects.add(short_effect)
            except Exception as e:
                print(f"Error processing {move_file}: {e}")
        
        # Group by effect type
        effect_groups = defaultdict(list)
        for move in field_effect_moves:
            effect = move['effect'].lower()
            
            # Categorize
            if 'trick room' in effect:
                effect_groups['Trick Room'].append(move)
            elif 'wonder room' in effect:
                effect_groups['Wonder Room'].append(move)
            elif 'magic room' in effect:
                effect_groups['Magic Room'].append(move)
            elif 'reflect' in effect and 'type' not in effect:
                effect_groups['Reflect'].append(move)
            elif 'light screen' in effect:
                effect_groups['Light Screen'].append(move)
            elif 'aurora veil' in effect:
                effect_groups['Aurora Veil'].append(move)
            elif 'stealth rock' in effect:
                effect_groups['Stealth Rock'].append(move)
            elif 'spikes' in effect and 'toxic' not in effect:
                effect_groups['Spikes'].append(move)
            elif 'toxic spikes' in effect:
                effect_groups['Toxic Spikes'].append(move)
            elif 'sticky web' in effect:
                effect_groups['Sticky Web'].append(move)
            elif 'safeguard' in effect:
                effect_groups['Safeguard'].append(move)
            elif 'mist' in effect and 'misty terrain' not in effect:
                effect_groups['Mist'].append(move)
            elif 'tailwind' in effect:
                effect_groups['Tailwind'].append(move)
            elif 'g-max' in effect:
                effect_groups['G-Max Effects'].append(move)
            else:
                effect_groups['Other Field Effects'].append(move)
        
        self.field_effect_moves = field_effect_moves
        self.effect_groups = dict(effect_groups)
        
        return {
            'total_moves': len(field_effect_moves),
            'categories': len(effect_groups),
            'moves_by_category': {k: len(v) for k, v in effect_groups.items()},
        }
    
    def get_formatted_output(self) -> str:
        """Get formatted text output of analysis."""
        output = []
        output.append("=== FIELD EFFECTS (Excluding Weather & Terrain) ===\n")
        output.append(f"Total moves with field effects: {len(self.field_effect_moves)}\n")
        
        for effect_type, moves in sorted(self.effect_groups.items()):
            output.append(f"\n{effect_type.upper()} ({len(moves)} moves):")
            output.append("-" * 60)
            for move in moves:
                effect_preview = move['effect'][:77] + "..." if len(move['effect']) > 80 else move['effect']
                output.append(f"  • {move['name']}: {effect_preview}")
        
        output.append(f"\n\n=== UNIQUE FIELD EFFECT TYPES ===")
        output.append(f"Total categories: {len(self.effect_groups)}")
        for effect_type in sorted(self.effect_groups.keys()):
            output.append(f"  • {effect_type}")
        
        return "\n".join(output)


class Plugin(ToolPluginBase):
    """Field Effects Analyzer plugin."""
    
    name = "analyze_field_effects"
    version = "1.0.0"
    description = "Analyzes and categorizes field effects in move data"
    default_config: Dict[str, str] = {
        "moves_dir": "pokeapi_database/move",
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
                help_text="Path to the pokeapi_database/move directory"
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
            text="Analyzes move effects and categorizes them by field effect type,\n"
                 "excluding weather and terrain effects.",
            wraplength=700,
            font=("TkDefaultFont", 9),
            foreground="gray60",
        )
        info.pack(pady=5)
        
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
        output_label = ttk.Label(frame, text="Analysis Results:", font=("TkDefaultFont", 10, "bold"))
        output_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.output_text = tk.Text(
            frame,
            height=20,
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
            button_frame, text="Analyze", command=on_execute, width=20
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
        """Execute the analysis."""
        moves_dir = Path(form_data.get("moves_dir", self.default_config["moves_dir"]))
        
        if not moves_dir.exists():
            raise ValueError(f"Moves directory not found: {moves_dir}")
        
        print(f"Analyzing field effects in {moves_dir}...")
        
        analyzer = FieldEffectsAnalyzer(moves_dir)
        results = analyzer.analyze()
        
        print(f"Found {results['total_moves']} moves with field effects")
        print(f"Categorized into {results['categories']} categories")
        
        output = analyzer.get_formatted_output()
        
        # Display in output area if it exists
        if hasattr(self, 'output_text'):
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, output)
            self.output_text.config(state=tk.DISABLED)
        
        print(output)
