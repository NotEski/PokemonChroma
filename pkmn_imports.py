"""
Type stubs for .pkmn DSL files.
This file provides type hints and IDE support for the Pokemon DSL.
"""

from typing import Callable, TypeVar, Any
from shared.pokemon.stats import BaseStats, EffortYield, Stat
from shared.pokemon.pokemon_types import PokemonType
from shared.pokemon.status_conditions import StatusCondition
from shared.pokemon.move import BaseMove, MoveMetaData, DamageClass, MoveCategory, MoveTarget
from shared.pokemon.abilities import Ability
from shared.items.items import Item
from shared.pokemon.hazard import EntryHazard
from shared.battle.field_effect import FieldEffect
from shared.pokemon.pokemon import BattleMon
from shared.battle.type_effectiveness import get_attack_multiplier as _get_attack_multiplier # type: ignore

# TypeVar for decorators
T = TypeVar('T', bound=type)

# ==============================================================================
# Built-in Functions (available in DSL)
# ==============================================================================

def max(*args: Any, **kwargs: Any) -> Any:
    """Return the largest item in an iterable or the largest of two or more arguments."""
    ...

def min(*args: Any, **kwargs: Any) -> Any:
    """Return the smallest item in an iterable or the smallest of two or more arguments."""
    ...

def len(obj: Any) -> int:
    """Return the length of an object."""
    ...

def randint(a: int, b: int) -> int:
    """Return a random integer N such that a <= N <= b."""
    ...

def print(*args: Any, **kwargs: Any) -> None:
    """Print values to stdout (for debugging purposes only)."""
    ...

# ==============================================================================
# Decorators
# ==============================================================================

def pokemon_type(type_id: str) -> Callable[[T], T]:
    """
    Decorator for defining Pokemon types.
    
    Args:
        type_id: The unique identifier for the type.
    
    Example:
        @pokemon_type("fire")
        class Fire:
            meta = {
                "display_name": "Fire",
                ...
            }
    """
    ...

def move(move_name: str) -> Callable[[T], T]:
    """
    Decorator for defining Pokemon moves.
    
    Args:
        move_name: The unique identifier for the move.
    
    Example:
        @move("thunderbolt")
        class Thunderbolt:
            meta = {"display_name": "Thunderbolt", ...}
            type = "electric"
            category = "special"
            power = 90
            accuracy = 100
            pp = 15
            ...
    """
    ...

def status(status_name: str) -> Callable[[T], T]:
    """
    Decorator for defining status conditions.
    
    Args:
        status_name: The unique identifier for the status condition.
    
    Example:
        @status("burn")
        class Burn:
            meta = {"display_name": "Burn", ...}
            ...
    """
    ...

def item(item_name: str) -> Callable[[T], T]:
    """
    Decorator for defining items.
    
    Args:
        item_name: The unique identifier for the item.
    
    Example:
        @item("potion")
        class Potion:
            meta = {"display_name": "Potion", ...}
            ...
    """
    ...

def ability(ability_name: str) -> Callable[[T], T]:
    """
    Decorator for defining Pokemon abilities.
    
    Args:
        ability_name: The unique identifier for the ability.
    
    Example:
        @ability("blaze")
        class Blaze:
            meta = {"display_name": "Blaze", ...}
            ...
    """
    ...

def hazard(hazard_name: str) -> Callable[[T], T]:
    """
    Decorator for defining entry hazards.
    
    Args:
        hazard_name: The unique identifier for the hazard.
    
    Example:
        @hazard("spikes")
        class Spikes:
            meta = {"display_name": "Spikes", ...}
            
            def on_entry(self, pokemon, layer_count):
                ...
    """
    ...

def field_effect(field_effect_name: str) -> Callable[[T], T]:
    """
    Decorator for defining field effects.
    
    Args:
        field_effect_name: The unique identifier for the field effect.
    
    Example:
        @field_effect("trick_room")
        class TrickRoom:
            meta = {
                "display_name": "Trick Room",
                "default_duration": 5
            }
            
            def on_apply(self, position):
                ...
    """
    ...

def pokemon(pokemon_name: str) -> Callable[[T], T]:
    """
    Decorator for defining Pokemon species.
    
    Args:
        pokemon_name: The unique identifier for the Pokemon.
    
    Example:
        @pokemon("bulbasaur")
        class Bulbasaur:
            id = 1
            display_name = "Bulbasaur"
            types = ["grass", "poison"]
            base_stats = BaseStats(hp=45, attack=49, ...)
            ...
    """
    ...

def mega_evolution(mega_evolution_name: str) -> Callable[[T], T]:
    """
    Decorator for defining Mega Evolutions.
    
    Args:
        mega_evolution_name: The unique identifier for the Mega Evolution.
    
    Example:
        @mega_evolution("charizard_x")
        class CharizardX:
            ...
    """
    ...

# ==============================================================================
# Helper Functions
# ==============================================================================

def get_status_condition(status_name: str) -> StatusCondition:
    """
    Retrieve a status condition by name.
    
    Args:
        status_name: The name of the status condition (e.g., "burn", "poison").
    
    Returns:
        The StatusCondition object.
    
    Raises:
        ValueError: If the status condition is not found.
    """
    ...

def get_move(move_name: str) -> BaseMove:
    """
    Retrieve a move by name.
    
    Args:
        move_name: The name of the move (e.g., "thunderbolt", "tackle").
    
    Returns:
        The BaseMove object.
    
    Raises:
        ValueError: If the move is not found.
    """
    ...

def get_ability(ability_name: str) -> Ability:
    """
    Retrieve an ability by name.
    
    Args:
        ability_name: The name of the ability (e.g., "blaze", "torrent").
    
    Returns:
        The Ability object.
    
    Raises:
        ValueError: If the ability is not found.
    """
    ...

def get_item(item_name: str) -> Item:
    """
    Retrieve an item by name.
    
    Args:
        item_name: The name of the item (e.g., "potion", "pokeball").
    
    Returns:
        The Item object.
    
    Raises:
        ValueError: If the item is not found.
    """
    ...

def get_attack_multiplier(
    attacking_type: PokemonType,
    defending_types: list[PokemonType]
) -> float:
    """
    Calculate the type effectiveness multiplier for an attack.
    
    Args:
        attacking_type: The type of the attacking move.
        defending_types: The types of the defending Pokemon.
    
    Returns:
        The effectiveness multiplier (e.g., 2.0 for super effective, 0.5 for not very effective).
    """
    ...


# ==============================================================================
# Re-exports (available in DSL namespace)
# ==============================================================================

__all__ = [
    # Built-ins that are not normally
    "randint",
    
    # Decorators
    "pokemon_type", "move", "status", "item", "ability",
    "hazard", "field_effect", "pokemon", "mega_evolution",
    
    # Helper functions
    "get_status_condition", "get_move", "get_ability", 
    "get_item", "get_attack_multiplier",
    
    # Imported classes
    "BaseStats", "EffortYield", "PokemonType", "Stat",
    "StatusCondition", "BaseMove", "Ability", "Item",
    "EntryHazard", "BattleMon", "FieldEffect", "MoveMetaData",
    "DamageClass", "MoveCategory", "MoveTarget",
]
