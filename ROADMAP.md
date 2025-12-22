# BattleManager - Feature Checklist

## Data & Setup
- [x] Pokemon factory to import them from the pokeapi database
- [x] Convert pokeapi json files into manageable per-species data files
- [ ] Convert GIF sprites into sprite sheets with metadata for animation

## Core Battle Mechanics
- [x] Move Priority System (moves processed in priority order)
- [x] Speed-based Turn Order (faster pokemon moves first)
- [x] Accuracy/Evasion Checks (moves can miss) - *basic function exists but not integrated into battle flow*
- [x] Type Effectiveness Application (super effective, not very effective, etc.)
- [x] PP Deduction (subtract PP when moves are used)
- [x] Critical Hit Calculation (fully implemented and integrated)
- [ ] Multi-target Move Support (moves hitting multiple pokemon) - *data structure exists but not implemented*
- [ ] Weather Effect Duration & Expiration - *partial: weather modifies damage but duration not tracked*
- [ ] Terrain Effect Application - *data structure exists but not implemented*
- [ ] Field Effect Management (Reflect, Light Screen, etc.) - *data structure exists but not implemented*

## Status Conditions
- [ ] Status Condition Infliction (applying status from moves) - *data structures exist but not implemented*
- [ ] Paralysis Effects (speed reduction, 25% chance to not move)
- [ ] Sleep Effects (can't move for 1-3 turns)
- [ ] Freeze Effects (can't move, 20% thaw chance each turn)
- [ ] Poison Damage (lose HP each turn)
- [x] Burn Damage (physical attack reduction implemented in damage calculation) - *HP loss per turn not implemented*
- [ ] Confusion (chance to hurt self)
- [ ] Flinching (checked but not implemented)
- [ ] Bound/Trapped Status (partially bound, wrap, etc.)

## Stat Stages
- [ ] Stat Stage Changes (moves that boost/lower stats) - *data structures exist but not applied*
- [ ] Stat Stage Application to Calculations - *battle state tracks stages but not used in stat calculations*
- [ ] Accuracy/Evasion Stage Effects - *stages tracked but not applied*

## Pokemon Features
- [ ] Experience Points (EXP gain from battles) - *experience field exists in Pokemon model but not calculated*
- [ ] Level Up System - *level field exists but leveling mechanics not implemented*
- [ ] Abilities (normal abilities) - *data structures and repository exist but not applied in battle*
- [ ] Hidden Abilities - *data structures exist but not implemented*
- [ ] Held Items (item effects during battle)
- [ ] Used Items (potions, status heals, etc.)

## Move Effects
- [ ] Multi-hit Moves (2-5 hits, etc.) - *min_hits/max_hits fields exist but not implemented*
- [ ] Recoil Damage (take damage from own move) - *drain field can be negative for recoil but not implemented*
- [ ] Healing Moves (Recover, Synthesis, etc.) - *healing field exists but not implemented*
- [ ] Draining Moves (absorb HP from target) - *drain field exists but not implemented*
- [ ] Protection Moves (Protect, Detect)
- [x] Priority Moves (+1, +2, etc. priority) - *priority field exists but not used*
- [ ] Two-turn Moves (Fly, Dig, Solar Beam)
- [ ] Charge Moves (must charge before attacking)

## Battle Actions
- [ ] Use Item Implementation (potions, pokeballs, etc.) - *action structure exists but process_item_use is empty*
- [x] Flee/Run Away Logic (implemented with escape calculator)
- [x] Switch Pokemon (implemented in battle_manager)
- [x] Catch Pokemon (catch_calculator fully implemented)
- [ ] Force Switch When Pokemon Faints

## Battle Flow
- [ ] Battle End Conditions (win/loss detection) - *partial: escape ends battle, no win/loss for faints*
- [ ] Fainted Pokemon Switch Enforcement - *faint detection exists but no forced switch*
- [ ] Turn-by-turn Battle Logging (BattleLogEntry population) - *BattleLogEntry created but not fully populated*
- [ ] End-of-Turn Effects (poison damage, weather damage, etc.)
- [ ] Switch-in Trigger Effects (abilities/items on switch) - *TODO comment exists but not implemented*
- [x] Prevent Fainted Pokemon from Acting - *Pokemon can faint (HP set to 0)*

## Double Battle Specific
- [ ] DoubleBattleManager Implementation (currently empty)
- [ ] Target Selection Validation (can't target ally with some moves)
- [ ] Multi-pokemon Turn Processing
- [ ] Spread Move Damage Calculation

## Advanced Features (Future)
- [ ] Triple Battles
- [ ] Rotation Battles
- [ ] Horde Battles
- [ ] Mega Evolution
- [ ] Z-Moves
- [ ] Dynamax/Gigantamax
- [ ] Terastallization 



More assets - Animated and static
- Gen6 - https://docs.google.com/spreadsheets/d/1Gn0UORn-unvcbUeQhQdEBz0ADNcH49BZZqQ1dpXm9eo/edit?gid=0#gid=0
- Gen7 - https://docs.google.com/spreadsheets/d/1FMcHbSKEWZc7v2Ur4cyJjT_NhO0gqXyU9kDhsOQhlBQ/edit?gid=0#gid=0
- Gen8 - https://docs.google.com/spreadsheets/d/1acgzAjh0dnFRQnjZu8kSjS177rKCzpFfEHRLtwuuXRU/edit?gid=0#gid=0
- Gen9 - https://docs.google.com/spreadsheets/d/1MCjDktTOOFjLKM5C-RW6SfBQGkjlxDSCZAZDma_ItuA/edit?gid=0#gid=0

