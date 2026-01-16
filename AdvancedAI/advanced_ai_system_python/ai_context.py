"""
AI Context and Battle State Wrappers

Provides convenient access to battle state and Pokemon information
for AI decision-making modules.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel

from shared.pokemon.pokemon import BattleMon
from shared.battle.position import BattlePosition
from shared.battle.weather import BattleWeather
from shared.battle.terrain import BattleTerrain


class AIBattleState(BaseModel):
    """
    Snapshot of current battle state for AI decisions.
    
    Attributes:
        active_team_mon: Current active Pokemon for this team
        opponent_mon: Current active opponent Pokemon
        battle_position: This team's battle position
        opponent_position: Opponent team's battle position
        team_party: List of all Pokemon in this team
        opponent_party: List of all opponent Pokemon
        weather_condition: Current weather (None if none)
        terrain_condition: Current terrain (None if none)
        is_trick_room: Whether trick room is active
        turn_number: Current turn count
    """
    
    model_config = {"arbitrary_types_allowed": True}
    
    active_team_mon: BattleMon
    opponent_mon: BattleMon
    battle_position: BattlePosition
    opponent_position: BattlePosition
    team_party: list[BattleMon]
    opponent_party: list[BattleMon]
    weather_condition: Optional[BattleWeather] = None
    terrain_condition: Optional[BattleTerrain] = None
    is_trick_room: bool = False
    turn_number: int = 0


class AIContext(BaseModel):
    """
    Wrapper for accessing battle state and Pokemon information.
    Used by AI modules to query current conditions without directly
    accessing BattleManager.
    """
    
    model_config = {"arbitrary_types_allowed": True}
    
    state: AIBattleState
    _move_memory: Dict[str, list[str]] = {}
    _threat_cache: Dict[str, float] = {}
    _role_cache: Dict[str, Optional[str]] = {}
    _prediction_history: list[Dict[str, Any]] = []
    
    # ===== ACTIVE POKEMON ACCESS =====
    
    @property
    def active_mon(self) -> BattleMon:
        """Get current active Pokemon"""
        return self.state.active_team_mon
    
    @property
    def opponent_mon(self) -> BattleMon:
        """Get opponent's current active Pokemon"""
        return self.state.opponent_mon
    
    @property
    def position(self) -> BattlePosition:
        """Get this team's battle position"""
        return self.state.battle_position
    
    @property
    def opponent_position(self) -> BattlePosition:
        """Get opponent's battle position"""
        return self.state.opponent_position
    
    # ===== PARTY ACCESS =====
    
    @property
    def team_party(self) -> list[BattleMon]:
        """Get all Pokemon in this team"""
        return self.state.team_party
    
    @property
    def opponent_party(self) -> list[BattleMon]:
        """Get all opponent Pokemon"""
        return self.state.opponent_party
    
    @property
    def available_team_mons(self) -> list[BattleMon]:
        """Get all non-fainted Pokemon on this team"""
        return [mon for mon in self.state.team_party if mon.current_hp > 0]
    
    @property
    def available_opponent_mons(self) -> list[BattleMon]:
        """Get all non-fainted opponent Pokemon"""
        return [mon for mon in self.state.opponent_party if mon.current_hp > 0]
    
    # ===== FIELD CONDITIONS =====
    
    @property
    def weather(self) -> Optional["BattleWeather"]:
        """Get current weather condition"""
        return self.state.weather_condition
    
    @property
    def terrain(self) -> Optional["BattleTerrain"]:
        """Get current terrain condition"""
        return self.state.terrain_condition
    
    @property
    def is_trick_room(self) -> bool:
        """Check if trick room is active"""
        return self.state.is_trick_room
    
    @property
    def turn_count(self) -> int:
        """Get current turn number"""
        return self.state.turn_number
    
    # ===== CACHE METHODS =====
    
    def get_move_memory(self, battler_id: str) -> list[str]:
        """Get move history for a battler (by unique ID)"""
        return self._move_memory.get(battler_id, [])
    
    def add_move_memory(self, battler_id: str, move_name: str) -> None:
        """Record a move used by a battler"""
        if battler_id not in self._move_memory:
            self._move_memory[battler_id] = []
        self._move_memory[battler_id].append(move_name)
    
    def get_threat_level(self, battler_id: str) -> float:
        """Get cached threat level (0-10 scale)"""
        return self._threat_cache.get(battler_id, 5.0)
    
    def set_threat_level(self, battler_id: str, threat: float) -> None:
        """Cache threat level for a battler"""
        self._threat_cache[battler_id] = max(0.0, min(10.0, threat))
    
    def get_role(self, battler_id: str) -> Optional[str]:
        """Get cached role detection result"""
        return self._role_cache.get(battler_id)
    
    def set_role(self, battler_id: str, role: str) -> None:
        """Cache detected role for a battler"""
        self._role_cache[battler_id] = role
    
    def clear_caches(self) -> None:
        """Clear all caches (call at battle start)"""
        self._move_memory.clear()
        self._threat_cache.clear()
        self._role_cache.clear()
        self._prediction_history.clear()
