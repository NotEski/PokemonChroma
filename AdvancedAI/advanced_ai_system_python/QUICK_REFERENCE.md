"""
Quick Reference Guide - Advanced AI System

Fast lookup for common tasks and API reference.
"""

# ============================================================================
# QUICK START
# ============================================================================

"""
1. Import the AI system
   from advanced_ai_system_python import AdvancedAI, AISettings, AIPersonality

2. Create configuration
   settings = AISettings(skill_level=70)

3. Initialize AI
   ai = AdvancedAI(settings, personality=AIPersonality.BALANCED)

4. Make decisions
   action = ai.choose_action(battle_manager, position)

5. Record observations
   ai.record_move_used(opponent_id, move)
   ai.record_switch(opponent_id, pokemon)
"""


# ============================================================================
# SKILL LEVELS & FEATURES
# ============================================================================

"""
50-54:  Core AI
        - Move scoring with 20+ factors
        - Threat assessment
        - Type advantage analysis
        
55-59:  + Setup Recognition
        - Detect sweeper setups
        - Predict sweep potential
        
60-64:  + Endgame Optimization
        - 1v1 final battle handling
        - Priority move weighting
        
65-84:  + Personalities
        - Aggressive, Defensive, Balanced, Hyper-Offensive
        
85-89:  + Prediction System
        - Move pattern prediction
        - Switch probability
        
90-99:  + Gimmicks (placeholder)
        
100:    All features enabled
"""


# ============================================================================
# COMMON API CALLS
# ============================================================================

"""
# Make a decision
action = ai.choose_action(battle_manager, position)

# Record moves (for memory/prediction)
ai.record_move_used(battler_id, move_object)

# Record switches (for prediction)
ai.record_switch(battler_id, pokemon_object)

# Check feature availability
enabled = ai.is_feature_enabled("feature_name")

# Get status report
status = ai.get_ai_status()

# Get threat assessment
threat_level, description = ai.get_threat_assessment(context)
"""


# ============================================================================
# THREAT LEVELS
# ============================================================================

"""
Threat Scale: 0 to 10+

0-2:    Minimal threat - Attack normally
2-4:    Low threat - Consider switching if bad matchup
4-6:    Moderate threat - Switch if type disadvantage
6-8:    High threat - Prioritize survival/response
8+:     Critical threat - Use defensive moves or switch
"""


# ============================================================================
# PERSONALITIES
# ============================================================================

"""
Aggressive         (1.4x damage, 0.6x healing)
  - Favor powerful moves
  - Ignore defense
  - Rarely switch

Defensive          (0.8x damage, 1.8x healing)
  - Prioritize healing
  - Set screens
  - Switch readily

Balanced           (1.0x all)
  - Standard play
  - Situational decisions
  - Default

Hyper Offensive    (1.8x damage, 0.2x healing)
  - Only max power
  - Never heal
  - No switching
"""


# ============================================================================
# MOVE TAG CATEGORIES
# ============================================================================

"""
move.has_tag("HealMove")              # Healing moves
move.has_tag("SetupMove")             # Stat boosters
move.has_tag("StatChangeMove")        # Any stat change
move.has_tag("FlinchMove")            # Flinch/paralysis
move.has_tag("DrainMove")             # Damage + heal
move.has_tag("RecoilMove")            # Damage + self-harm
move.has_tag("HazardMove")            # Entry hazards
move.has_tag("HazardRemovalMove")     # Removes hazards
move.has_tag("ScreenMove")            # Screen setup
move.has_tag("StatusMove")            # Status infliction
move.has_tag("SwitchOutMove")         # Forced switch
move.has_tag("CriticalHitMove")       # High crit
move.has_tag("WeatherMove")           # Weather setup
move.has_tag("TerrainMove")           # Terrain setup
"""


# ============================================================================
# CONFIGURATION
# ============================================================================

"""
AISettings(
    skill_level=75,                    # 1-100
    use_move_memory=True,              # Track opponent moves
    prefer_type_advantage=True,        # Prioritize type matchups
    max_move_memory_size=10,           # Moves to remember
    hazard_preference=0.5,             # Hazard setup preference
    healing_threshold=0.5,             # Heal when below this HP
)
"""


# ============================================================================
# CONTEXT USAGE
# ============================================================================

"""
from advanced_ai_system_python import AIContext

context = AIContext(battle_manager, position)

# Access information
context.active_mon           # Current Pokemon
context.opponent_mon         # Opponent Pokemon
context.weather             # Current weather
context.terrain             # Current terrain
context.hazards             # Field hazards dict
context.screens             # Active screens dict

# Get cached data
threat_level = context.get_threat_level()
move_memory = context.get_move_memory()
role = context.get_role()

# Set cached data
context.set_threat_level(level)
context.set_move_memory(memory)
context.set_role(role)
"""


