from pydantic import BaseModel
from typing import Any

class BattlePosition(BaseModel):
    team_id: int = 0
    pokemon_index: int = 0

    def set(self, other: 'BattlePosition'):
        if isinstance(other, tuple) and len(other) == 2:
            self.team_id = other[0]
            self.pokemon_index = other[1]
            return
        self.team_id = other.team_id
        self.pokemon_index = other.pokemon_index

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, (BattlePosition|tuple)):
            return NotImplemented
        if isinstance(other, tuple) and len(other) == 2: # type: ignore
            other_team_id: int = other[0] # type: ignore
            other_pokemon_index: int = other[1] # type: ignore
            if not isinstance(other_team_id, int) or not isinstance(other_pokemon_index, int):
                return NotImplemented
            return self.team_id == other_team_id and self.pokemon_index == other_pokemon_index
        elif not isinstance(other, BattlePosition):
            return NotImplemented
        return self.team_id == other.team_id and self.pokemon_index == other.pokemon_index

    def __hash__(self):
        return hash((self.team_id, self.pokemon_index))