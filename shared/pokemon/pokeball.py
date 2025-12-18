from pydantic import BaseModel
from typing import Optional

class Pokeball(BaseModel):
    name: str
    catch_rate_modifier: float  # Multiplier to the base catch rate of the Pokemon
    special_effect: Optional[str] = None  # e.g., "higher catch rate for certain types"