# ============================================================================
# ROLE DETECTION
# ============================================================================

"""
7 detected roles:

SWEEPER          - High speed, offensive stats, setup moves
WALL            - High defense, defensive stats, healing
TANK            - High defense, no healing, support role
SUPPORT         - Healing/status/screen moves, utility
WALLBREAKER     - High attack, powerful moves for defense break
PIVOT           - Switching moves (U-turn, Volt Switch)
LEAD            - Opening Pokemon, hazard setup
MIXED           - Balanced offense/defense stats
"""


# ============================================================================
# TYPE EFFECTIVENESS
# ============================================================================

"""
from shared.battle.type_effectiveness import get_effectiveness

# Get damage multiplier
multiplier = get_effectiveness(attacking_type, defending_type)

super_effective = multiplier > 1.0      # > 1.0
not_very_effective = multiplier < 1.0  # < 1.0
neutral = multiplier == 1.0            # = 1.0

# Common multipliers
2.0:  Super effective
1.0:  Neutral
0.5:  Not very effective
0.0:  No effect (rare)
"""


# ============================================================================
# MOVE SCORING FACTORS
# ============================================================================

"""
Type Effectiveness:     +30 super effective, -15 weak
STAB:                   +25
Power:                  +1 per power point
Accuracy:               -penalties for low
Priority:               +15 per level
Setup Moves:            +30-40
Healing:                +40-60 (scales with damage)
Status Moves:           +10-20
Field Benefits:         ±10
Recoil/Drain:          -30 low HP or +healing bonus
Weather/Terrain:        ±10
Personality Modifiers:  ×0.2 to ×1.8
"""


# ============================================================================
# DEBUGGING & MONITORING
# ============================================================================

"""
# Get AI status
status = ai.get_ai_status()
print(status)
# {
#   'skill_level': 70,
#   'personality': 'Balanced',
#   'features_enabled': {
#       'core': True,
#       'setup_recognition': True,
#       ...
#   }
# }

# Get threat assessment
threat_level, description = ai.get_threat_assessment(context)
print(f"Threat: {threat_level:.1f} - {description}")

# Check feature before using
if ai.is_feature_enabled("prediction"):
    # Use prediction features
    pass
"""


# ============================================================================
# INTEGRATION PATTERN
# ============================================================================

"""
class MyBattleManager:
    def __init__(self):
        self.ai = AdvancedAI(
            AISettings(skill_level=70),
            personality=AIPersonality.BALANCED
        )
    
    def ai_turn(self, position):
        # Get AI decision
        action = self.ai.choose_action(self, position)
        
        # Execute action
        self.submit_action(action)
    
    def opponent_moved(self, opponent_id, move):
        # Record for move memory
        self.ai.record_move_used(opponent_id, move)
    
    def opponent_switched(self, opponent_id, pokemon):
        # Record for prediction
        self.ai.record_switch(opponent_id, pokemon)
"""


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Q: AI making bad move choices?
A: Check threat assessment - may need move scoring calibration
   - Adjust personality to test different playstyles
   - Check move tags are correct (no hardcoded moves)

Q: Feature not working?
A: Check skill level threshold met for feature
   - Use is_feature_enabled("feature_name") to verify
   - Check FEATURE_GATES in settings.py for requirements

Q: Type annotations errors?
A: Run PyRight to verify compliance
   - pyright advanced_ai_system_python/
   - Check TYPE_CHECKING imports are correct

Q: Move memory not working?
A: Ensure record_move_used() called after each opponent move
   - Check battler_id format matches your system
   - Verify move objects have has_tag() method
"""


# ============================================================================
# PERFORMANCE NOTES
# ============================================================================

"""
Typical decision time: <100ms per decision
Memory usage: ~2-5MB per AI instance
Move scoring: 20+ factors evaluated per move
Threat calculation: ~5-10 opponent stats checked

Optimization tips:
- Reuse AISettings objects
- Cache type matchups
- Limit move memory size (default 10 moves)
- Disable unused personalities
"""


# ============================================================================
# VERSION & REFERENCES
# ============================================================================

"""
Advanced AI System v1.0.0 (Python Port)

Files:
- README.md: Full documentation
- TAG_GAPS.md: Move tag system gaps
- test_integration.py: Examples and tests
- COMPLETION_SUMMARY.md: Project overview

External resources:
- engine/repositories/moves/: Move definitions and tags
- shared/pokemon/: BattleMon, BaseMove, types
- shared/battle/: BattleManager, BattleAction interfaces
"""


if __name__ == "__main__":
    print(__doc__)
