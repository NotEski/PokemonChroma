#!/usr/bin/env python3
"""
Analyze field effects in moves, excluding weather and terrain.
"""

import json
from pathlib import Path
from collections import defaultdict

def main():
    moves_dir = Path("pokeapi_database/move")
    
    # Track all moves that mention "field" or specific effects
    field_effect_moves = []
    all_effects = set()
    
    # Exclude weather and terrain related phrases
    exclude_phrases = [
        'weather', 'electric terrain', 'grassy terrain', 'misty terrain', 'psychic terrain',
        'rain', 'sunny', 'hail', 'sandstorm', 'snow'
    ]
    
    for move_file in sorted(moves_dir.glob("*.json")):
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
    
    # Print results
    print("=== FIELD EFFECTS (Excluding Weather & Terrain) ===\n")
    print(f"Total moves with field effects: {len(field_effect_moves)}\n")
    
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
    
    for effect_type, moves in sorted(effect_groups.items()):
        print(f"\n{effect_type.upper()} ({len(moves)} moves):")
        print("-" * 60)
        for move in moves:
            print(f"  • {move['name']}: {move['effect'][:80]}...")
    
    print(f"\n\n=== UNIQUE FIELD EFFECT TYPES ===")
    print(f"Total categories: {len(effect_groups)}")
    for effect_type in sorted(effect_groups.keys()):
        print(f"  • {effect_type}")

if __name__ == "__main__":
    main()
