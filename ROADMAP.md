# BattleManager - Feature Checklist

## Data & Setup
- [ ] Pokemon factory to import them from the pokeapi database
- [ ] Convert pokeapi json files into manageable per-species data files
- [ ] Convert GIF sprites into sprite sheets with metadata for animation

## Core Battle Mechanics
- [ ] Move Priority System (moves processed in priority order)
- [ ] Speed-based Turn Order (faster pokemon moves first)
- [ ] Accuracy/Evasion Checks (moves can miss)
- [ ] Type Effectiveness Application (super effective, not very effective, etc.)
- [x] PP Deduction (subtract PP when moves are used)
- [ ] Critical Hit Calculation (implemented, needs integration)
- [ ] Multi-target Move Support (moves hitting multiple pokemon)
- [ ] Weather Effect Duration & Expiration
- [ ] Terrain Effect Application
- [ ] Field Effect Management (Reflect, Light Screen, etc.)

## Status Conditions
- [ ] Status Condition Infliction (applying status from moves)
- [ ] Paralysis Effects (speed reduction, 25% chance to not move)
- [ ] Sleep Effects (can't move for 1-3 turns)
- [ ] Freeze Effects (can't move, 20% thaw chance each turn)
- [ ] Poison Damage (lose HP each turn)
- [ ] Burn Damage (lose HP each turn, physical attack reduction - partial)
- [ ] Confusion (chance to hurt self)
- [ ] Flinching (checked but not implemented)
- [ ] Bound/Trapped Status (partially bound, wrap, etc.)

## Stat Stages
- [ ] Stat Stage Changes (moves that boost/lower stats)
- [ ] Stat Stage Application to Calculations
- [ ] Accuracy/Evasion Stage Effects

## Pokemon Features
- [ ] Experience Points (EXP gain from battles)
- [ ] Level Up System
- [ ] Abilities (normal abilities)
- [ ] Hidden Abilities
- [ ] Held Items (item effects during battle)
- [ ] Used Items (potions, status heals, etc.)

## Move Effects
- [ ] Multi-hit Moves (2-5 hits, etc.)
- [ ] Recoil Damage (take damage from own move)
- [ ] Healing Moves (Recover, Synthesis, etc.)
- [ ] Draining Moves (absorb HP from target)
- [ ] Protection Moves (Protect, Detect)
- [ ] Priority Moves (+1, +2, etc. priority)
- [ ] Two-turn Moves (Fly, Dig, Solar Beam)
- [ ] Charge Moves (must charge before attacking)

## Battle Actions
- [ ] Use Item Implementation (potions, pokeballs, etc.)
- [ ] Flee/Run Away Logic
- [ ] Switch Pokemon (partially implemented)
- [ ] Catch Pokemon (empty catch_calculator.py)
- [ ] Force Switch When Pokemon Faints

## Battle Flow
- [ ] Battle End Conditions (win/loss detection)
- [ ] Fainted Pokemon Switch Enforcement
- [ ] Turn-by-turn Battle Logging (BattleLogEntry population)
- [ ] End-of-Turn Effects (poison damage, weather damage, etc.)
- [ ] Switch-in Trigger Effects (abilities/items on switch)
- [ ] Prevent Fainted Pokemon from Acting

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