"""
Threat Assessment System

Evaluates the threat level (0-10 scale) of opponent Pokemon.

Ported from [008] Threat_Assessment.rb
"""

from typing import TYPE_CHECKING
from shared.battle.type_effectiveness import (
    effectiveness as effectiveness_multiplier,
)
from shared.pokemon.move_tags import (
    HealMove,
    SetupMove
)

if TYPE_CHECKING:
    from shared.pokemon.pokemon import BattleMon
    from .ai_context import AIContext


class ThreatAssessment:
    """
    Evaluates how threatening each opponent Pokemon is on a 0-10 scale.
    
    Threat level considers:
    - Current stat stages (boosts/debuffs)
    - Type matchups against user's team
    - Health percentage
    - Typing and role
    - Move pool (known moves)
    """
    
    def __init__(self) -> None:
        pass
    
    def calculate_threat(
        self,
        context: "AIContext",
    ) -> float:
        """
        Calculate threat level of opponent Pokemon (0-10 scale).
        
        Args:
            context: AIContext with battle state
            
        Returns:
            Float threat level from 0.0 (not threatening) to 10.0 (extremely threatening)
        """
        opponent: "BattleMon" = context.opponent_mon
        user: "BattleMon" = context.active_mon
        
        threat: float = 5.0  # Baseline neutral threat
        
        # Positive stat stages increase threat
        threat += self._threat_from_stat_boosts(opponent)
        
        # Type matchups
        threat += self._threat_from_type_matchup(opponent, user)
        
        # Health factor
        threat += self._threat_from_health(opponent)
        
        # Move threats
        threat += self._threat_from_moves(opponent, context)
        
        # Clamp to 0-10 scale
        return max(0.0, min(10.0, threat))
    
    def calculate_team_threat(
        self,
        context: "AIContext",
    ) -> float:
        """
        Calculate average threat of opponent team.
        
        Args:
            context: AIContext with battle state
            
        Returns:
            Average threat level of the team
        """
        opponents: list["BattleMon"] = context.opponent_party
        
        if not opponents:
            return 5.0
        
        # Calculate threat for each opponent individually
        total_threat: float = 0.0
        for opp in opponents:
            # Create temporary context for each opponent
            temp_state = context.state.model_copy(deep=True)
            temp_state.opponent_mon = opp
            temp_context = AIContext(state=temp_state)
            total_threat += self.calculate_threat(temp_context)
        
        return total_threat / len(opponents)
    
    # ===== THREAT FACTORS =====
    
    def _threat_from_stat_boosts(self, opponent: "BattleMon") -> float:
        """Evaluate threat from positive stat stages"""
        threat: float = 0.0
        
        if not hasattr(opponent, "battle_state"):
            return 0.0
        
        stats = opponent.battle_state.stat_stages
        
        # Attack boost
        if hasattr(stats, "attack_stat_stage") and stats.attack_stat_stage > 0:
            threat += stats.attack_stat_stage * 0.3  # Each +1 attack adds 0.3 threat
        
        # Special Attack boost
        if hasattr(stats, "special_attack_stat_stage") and stats.special_attack_stat_stage > 0:
            threat += stats.special_attack_stat_stage * 0.3
        
        # Speed boost (flexibility)
        if hasattr(stats, "speed_stat_stage") and stats.speed_stat_stage > 0:
            threat += stats.speed_stat_stage * 0.2
        
        # Defense/Special Defense boosts reduce threat
        if hasattr(stats, "defense_stat_stage") and stats.defense_stat_stage > 0:
            threat -= stats.defense_stat_stage * 0.15
        if hasattr(stats, "special_defense_stat_stage") and stats.special_defense_stat_stage > 0:
            threat -= stats.special_defense_stat_stage * 0.15
        
        return threat
    
    def _threat_from_type_matchup(self, opponent: "BattleMon", user: "BattleMon") -> float:
        """Evaluate type effectiveness advantage"""
        threat: float = 0.0
        
        if not hasattr(opponent, "pokemon_base") or not hasattr(user, "pokemon_base"):
            return 0.0
        
        opponent_types = opponent.pokemon_base.types
        user_types = user.pokemon_base.types
        
        # Check if opponent has type advantage
        for opp_type in opponent_types:
            for user_type in user_types:
                effectiveness: float = effectiveness_multiplier(opp_type, user_type)
                
                if effectiveness > 1.0:  # Opponent super-effective
                    threat += (effectiveness - 1.0) * 2.0  # Up to +1.0 per type
                elif effectiveness < 1.0:  # Opponent weak
                    threat -= (1.0 - effectiveness) * 1.5
        
        return threat
    
    def _threat_from_health(self, opponent: "BattleMon") -> float:
        """Evaluate threat based on remaining health"""
        if not opponent.current_hp or not opponent.max_hp:
            return 0.0
        
        hp_percentage: float = opponent.current_hp / opponent.max_hp
        
        # Full health is more threatening
        if hp_percentage > 0.75:
            return 0.5
        elif hp_percentage > 0.5:
            return 0.0
        elif hp_percentage > 0.25:
            return -0.5
        else:  # Critical health
            return -1.0
    
    def _threat_from_moves(self, opponent: "BattleMon", context: "AIContext") -> float:
        """Evaluate threat from move pool"""
        threat: float = 0.0
        
        if not hasattr(opponent, "move_set"):
            return 0.0
        
        for move in opponent.move_set.moves.values():
            if not move or not move.base_move:
                continue
            
            # Priority moves are threatening
            if move.priority > 0:
                threat += 0.5
            
            # Healing moves increase longevity
            if move.has_tag(HealMove):
                threat += 0.3
            
            # Setup moves indicate sweeper threat
            if move.has_tag(SetupMove):
                threat += 0.5
        
        return threat
    
    def is_critical_threat(
        self,
        context: "AIContext",
    ) -> bool:
        """
        Check if opponent is an immediate critical threat.
        
        Args:
            context: AIContext with battle state
            
        Returns:
            True if threat level >= 8.0
        """
        threat: float = self.calculate_threat(context)
        return threat >= 8.0
    
    def can_outspeed(self, user: "BattleMon", opponent: "BattleMon", context: "AIContext") -> bool:
        """
        Check if user can outspeed opponent considering Trick Room.
        
        Args:
            user: Current BattleMon
            opponent: Opponent BattleMon
            context: AIContext with battle state
            
        Returns:
            True if user will move first
        """
        user_speed: int = user.pokemon_base.base_stats.speed if hasattr(user, "pokemon_base") else 0
        opponent_speed: int = opponent.pokemon_base.base_stats.speed if hasattr(opponent, "pokemon_base") else 0
        
        if context.is_trick_room:
            # Trick room reverses speed order
            return user_speed < opponent_speed
        else:
            return user_speed > opponent_speed
