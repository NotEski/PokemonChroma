"""
Move Effects Analyzer Plugin

Analyzes all move effects in the Pokemon database to identify required functions
and variables for move implementation.
"""

import json
import re
import tkinter as tk
from collections import defaultdict
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase


class MoveAnalyzer:
    """Analyzes move effects to determine implementation requirements."""
    
    def __init__(self, moves_dir: Path):
        self.moves_dir = Path(moves_dir)
        self.short_effects = set()
        self.move_short_effects = {}
        self.required_functions = {}
        self.variable_needs = {}
    
    def extract_short_effects(self) -> Tuple[List[str], Dict[str, str]]:
        """Extract all unique short effects from move JSONs."""
        short_effects: Set[str] = set()
        move_short_effects: Dict[str, str] = {}
        
        if not self.moves_dir.exists():
            raise ValueError(f"Path {self.moves_dir} does not exist")
        
        json_files = sorted(self.moves_dir.glob("*.json"))
        
        for move_file in json_files:
            if move_file.name == "_index.json":
                continue
                
            try:
                with open(move_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract short effect
                if "effect_entries" in data and data["effect_entries"]:
                    effect_entry = data["effect_entries"][0]
                    if "short_effect" in effect_entry:
                        short_effect = effect_entry["short_effect"]
                        short_effects.add(short_effect)
                        move_name = move_file.stem
                        move_short_effects[move_name] = short_effect
            except Exception as e:
                pass
        
        self.short_effects = sorted(short_effects)
        self.move_short_effects = move_short_effects
        return sorted(list(short_effects)), move_short_effects
    
    def analyze_effects(self, short_effects: List[str]) -> Dict[str, Set[str]]:
        """Analyze effects to determine required functions and variables."""
        
        function_patterns = {
            "drain": r"drain|absorb|leech|restore hp",
            "recoil": r"recoil|backfire|user takes damage",
            "healing": r"heal|restore|recover|cure",
            "status_condition": r"burn|freeze|paralyze|poison|sleep|confuse|badly poison|toxic|infatuation|curse|taunt|encore|lock-on|mean look|perish|smiles|trapped|torment",
            "raise_stats": r"raise|increase|boost|up|sharpen|growth",
            "lower_stats": r"lower|reduce|decrease|down|lowers",
            "weather": r"weather|sandstorm|rain|hail|sunny|snow|shadow|mist|terrain|reflect|light screen|safeguard",
            "field_effect": r"field|terrain|screens|spikes|stealth rock|sticky web|hazard|entry hazard|trick room",
            "protect": r"protect|immune|block|shield|guard|safeguard|negate",
            "stat_swap": r"swap|switch|exchange|copy|mirror",
            "type_change": r"type change|becomes|changes type",
            "accuracy": r"accuracy|miss|hits surely|ignores evasion|never misses",
            "evasion": r"evasion|accuracy.*lower|miss",
            "multi_turn": r"next turn|charge|two turns|after|later|end of turn",
            "conditional": r"if|depends|based on|condition",
            "priority": r"priority|first|turn order",
            "item": r"item|held item|berry|orb|gem",
            "ability": r"ability|hidden power|nature",
            "flinch": r"flinch|back up",
            "trap": r"trap|bind|wrap|clamp|immobilize",
            "substitute": r"substitute|dummy|copy",
            "damage_scale": r"based on|hp percentage|opponent.*damage|user.*damage|target.*damage|level",
            "switch": r"switch|swap out|escape|flee",
            "forced_move": r"forced to|forced switch",
            "contact": r"contact|physical|punch|kick|blade",
            "spread": r"affect.*nearby|spread|around|adjacent",
        }
        
        required_functions = defaultdict(set)
        
        for effect in short_effects:
            effect_lower = effect.lower()
            
            for func_type, pattern in function_patterns.items():
                if re.search(pattern, effect_lower):
                    required_functions[func_type].add(effect)
        
        self.required_functions = dict(required_functions)
        return dict(required_functions)
    
    def extract_variable_needs(self, short_effects: List[str]) -> Dict[str, Set[str]]:
        """Identify variables that need to be tracked based on effects."""
        
        variable_patterns = {
            "status_condition": r"burn|freeze|paralyze|poison|sleep|confuse|badly poison|toxic|infatuation|curse|taunt|encore|lock-on|mean look|perish|smiles|trapped|torment|ability",
            "field_effects": r"spikes|stealth rock|sticky web|reflect|light screen|safeguard|trick room|weather|terrain|mist|hail|rain|sandstorm|sunny",
            "drain_recoil": r"drain|recoil|backfire|absorb|leech|user takes damage",
            "healing_percentage": r"heal|restore|recover|cure|hp",
            "stat_changes": r"raise|lower|increase|decrease|boost|down|up|sharpen",
            "type_tracking": r"type|becomes",
            "turn_counter": r"next turn|two turns|end of turn|after|later|charge",
            "target_tracking": r"target|opponent|user|selected|adjacent|nearby",
            "item_tracking": r"item|held item|berry|orb",
            "ability_tracking": r"ability|hidden power",
            "priority_tracking": r"priority|first|turn order",
            "damage_taken": r"damage.*taken|damage dealt|damage inflicted",
            "previous_state": r"previous|last|before|prior",
            "hit_count": r"hit|strike|times|hits",
            "accuracy_evasion": r"accuracy|evasion|miss|hits surely",
        }
        
        variable_needs = defaultdict(set)
        
        for effect in short_effects:
            effect_lower = effect.lower()
            
            for var_type, pattern in variable_patterns.items():
                if re.search(pattern, effect_lower):
                    variable_needs[var_type].add(effect)
        
        self.variable_needs = dict(variable_needs)
        return dict(variable_needs)
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report."""
        output = []
        output.append("=" * 100)
        output.append("POKEMON MOVE EFFECTS ANALYSIS REPORT")
        output.append("=" * 100)
        output.append(f"\nTotal Unique Short Effects: {len(self.short_effects)}\n")
        
        # SECTION 1: Summary
        output.append("\n" + "=" * 100)
        output.append("SUMMARY")
        output.append("=" * 100)
        output.append(f"Function categories identified: {len(self.required_functions)}")
        output.append(f"Variable types to track: {len(self.variable_needs)}")
        
        function_list = sorted(self.required_functions.items(), key=lambda x: len(x[1]), reverse=True)
        output.append(f"\nTop 10 Function Categories:")
        for func_name, effects in function_list[:10]:
            output.append(f"  {func_name}: {len(effects)} effects")
        
        variable_list = sorted(self.variable_needs.items(), key=lambda x: len(x[1]), reverse=True)
        output.append(f"\nTop 10 Variable Types:")
        for var_name, effects in variable_list[:10]:
            output.append(f"  {var_name}: {len(effects)} effects")
        
        # SECTION 2: Required Functions
        output.append("\n\n" + "=" * 100)
        output.append("REQUIRED FUNCTIONS FOR MOVE IMPLEMENTATION")
        output.append("=" * 100)
        
        for func_name, effects in function_list:
            output.append(f"\n{func_name.upper()} ({len(effects)} effects)")
            output.append("-" * 80)
            output.append(f"Example effects:")
            for effect in sorted(effects)[:3]:
                output.append(f"  • {effect}")
            if len(effects) > 3:
                output.append(f"  ... and {len(effects) - 3} more")
        
        # SECTION 3: Required Variables
        output.append("\n\n" + "=" * 100)
        output.append("REQUIRED VARIABLES TO TRACK")
        output.append("=" * 100)
        
        for var_name, effects in variable_list:
            output.append(f"\n{var_name.upper()} ({len(effects)} effects)")
            output.append("-" * 80)
            output.append(f"Example effects that need this:")
            for effect in sorted(effects)[:3]:
                output.append(f"  • {effect}")
            if len(effects) > 3:
                output.append(f"  ... and {len(effects) - 3} more")
        
        return "\n".join(output)


class Plugin(ToolPluginBase):
    """Move Effects Analyzer plugin."""
    
    name = "analyze_moves"
    version = "1.0.0"
    description = "Analyzes all move effects to identify implementation requirements"
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
            text="Scans all moves in the database and identifies:\n"
                 "• Function categories needed for move implementation\n"
                 "• Variables that must be tracked during battle",
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
            height=22,
            width=100,
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
        
        print(f"Analyzing moves in {moves_dir}...")
        
        analyzer = MoveAnalyzer(moves_dir)
        
        # Extract and analyze
        short_effects_list, move_effects = analyzer.extract_short_effects()
        analyzer.analyze_effects(short_effects_list)
        analyzer.extract_variable_needs(short_effects_list)
        
        print(f"Found {len(short_effects_list)} unique move effects")
        print(f"Identified {len(analyzer.required_functions)} function categories")
        print(f"Identified {len(analyzer.variable_needs)} variable types")
        
        # Generate report
        report = analyzer.generate_report()
        
        # Display in output area if it exists
        if hasattr(self, 'output_text'):
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, report)
            self.output_text.config(state=tk.DISABLED)
        
        print(report)
