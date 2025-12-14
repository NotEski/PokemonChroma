from pydantic import BaseModel, Field
from typing import List
from shared.pokemon.team import Team

class BattleTrainer(BaseModel):
    name: str
    team: Team