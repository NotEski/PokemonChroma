"""
Endgame Scenarios System

Specialized logic for 1v1 and endgame battle situations.

Ported from [020] Endgame_Scenarios.rb
"""

from shared.pokemon.pokemon import BattleMon
from shared.pokemon.move import BaseMove
from shared.pokemon.move_tags import (
    HealMove
)

from .ai_context import AIContext


class EndgameScenarios:
    """
    Handles decision-making in critical battle endgames.
    
    Optimizes for:
    - 1v1 situations
    - Last Pokemon scenarios
    - Priority move usage when slower
    - Survival strategy over damage
    """
    
    def __init__(self) -> None:
        pass
    
    def is_endgame_scenario(
        self,
        context: "AIContext",
    ) -> bool:
        """
        Check if battle is in endgame (1v1 or 2v2).
        
        Args:
            context: AIContext with battle state
            
        Returns:
            True if endgame scenario detected
        """
        team: list["BattleMon"] = context.team_party
        opponent_team: list["BattleMon"] = context.opponent_party
        
        active_user_mons: int = sum(1 for mon in team if mon.current_hp > 0)
        active_opponent_mons: int = sum(1 for mon in opponent_team if mon.current_hp > 0)
        
        # 1v1 or when team is heavily depleted
        return (active_user_mons <= 1 or active_opponent_mons <= 1)
    
    def prioritize_priority_moves(
        self,
        user: "BattleMon",
        opponent: "BattleMon",
        context: "AIContext",
    ) -> bool:
        """
        Determine if priority moves should be heavily weighted.
        
        Args:
            user: Current BattleMon
            opponent: Opponent BattleMon
            context: AIContext with battle state
            
        Returns:
            True if priority moves should be strongly prioritized
        """
        # Prioritize priority if slower
        if hasattr(user, "pokemon_base") and hasattr(opponent, "pokemon_base"):
            user_speed: int = user.pokemon_base.base_stats.speed
            opponent_speed: int = opponent.pokemon_base.base_stats.speed
            
            if user_speed < opponent_speed:
                return True
        
        # Prioritize if user is low HP
        if user.current_hp and user.max_hp:
            hp_percentage: float = user.current_hp / user.max_hp
            if hp_percentage < 0.25:
                return True
        
        return False
    
    def prioritize_survival(
        self,
        user: "BattleMon",
        opponent: "BattleMon",
        context: "AIContext",
    ) -> bool:
        """
        Determine if survival should be prioritized over offense.
        
        Args:
            user: Current BattleMon
            opponent: Opponent BattleMon
            context: AIContext with battle state
            
        Returns:
            True if survival moves should be prioritized
        """
        if not user.current_hp or not user.max_hp:
            return False
        
        hp_percentage: float = user.current_hp / user.max_hp
        
        # Under 33% HP = prioritize survival
        if hp_percentage < 0.33:
            return True
        
        # Check if opponent can 2HKO
        if opponent.current_hp and opponent.max_hp:
            opponent_hp_percentage: float = opponent.current_hp / opponent.max_hp
            
            # If opponent is healthy and we're damaged = survive
            if opponent_hp_percentage > 0.6 and hp_percentage < 0.5:
                return True
        
        return False
    
    def evaluate_final_pokemon_scenario(
        self,
        context: AIContext,
    ) -> dict[str, float | bool]:
        """
        Analyze 1v1 final matchup.
        
        Args:
            context: AIContext with battle state
            
        Returns:
            Dict with scenario analysis
        """
        user_last_mon: BattleMon = context.active_mon
        opponent_last_mon: BattleMon = context.opponent_mon
        
        analysis: dict[str, float | bool] = {
            "user_hp_percent": 0.0,
            "opponent_hp_percent": 0.0,
            "can_outspeed": False,
            "will_lose_1v1": False,
            "should_switch": False,
            "priority_strategy": False,
            "should_prioritize_survival": False,
        }
        
        if user_last_mon.current_hp and user_last_mon.max_hp:
            analysis["user_hp_percent"] = user_last_mon.current_hp / user_last_mon.max_hp
        
        if opponent_last_mon.current_hp and opponent_last_mon.max_hp:
            analysis["opponent_hp_percent"] = opponent_last_mon.current_hp / opponent_last_mon.max_hp
        
        # Speed analysis
        if hasattr(user_last_mon, "pokemon_base") and hasattr(opponent_last_mon, "pokemon_base"):
            user_speed: int = user_last_mon.pokemon_base.base_stats.speed
            opponent_speed: int = opponent_last_mon.pokemon_base.base_stats.speed
            
            if context.state.is_trick_room:
                analysis["can_outspeed"] = user_speed < opponent_speed
            else:
                analysis["can_outspeed"] = user_speed > opponent_speed
        
        # Loss condition evaluation
        if not analysis["can_outspeed"] and analysis["user_hp_percent"] < 0.5:
            analysis["will_lose_1v1"] = True
            analysis["priority_strategy"] = True
        
        return analysis
    
    def score_endgame_move(
        self,
        context: AIContext,
        move: BaseMove,
    ) -> float:
        """
        Score a move with endgame priorities.
        
        Args:
            context: AIContext with battle state
            move: BaseMove to score
            
        Returns:
            Endgame-adjusted score
        """
        user: BattleMon = context.active_mon
        opponent: BattleMon = context.opponent_mon
        
        score: float = 0.0
        
        # Priority move bonus in 1v1
        if hasattr(move, "priority") and move.priority > 0:
            score += move.priority * 20.0
            
            # Extra bonus if slower
            if hasattr(user, "pokemon_base") and hasattr(opponent, "pokemon_base"):
                user_speed: int = user.pokemon_base.base_stats.speed
                opponent_speed: int = opponent.pokemon_base.base_stats.speed
                
                if user_speed < opponent_speed:
                    score += 50.0
        
        # Healing moves bonus when low HP
        if hasattr(move, "has_tag") and move.has_tag(HealMove):
            if user.current_hp and user.max_hp:
                hp_percentage: float = user.current_hp / user.max_hp
                if hp_percentage < 0.5:
                    score += 60.0
        
        # High power move bonus in endgame
        if hasattr(move, "power") and move.power and move.power >= 80:
            if opponent.current_hp and opponent.max_hp:
                opp_hp_percent: float = opponent.current_hp / opponent.max_hp
                
                # Can KO with powerful move
                if opp_hp_percent < 0.5:
                    score += 40.0
        
        return score
