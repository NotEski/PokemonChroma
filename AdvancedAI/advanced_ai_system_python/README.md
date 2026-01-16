# Advanced AI System - Python Port

A comprehensive, skill-gated AI system for Pokemon battle decision-making, ported from the Ruby Essentials Advanced AI system. Implements intelligent move selection, threat assessment, switching decisions, setup recognition, endgame optimization, and personality-based playstyles.

## Overview

The Advanced AI System coordinates multiple intelligence modules to make competitive battle decisions:

- **Move Scoring** (20+ factors): Type effectiveness, STAB, power, accuracy, priority, effects
- **Threat Assessment** (0-10 scale): Opponent danger evaluation
- **Switch Intelligence**: Type matchups, role fit, coverage analysis
- **Setup Recognition**: Detect and counter sweepers
- **Endgame Optimization**: 1v1 final battle scenarios
- **Move Prediction**: Opponent move pattern analysis
- **Role Detection**: Identify Pokemon roles (Sweeper, Tank, Support, etc.)
- **Field Effects**: Weather, terrain, screens, hazard awareness
- **Battle Personalities**: Aggressive, Defensive, Balanced, Hyper Offensive playstyles
- **Skill-Level Gating**: Features unlock at: 50 (core), 55 (setup), 60 (endgame), 65 (personalities), 85 (prediction), 90 (gimmicks), 100 (all)

## Installation

### Requirements
- Python 3.9+
- PyRight type checking
- Shared Pokemon module (engine)
- Move repository with tag system

### Setup

```bash
# Clone or add to your project
# Add to path or import from module

from advanced_ai_system_python import AdvancedAI, AISettings, AIPersonality
```

## Quick Start

### Basic Usage

```python
from advanced_ai_system_python import AdvancedAI, AISettings, AIPersonality

# Create settings with skill level 70
settings = AISettings(
    skill_level=70,
    use_move_memory=True,
    prefer_type_advantage=True,
)

# Initialize AI with balanced personality
ai = AdvancedAI(settings, personality=AIPersonality.BALANCED)

# Make a decision in battle
action = ai.choose_action(battle_manager, position)

# battle_manager.submit_action(action)
```

### Integration with Battle Manager

```python
# When opponent makes a move
ai.record_move_used(opponent_id, move_used)

# When opponent switches
ai.record_switch(opponent_id, pokemon_switched_to)

# Get threat assessment
threat_level, description = ai.get_threat_assessment(context)
```

## Architecture

### Module Organization

```
advanced_ai_system_python/
├── settings.py              # Configuration and feature gating
├── ai_context.py            # Battle state wrapper
├── ai_player.py             # AI player interface
├── move_scorer.py           # Move evaluation (20+ factors)
├── threat_assessment.py     # 0-10 threat scale
├── switch_intelligence.py   # Switching decisions
├── setup_recognition.py     # Setup threat detection
├── endgame_scenarios.py     # 1v1 optimization
├── prediction_system.py     # Move/switch prediction
├── role_detection.py        # Pokemon role identification
├── field_effects.py         # Weather/terrain/screens
├── move_memory.py           # Opponent move history
├── battle_personalities.py  # Personality modifiers
├── advanced_ai.py           # Main orchestrator
├── TAG_GAPS.md             # Move tag system documentation
└── test_integration.py      # Integration tests
```

### Data Flow

```
choose_action()
├── Create AI context from battle manager
├── Calculate threat assessment
├── Check endgame scenarios (skill >= 60)
├── Check setup threats (skill >= 55)
├── Evaluate switching (skill >= 50)
├── Score all available moves
├── Apply personality modifiers
└── Return best action (MoveAction or SwitchAction)
```

## Feature Gating

Features unlock based on skill level:

| Level | Features |
|-------|----------|
| 50-54 | Core move scoring, threat assessment |
| 55-59 | Setup threat detection and response |
| 60-64 | Endgame optimization (1v1 scenarios) |
| 65-84 | Personality-based decision modifiers |
| 85-89 | Move/switch prediction system |
| 90-99 | Gimmick handling (not yet implemented) |
| 100 | All features enabled |

### Checking Features

```python
ai = AdvancedAI(AISettings(skill_level=75))

# Check if feature enabled
if ai.is_feature_enabled("prediction"):
    # Use prediction system
    pass

# Get all status
status = ai.get_ai_status()
for feature, enabled in status['features_enabled'].items():
    print(f"{feature}: {enabled}")
```

## Personalities

### Types

1. **Aggressive** (1.4x damage, 0.6x healing)
   - Favors powerful attacking moves
   - Ignores defensive strategies
   - Rare switching

2. **Defensive** (1.8x healing, 1.5x status moves)
   - Prioritizes healing and protection
   - Sets screens and hazard removal
   - Switches readily

3. **Balanced** (1.0x all factors)
   - Standard competitive play
   - Situational decisions
   - Default personality

4. **Hyper Offensive** (1.8x damage, 0.2x healing)
   - Only maximum power moves
   - Never switches unless necessary
   - Ignores defense entirely

### Using Personalities

```python
# Create AI with specific personality
ai = AdvancedAI(settings, personality=AIPersonality.AGGRESSIVE)

# Personality affects:
# - Move scoring multipliers
# - Switch decision thresholds
# - Priority vs healing preference
```

## Move Scoring System

Move scores range from 0-200+, considering:

