# Auto-generated from pokeapi_database/type/*.json
# Do not edit by hand. Regenerate via tools/generate_type_chart.py

from typing import Mapping
from shared.pokemon.types import PokemonType

TYPE_EFFECTIVENESS: Mapping[PokemonType, dict[PokemonType, float]] = {
    PokemonType.NORMAL: {
        PokemonType.GHOST: 0.0,
        PokemonType.ROCK: 0.5,
        PokemonType.STEEL: 0.5,
    },
    PokemonType.FIRE: {
        PokemonType.BUG: 2.0,
        PokemonType.DRAGON: 0.5,
        PokemonType.FIRE: 0.5,
        PokemonType.GRASS: 2.0,
        PokemonType.ICE: 2.0,
        PokemonType.ROCK: 0.5,
        PokemonType.STEEL: 2.0,
        PokemonType.WATER: 0.5,
    },
    PokemonType.WATER: {
        PokemonType.DRAGON: 0.5,
        PokemonType.FIRE: 2.0,
        PokemonType.GRASS: 0.5,
        PokemonType.GROUND: 2.0,
        PokemonType.ROCK: 2.0,
        PokemonType.WATER: 0.5,
    },
    PokemonType.ELECTRIC: {
        PokemonType.DRAGON: 0.5,
        PokemonType.ELECTRIC: 0.5,
        PokemonType.FLYING: 2.0,
        PokemonType.GRASS: 0.5,
        PokemonType.GROUND: 0.0,
        PokemonType.WATER: 2.0,
    },
    PokemonType.GRASS: {
        PokemonType.BUG: 0.5,
        PokemonType.DRAGON: 0.5,
        PokemonType.FIRE: 0.5,
        PokemonType.FLYING: 0.5,
        PokemonType.GRASS: 0.5,
        PokemonType.GROUND: 2.0,
        PokemonType.POISON: 0.5,
        PokemonType.ROCK: 2.0,
        PokemonType.STEEL: 0.5,
        PokemonType.WATER: 2.0,
    },
    PokemonType.ICE: {
        PokemonType.DRAGON: 2.0,
        PokemonType.FIRE: 0.5,
        PokemonType.FLYING: 2.0,
        PokemonType.GRASS: 2.0,
        PokemonType.GROUND: 2.0,
        PokemonType.ICE: 0.5,
        PokemonType.STEEL: 0.5,
        PokemonType.WATER: 0.5,
    },
    PokemonType.FIGHTING: {
        PokemonType.BUG: 0.5,
        PokemonType.DARK: 2.0,
        PokemonType.FAIRY: 0.5,
        PokemonType.FLYING: 0.5,
        PokemonType.GHOST: 0.0,
        PokemonType.ICE: 2.0,
        PokemonType.NORMAL: 2.0,
        PokemonType.POISON: 0.5,
        PokemonType.PSYCHIC: 0.5,
        PokemonType.ROCK: 2.0,
        PokemonType.STEEL: 2.0,
    },
    PokemonType.POISON: {
        PokemonType.FAIRY: 2.0,
        PokemonType.GHOST: 0.5,
        PokemonType.GRASS: 2.0,
        PokemonType.GROUND: 0.5,
        PokemonType.POISON: 0.5,
        PokemonType.ROCK: 0.5,
        PokemonType.STEEL: 0.0,
    },
    PokemonType.GROUND: {
        PokemonType.BUG: 0.5,
        PokemonType.ELECTRIC: 2.0,
        PokemonType.FIRE: 2.0,
        PokemonType.FLYING: 0.0,
        PokemonType.GRASS: 0.5,
        PokemonType.POISON: 2.0,
        PokemonType.ROCK: 2.0,
        PokemonType.STEEL: 2.0,
    },
    PokemonType.FLYING: {
        PokemonType.BUG: 2.0,
        PokemonType.ELECTRIC: 0.5,
        PokemonType.FIGHTING: 2.0,
        PokemonType.GRASS: 2.0,
        PokemonType.ROCK: 0.5,
        PokemonType.STEEL: 0.5,
    },
    PokemonType.PSYCHIC: {
        PokemonType.DARK: 0.0,
        PokemonType.FIGHTING: 2.0,
        PokemonType.POISON: 2.0,
        PokemonType.PSYCHIC: 0.5,
        PokemonType.STEEL: 0.5,
    },
    PokemonType.BUG: {
        PokemonType.DARK: 2.0,
        PokemonType.FAIRY: 0.5,
        PokemonType.FIGHTING: 0.5,
        PokemonType.FIRE: 0.5,
        PokemonType.FLYING: 0.5,
        PokemonType.GHOST: 0.5,
        PokemonType.GRASS: 2.0,
        PokemonType.POISON: 0.5,
        PokemonType.PSYCHIC: 2.0,
        PokemonType.STEEL: 0.5,
    },
    PokemonType.ROCK: {
        PokemonType.BUG: 2.0,
        PokemonType.FIGHTING: 0.5,
        PokemonType.FIRE: 2.0,
        PokemonType.FLYING: 2.0,
        PokemonType.GROUND: 0.5,
        PokemonType.ICE: 2.0,
        PokemonType.STEEL: 0.5,
    },
    PokemonType.GHOST: {
        PokemonType.DARK: 0.5,
        PokemonType.GHOST: 2.0,
        PokemonType.NORMAL: 0.0,
        PokemonType.PSYCHIC: 2.0,
    },
    PokemonType.DRAGON: {
        PokemonType.DRAGON: 2.0,
        PokemonType.FAIRY: 0.0,
        PokemonType.STEEL: 0.5,
    },
    PokemonType.DARK: {
        PokemonType.DARK: 0.5,
        PokemonType.FAIRY: 0.5,
        PokemonType.FIGHTING: 0.5,
        PokemonType.GHOST: 2.0,
        PokemonType.PSYCHIC: 2.0,
    },
    PokemonType.STEEL: {
        PokemonType.ELECTRIC: 0.5,
        PokemonType.FAIRY: 2.0,
        PokemonType.FIRE: 0.5,
        PokemonType.ICE: 2.0,
        PokemonType.ROCK: 2.0,
        PokemonType.STEEL: 0.5,
        PokemonType.WATER: 0.5,
    },
    PokemonType.FAIRY: {
        PokemonType.DARK: 2.0,
        PokemonType.DRAGON: 2.0,
        PokemonType.FIGHTING: 2.0,
        PokemonType.FIRE: 0.5,
        PokemonType.POISON: 0.5,
        PokemonType.STEEL: 0.5,
    },
}




