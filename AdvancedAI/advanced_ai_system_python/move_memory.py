"""
Move Memory System

Tracks opponent move history and usage patterns.

Ported from [007] Move_Memory.rb
"""

from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
from uuid import UUID


class MoveMemory:
    """
    Tracks moves used by each opponent Pokemon.
    
    Maintains a history of moves observed, allowing the AI to:
    - Identify signature moves not yet revealed
    - Predict likely moves based on history
    - Build a picture of moveset composition
    """
    
    # Maximum recent moves to track per Pokemon
    MAX_HISTORY: int = 10
    
    def __init__(self) -> None:
        # battler_id -> deque of move names
        self.move_history: Dict[UUID, deque[str]] = defaultdict(lambda: deque(maxlen=self.MAX_HISTORY))
        
        # battler_id -> set of moves seen (all-time)
        self.moves_seen: Dict[UUID, set[str]] = defaultdict(set)
        
        # battler_id -> dict of move_name -> usage count
        self.move_frequency: Dict[UUID, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    def record_move_used(self, battler_id: UUID, move_name: str) -> None:
        """
        Record that a battler used a move.
        
        Args:
            battler_id: Unique identifier for the battler (UUID)
            move_name: Name of the move used
        """
        self.move_history[battler_id].append(move_name)
        self.moves_seen[battler_id].add(move_name)
        self.move_frequency[battler_id][move_name] += 1
    
    def get_move_history(self, battler_id: UUID) -> list[str]:
        """
        Get recent move history for a battler.
        
        Args:
            battler_id: Unique identifier for the battler (UUID)
            
        Returns:
            List of recent moves (oldest to newest)
        """
        return list(self.move_history[battler_id])
    
    def get_moves_seen(self, battler_id: UUID) -> set[str]:
        """
        Get all moves ever seen from a battler.
        
        Args:
            battler_id: Unique identifier for the battler (UUID)
            
        Returns:
            Set of move names
        """
        return self.moves_seen[battler_id].copy()
    
    def get_move_frequency(self, battler_id: UUID) -> Dict[str, int]:
        """
        Get usage frequency of each move.
        
        Args:
            battler_id: Unique identifier for the battler (UUID)
            
        Returns:
            Dict mapping move names to usage counts
        """
        return dict(self.move_frequency[battler_id])
    
    def get_most_used_moves(self, battler_id: UUID, limit: int = 3) -> list[Tuple[str, int]]:
        """
        Get the most frequently used moves.
        
        Args:
            battler_id: Unique identifier for the battler (UUID)
            limit: Maximum number of moves to return
            
        Returns:
            List of (move_name, count) tuples, sorted by frequency descending
        """
        frequency: Dict[str, int] = self.get_move_frequency(battler_id)
        return sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def likely_move_next(self, battler_id: UUID, moveset_size: int = 4) -> Optional[str]:
        """
        Predict the most likely move to be used next.
        
        Args:
            battler_id: Unique identifier for the battler (UUID)
            moveset_size: Expected number of moves in moveset (default 4)
            
        Returns:
            Most likely move name, or None if no data
        """
        frequency: Dict[str, int] = self.get_move_frequency(battler_id)
        if not frequency:
            return None
        
        # Most frequently used move is most likely
        most_used: Tuple[str, int] = max(frequency.items(), key=lambda x: x[1])
        return most_used[0]
    
    def get_unrevealed_move_slots(self, battler_id: UUID, moveset_size: int = 4) -> int:
        """
        Estimate unrevealed move slots in a moveset.
        
        Args:
            battler_id: Unique identifier for the battler (UUID)
            moveset_size: Expected moveset size (default 4)
            
        Returns:
            Number of moves likely not yet seen
        """
        moves_seen_count: int = len(self.get_moves_seen(battler_id))
        return max(0, moveset_size - moves_seen_count)
    
    def reset_battler_history(self, battler_id: UUID) -> None:
        """
        Clear history for a specific battler (e.g., faints).
        
        Args:
            battler_id: Unique identifier for the battler (UUID)
        """
        self.move_history[battler_id].clear()
        self.moves_seen[battler_id].clear()
        self.move_frequency[battler_id].clear()
    
    def clear_all_history(self) -> None:
        """Clear all recorded histories (call at battle start)"""
        self.move_history.clear()
        self.moves_seen.clear()
        self.move_frequency.clear()
