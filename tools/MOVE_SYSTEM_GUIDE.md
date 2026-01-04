# Pokemon Move System Implementation Guide

## Analysis Summary

A comprehensive analysis has been performed on all **938 moves** in the PokeAPI database, extracting and categorizing all **416 unique short effects**.

This analysis identifies:
- 25 distinct function categories needed
- 15 variable types to track during battle
- Detailed breakdown of each mechanic

---

## SECTION 1: REQUIRED FUNCTIONS (25 Categories)

### Priority 1: High Impact Functions (40+ effects each)
These cover the majority of move mechanics:

1. **RAISE_STATS** (77 effects) - **DONE**
   - Increases pokemon stats (Attack, Defense, Special Attack, Special Defense, Speed, Accuracy, Evasion)
   - Most common mechanic in the move pool
   - Example: "Has a 10% chance to raise the user's Attack by one stage"

2. **LOWER_STATS** (61 effects) - **DONE**
   - Decreases pokemon stats
   - Nearly as common as raise_stats
   - Example: "Has a 100% chance to lower the target's Special Attack by one stage"

3. **STATUS_CONDITION** (60 effects) - **DONE**
   - Apply major status effects: Burn, Freeze, Paralyze, Sleep, Poison, Badly Poison
   - Apply secondary conditions: Confusion, Infatuation, Curse
   - Remove status conditions
   - Example: "Burns the target"

4. **MULTI_TURN** (48 effects)
   - Handle moves that require setup/charge turns
   - Handle moves that persist over multiple turns
   - Track turn counter for multi-turn effects
   - Example: "Carries the target high into the air, dodging all attacks against either, and drops it next turn"

5. **CONDITIONAL** (42 effects)
   - Execute effects based on battle conditions
   - Weather-dependent effects
   - Terrain-dependent effects
   - Stat-dependent effects
   - Example: "Has double power against Pokémon that have less than half their max HP remaining"

6. **DAMAGE_SCALE** (37 effects)
   - Calculate scaled damage based on various factors
   - HP percentage scaling
   - Level scaling
   - Opponent's damage comparison
   - User's damage comparison
   - Example: "Damages the target for 75% of its remaining HP"

### Priority 2: Medium Impact Functions (15-40 effects each)

7. **WEATHER** (28 effects) - **DONE**
   - Set/remove weather effects: Rain, Sunny, Hail, Sandstorm, Snow, Shadow Sky
   - Duration tracking (typically 5 turns)
   - Example: "Changes the weather to rain for five turns"

8. **HEALING** (25 effects) - **DONE**
   - Restore HP (fixed amount or percentage)
   - Self-healing
   - Ally healing
   - Weather-affected healing
   - Example: "Heals the user by half its max HP"

9. **STAT_SWAP** (22 effects)
   - Swap stats between pokemon
   - Copy stats from target
   - Exchange specific stats
   - Average stats
   - Example: "Exchanges the user's Speed with the target's"

10. **PROTECT** (17 effects)
    - Block/protect from damage or effects
    - Conditional protection
    - Example: "Blocks damaging attacks and damages attacking Pokémon for 1/8 their max HP"

### Priority 3: Lower Impact Functions (5-15 effects each)

11. **FIELD_EFFECT** (15 effects)
    - Set/remove field effects: Spikes, Stealth Rock, Sticky Web, Trick Room
    - Reflect/Light Screen
    - Terrain changes
    - Example: "Covers the opposing field, lowering opponents' Speed by one stage upon switching in"

12. **SWITCH** (14 effects)
    - Force switch pokemon
    - Allow trainer to switch out
    - Pass effects to replacement
    - Example: "Allows the trainer to switch out the user and pass effects along to its replacement"

13. **ITEM** (13 effects)
    - Interact with held items
    - Steal items
    - Give items
    - Use/consume items
    - Example: "Gives the user's held item to the target"

14. **RECOIL** (11 effects) - **DONE**
    - Inflict recoil damage to user
    - Percentage or fixed amount
    - Conditional recoil
    - Example: "If the user misses, it takes half the damage it would have inflicted in recoil"

