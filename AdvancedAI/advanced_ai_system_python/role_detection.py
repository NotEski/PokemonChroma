"""
Role Detection System

Detects Pokemon roles based on stats, moves, and typing.

Ported from [011] Role_Detection.rb
"""

from enum import Enum

from shared.pokemon.move_tags import (
    HealMove,
    SetupMove,
    SwitchOutMove,
    SupportMove,
    StatusConditionMove
)

from shared.pokemon.pokemon import BattleMon


class PokemonRole(str, Enum):
    """Identified Pokemon roles"""
    SWEEPER = "sweeper"
    WALL = "wall"
    TANK = "tank"
    SUPPORT = "support"
    WALLBREAKER = "wallbreaker"
    PIVOT = "pivot"
    LEAD = "lead"
    MIXED = "mixed"


class RoleDetection:
    """
    Detects Pokemon roles based on:
    - Stat distribution (speed, attack, defense)
    - Move pool (setup, healing, status, damage)
    - Abilities
    - Item
    """
    
    def __init__(self) -> None:
        pass
    
    def detect_role(self, pokemon: "BattleMon") -> PokemonRole:
        """
        Detect the primary role of a Pokemon.
        
        Args:
            pokemon: BattleMon to analyze
            
        Returns:
            PokemonRole enum value
        """
        stats: dict[str, int] = self._get_stat_profile(pokemon)
        moves: dict[str, int] = self._get_move_analysis(pokemon)
        
        # Role detection logic
        if moves["setup_moves"] >= 2 and stats["speed"] >= 3:
            return PokemonRole.SWEEPER
        elif stats["defense"] >= 3 and stats["hp"] >= 3:
            if moves["healing"] >= 1:
                return PokemonRole.WALL
            else:
                return PokemonRole.TANK
        elif moves["support_moves"] >= 2:
            return PokemonRole.SUPPORT
        elif moves["high_power_moves"] >= 3 and stats["attack"] >= 3:
            return PokemonRole.WALLBREAKER
        elif moves["pivot_moves"] >= 1:
            return PokemonRole.PIVOT
        else:
            return PokemonRole.MIXED
    
    # ===== STAT ANALYSIS =====
    
    def _get_stat_profile(self, pokemon: BattleMon) -> dict[str, int]:
        """
        Analyze stat distribution.
        
        Args:
            pokemon: BattleMon to analyze
            
        Returns:
            Dict with stat comparative rankings
        """
        profile: dict[str, int] = {
            "hp": 2,
            "attack": 2,
            "defense": 2,
            "sp_attack": 2,
            "sp_defense": 2,
            "speed": 2,
        }
        
        if not hasattr(pokemon, "battle_state"):
            return profile
        
        stats = pokemon.battle_state.stat_stages
        total: int = stats.total
        
        if total == 0:
            return profile
        
        # Rank stats from 1 (lowest) to 5 (highest)
        
        sorted_stats: list[tuple[str, int]] = sorted(stats.to_dict.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (stat_name, _) in enumerate(sorted_stats):
            profile[stat_name] = 5 - (rank // 2)  # Group into 3 tiers
        
        return profile
    
    def _get_move_analysis(self, pokemon: BattleMon) -> dict[str, int]:
        """
        Analyze move pool composition.
        
        Args:
            pokemon: BattleMon to analyze
            
        Returns:
            Dict with move type counts
        """
        analysis: dict[str, int] = {
            "setup_moves": 0,
            "high_power_moves": 0,
            "healing": 0,
            "support_moves": 0,
            "pivot_moves": 0,
            "status_moves": 0,
            "total_moves": 0,
        }
        
        if not hasattr(pokemon, "move_set"):
            return analysis
        
        for move in pokemon.move_set.moves.values():
            
            move = move.base_move
            analysis["total_moves"] += 1
            
            # Setup moves
            if move.has_tag(SetupMove):
                analysis["setup_moves"] += 1
            
            # High power moves
            if hasattr(move, "power") and move.power and move.power >= 80:
                analysis["high_power_moves"] += 1
            
            # Healing
            if move.has_tag(HealMove):
                analysis["healing"] += 1
            
            # Support moves
            if move.has_tag(SupportMove):
                analysis["support_moves"] += 1
            
            # Pivot moves
            if move.has_tag(SwitchOutMove):
                analysis["pivot_moves"] += 1
            
            # Status moves
            if move.has_tag(StatusConditionMove):
                analysis["status_moves"] += 1
        
        return analysis
    
    def is_sweeper(self, pokemon: "BattleMon") -> bool:
        """Check if Pokemon is a sweeper"""
        return self.detect_role(pokemon) == PokemonRole.SWEEPER
    
    def is_wall_or_tank(self, pokemon: "BattleMon") -> bool:
        """Check if Pokemon is a wall/tank"""
        role = self.detect_role(pokemon)
        return role in (PokemonRole.WALL, PokemonRole.TANK)
    
    def is_support(self, pokemon: "BattleMon") -> bool:
        """Check if Pokemon is support"""
        return self.detect_role(pokemon) == PokemonRole.SUPPORT
    
    def is_pivot(self, pokemon: "BattleMon") -> bool:
        """Check if Pokemon has pivot capabilities"""
        return self.detect_role(pokemon) == PokemonRole.PIVOT
