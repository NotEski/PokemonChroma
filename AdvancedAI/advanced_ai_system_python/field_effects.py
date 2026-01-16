"""
Field Effects Awareness

Evaluates and responds to weather, terrain, and field effects.

Ported from [010] Field_Effects.rb
"""

from typing import TYPE_CHECKING, Optional, Dict
from shared.battle.weather import BattleWeather
from shared.battle.terrain import BattleTerrain

if TYPE_CHECKING:
    from shared.pokemon.pokemon import BattleMon
    from shared.pokemon.move import BaseMove
    from .ai_context import AIContext


class FieldEffects:
    """
    Analyzes active field effects and their impact on battle decisions.
    
    Considers:
    - Weather (rain, sun, hail, sandstorm)
    - Terrain (grassy, psychic, misty, electric)
    - Trick Room status
    - Active screens and hazards (via context)
    """
    
    def __init__(self):
        pass
    
    def get_weather_benefit(
        self,
        pokemon: "BattleMon",
        weather: Optional[BattleWeather],
    ) -> float:
        """
        Evaluate how much current weather benefits a Pokemon.
        
        Args:
            pokemon: BattleMon to evaluate
            weather: Current weather condition
            
        Returns:
            Benefit score (-1.0 to 1.0 scale)
        """
        if not weather or not hasattr(pokemon, "types"):
            return 0.0
        
        # Map weather to benefited types
        weather_benefits = {
            BattleWeather.RAIN: ["water"],
            BattleWeather.HARSH_SUNLIGHT: ["fire"],
            BattleWeather.HAIL: ["ice"],
            BattleWeather.SANDSTORM: ["rock", "ground", "steel"],
        }
        
        if weather not in weather_benefits:
            return 0.0
        
        benefited_types = weather_benefits[weather]
        
        # Check if this Pokemon benefits
        type_names = [t.name if hasattr(t, "name") else str(t).lower() for t in pokemon.types]
        
        for type_name in type_names:
            if any(bt in type_name.lower() for bt in benefited_types):
                return 0.5
        
        # Check for disadvantage
        weather_disadvantages = {
            BattleWeather.HARSH_SUNLIGHT: ["water"],
            BattleWeather.RAIN: ["fire"],
            BattleWeather.SANDSTORM: ["water", "fire", "flying"],
        }
        
        if weather in weather_disadvantages:
            disadvantaged_types = weather_disadvantages[weather]
            for type_name in type_names:
                if any(dt in type_name.lower() for dt in disadvantaged_types):
                    return -0.3
        
        return 0.0
    
    def weather_affects_move(
        self,
        move: "BaseMove",
        weather: Optional[BattleWeather],
    ) -> float:
        """
        Evaluate if current weather affects this move's effectiveness.
        
        Args:
            move: Move to evaluate
            weather: Current weather condition
            
        Returns:
            Effect multiplier or adjustment (-1.0 to 1.0)
        """
        if not weather or not move:
            return 0.0
        
        move_type = move.type
        if not move_type:
            return 0.0
        
        type_name = move_type.name if hasattr(move_type, "name") else str(move_type).lower()
        
        # Weather boosts specific move types
        if weather == BattleWeather.RAIN and "water" in type_name.lower():
            return 0.3  # Water moves boosted
        elif weather == BattleWeather.HARSH_SUNLIGHT and "fire" in type_name.lower():
            return 0.3  # Fire moves boosted
        elif weather == BattleWeather.SANDSTORM and any(t in type_name.lower() for t in ["rock", "ground", "steel"]):
            return 0.2  # Rock/Ground/Steel slightly boosted
        
        return 0.0
    
    def terrain_affects_move(
        self,
        move: "BaseMove",
        terrain: Optional[BattleTerrain],
    ) -> float:
        """
        Evaluate if current terrain affects this move's effectiveness.
        
        Args:
            move: Move to evaluate
            terrain: Current terrain condition
            
        Returns:
            Effect multiplier or adjustment
        """
        if not terrain or not move:
            return 0.0
        
        # Psychic terrain blocks priority moves
        if terrain == BattleTerrain.PSYCHIC:
            if hasattr(move, "priority") and move.priority > 0:
                return -100.0  # Basically unusable
        
        # Electric terrain boosts electric moves
        if move.type:
            type_name = move.type.name if hasattr(move.type, "name") else str(move.type).lower()
            
            if terrain == BattleTerrain.GRASSY and "grass" in type_name.lower():
                return 0.2
            elif terrain == BattleTerrain.ELECTRIC and "electric" in type_name.lower():
                return 0.2
            elif terrain == BattleTerrain.PSYCHIC and "psychic" in type_name.lower():
                return 0.2
        
        return 0.0
    
    def trick_room_affects_decision(
        self,
        user: BattleMon,
        opponent: BattleMon,
        is_trick_room: bool,
    ) -> bool:
        """
        Determine if Trick Room status affects speed-dependent decisions.
        
        Args:
            user: User Pokemon
            opponent: Opponent Pokemon
            is_trick_room: Whether Trick Room is active
            
        Returns:
            True if decision logic should be speed-reversed
        """
        if not is_trick_room:
            return False
        
        # Trick room is strategically important when user is slower
        return user.stat_speed < opponent.stat_speed
    
    def hazards_present(self, context: AIContext) -> Dict[str, bool]:
        """
        Check what hazards are present on opponent's side.
        
        Args:
            context: AIContext with battle state
            
        Returns:
            Dict of hazard_name -> is_present
        """
        hazards: Dict[str, bool] = {
            "stealth_rock": False,
            "spikes": False,
            "toxic_spikes": False,
            "sticky_web": False,
            "reflect": False,
            "light_screen": False,
        }
        
        # Would check BattleManager.field_effects for actual hazard state
        # For now, return empty dict (hazards not fully tracked in context)
        
        return hazards
    
    def screens_active(self, context: "AIContext", team_side: bool = True) -> Dict[str, bool]:
        """
        Check what screens are active.
        
        Args:
            context: AIContext with battle state
            team_side: True to check user's screens, False for opponent
            
        Returns:
            Dict of screen_name -> is_active
        """
        screens: Dict[str, bool] = {
            "reflect": False,
            "light_screen": False,
            "aurora_veil": False,
        }
        
        # Would check BattleManager for actual screen state
        
        return screens