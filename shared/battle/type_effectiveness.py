# Auto-generated from pokeapi_database/type/*.json
# Do not edit by hand. Regenerate via tools/generate_type_chart.py

from enum import Enum
from engine.repositories.repository import type_repository
from shared.pokemon.pokemon_types import PokemonType


class EffectivenessLevel(Enum):
    NO_EFFECT = 0
    NOT_EFFECTIVE = 1
    NORMAL_EFFECTIVE = 2
    SUPER_EFFECTIVE = 3


def offensive_effectiveness_all(attacking_type: PokemonType) -> dict[PokemonType, float]:
    """Get the offensive type effectiveness chart for a given attacking type.

    Args:
        attacking_type: The attacking PokemonType.
    Returns:
        A dictionary mapping defending PokemonTypes to their effectiveness multiplier.
    """
    effectiveness = attacking_type.effectiveness.copy()

    for _type in type_repository.list():
        if _type not in effectiveness:
            effectiveness[PokemonType(_type)] = 1.0
    return effectiveness

def defensive_effectiveness_all(defending_type: PokemonType) -> dict[PokemonType, float]:
    """Get the defensive type effectiveness chart for a given defending type.

    Args:
        defending_type: The defending PokemonType.
    Returns:
        A dictionary mapping attacking PokemonTypes to their effectiveness multiplier.
    """
    effectiveness: dict[PokemonType, float] = {}
    for attacking_type in type_repository.list():
        attacking_effectiveness = PokemonType(attacking_type).effectiveness
        multiplier = attacking_effectiveness.get(defending_type, 1.0)
        effectiveness[PokemonType(attacking_type)] = multiplier
    return effectiveness

def effectiveness(attacking_type: PokemonType, defending_type: PokemonType) -> float:
    """Get the offensive type effectiveness multiplier for a given attacking and defending type.

    Args:
        attacking_type: The attacking Pokemon Type.
        defending_type: The defending Pokemon Type.
    Returns:
        The effectiveness multiplier as a float.
    """
    return attacking_type.effectiveness.get(defending_type, 1.0)

def effectiveness_multiplier(attacking_type: PokemonType, defending_types: list[PokemonType]) -> float:
    multiplier = 1.0
    for defending_type in defending_types:
        multiplier *= effectiveness(attacking_type, defending_type)
    return multiplier

def get_attack_multiplier(attacking_type: PokemonType, defending_types: list[PokemonType]) -> float:
    """Calculate the total attack multiplier for an attacking type against multiple defending types.

    Args:
        attacking_type: The attacking Pokemon Type.
        defending_types: A list of defending Pokemon Types.
    Returns:
        The total effectiveness multiplier as a float.
    """
    multiplier = 1.0
    for defending_type in defending_types:
        multiplier *= effectiveness(attacking_type, defending_type)
    return multiplier

def get_effectiveness_level(multiplier: float) -> EffectivenessLevel:
    """Convert a multiplier to an EffectivenessLevel.

    Args:
        multiplier: The effectiveness multiplier.
    Returns:
        The corresponding EffectivenessLevel.
    """
    if multiplier == 0.0:
        return EffectivenessLevel.NO_EFFECT
    elif 0.0 < multiplier < 1.0:
        return EffectivenessLevel.NOT_EFFECTIVE
    elif multiplier == 1.0:
        return EffectivenessLevel.NORMAL_EFFECTIVE
    else:  # multiplier > 1.0
        return EffectivenessLevel.SUPER_EFFECTIVE

def effectiveness_message(level: EffectivenessLevel) -> str:
    match level:
        case EffectivenessLevel.SUPER_EFFECTIVE:
            return "It's super effective!"
        case EffectivenessLevel.NOT_EFFECTIVE:
            return "It's not very effective..."
        case EffectivenessLevel.NO_EFFECT:
            return "It had no effect!"
        case EffectivenessLevel.NORMAL_EFFECTIVE:
            return ""
        case _:
            return ""