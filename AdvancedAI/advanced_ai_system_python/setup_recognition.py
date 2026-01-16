"""
Setup Recognition System

Detects and counters Pokemon setup sweepers.

Ported from [019] Setup_Recognition.rb
"""

from typing import TYPE_CHECKING
from shared.pokemon.move_tags import SetupMove, StatChangeReceivedMove
from shared.battle.type_effectiveness import effectiveness_multiplier

if TYPE_CHECKING:
    from shared.pokemon.pokemon import BattleMon
    from shared.pokemon.move import BaseMove
    from .ai_context import AIContext


class SetupRecognition:
    """
    Identifies setup sweepers and evaluates counter strategies.
    
    Detects:
    - Setup moves used by opponent
    - Stat stage accumulation
    - Setup sweeper roles
    - Optimal counters
    """
    
    def __init__(self) -> None:
        pass
    
    def detect_setup_threat(
        self,
        opponent: "BattleMon",
    ) -> tuple[bool, int]:
        """
        Detect if opponent is attempting setup.
        
        Args:
            opponent: Opponent BattleMon to evaluate
            
        Returns:
            Tuple of (is_setup_threat, total_boost_stages)
        """
        if not hasattr(opponent, "battle_state"):
            return False, 0
        
        stats = opponent.battle_state.stat_stages
        
        # Count total positive boost stages
        total_boosts: int = 0
        
        if hasattr(stats, "attack_stat_stage") and stats.attack_stat_stage > 0:
            total_boosts += stats.attack_stat_stage
        if hasattr(stats, "special_attack_stat_stage") and stats.special_attack_stat_stage > 0:
            total_boosts += stats.special_attack_stat_stage
        if hasattr(stats, "speed_stat_stage") and stats.speed_stat_stage > 0:
            total_boosts += stats.speed_stat_stage
        if hasattr(stats, "defense_stat_stage") and stats.defense_stat_stage > 0:
            total_boosts += stats.defense_stat_stage
        if hasattr(stats, "special_defense_stat_stage") and stats.special_defense_stat_stage > 0:
            total_boosts += stats.special_defense_stat_stage
        
        # 3+ boost stages indicates setup threat
        is_threat: bool = total_boosts >= 3
        
        return is_threat, total_boosts
    
    def get_setup_moves_available(
        self,
        opponent: "BattleMon",
    ) -> list[tuple[str, str]]:
        """
        Get available setup moves for opponent.
        
        Args:
            opponent: Opponent BattleMon to evaluate
            
        Returns:
            List of (move_name, effect_type) tuples
        """
        setup_moves: list[tuple[str, str]] = []
        
        if not hasattr(opponent, "move_set"):
            return setup_moves
        
        for move_slot, move in opponent.move_set.moves.items():
            if not move_slot or not move:
                continue
            
            # Check for setup moves via tags
            if move.has_tag(SetupMove):
                effect_type: str = self._get_setup_type(move.base_move)
                setup_moves.append((move.name, effect_type))
        
        return setup_moves
    
    def _get_setup_type(self, move: BaseMove) -> str:
        """
        Categorize the type of setup move.
        
        Args:
            move: BaseMove to categorize
            
        Returns:
            Setup type string (e.g., "offensive", "defensive", "mixed")
        """
        # Check move tags for stat changes
        if hasattr(move, "move_tags"):
            attack_boost: bool = False
            defense_boost: bool = False
            speed_boost: bool = False
            
            for tag in move.move_tags:
                if isinstance(tag, StatChangeReceivedMove):
                    if tag.stat.value == "attack" or tag.stat.value == "special_attack":
                        attack_boost = True
                    elif tag.stat.value == "defense" or tag.stat.value == "special_defense":
                        defense_boost = True
                    elif tag.stat.value == "speed":
                        speed_boost = True
            
            if attack_boost and not defense_boost:
                return "offensive"
            elif defense_boost and not attack_boost:
                return "defensive"
            elif attack_boost and defense_boost:
                return "mixed"
            elif speed_boost:
                return "speed"
        
        return "special"
    
    def should_use_hazard_removal(
        self,
        user: "BattleMon",
        opponent: "BattleMon",
        context: "AIContext",
    ) -> bool:
        """
        Determine if hazard removal should be prioritized.
        
        Args:
            user: Current BattleMon
            opponent: Opponent BattleMon
            context: AIContext with battle state
            
        Returns:
            True if hazard removal move should be prioritized
        """
        # Check if user is sweeper taking hazard damage
        if not user.current_hp or not user.max_hp:
            return False
        
        hp_percentage: float = user.current_hp / user.max_hp
        
        # Low HP sweepers benefit from hazard removal
        if hp_percentage < 0.5:
            # Check if user is a sweeper via moves

            setup_move_count: int = sum(
                1 for move in user.move_set.moves.values() if move.has_tag(SetupMove)
            )
            
            if setup_move_count >= 2:
                return True
        
        return False
    
    def predict_sweep_potential(
        self,
        context: AIContext,
        opponent: BattleMon,
    ) -> float:
        """
        Evaluate how likely opponent is to sweep the team.
        
        Args:
            context: AIContext with battle state
            opponent: Opponent BattleMon to evaluate
            
        Returns:
            Sweep potential score (0-1.0)
        """
        team: list[BattleMon] = context.team_party
        score: float = 0.0
        
        # More boosts = higher sweep potential
        _, total_boosts = self.detect_setup_threat(opponent)
        score += min(total_boosts / 6.0, 0.4)  # Max 0.4 from boosts
        
        # Number of team members it beats type-wise
        beaten_count: int = 0
        if hasattr(opponent, "pokemon_base"):
            for team_mon in team:
                if not hasattr(team_mon, "pokemon_base"):
                    continue
                
                advantage_count: int = 0
                for opp_type in opponent.pokemon_base.types:
                    effectiveness: float = effectiveness_multiplier(opp_type, team_mon.pokemon_base.types)
                    if effectiveness > 1.0:
                        advantage_count += 1
                
                if advantage_count > 0:
                    beaten_count += 1
        
        score += (beaten_count / max(len(team), 1)) * 0.6  # Max 0.6 from coverage
        
        return min(score, 1.0)