15. **ACCURACY** (11 effects)
    - Guarantee hit regardless of accuracy/evasion
    - Ignore evasion modifications
    - Example: "Guarantees a critical hit with the user's next move"

16. **EVASION** (9 effects)
    - Modify accuracy or evasion
    - Reduce opponent accuracy
    - Increase user evasion
    - Example: "Has a 30% chance to lower the target's accuracy by one stage"

17. **FLINCH** (10 effects)
    - Cause flinching (pokemon loses turn)
    - Conditional flinch
    - Example: "Has a 20% chance to make the target flinch"

### Priority 4: Niche Functions (1-5 effects each)

18. **DRAIN** (4 effects) - Drain percentage of damage to heal user
19. **ABILITY** (6 effects) - Change/copy pokemon abilities
20. **TYPE_CHANGE** (5 effects) - Change pokemon types
21. **PRIORITY** (8 effects) - Handle priority mechanics
22. **CONTACT** (6 effects) - Handle contact-based move effects
23. **SPREAD** (10 effects) - Affect multiple/adjacent pokemon
24. **TRAP** (2 effects) - Trap pokemon preventing switch-out
25. **FORCED_MOVE** (1 effect) - Force pokemon to use specific move
26. **SUBSTITUTE** (1 effect) - Create substitute or dummy

---

## SECTION 2: REQUIRED VARIABLES TO TRACK (15 Types)

### Critical Variables (50+ effects)

1. **TARGET_TRACKING** (318 effects) - ESSENTIAL
   - Which pokemon is targeted
   - Multiple targets vs single target
   - User's own pokemon (for self-affecting moves)
   - Affects: Nearly every move needs proper target information

2. **STAT_CHANGES** (129 effects) - ESSENTIAL
   - Current stat modification levels
   - Track changes per pokemon per stat
   - Persistence across turns
   - Reset on switch-out
   - Example stats: Attack, Defense, Sp. Atk, Sp. Def, Speed, Accuracy, Evasion

3. **STATUS_CONDITION** (66 effects) - ALREADY IDENTIFIED ✓
   - Current major status (Burn, Freeze, Paralyze, Sleep, Poison, Badly Poison)
   - Turn counters for temporary status
   - Secondary conditions (Confusion, Infatuation, Curse, Taunt, Encore, etc.)

### Important Variables (20-50 effects)

4. **HEALING_PERCENTAGE** (51 effects) - ALREADY IDENTIFIED ✓
   - Healing amounts (1/8, 1/4, 1/3, 1/2, 2/3, 3/4)
   - Weather-affected healing
   - Terrain-affected healing
   - Drain percentages

5. **TURN_COUNTER** (48 effects)
   - Multi-turn move duration
   - Weather duration
   - Field effect duration
   - Temporary stat boost duration
   - Status condition duration
   - Move disable counter
   - Example: "For five turns..." mechanics

6. **HIT_COUNT** (48 effects)
   - Multi-hit move tracking (2-5 hits) - **DONE**
   - Consecutive hit tracking
   - Power scaling with hits
   - Example: "Hits 2-5 times in one turn"

7. **FIELD_EFFECTS** (31 effects) - ALREADY IDENTIFIED ✓
   - Current weather
   - Current terrain
   - Persistent environmental effects (Spikes, Stealth Rock, etc.)
   - Screen effects (Reflect, Light Screen)
   - Trick Room status

### Moderate Variables (10-30 effects)

8. **PREVIOUS_STATE** (27 effects)
   - Last move used (for move copying/disabling)
   - Last pokemon switched in
   - Previous types
   - Previous moves
   - Example: "Changes the user's type to a random type either resistant or immune to the last move used against it"

9. **TYPE_TRACKING** (21 effects)
   - Current pokemon type(s)
   - Type additions/removals
   - Type changes
   - Type interactions with field effects

10. **ACCURACY_EVASION** (17 effects)
    - Accuracy modifications
    - Evasion modifications
    - Whether hit always lands
    - Example: "Forces the target to have no evasion"

