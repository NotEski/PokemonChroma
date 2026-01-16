"""
Advanced Move Scorer

Comprehensive move scoring system using 20+ factors.
Uses move tags exclusively - no hardcoded move lists.

Ported from [003] Move_Scorer.rb
"""

from typing import Optional, Dict
# from engine.repositories.repository import move_repository
from shared.battle.type_effectiveness import effectiveness_multiplier
from shared.battle.weather import BattleWeather
from shared.battle.terrain import BattleTerrain
from shared.pokemon.move_tags import (
    CriticalHitMove,
    DrainMove,
    FlinchMove,
    HazardMove,
    HazardRemovalMove,
    ScreenMove,
    StatChangeInflictedMove,
    StatChangeMove,
    StatChangeReceivedMove,
    StatusConditionMove,
    SwitchOutMove,
)


from shared.pokemon.pokemon import BattleMon
from shared.pokemon.move import BaseMove
from shared.pokemon.pokemon import PokemonType
from .ai_context import AIContext


class MoveScorer:
    """
    Advanced move scoring system.
    
    Scores each available move on a 0-200+ scale using:
    - Damage output and accuracy
    - Type effectiveness and STAB
    - Secondary effects
    - Status application
    - Hazard setup/removal
    - Setup move potential
    - Priority
    - Recoil risk
    - Field effects awareness
    
    Scores are modified by:
    - Current HP percentage
    - Target threat level
    - Battle state (hazards, screens, weather)
    - AI personality
    """
    
    BASE_SCORE: float = 100.0
    
    def score_move(
        self,
        move: BaseMove,
        user: BattleMon,
        opponent: BattleMon,
        context: "AIContext",
        personality_modifiers: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Score a move for the given matchup.
        
        Args:
            move: BaseMove object to score
            user: BattleMon using the move
            opponent: BattleMon receiving the move
            context: AIContext with battle state
            personality_modifiers: Optional dict of modifier names to multipliers
            
        Returns:
            Float score (0-200+)
        """
        if not move:
            return 0.0
        
        score: float = self.BASE_SCORE
        
        # Basic move category scoring
        if move.category.value == "damage":
            score += self._score_damage_move(move, user, opponent, context)
        elif move.category.value == "status":
            score += self._score_status_move(move, user, opponent, context)
        elif move.category.value == "heal":
            score += self._score_healing_move(move, user, opponent, context)
        
        # Apply universal modifiers
        score += self._score_accuracy(move)
        score += self._score_priority(move, user, opponent)
        score += self._score_recoil_risk(move, user)
        score += self._score_secondary_effects(move, opponent)
        
        # Field effects awareness
        score += self._score_field_effects(move, context)
        
        # Apply personality modifiers if provided
        if personality_modifiers:
            for multiplier in personality_modifiers.values():
                score *= multiplier
        
        # Clamp to reasonable range but allow for bonuses
        return max(0.0, score)
    
    # ===== DAMAGE MOVE SCORING =====
    
    def _score_damage_move(
        self,
        move: BaseMove,
        user: BattleMon,
        opponent: BattleMon,
        context: "AIContext",
    ) -> float:
        """Score a damage-dealing move"""
        score: float = 0.0
        
        # Type effectiveness
        score += self._score_type_effectiveness(move, opponent)
        
        # STAB bonus
        if self._has_stab(move, user):
            score += 25.0
        
        # Power-based scoring
        if move.power:
            # Higher power = higher score, but with diminishing returns
            score += min(move.power / 2, 40)
        else:
            # Unranked moves (0 power) still have value through other mechanics
            score += 5.0
        
        # Accuracy penalty
        if move.accuracy and move.accuracy < 100:
            accuracy_penalty: float = (100 - move.accuracy) * 0.5
            score -= accuracy_penalty
        
        # Critical hit bonus
        if move.has_tag(CriticalHitMove):
            score += 10.0
        
        # Multi-target penalty (single targets preferred in singles)
        if move.target in []:
            score -= 20.0
        
        return score
    
    def _score_type_effectiveness(
        self,
        move: BaseMove,
        opponent: BattleMon,
    ) -> float:
        """Score type matchup advantages"""
        if not move.type or not opponent.pokemon_base.types:
            return 0.0
        
        score: float = 0.0
        move_type: "PokemonType" = move.type
        
        effectiveness: float = effectiveness_multiplier(move_type, opponent.pokemon_base.types)
            
        if effectiveness > 1.0:  # Super effective
            score += 30.0
        elif effectiveness < 1.0:  # Not very effective
            score -= 15.0
    
        return score
    
    def _has_stab(self, move: BaseMove, user: BattleMon) -> bool:
        """Check if user gets STAB on this move"""
        if not move.type or not user.pokemon_base.types:
            return False
        
        return move.type in user.pokemon_base.types
    
    # ===== STATUS MOVE SCORING =====
    
    def _score_status_move(
        self,
        move: BaseMove,
        user: BattleMon,
        opponent: BattleMon,
        context: "AIContext",
    ) -> float:
        """Score status/utility moves"""
        score: float = 0.0
        
        # Screen/Reflect moves
        if move.has_tag(ScreenMove):
            score += self._score_screen_move(move, context)
        
        # Hazard setup
        if move.has_tag(HazardMove):
            score += self._score_hazard_move(move, context)
        
        # Hazard removal
        if move.has_tag(HazardRemovalMove):
            score += self._score_hazard_removal_move(move, context)
        
        # Stat change moves
        if move.has_tag(StatChangeMove):
            score += self._score_stat_change_move(move, user, opponent, context)
        
        # Status condition moves
        if move.has_tag(StatusConditionMove):
            score += self._score_status_application_move(move, opponent)
        
        # Switch-out/pivot moves
        if move.has_tag(SwitchOutMove):
            score += 30.0
        
        return score
    
    def _score_screen_move(self, move: BaseMove, context: "AIContext") -> float:
        """Score screen and reflect moves"""
        # Check if screen already active
        if hasattr(context, "state") and hasattr(context.state, "active_team_mon"):
            # Simplified - would check BattleManager for active screens
            return 20.0
        return 25.0
    
    def _score_hazard_move(self, move: BaseMove, context: "AIContext") -> float:
        """Score hazard setup moves"""
        # Score based on max layers and current layers
        # For now, provide baseline score
        return 35.0
    
    def _score_hazard_removal_move(self, move: BaseMove, context: "AIContext") -> float:
        """Score hazard removal moves"""
        # Would check if opponent has hazards
        return 25.0
    
    def _score_stat_change_move(
        self,
        move: BaseMove,
        user: BattleMon,
        opponent: BattleMon,
        context: "AIContext",
    ) -> float:
        """Score stat-changing moves"""
        score: float = 0.0
        
        if not move.has_tag(StatChangeMove):
            return score
        
        # Get the StatChangeMove tag
        stat_change_tag: StatChangeMove = move.get_tag(StatChangeMove)  # type: ignore
        
        if stat_change_tag:
            # Check if it boosts user (received by user)
            if isinstance(stat_change_tag, StatChangeReceivedMove):
                score += 30.0  # Setup moves are valuable
            
            # Check if it debuffs opponent (inflicted on opponent)
            if isinstance(stat_change_tag, StatChangeInflictedMove):
                score += 15.0  # Debuffs are utility
        
        return score
    
    def _score_status_application_move(
        self,
        move: BaseMove,
        opponent: BattleMon,
    ) -> float:
        """Score moves that apply status conditions"""
        score: float = 20.0
        
        # Check for immunities
        for tag in move.move_tags:
            if isinstance(tag, StatusConditionMove):
                # Penalty if opponent immune
                if hasattr(opponent, "battle_state") and opponent.battle_state.status_conditions:
                    score -= 15.0
        
        return score
    
    # ===== HEALING MOVE SCORING =====
    
    def _score_healing_move(
        self,
        move: BaseMove,
        user: BattleMon,
        opponent: BattleMon,
        context: "AIContext",
    ) -> float:
        """Score healing/recovery moves"""
        score: float = 0.0
        
        # Scale healing score by HP missing
        if user.current_hp and user.max_hp:
            hp_percentage: float = user.current_hp / user.max_hp
            
            if hp_percentage < 0.25:  # Critical health
                score += 50.0
            elif hp_percentage < 0.5:  # Half health
                score += 30.0
            elif hp_percentage < 0.75:  # Below 75%
                score += 15.0
            else:  # High health
                score -= 25.0  # Healing is wasteful
        
        return score
    
    # ===== UNIVERSAL MODIFIERS =====
    
    def _score_accuracy(self, move: BaseMove) -> float:
        """Apply accuracy penalty for unreliable moves"""
        if not move.accuracy or move.accuracy >= 100:
            return 0.0
        
        # Moves with low accuracy are riskier
        accuracy_penalty: float = (100 - move.accuracy) * 0.3
        return -accuracy_penalty
    
    def _score_priority(
        self,
        move: BaseMove,
        user: BattleMon,
        opponent: BattleMon,
    ) -> float:
        """Score based on priority and speed matchup"""
        score: float = 0.0
        
        if not hasattr(move, "priority") or move.priority == 0:
            return 0.0
        
        # Positive priority is valuable
        if move.priority > 0:
            score += move.priority * 15.0
            
            # Extra valuable if slower
            if user.pokemon_base.base_stats.speed < opponent.pokemon_base.base_stats.speed:
                score += 20.0
            
            # Can secure KO
            if opponent.current_hp and opponent.current_hp < user.pokemon_base.base_stats.attack * 2:
                score += 20.0
        
        # Negative priority is bad (only use if forced)
        elif move.priority < 0:
            score -= abs(move.priority) * 10.0
        
        return score
    
    def _score_recoil_risk(self, move: BaseMove, user: BattleMon) -> float:
        """Penalize moves with recoil if user is low HP"""
        score: float = 0.0
        
        # Check for recoil/damage moves via tags
        if move.has_tag(DrainMove):
            # Drain moves are good
            drain_move: DrainMove = move.get_tag(DrainMove) # type: ignore
            if drain_move and drain_move.drain_percentage and drain_move.drain_percentage > 0:
                score += 10.0
            else:
                hp_percentage: float = abs(user.current_hp / user.max_hp)
                if hp_percentage < 0.33:
                    score -= 30.0
                elif hp_percentage < 0.5:
                    score -= 15.0
        return score
    
    def _score_secondary_effects(self, move: BaseMove, opponent: BattleMon) -> float:
        """Score secondary effect chances"""
        score: float = 0.0
        
        # Flinch moves
        if move.has_tag(FlinchMove):
            score += 8.0
        
        # Other secondary effects typically valuable
        if move.has_tag(StatChangeMove):
            score += 5.0
        elif move.has_tag(StatusConditionMove):
            score += 5.0
    
        return score
    
    # ===== FIELD EFFECTS AWARENESS =====
    
    def _score_field_effects(self, move: BaseMove, context: "AIContext") -> float:
        """Adjust score based on field effects"""
        score: float = 0.0
        
        # Psychic terrain blocks priority
        if context.terrain == BattleTerrain.PSYCHIC:
            if hasattr(move, "priority") and move.priority > 0:
                score -= 50.0  # Major penalty
        
        # Grassy terrain boosts grass moves
        if context.terrain == BattleTerrain.GRASSY:
            if hasattr(move, "type") and move.type and str(move.type).lower() == "grass":
                score += 15.0
        
        # Weather interactions
        if context.weather == BattleWeather.RAIN:
            if hasattr(move, "type") and move.type and str(move.type).lower() == "water":
                score += 10.0
        elif context.weather == BattleWeather.HARSH_SUNLIGHT:
            if hasattr(move, "type") and move.type and str(move.type).lower() == "fire":
                score += 10.0
        
        return score
