"""
AI Player Interface

Provides the interface for the AI to submit actions to BattleManager.
Functions like a player trainer but with automated decision-making.
"""

from typing import TYPE_CHECKING, Optional, Any
from abc import ABC, abstractmethod

from shared.pokemon.move import Move
from shared.pokemon.pokemon import Pokemon

if TYPE_CHECKING:
    from engine.battle.battle_manager import BattleManager
    from shared.battle.battle_actions import BattleAction
    from shared.battle.position import BattlePosition


class AIPlayer(ABC):
    """
    Abstract base for AI player implementations.
    
    The AI player queries the battle manager for available actions,
    makes decisions through the AdvancedAI system, and submits actions
    via BattleManager.submit_action().
    """
    
    def __init__(self, trainer_name: str = "Advanced AI") -> None:
        self.trainer_name: str = trainer_name
        self.battle_manager: Optional["BattleManager"] = None
    
    def set_battle_manager(self, battle_manager: "BattleManager") -> None:
        """Register the BattleManager instance"""
        self.battle_manager = battle_manager
    
    @abstractmethod
    def choose_action(self, position: "BattlePosition") -> "BattleAction":
        """
        Choose an action (MoveAction or SwitchAction) for the given position.
        
        Args:
            position: BattlePosition indicating which Pokemon this is
            
        Returns:
            MoveAction or SwitchAction to submit to battle_manager
        """
        pass
    
    def submit_action(self, action: "BattleAction") -> None:
        """
        Submit an action to the BattleManager.
        
        Args:
            action: MoveAction or SwitchAction
            
        Raises:
            RuntimeError: If battle_manager not set or action invalid
        """
        if not self.battle_manager:
            raise RuntimeError("Battle manager not set for AI player")
        
        self.battle_manager.submit_action(action)
    
    def get_available_moves(self, position: BattlePosition) -> list[tuple[int, Move]]:
        """
        Get available moves for the active Pokemon at position.
        
        Args:
            position: BattlePosition
            
        Returns:
            List of (move_index, Move) tuples
        """
        if not self.battle_manager:
            return []
        
        # Get the active Pokemon at this position
        team = self.battle_manager.teams[position.team_id]
        active_mon = team.active_battlemon
        
        if not active_mon:
            return []
        
        # Return available moves with their indices
        available: list[tuple[int, Move]] = []
        for idx, move in enumerate(active_mon.move_set.moves.values()):
            if move and move.current_pp > 0:
                available.append((idx, move))
        
        return available
    
    def get_switchable_pokemon(self, position: BattlePosition) -> list[tuple[int, Pokemon]]:
        """
        Get Pokemon available to switch to (not fainted, not active).
        
        Args:
            position: BattlePosition
            
        Returns:
            List of (party_index, Pokemon) tuples
        """
        if not self.battle_manager:
            return []
        
        team = self.battle_manager.teams[position.team_id]
        _battlemon = team.active_battlemon
        if not _battlemon:
            return []        
        active_battlemon: Pokemon = _battlemon.pokemon_reference

        switchable: list[tuple[int, Pokemon]] = []
        for idx, mon in enumerate(team.pokemon_team):
            # Can switch to any non-fainted Pokemon that's not currently active
            if mon.current_hp > 0 and mon != active_battlemon:
                switchable.append((idx, mon))
        
        return switchable


class AdvancedAIPlayer(AIPlayer):
    """
    AI Player that uses the Advanced AI System for decision-making.
    
    This class integrates with the AdvancedAI orchestrator to make
    intelligent decisions based on battle state.
    """
    
    def __init__(self, advanced_ai: Any, trainer_name: str = "Advanced AI") -> None:
        """
        Initialize the Advanced AI Player.
        
        Args:
            advanced_ai: AdvancedAI orchestrator instance
            trainer_name: Name of this AI trainer
        """
        super().__init__(trainer_name)
        self.advanced_ai: Any = advanced_ai
    
    def choose_action(self, position: BattlePosition) -> BattleAction:
        """
        Use AdvancedAI system to choose action.
        
        Args:
            position: BattlePosition
            
        Returns:
            MoveAction or SwitchAction
        """
        if not self.battle_manager:
            raise RuntimeError("Battle manager not set")
        
        # Let Advanced AI system choose the action
        action = self.advanced_ai.choose_action(self.battle_manager, position)
        
        return action
