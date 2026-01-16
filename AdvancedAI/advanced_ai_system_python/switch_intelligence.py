"""
Switch Intelligence System

Advanced switching decisions based on type matchups, threats, and field state.

Ported from [012] Switch_Intelligence.rb
"""

from typing import TYPE_CHECKING, Optional

from .threat_assessment import ThreatAssessment
from shared.battle.type_effectiveness import effectiveness_multiplier

if TYPE_CHECKING:
    from shared.pokemon.pokemon import BattleMon
    from .ai_context import AIContext


class SwitchIntelligence:
    """
    Evaluates switching decisions and selects optimal Pokemon.
    
    Considers:
    - Type matchups against opponent
    - Current threat level
    - Setup sweeper detection
    - Stat boosts on field
    - Entry hazard damage
    - Weather/terrain effects
    """
    
    def __init__(self) -> None:
        pass
    
    def should_switch(
        self,
        context: "AIContext",
    ) -> bool:
        """
        Determine if switching is strategically favorable.
        
        Args:
            context: AIContext with battle state
            
        Returns:
            True if switching is recommended
        """
        active: "BattleMon" = context.active_mon
        opponent: "BattleMon" = context.opponent_mon
        
        # Don't switch if active Pokemon is at high HP and not at disadvantage
        if active.current_hp and active.max_hp:
            hp_percentage: float = active.current_hp / active.max_hp
            
            # High HP and no threat = stay in
            if hp_percentage > 0.75:
                threat_assessment: ThreatAssessment = ThreatAssessment()
                threat: float = threat_assessment.calculate_threat(context)
                if threat < 6.0:
                    return False
        
        # Check type matchup
        if not self._has_type_advantage(active, opponent):
            return True
        
        # Check if opponent is setup threat
        if self._opponent_is_setup_threat(opponent):
            return True
        
        return False
    
    def find_best_switch(
        self,
        context: "AIContext",
    ) -> Optional["BattleMon"]:
        """
        Find the best Pokemon to switch to.
        
        Args:
            context: AIContext with battle state
            
        Returns:
            Best BattleMon to switch to, or None if none available
        """
        available_mons: list["BattleMon"] = context.available_team_mons
        opponent: "BattleMon" = context.opponent_mon
        
        # Remove currently active mon from available
        available_mons = [mon for mon in available_mons if mon != context.active_mon]
        
        if not available_mons:
            return None
        
        best_score: float = -float("inf")
        best_mon: Optional["BattleMon"] = None
        
        for mon in available_mons:
            score: float = self._score_switch_candidate(mon, opponent, context)
            
            if score > best_score:
                best_score = score
                best_mon = mon
        
        return best_mon
    
    # ===== TYPE MATCHUP ANALYSIS =====
    
    def _has_type_advantage(self, user: "BattleMon", opponent: "BattleMon") -> bool:
        """
        Check if user has type advantage over opponent.
        
        Args:
            user: BattleMon to check
            opponent: Opponent BattleMon
            
        Returns:
            True if user has at least neutral/advantage matchup
        """
        
        if not hasattr(user, "pokemon_base") or not hasattr(opponent, "pokemon_base"):
            return True
        
        user_types = user.pokemon_base.types
        
        # Count super-effective coverage
        super_effective_count: int = 0
        weak_to_count: int = 0
        
        for user_type in user_types:
            effectiveness: float = effectiveness_multiplier(user_type, opponent.pokemon_base.types)
            
            if effectiveness > 1.0:
                super_effective_count += 1
            elif effectiveness < 1.0:
                weak_to_count += 1
        
        # Advantage if more super-effective coverage than weaknesses
        return super_effective_count >= weak_to_count
    
    def _get_type_coverage_score(self, user: "BattleMon", opponent: "BattleMon") -> float:
        """
        Score type effectiveness matchup.
        
        Args:
            user: BattleMon to evaluate
            opponent: Opponent BattleMon
            
        Returns:
            Score from -2.0 (bad) to +2.0 (excellent)
        """
        score: float = 0.0
        
        if not hasattr(user, "pokemon_base") or not hasattr(opponent, "pokemon_base"):
            return 0.0        

        for user_type in user.pokemon_base.types:
            effectiveness: float = effectiveness_multiplier(user_type, opponent.pokemon_base.types)
        
            if effectiveness > 1.0:
                score += 1.0  # Super effective
            elif effectiveness < 1.0:
                score -= 0.5  # Not very effective
        
        return max(-2.0, min(2.0, score))
    
    # ===== SETUP THREAT DETECTION =====
    
    def _opponent_is_setup_threat(self, opponent: "BattleMon") -> bool:
        """
        Check if opponent is a setup sweep threat.
        
        Args:
            opponent: Opponent BattleMon to evaluate
            
        Returns:
            True if opponent has dangerous stat boosts or setup moves
        """
        if not hasattr(opponent, "battle_state"):
            return False
        
        stats = opponent.battle_state.stat_stages
        
        # Check for positive boosts
        positive_boosts: int = 0
        
        if stats.attack_stat_stage > 0:
            positive_boosts += stats.attack_stat_stage
        if stats.special_attack_stat_stage > 0:
            positive_boosts += stats.special_attack_stat_stage
        if stats.speed_stat_stage > 0:
            positive_boosts += stats.speed_stat_stage
        
        # If 3+ total boost stages, is a threat
        return positive_boosts >= 3
    
    # ===== CANDIDATE SCORING =====
    
    def _score_switch_candidate(
        self,
        candidate: BattleMon,
        opponent: BattleMon,
        context: AIContext,
    ) -> float:
        """
        Score how good a switch candidate is.
        
        Args:
            candidate: Pokemon to evaluate
            opponent: Opponent Pokemon
            context: AIContext with battle state
            
        Returns:
            Score (higher is better)
        """
        score: float = 50.0  # Baseline
        
        # Type matchup (most important)
        type_score: float = self._get_type_coverage_score(candidate, opponent)
        score += type_score * 30.0
        
        # Health
        if candidate.current_hp and candidate.max_hp:
            hp_percentage: float = candidate.current_hp / candidate.max_hp
            score += hp_percentage * 20.0
        
        # Role compatibility
        score += self._score_role_fit(candidate, opponent)
        
        # Move coverage
        score += self._score_move_coverage(candidate, opponent)
        
        return score
    
    def _score_role_fit(self, candidate: BattleMon, opponent: BattleMon) -> float:
        """
        Score how well candidate's role fits against opponent.
        
        Args:
            candidate: Candidate Pokemon
            opponent: Opponent Pokemon
            
        Returns:
            Score bonus/penalty
        """
        score: float = 0.0
        
        # Wall vs sweeper is good matchup
        if self._is_defensive_type(candidate) and self._is_offensive_type(opponent):
            score += 15.0
        
        # Sweeper vs defensive wall
        elif self._is_offensive_type(candidate) and self._is_defensive_type(opponent):
            score += 10.0
        
        return score
    
    def _is_defensive_type(self, pokemon: "BattleMon") -> bool:
        """Check if Pokemon has defensive stats/typing"""
        if not hasattr(pokemon, "pokemon_base"):
            return False
        
        base_stats = pokemon.pokemon_base.base_stats
        
        # High defense/spdef suggests defensive role
        avg_defense: float = (base_stats.defense + base_stats.special_defense) / 2
        return avg_defense > base_stats.attack and avg_defense > base_stats.special_attack
    
    def _is_offensive_type(self, pokemon: "BattleMon") -> bool:
        """Check if Pokemon has offensive stats/typing"""
        if not hasattr(pokemon, "pokemon_base"):
            return False
        
        base_stats = pokemon.pokemon_base.base_stats
        
        # High attack/spatk suggests offensive role
        avg_offense: float = (base_stats.attack + base_stats.special_attack) / 2
        return avg_offense > base_stats.defense and avg_offense > base_stats.special_defense
    
    def _score_move_coverage(self, candidate: "BattleMon", opponent: "BattleMon") -> float:
        """
        Score how well candidate can cover opponent's types.
        
        Args:
            candidate: Candidate Pokemon
            opponent: Opponent Pokemon
            
        Returns:
            Score bonus for move coverage
        """

        score: float = 0.0
        
        if not hasattr(candidate, "move_set"):
            return 0.0
        
        # Check moves for coverage
        for move in candidate.move_set.moves.values():
            
            # Check effectiveness against opponent types
            if hasattr(opponent, "pokemon_base"):
                effectiveness: float = effectiveness_multiplier(move.type, opponent.types)
                if effectiveness > 1.0:
                    score += 10.0
        
        return score
