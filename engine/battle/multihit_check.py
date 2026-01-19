from typing import Optional
from shared.pokemon.move import BaseMove
from shared.pokemon.move_tags import MultiHitMove
from random import choices

def multihit_check(move: BaseMove) -> int:
    """Check the amount of times a multi-hit move will hit."""
    multimove_tag: Optional[MultiHitMove] = move.get_tag(MultiHitMove) # type: ignore

    if not move.is_multi_hit or multimove_tag is None:
        return 1
    
    # Run checks for abilities or items that may affect multi-hit moves here
    # e.g. Skill Link, etc.

    weights: dict[int, int] = multimove_tag.hits

    hit_amounts = list(weights.keys())
    hit_weights = list(weights.values())
    move_hits = choices(hit_amounts, weights=hit_weights)[0]
    
    return move_hits