def offensive_effectiveness_all(attacking_type: PokemonType) -> dict[PokemonType, float]:
    """Get the offensive type effectiveness chart for a given attacking type.

    Args:
        attacking_type: The attacking PokemonType.
    Returns:
        A dictionary mapping defending PokemonTypes to their effectiveness multiplier.
    """
    effectiveness: dict[PokemonType, float] = {}
    effectiveness = TYPE_EFFECTIVENESS.get(attacking_type, {})
    for _type in PokemonType:
        if _type not in effectiveness:
            effectiveness[_type] = 1.0
    return effectiveness

def defensive_effectiveness_all(defending_type: PokemonType) -> dict[PokemonType, float]:
    """Get the defensive type effectiveness chart for a given defending type.

    Args:
        defending_type: The defending PokemonType.
    Returns:
        A dictionary mapping attacking PokemonTypes to their effectiveness multiplier.
    """
    effectiveness: dict[PokemonType, float] = {}
    for attacking_type in PokemonType:
        attacking_effectiveness = TYPE_EFFECTIVENESS.get(attacking_type, {})
        multiplier = attacking_effectiveness.get(defending_type, 1.0)
        effectiveness[attacking_type] = multiplier
    return effectiveness

def effectiveness(attacking_type: PokemonType, defending_type: PokemonType) -> float:
    """Get the offensive type effectiveness multiplier for a given attacking and defending type.

    Args:
        attacking_type: The attacking PokemonType.
        defending_type: The defending PokemonType.
    Returns:
        The effectiveness multiplier as a float.
    """
    attacking_effectiveness = TYPE_EFFECTIVENESS.get(attacking_type, {})
    return attacking_effectiveness.get(defending_type, 1.0)

def get_attack_multiplier(attacking_type: PokemonType, defending_types: list[PokemonType]) -> float:
    """Calculate the total attack multiplier for an attacking type against multiple defending types.

    Args:
        attacking_type: The attacking PokemonType.
        defending_types: A list of defending PokemonTypes.
    Returns:
        The total effectiveness multiplier as a float.
    """
    multiplier = 1.0
    for defending_type in defending_types:
        multiplier *= effectiveness(attacking_type, defending_type)
    return multiplier