### Damage Factors (+30 to -30)
- Type effectiveness: +30 (super effective), -15 (not very effective)
- STAB: +25 (same-type attack bonus)
- Accuracy: -penalties for low accuracy
- Recoil/Drain: -30 (low HP recoil) or +healing bonus

### Special Factors (+5 to +60)
- Priority: +15 per priority level
- Setup moves: +30-40
- Healing moves: +40-60 (scales with opponent damage)
- Status moves: +10-20
- Field effects: ±10 (weather/terrain dependent)

### Personality Modifiers (×0.2 to ×1.8)
- Applied after base scoring
- Personality-specific move category preferences

## Threat Assessment

Threat scale: 0-10+

### Threat Factors
- **Stat stages** (+0.3 per attack stage, +0.2 per speed stage)
- **Type advantage** (×2 if weak, ×1.5 if resists, ×1.0 neutral)
- **Health** (0.5 full HP, -1.0 critical)
- **Moves** (+0.5 priority, +0.3 healing, +0.5 setup)

### Threat Levels
- 0-2: Minimal threat
- 2-4: Low threat
- 4-6: Moderate threat
- 6-8: High threat
- 8+: Critical threat

## Move Tag System

All move categorization uses tags (no hardcoded moves):

### Available Tags
- `HealMove`: Healing moves
- `SetupMove`: Stat-boosting setup
- `StatChangeMove`: Any stat modification
- `FlinchMove`: Flinch/paralysis
- `DrainMove`: Damage with heal portion
- `RecoilMove`: Damage with self-harm
- `HazardMove`: Entry hazard setup
- `HazardRemovalMove`: Removes hazards
- `ScreenMove`: Screen setup
- `StatusMove`: Status infliction
- `SwitchOutMove`: Forces switch
- `CriticalHitMove`: High crit rate
- `WeatherMove`: Weather setup
- `TerrainMove`: Terrain setup

### Tag Gaps

See [TAG_GAPS.md](TAG_GAPS.md) for documentation on:
- Multi-stat setup moves
- Weather-dependent effects
- Protect variant effects
- Hazard removal specifics
- Spread move identification
- OHKO move tagging
- Move accuracy variations
- Stat change amounts

## Configuration

### AISettings

```python
from advanced_ai_system_python import AISettings

settings = AISettings(
    skill_level=75,                      # 1-100
    use_move_memory=True,               # Track opponent moves
    prefer_type_advantage=True,         # Prioritize type matchups
    max_move_memory_size=10,           # Moves to remember
    hazard_preference=0.5,             # Preference for hazard setup (0-1)
    healing_threshold=0.5,             # HP threshold for healing (0-1)
)
```

## AI Context

The `AIContext` class provides safe access to battle state:

```python
from advanced_ai_system_python import AIContext

context = AIContext(battle_manager, position)

# Access battle info
active_mon = context.active_mon          # Current Pokemon
opponent_mon = context.opponent_mon      # Opponent Pokemon
weather = context.weather                # Current weather
terrain = context.terrain               # Current terrain

# Caching methods
context.set_threat_level(threat_value)
threat = context.get_threat_level()

context.set_move_memory(memory_object)
memory = context.get_move_memory()
```

## Testing

### Run Integration Tests

```bash
python test_integration.py

# Or with pytest
pytest test_integration.py -v
```

### Run Examples

```bash
python test_integration.py  # Runs all examples
```

## Porting Notes

This AI system is ported from Ruby Essentials Advanced AI system:
- **Original**: 26 files in AdvancedAI/Advanced AI System/
- **Port**: 15 modules + orchestrator in advanced_ai_system_python/
- **Key Changes**:
  - Tag-based move categorization (no hardcoded moves)
  - Type annotations for PyRight compatibility
  - External player pattern (no BattleManager integration)
  - Singles-focused (stubs for Doubles/Triples)
  - Skill-level gating for progressive feature unlock

## Compatibility

- **Python**: 3.9+
- **Type Checking**: PyRight strict mode
- **Engine**: Pokemon Fan Game (engine.battle, shared.pokemon modules)
- **Battle Format**: Singles (primary), Doubles/Triples (stubs)
- **AI Format**: External player, stateless decisions

## Future Enhancements

### v1.5
- Multi-stat setup move categorization
- Stat change amount specification
- Enhanced hazard removal tagging

### v2.0
- Weather-dependent move effects
- Protect variant sub-tags
- Move accuracy weather variations

### v2.5+
- Spread move identification (Doubles)
- OHKO move explicit tagging
- Gimmick handling (Terastallization, Dynamax, Z-Moves)
- Doubles/Triples full implementation

## Credits

- **Original Design**: Ruby Essentials Advanced AI System
- **Port & Enhancement**: Python implementation for Pokemon Fan Game
- **Type System**: PyRight-compliant annotations for safety
- **Tag System**: Move repository integration

## License

See parent project license.

## Support

For issues or questions:
1. Check [TAG_GAPS.md](TAG_GAPS.md) for move system limitations
2. Review test_integration.py for usage examples
3. Check AI context logging for decision traces
4. Reference move scorer for factor breakdown

## Version

**Advanced AI System v1.0.0 (Python Port)**
- 14 intelligence modules
- 9 skill levels / feature gates
- 4 personality types
- 20+ move scoring factors
- Full PyRight type annotations
