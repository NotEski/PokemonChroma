from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import core_schema, CoreSchema
from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.repositories.repository import TypeRepository

type_repository: Optional['TypeRepository'] = None

def setup_pokemon_type_repository(repository: 'TypeRepository') -> None:
    """Function to setup the PokemonType repository by loading all types from the repository."""
    global type_repository
    type_repository = repository

class PokemonTypeData(BaseModel):
    model_config = {"frozen": True}

    name: str
    id: str
    icon: bytes

    effectiveness: dict['PokemonType', float] = {}

    def __hash__(self) -> int:
        return hash(self.id)

class PokemonType(str):
    def __new__(cls, value: str) -> 'PokemonType':
        return str.__new__(cls, value)
    
    def __get_type_data__(self) -> PokemonTypeData:
        global type_repository
        if type_repository is None:
            raise ValueError("Type repository is not initialized. Call setup_pokemon_type_repository first.")
        return_type = type_repository.get(self)
        if not return_type:
            raise ValueError(f"PokemonType '{self}' not found in repository.")
        return return_type
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance),
                return_schema=core_schema.str_schema(),
            ),
        )

    @property
    def name(self) -> str:
        return self.__get_type_data__().name
    
    @property
    def icon(self) -> bytes:
        return self.__get_type_data__().icon
    
    @property
    def effectiveness(self) -> dict['PokemonType', float]:
        return self.__get_type_data__().effectiveness