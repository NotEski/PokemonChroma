"""
Battle Personalities System

Defines AI personalities that modify decision-making.

Ported from [021] Battle_Personalities.rb
"""

from typing import Dict
from enum import Enum

from shared.pokemon.move_tags import HealMove, SetupMove, SwitchOutMove

from shared.pokemon.pokemon import BattleMon
from shared.pokemon.move import BaseMove


class AIPersonality(str, Enum):
    """AI personality types"""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"
    HYPER_OFFENSIVE = "hyper_offensive"


class BattlePersonalities:
    """
    Applies personality-based modifiers to move scoring.
    
    Personalities:
    - Aggressive: Favors powerful moves, ignores defense
    - Defensive: Prioritizes defense and healing
    - Balanced: Standard competitive play
    - Hyper Offensive: Only uses maximum power moves
    """
    
    def __init__(self, personality: AIPersonality = AIPersonality.BALANCED) -> None:
        self.personality: AIPersonality = personality
        self.modifiers: Dict[str, float] = self._load_personality_modifiers(personality)
    
    def _load_personality_modifiers(self, personality: AIPersonality) -> Dict[str, float]:
        """
        Load score modifiers for a personality.
        
        Args:
            personality: AI personality enum
            
        Returns:
            Dict mapping move categories to score multipliers
        """
        if personality == AIPersonality.AGGRESSIVE:
            return {
                "damage_move": 1.4,
                "setup_move": 1.2,
                "healing_move": 0.6,
                "status_move": 0.8,
                "switch_move": 0.5,
                "defensive_stat": 0.7,
            }
        
        elif personality == AIPersonality.DEFENSIVE:
            return {
                "damage_move": 0.8,
                "setup_move": 1.1,
                "healing_move": 1.8,
                "status_move": 1.5,
                "switch_move": 1.2,
                "defensive_stat": 1.4,
            }
        
        elif personality == AIPersonality.HYPER_OFFENSIVE:
            return {
                "damage_move": 1.8,
                "setup_move": 1.5,
                "healing_move": 0.2,
                "status_move": 0.4,
                "switch_move": 0.3,
                "defensive_stat": 0.4,
            }
        
        else:  # BALANCED
            return {
                "damage_move": 1.0,
                "setup_move": 1.0,
                "healing_move": 1.0,
                "status_move": 1.0,
                "switch_move": 1.0,
                "defensive_stat": 1.0,
            }
    
    def get_personality_modifiers(self) -> Dict[str, float]:
        """
        Get all personality modifiers.
        
        Returns:
            Dict of modifier_name -> multiplier
        """
        return self.modifiers.copy()
    
    def apply_personality_to_move_score(
        self,
        base_score: float,
        move: BaseMove,
        user: "BattleMon",
    ) -> float:
        """
        Apply personality modifiers to a move score.
        
        Args:
            base_score: Base move score
            move: BaseMove being scored
            user: "BattleMon" using the move
            
        Returns:
            Personality-adjusted score
        """
        score: float = base_score
        
        # Determine move category
        if hasattr(move, "category"):
            category_str: str = str(move.category).lower()
            
            if "damage" in category_str:
                score *= self.modifiers.get("damage_move", 1.0)
            elif "heal" in category_str:
                score *= self.modifiers.get("healing_move", 1.0)
            elif "status" in category_str:
                score *= self.modifiers.get("status_move", 1.0)
        
        # Check for setup moves
        if hasattr(move, "has_tag") and move.has_tag(SetupMove):
            score *= self.modifiers.get("setup_move", 1.0)
        
        # Check for healing moves
        if hasattr(move, "has_tag") and move.has_tag(HealMove):
            score *= self.modifiers.get("healing_move", 1.0)
        
        # Check for switch moves
        if hasattr(move, "has_tag") and move.has_tag(SwitchOutMove):
            score *= self.modifiers.get("switch_move", 1.0)
        
        return score
    
    def should_switch_based_on_personality(
        self,
        switch_probability: float,
    ) -> bool:
        """
        Determine if personality affects switch decision.
        
        Args:
            switch_probability: Base probability of switching
            
        Returns:
            Adjusted switch decision
        """
        # Aggressive and hyper-offensive personalities rarely switch
        if self.personality == AIPersonality.AGGRESSIVE:
            return switch_probability > 0.7
        elif self.personality == AIPersonality.HYPER_OFFENSIVE:
            return switch_probability > 0.85
        
        # Defensive personality switches more readily
        elif self.personality == AIPersonality.DEFENSIVE:
            return switch_probability > 0.3
        
        # Balanced uses base probability
        else:
            return switch_probability > 0.5
    
    def get_personality_name(self) -> str:
        """
        Get human-readable personality name.
        
        Returns:
            Personality name
        """
        names: Dict[AIPersonality, str] = {
            AIPersonality.AGGRESSIVE: "Aggressive",
            AIPersonality.DEFENSIVE: "Defensive",
            AIPersonality.BALANCED: "Balanced",
            AIPersonality.HYPER_OFFENSIVE: "Hyper Offensive",
        }
        
        return names.get(self.personality, "Unknown")
    
    @classmethod
    def from_string(cls, personality_str: str) -> "BattlePersonalities":
        """
        Create BattlePersonalities from string.
        
        Args:
            personality_str: Personality name as string
            
        Returns:
            BattlePersonalities instance
        """
        personality_map: Dict[str, AIPersonality] = {
            "aggressive": AIPersonality.AGGRESSIVE,
            "defensive": AIPersonality.DEFENSIVE,
            "balanced": AIPersonality.BALANCED,
            "hyper_offensive": AIPersonality.HYPER_OFFENSIVE,
        }
        
        personality: AIPersonality = personality_map.get(personality_str.lower(), AIPersonality.BALANCED)
        return cls(personality)
