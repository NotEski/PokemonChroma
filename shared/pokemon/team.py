from pydantic import BaseModel, Field
from typing import List
from .pokemon import Pokemon


class Team(BaseModel):
    pokemons: List[Pokemon] = Field(min_items=1, max_items=6)