11. **ITEM_TRACKING** (13 effects)
    - Held item identification
    - Item consumption
    - Item transferal
    - Berry identification

### Niche Variables (5-10 effects)

12. **DAMAGE_TAKEN** (9 effects)
    - Total damage dealt to all targets
    - Damage to specific target
    - Used for drain/recoil calculations

13. **PRIORITY_TRACKING** (8 effects)
    - Move priority level
    - Turn order mechanics
    - First move after entry

14. **ABILITY_TRACKING** (6 effects)
    - Current ability
    - Ability changes/copies
    - Ability suppression

### Additional Variables Needed (complementary to above)

15. **DRAIN_RECOIL** (15 effects) - ALREADY IDENTIFIED ✓
    - Drain/recoil percentages
    - Healing/damage calculations

---

## SECTION 3: RECOMMENDED IMPLEMENTATION PRIORITIES

### Phase 1: Core Battle System (Foundation)
1. **TARGET_TRACKING** - Must be in place for all moves
2. **RAISE_STATS** / **LOWER_STATS** - Most used mechanics
3. **STATUS_CONDITION** - Core battle mechanic
4. **DAMAGE_SCALE** - Fundamental damage calculation

### Phase 2: Environmental System
5. **WEATHER** - Affects many moves and abilities
6. **FIELD_EFFECT** - Important for strategy
7. **TURN_COUNTER** - Enables duration tracking

### Phase 3: Extended Mechanics
8. **HEALING** - Quality of life / strategy
9. **STAT_SWAP** - Special interaction mechanics
10. **MULTI_TURN** - Charge-up moves
11. **CONDITIONAL** - Logic gates for effects

### Phase 4: Polish & Edge Cases
12. All remaining functions
13. All remaining variable types

---

## SECTION 4: DATA STRUCTURE RECOMMENDATIONS

### Pokemon State Object (per pokemon in battle)
```python
pokemon_state = {
    "id": "string",
    "current_hp": "int",
    "status_condition": "enum (none, burn, freeze, paralyze, sleep, poison, badly_poison)",
    "secondary_conditions": ["confusion", "infatuation", "curse", "taunt", "encore", ...],
    "stat_changes": {
        "attack": 0,           # range: -6 to +6
        "defense": 0,
        "sp_attack": 0,
        "sp_defense": 0,
        "speed": 0,
        "accuracy": 0,
        "evasion": 0,
    },
    "type_current": ["type1", "type2"],  # can be modified mid-battle
    "item": "string or null",
    "ability": "string",
    "last_move_used": "string",
    "turn_active": "int",  # counter for various durations
    "hits_this_turn": "int",  # for multi-hit tracking
    "damage_taken_this_turn": "int",  # for drain calculations
}
```

### Battle Field Object
```python
field_state = {
    "weather": "enum (none, rain, sunny, hail, sandstorm, snow, shadow_sky)",
    "weather_turns_remaining": "int",
    "terrain": "enum (none, electric, psychic, grassy, misty)",
    "terrain_turns_remaining": "int",
    "side_effects": {
        "opponent": ["spikes_1", "stealth_rock", "sticky_web", "reflect", "light_screen", ...],
        "user": [...],
    },
    "trick_room_active": "bool",
    "trick_room_turns_remaining": "int",
}
```

---

## SECTION 5: NEXT STEPS

1. **Review this report** - Understand the scope of mechanics needed
2. **Design data structures** - For pokemon state and battle field
3. **Implement Priority 1 functions** - Foundation functions
4. **Create test cases** - For each mechanic
5. **Build incrementally** - Phase by phase approach
6. **Document implementations** - As you build

---

## APPENDIX: Complete Short Effects List

See `move_analysis_report.txt` for the complete list of all 416 unique short effects, organized by category and frequency.

---

**Report Generated:** January 4, 2026  
**Analysis Scope:** 938 moves from PokeAPI database  
**Unique Effects Found:** 416  
**Function Categories:** 25  
**Variable Types:** 15
