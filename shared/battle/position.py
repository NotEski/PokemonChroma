from pydantic import BaseModel

class BattlePosition(BaseModel):
    team_id: int = 0
    pokemon_index: int = 0

    def set(self, other: 'BattlePosition'):
        if isinstance(other, tuple) and len(other) == 2:
            self.team_id = other[0]
            self.pokemon_index = other[1]
            return
        elif not isinstance(other, BattlePosition):
            raise ValueError("Can only set from another BattlePosition instance.")
        self.team_id = other.team_id
        self.pokemon_index = other.pokemon_index

    def __eq__(self, other):
        if isinstance(other, tuple) and len(other) == 2:
            return self.team_id == other[0] and self.pokemon_index == other[1]
        elif not isinstance(other, BattlePosition):
            return NotImplemented
        return self.team_id == other.team_id and self.pokemon_index == other.pokemon_index

    def __hash__(self):
        return hash((self.team_id, self.pokemon_index))