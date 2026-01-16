"""
Integration Test and Example Usage for Advanced AI System

Demonstrates how to initialize and use the Advanced AI for battle decisions.
"""

from typing import Optional
from advanced_ai_system_python import (
    AdvancedAI,
    AISettings,
    AISkillLevel,
    BattlePersonalities,
    AIPersonality,
)


def example_ai_initialization() -> AdvancedAI:
    """
    Example: Initialize Advanced AI with specific skill level and personality.
    
    Returns:
        Configured AdvancedAI instance
    """
    # Create settings with skill level 70 (advanced features enabled)
    settings: AISettings = AISettings(
        skill_level=70,
        use_move_memory=True,
        prefer_type_advantage=True,
    )
    
    # Create AI with balanced personality
    ai: AdvancedAI = AdvancedAI(
        settings=settings,
        personality=AIPersonality.BALANCED,
    )
    
    return ai


def example_feature_gating() -> None:
    """
    Example: Check which features are enabled at different skill levels.
    """
    # Skill level 50: Core features only
    settings_50: AISettings = AISettings(skill_level=50)
    ai_50: AdvancedAI = AdvancedAI(settings_50)
    
    print("Skill Level 50 Features:")
    print(f"  Core AI: {ai_50.is_feature_enabled('core')}")
    print(f"  Setup Recognition: {ai_50.is_feature_enabled('setup_recognition')}")
    print(f"  Endgame: {ai_50.is_feature_enabled('endgame')}")
    print(f"  Personalities: {ai_50.is_feature_enabled('personalities')}")
    print(f"  Prediction: {ai_50.is_feature_enabled('prediction')}")
    print()
    
    # Skill level 80: Most features
    settings_80: AISettings = AISettings(skill_level=80)
    ai_80: AdvancedAI = AdvancedAI(settings_80)
    
    print("Skill Level 80 Features:")
    print(f"  Core AI: {ai_80.is_feature_enabled('core')}")
    print(f"  Setup Recognition: {ai_80.is_feature_enabled('setup_recognition')}")
    print(f"  Endgame: {ai_80.is_feature_enabled('endgame')}")
    print(f"  Personalities: {ai_80.is_feature_enabled('personalities')}")
    print(f"  Prediction: {ai_80.is_feature_enabled('prediction')}")
    print()


def example_personality_selection() -> None:
    """
    Example: Create AI with different personalities.
    """
    personalities = [
        AIPersonality.AGGRESSIVE,
        AIPersonality.DEFENSIVE,
        AIPersonality.BALANCED,
        AIPersonality.HYPER_OFFENSIVE,
    ]
    
    settings: AISettings = AISettings(skill_level=70)
    
    print("Available Personalities:")
    for personality in personalities:
        ai: AdvancedAI = AdvancedAI(settings, personality)
        print(f"  {ai.personality.get_personality_name()}")
    print()


def example_ai_status() -> None:
    """
    Example: Display AI status and enabled features.
    """
    settings: AISettings = AISettings(skill_level=75)
    ai: AdvancedAI = AdvancedAI(settings, AIPersonality.DEFENSIVE)
    
    status: dict = ai.get_ai_status()
    
    print("AI Status:")
    print(f"  Skill Level: {status['skill_level']}")
    print(f"  Personality: {status['personality']}")
    print(f"  Enabled Features:")
    
    for feature, enabled in status['features_enabled'].items():
        status_str = "✓" if enabled else "✗"
        print(f"    {status_str} {feature}")
    print()


class TestIntegration:
    """
    Integration test suite for Advanced AI System.
    
    Note: These tests require a functional BattleManager instance.
    Run with: pytest test_advanced_ai_integration.py
    """
    
    def test_ai_initialization(self) -> None:
        """Test that AI initializes without errors."""
        settings: AISettings = AISettings(skill_level=70)
        ai: AdvancedAI = AdvancedAI(settings)
        
        assert ai is not None
        assert ai.skill_level == 70
        assert ai.move_scorer is not None
        assert ai.threat_assessment is not None
        assert ai.switch_intelligence is not None
        assert ai.setup_recognition is not None
        assert ai.endgame_scenarios is not None
        assert ai.prediction_system is not None
        assert ai.role_detection is not None
        assert ai.field_effects is not None
        assert ai.move_memory is not None
    
    def test_feature_gating(self) -> None:
        """Test that feature gating works correctly."""
        # Level 50: only core
        ai_50: AdvancedAI = AdvancedAI(AISettings(skill_level=50))
        assert ai_50.is_feature_enabled("core")
        assert not ai_50.is_feature_enabled("setup_recognition")
        assert not ai_50.is_feature_enabled("endgame")
        
        # Level 60: core + setup + endgame
        ai_60: AdvancedAI = AdvancedAI(AISettings(skill_level=60))
        assert ai_60.is_feature_enabled("core")
        assert ai_60.is_feature_enabled("setup_recognition")
        assert ai_60.is_feature_enabled("endgame")
        
        # Level 85: most features
        ai_85: AdvancedAI = AdvancedAI(AISettings(skill_level=85))
        assert ai_85.is_feature_enabled("prediction")
        assert not ai_85.is_feature_enabled("gimmicks")
        
        # Level 100: all features
        ai_100: AdvancedAI = AdvancedAI(AISettings(skill_level=100))
        assert ai_100.is_feature_enabled("gimmicks")
    
    def test_personality_initialization(self) -> None:
        """Test that personalities initialize correctly."""
        personalities = [
            AIPersonality.AGGRESSIVE,
            AIPersonality.DEFENSIVE,
            AIPersonality.BALANCED,
            AIPersonality.HYPER_OFFENSIVE,
        ]
        
        settings: AISettings = AISettings(skill_level=70)
        
        for personality in personalities:
            ai: AdvancedAI = AdvancedAI(settings, personality)
            assert ai.personality is not None
            assert ai.personality.personality == personality
    
    def test_ai_status(self) -> None:
        """Test that AI status reporting works."""
        settings: AISettings = AISettings(skill_level=70)
        ai: AdvancedAI = AdvancedAI(settings, AIPersonality.BALANCED)
        
        status: dict = ai.get_ai_status()
        
        assert status["skill_level"] == 70
        assert status["personality"] == "Balanced"
        assert "features_enabled" in status
        assert isinstance(status["features_enabled"], dict)


def main() -> None:
    """Run example demonstrations."""
    print("=" * 60)
    print("Advanced AI System - Integration Examples")
    print("=" * 60)
    print()
    
    print("1. AI Initialization Example")
    print("-" * 60)
    ai = example_ai_initialization()
    print(f"Initialized AI with skill level: {ai.skill_level}")
    print()
    
    print("2. Feature Gating Example")
    print("-" * 60)
    example_feature_gating()
    
    print("3. Personality Selection Example")
    print("-" * 60)
    example_personality_selection()
    
    print("4. AI Status Example")
    print("-" * 60)
    example_ai_status()
    
    print("=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
