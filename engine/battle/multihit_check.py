from shared.pokemon.move import BaseMove
from shared.pokemon.move_tags import MultiHitMove
from shared.pokemon.pokemon import BattleMon
from random import choices


default_weights = {
    2: 35,
    3: 35,
    4: 15,
    5: 15
}


def multihit_check(move: BaseMove, attacker: BattleMon, target: BattleMon) -> int:
    """Check the amount of times a multi-hit move will hit."""
    # sanity check
    if not move.is_multi_hit:
        return 1
    
    # Run checks for abilities or items that may affect multi-hit moves here
    # e.g. Skill Link, etc.
    
    multimove_tag = move.get_tag(MultiHitMove)

    if multimove_tag.hits is None:
        weights = default_weights
    else:
        weights = multimove_tag.hits

    hit_amounts = list(weights.keys())
    hit_weights = list(weights.values())
    move_hits = choices(hit_amounts, weights=hit_weights)[0]
    
    return move_hits