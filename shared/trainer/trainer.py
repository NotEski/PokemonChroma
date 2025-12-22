from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from shared.pokemon.pokemon import PokemonTeam
import uuid

class PronounMixin(BaseModel):
    subject_pronoun: str
    object_pronoun: str
    posessive_pronoun: str

class PronounEnum(str, Enum):
    HE_HIM = ["he/him", "he", "him", "his"]
    SHE_HER = ["she/her", "she", "her", "hers"]
    THEY_THEM = ["they/them", "they", "them", "theirs"]
    CUSTOM = ["custom", "custom", "custom", "custom"]

    def to_pronoun_mixin(self, custom_pronouns: Optional[dict] = None) -> PronounMixin:
        if self == PronounEnum.CUSTOM and custom_pronouns:
            return PronounMixin(
                subject_pronoun=custom_pronouns.get("subject_pronoun", "they"),
                object_pronoun=custom_pronouns.get("object_pronoun", "them"),
                posessive_pronoun=custom_pronouns.get("posessive_pronoun", "theirs"),
            )
        else:
            return PronounMixin(
                subject_pronoun=self.value[1],
                object_pronoun=self.value[2],
                posessive_pronoun=self.value[3],
            )


class OriginalTrainer(object):
    name: str
    unique_id: str
    pronouns: Optional[PronounMixin] = None
    trainer_type: Optional[str] = None  # e.g., "Ace Trainer", "Gym Leader", etc.


class Trainer(BaseModel):
    name: str
    unique_id: Optional[str] = None # this is a hidden field that is generated if not provided
    id_number: int = Field(default=0)
    team: PokemonTeam

    pronouns: PronounMixin = Field(default=PronounEnum.THEY_THEM.to_pronoun_mixin())

    trainer_type: Optional[str] = None  # e.g., "Ace Trainer", "Gym Leader", etc.

    def __init__(self, **data):
        if 'unique_id' not in data or data['unique_id'] is None:
            data['unique_id'] = str(uuid.uuid4())
        data['id_number'] = self.calculate_id_number(data['unique_id'])
        super().__init__(**data)

    def calculate_id_number(self, unique_id: str) -> int:
        # Simple hash function to convert unique_id to a numeric ID
        return sum(ord(char) for char in unique_id) % 1000000  # Limit to 6 digits
    
    def original_trainer_factory(self) -> OriginalTrainer:
        name: str = self.name

        return OriginalTrainer(
            name=name,
            unique_id=self.unique_id,
            pronouns=self.pronouns.model_copy() if self.pronouns else None,
            trainer_type=self.trainer_type
        )





