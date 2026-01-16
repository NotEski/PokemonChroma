"""
Script to analyze all moves in the pokeapi_database and compile:
1. All short effects
2. Required functions for move implementations
3. Required variables to track during battle
"""

import json
from pathlib import Path
from collections import defaultdict
import re

# Path to moves folder
MOVES_PATH = Path(__file__).parent.parent / "database_download" / "pokeapi_database" / "move"

def extract_short_effects():
    """Extract all unique short effects from move JSONs."""
    short_effects = set()
    move_short_effects = {}
    
    if not MOVES_PATH.exists():
        print(f"Error: Path {MOVES_PATH} does not exist")
        return short_effects, move_short_effects
    
    json_files = sorted(MOVES_PATH.glob("*.json"))
    print(f"Found {len(json_files)} move files")
    
    for move_file in json_files:
        if move_file.name == "_index.json":
            continue
            
        try:
            with open(move_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract short effect
            if "effect_entries" in data and data["effect_entries"]:
                effect_entry = data["effect_entries"][0]  # Get first entry (usually English)
                if "short_effect" in effect_entry:
                    short_effect = effect_entry["short_effect"]
                    short_effects.add(short_effect)
                    move_name = move_file.stem
                    move_short_effects[move_name] = short_effect
        except Exception as e:
            print(f"Error processing {move_file.name}: {e}")
    
    return sorted(short_effects), move_short_effects


def analyze_effects(short_effects):
    """Analyze effects to determine required functions and variables."""
    
    function_patterns = {
        # Damage/Healing
        "drain": r"drain|absorb|leech|restore hp",
        "recoil": r"recoil|backfire|user takes damage",
        "healing": r"heal|restore|recover|cure",
        
        # Status Effects
        "status_condition": r"burn|freeze|paralyze|poison|sleep|confuse|badly poison|toxic|infatuation|curse|taunt|encore|lock-on|mean look|perish|smiles|trapped|torment",
        
        # Stat Modifications
        "raise_stats": r"raise|increase|boost|up|sharpen|growth",
        "lower_stats": r"lower|reduce|decrease|down|down|lowers",
        
        # Field/Weather Effects
        "weather": r"weather|sandstorm|rain|hail|sunny|snow|shadow|mist|terrain|reflect|light screen|safeguard",
        "field_effect": r"field|terrain|screens|spikes|stealth rock|sticky web|hazard|entry hazard|trick room",
        
        # Pokemon Effects
        "protect": r"protect|immune|block|shield|guard|safeguard|negate",
        "stat_swap": r"swap|switch|exchange|copy|mirror",
        "type_change": r"type change|becomes|changes type",
        
        # Accuracy/Evasion
        "accuracy": r"accuracy|miss|hits surely|ignores evasion|never misses",
        "evasion": r"evasion|accuracy.*lower|miss",
        
        # Multi-turn/Conditional
        "multi_turn": r"next turn|charge|two turns|after|later|end of turn",
        "conditional": r"if|depends|based on|condition",
        
        # Priority
        "priority": r"priority|first|turn order",
        
        # Item/Pokemon Effects
        "item": r"item|held item|berry|orb|gem",
        "ability": r"ability|hidden power|nature",
        
        # Battle Effects
        "flinch": r"flinch|back up",
        "trap": r"trap|bind|wrap|clamp|immobilize",
        "substitute": r"substitute|dummy|copy",
        
        # Damage Scaling
        "damage_scale": r"based on|hp percentage|opponent.*damage|user.*damage|target.*damage|level",
        
        # Switch/Movement
        "switch": r"switch|swap out|escape|flee",
        "forced_move": r"forced to|forced switch",
        
        # Special Mechanics
        "contact": r"contact|physical|punch|kick|blade",
        "spread": r"affect.*nearby|spread|around|adjacent",
    }
    
    required_functions = defaultdict(set)
    
    for effect in short_effects:
        effect_lower = effect.lower()
        
        for func_type, pattern in function_patterns.items():
            if re.search(pattern, effect_lower):
                required_functions[func_type].add(effect)
    
    return required_functions


def extract_variable_needs(short_effects):
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
    
    return variable_needs


def generate_report(short_effects, required_functions, variable_needs, move_short_effects):
    """Generate comprehensive analysis report."""
    
    output = []
    output.append("=" * 100)
    output.append("POKEMON MOVE EFFECTS ANALYSIS REPORT")
    output.append("=" * 100)
    output.append(f"\nTotal Unique Short Effects: {len(short_effects)}\n")
    
    # SECTION 1: All Short Effects
    output.append("\n" + "=" * 100)
    output.append("SECTION 1: ALL SHORT EFFECTS")
    output.append("=" * 100)
    output.append(f"\n({len(short_effects)} unique effects)\n")
    
    for i, effect in enumerate(short_effects, 1):
        output.append(f"{i:3d}. {effect}")
    
    # SECTION 2: Required Functions
    output.append("\n\n" + "=" * 100)
    output.append("SECTION 2: REQUIRED FUNCTIONS FOR MOVE IMPLEMENTATION")
    output.append("=" * 100)
    output.append("\nThe following functions would need to be implemented to handle all move effects:\n")
    
    function_list = sorted(required_functions.items(), key=lambda x: len(x[1]), reverse=True)
    
    for func_name, effects in function_list:
        output.append(f"\n{func_name.upper()} ({len(effects)} effects)")
        output.append("-" * 80)
        output.append(f"Purpose: Handle moves that {func_name.replace('_', ' ')} mechanics")
        output.append(f"Example effects:")
        for effect in sorted(effects)[:3]:
            output.append(f"  • {effect}")
        if len(effects) > 3:
            output.append(f"  ... and {len(effects) - 3} more")
    
    # SECTION 3: Required Variables
    output.append("\n\n" + "=" * 100)
    output.append("SECTION 3: REQUIRED VARIABLES TO TRACK")
    output.append("=" * 100)
    output.append("\nThe following variables would need to be tracked during battle:\n")
    
    variable_list = sorted(variable_needs.items(), key=lambda x: len(x[1]), reverse=True)
    
    for var_name, effects in variable_list:
        output.append(f"\n{var_name.upper()} ({len(effects)} effects)")
        output.append("-" * 80)
        output.append(f"Example effects that need this:")
        for effect in sorted(effects)[:3]:
            output.append(f"  • {effect}")
        if len(effects) > 3:
            output.append(f"  ... and {len(effects) - 3} more")
    
    # SECTION 4: Summary Recommendations
    output.append("\n\n" + "=" * 100)
    output.append("SECTION 4: SUMMARY & RECOMMENDATIONS")
    output.append("=" * 100)
    output.append(f"""
FUNCTION SUMMARY:
- Total unique function categories needed: {len(required_functions)}
- Most common: {function_list[0][0]} ({len(function_list[0][1])} effects)

VARIABLE SUMMARY:
- Total unique variable types to track: {len(variable_needs)}
- Most critical: {variable_list[0][0]} ({len(variable_list[0][1])} effects)

ALREADY IDENTIFIED VARIABLES (from requirements):
✓ status_condition - Applied to affected pokemon
✓ field_effects - Persistent environmental changes
✓ drain_recoil - Damage scaling mechanics
✓ healing_percentage - HP restoration calculations

ADDITIONAL VARIABLES NEEDED:
""")
    
    additional_vars = [var for var, _ in variable_list if var not in 
                      ["status_condition", "field_effects", "drain_recoil", "healing_percentage"]]
    
    for var in additional_vars:
        count = len(variable_needs[var])
        output.append(f"  • {var}: {count} effects require this")
    
    # SECTION 5: Detailed function breakdown
    output.append("\n\n" + "=" * 100)
    output.append("SECTION 5: DETAILED FUNCTION BREAKDOWN")
    output.append("=" * 100)
    
    function_details = {
        "status_condition": "Apply/remove status conditions (burn, freeze, paralyze, sleep, etc.)",
        "damage_scale": "Calculate scaled damage (based on HP %, level, opponent damage, etc.)",
        "drain": "Drain a percentage of damage dealt to heal the user",
        "recoil": "Inflict recoil damage to the user",
        "healing": "Restore HP (fixed amount or percentage)",
        "raise_stats": "Increase pokemon stats (Attack, Defense, Speed, etc.)",
        "lower_stats": "Decrease pokemon stats",
        "weather": "Set/remove weather effects (rain, hail, sandstorm, sunny, etc.)",
        "field_effect": "Set/remove field/terrain effects (spikes, stealth rock, trick room, etc.)",
        "protect": "Block/protect from damage or effects",
        "stat_swap": "Swap, copy, or exchange stats between pokemon",
        "type_change": "Change a pokemon's type",
        "accuracy": "Guarantee hit regardless of accuracy/evasion",
        "evasion": "Modify accuracy or evasion",
        "multi_turn": "Handle multi-turn moves (charge, then attack)",
        "conditional": "Execute based on conditions (weather, terrain, stat values, etc.)",
        "priority": "Handle priority mechanics",
        "item": "Interact with held items",
        "ability": "Interact with abilities",
        "flinch": "Cause flinching (pokemon loses turn)",
        "trap": "Trap pokemon preventing switch-out",
        "substitute": "Create substitute or dummy",
        "switch": "Force switch or allow switch",
        "forced_move": "Force pokemon to use specific move",
        "contact": "Handle contact-based move mechanics",
        "spread": "Affect multiple/adjacent pokemon",
    }
    
    for func_name in sorted(required_functions.keys()):
        if func_name in function_details:
            output.append(f"\n• {func_name.upper()}")
            output.append(f"  Description: {function_details[func_name]}")
            output.append(f"  Effects affected: {len(required_functions[func_name])}")
    
    return "\n".join(output)


def main():
    """Main execution."""
    print("Analyzing Pokemon moves...")
    
    short_effects, move_short_effects = extract_short_effects()
    
    if not short_effects:
        print("No short effects found!")
        return
    
    print(f"Found {len(short_effects)} unique short effects")
    
    required_functions = analyze_effects(short_effects)
    variable_needs = extract_variable_needs(short_effects)
    
    report = generate_report(short_effects, required_functions, variable_needs, move_short_effects)
    
    # Save report
    output_file = Path(__file__).parent / "move_analysis_report.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {output_file}")
    print("\n" + "=" * 100)
    print(f"ANALYSIS COMPLETE")
    print("=" * 100)
    print(f"Total unique short effects: {len(short_effects)}")
    print(f"Function categories identified: {len(required_functions)}")
    print(f"Variable types to track: {len(variable_needs)}")
    
    # Print summary to console
    print("\nTop 10 Function Categories by Effect Count:")
    function_list = sorted(required_functions.items(), key=lambda x: len(x[1]), reverse=True)
    for func_name, effects in function_list[:10]:
        print(f"  {func_name}: {len(effects)} effects")
    
    print("\nTop 10 Variable Types by Effect Count:")
    variable_list = sorted(variable_needs.items(), key=lambda x: len(x[1]), reverse=True)
    for var_name, effects in variable_list[:10]:
        print(f"  {var_name}: {len(effects)} effects")


if __name__ == "__main__":
    main()
