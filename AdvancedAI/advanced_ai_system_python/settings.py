"""
AI Settings and Configuration

Defines skill levels, feature gates, and configuration thresholds
for the Advanced AI System.
"""

from dataclasses import dataclass
from enum import IntEnum


class AISkillLevel(IntEnum):
    """AI Skill level tiers that gate features"""
    BASIC = 50  # Core AI
    INTERMEDIATE = 55  # Setup recognition
    ADVANCED = 60  # Endgame scenarios
    EXPERT = 65  # Battle personalities
    MASTER = 85  # Advanced prediction
    ELITE = 90  # Complex gimmicks
    LEGENDARY = 100  # All features


@dataclass
class AISettings:
    """
    Configuration for Advanced AI behavior.
    
    Attributes:
        skill_level: AI skill (50-100) determining which features are enabled
        use_move_memory: Track opponent move history
        use_threat_assessment: Evaluate opponent threat level
        use_field_effects: Apply weather/terrain awareness
        use_role_detection: Detect Pokemon roles
        use_switch_intelligence: Advanced switching decisions
        use_setup_recognition: Detect and counter setup sweepers
        use_endgame_scenarios: 1v1 optimization
        use_prediction_system: Predict opponent actions
        use_personality_system: Apply personality-based score modifiers
    """
    
    skill_level: int = 75  # Default to EXPERT tier
    
    # Core features
    use_move_memory: bool = True
    use_threat_assessment: bool = True
    use_field_effects: bool = True
    use_role_detection: bool = True
    
    # Advanced features
    use_switch_intelligence: bool = True
    use_setup_recognition: bool = True
    use_endgame_scenarios: bool = True
    use_prediction_system: bool = True
    use_personality_system: bool = True
    
    def __post_init__(self):
        """Validate skill level is in valid range"""
        if not 50 <= self.skill_level <= 100:
            raise ValueError(f"Skill level must be 50-100, got {self.skill_level}")
        
        # Auto-gate features based on skill level
        if self.skill_level < AISkillLevel.INTERMEDIATE:
            self.use_setup_recognition = False
        if self.skill_level < AISkillLevel.ADVANCED:
            self.use_endgame_scenarios = False
        if self.skill_level < AISkillLevel.EXPERT:
            self.use_personality_system = False
        if self.skill_level < AISkillLevel.MASTER:
            self.use_prediction_system = False
    
    @classmethod
    def from_skill_level(cls, skill: int) -> "AISettings":
        """Create settings from a skill level (50-100)"""
        settings = cls()
        settings.skill_level = skill
        settings.__post_init__()  # Re-validate and gate features
        return settings


# Default settings by tier
SETTINGS_BASIC = AISettings.from_skill_level(AISkillLevel.BASIC)
SETTINGS_INTERMEDIATE = AISettings.from_skill_level(AISkillLevel.INTERMEDIATE)
SETTINGS_ADVANCED = AISettings.from_skill_level(AISkillLevel.ADVANCED)
SETTINGS_EXPERT = AISettings.from_skill_level(AISkillLevel.EXPERT)
SETTINGS_MASTER = AISettings.from_skill_level(AISkillLevel.MASTER)
SETTINGS_ELITE = AISettings.from_skill_level(AISkillLevel.ELITE)
SETTINGS_LEGENDARY = AISettings.from_skill_level(AISkillLevel.LEGENDARY)


# Feature threshold reference
FEATURE_GATES = {
    "move_memory": AISkillLevel.BASIC,
    "threat_assessment": AISkillLevel.BASIC,
    "field_effects": AISkillLevel.BASIC,
    "role_detection": AISkillLevel.BASIC,
    "switch_intelligence": AISkillLevel.BASIC,
    "setup_recognition": AISkillLevel.INTERMEDIATE,
    "endgame_scenarios": AISkillLevel.ADVANCED,
    "personality_system": AISkillLevel.EXPERT,
    "prediction_system": AISkillLevel.MASTER,
}
