"""
Prediction System

Predicts opponent moves and switches based on patterns and state.

Ported from [016] Prediction_System.rb
"""

from typing import Optional
from collections import deque
from uuid import UUID

from shared.battle.type_effectiveness import effectiveness_multiplier

from shared.pokemon.pokemon import BattleMon
from .ai_context import AIContext
from .move_memory import MoveMemory


class PredictionSystem:
    """
    Predicts opponent's next action using pattern recognition.
    
    Predicts:
    - Likely next move based on history
    - Probable switches
    - Setup move timing
    - Hazard setup patterns
    """
    
    def __init__(self) -> None:
        self.switch_history: deque[bool] = deque(maxlen=10)
    
    def predict_next_move(
        self,
        opponent: BattleMon,
        context: AIContext,
        move_memory: MoveMemory,
    ) -> Optional[str]:
        """
        Predict opponent's most likely next move.
        
        Args:
            opponent: Opponent Pokemon to predict for
            context: AIContext with battle state
            move_memory: MoveMemory instance with move history
            
        Returns:
            Predicted move name, or None if uncertain
        """
        if not hasattr(opponent, "pokemon_reference"):
            return None
        
        battler_id: UUID = opponent.pokemon_reference.id
        
        # Get most used move from history
        most_used = move_memory.likely_move_next(battler_id)
        
        if most_used:
            return most_used
        
        # If no history, predict first move in moveset
        if hasattr(opponent, "move_set"):
            for move in opponent.move_set.moves.values():
                if move and move.base_move:
                    return move.base_move.name
        
        return None
    
    def predict_switch_probability(
        self,
        opponent: BattleMon,
        user: BattleMon,
    ) -> float:
        """
        Estimate probability opponent will switch.
        
        Args:
            opponent: Current opponent Pokemon
            user: Current user Pokemon
            context: AIContext with battle state
            
        Returns:
            Probability (0.0-1.0) that opponent will switch
        """
        probability: float = 0.0
        
        # Opponent at low HP = more likely to switch
        if opponent.current_hp and opponent.max_hp:
            hp_percentage: float = opponent.current_hp / opponent.max_hp
            
            if hp_percentage < 0.25:
                probability += 0.4
            elif hp_percentage < 0.5:
                probability += 0.2
        
        # At type disadvantage = likely to switch
        if not self._has_type_advantage(opponent, user):
            probability += 0.3
        
        # Recently switched = unlikely to switch again
        if len(self.switch_history) > 0:
            if self.switch_history[-1]:  # True if last action was switch
                probability -= 0.2
        
        return max(0.0, min(1.0, probability))
    
    def predict_hazard_setup(
        self,
        opponent: BattleMon,
        context: AIContext,
        move_memory: MoveMemory,
    ) -> bool:
        """
        Predict if opponent will set up hazards next turn.
        
        Args:
            opponent: Opponent Pokemon to predict for
            context: AIContext with battle state
            move_memory: MoveMemory with move history
            
        Returns:
            True if hazard setup is likely
        """
        if not hasattr(opponent, "pokemon_reference"):
            return False
        
        battler_id: UUID = opponent.pokemon_reference.id
        
        # Check move history for hazard moves
        move_history = move_memory.get_move_history(battler_id)
        
        if not move_history:
            return False
        
        # Recent hazard setup suggests pattern
        recent_hazard_count: int = sum(
            1 for move in move_history[-5:]
            if move in ["stealth_rock", "spikes", "toxic_spikes", "sticky_web"]
        )
        
        return recent_hazard_count >= 2
    
    def predict_stat_boost_move(
        self,
        opponent: "BattleMon",
        context: "AIContext",
    ) -> bool:
        """
        Predict if opponent will use a stat-boosting move.
        
        Args:
            opponent: Opponent Pokemon to predict for
            context: AIContext with battle state
            
        Returns:
            True if stat boost move is predicted
        """
        if not hasattr(opponent, "battle_state"):
            return False
        
        # If already boosted, likely to attack
        stats = opponent.battle_state.stat_stages
        current_boosts: int = 0
        
        if hasattr(stats, "attack_stat_stage"):
            current_boosts += abs(stats.attack_stat_stage)
        if hasattr(stats, "special_attack_stat_stage"):
            current_boosts += abs(stats.special_attack_stat_stage)
        
        # High boosts = likely to attack not boost more
        if current_boosts >= 4:
            return False
        
        # Moderate boosts = likely to boost more
        return current_boosts >= 2
    
    def record_switch(self, switched: bool) -> None:
        """
        Record that opponent switched or stayed.
        
        Args:
            switched: True if opponent switched last turn
        """
        self.switch_history.append(switched)
    
    def _has_type_advantage(self, user: BattleMon, opponent: BattleMon) -> bool:
        """Check if user has type advantage"""
        
        if not hasattr(user, "pokemon_base") or not hasattr(opponent, "pokemon_base"):
            return True
        
        advantage_count: int = 0
        
        for user_type in user.types:
            effectiveness: float = effectiveness_multiplier(user_type, opponent.types)
            if effectiveness > 1.0:
                advantage_count += 1
        
        return advantage_count > 0
