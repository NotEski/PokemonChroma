from pydantic import BaseModel, Field
from typing import Dict, TypeVar, Generic

from shared.pokemon.pokemon import PokemonBase
from shared.pokemon.abilities import Ability
from shared.pokemon.move import BaseMove

T = TypeVar('T')


class BaseRepository(BaseModel, Generic[T]):
    """Generic base repository for managing entities."""
    items: Dict[str, T] = Field(default_factory=dict)

    def create(self, item: T, force: bool = False):
        key = item.name.lower()
        if key in self.items and not force:
            raise ValueError(f"{type(item).__name__} with name '{item.name}' already exists.")
        self.items[key] = item

    def get(self, key: str) -> T:
        return self.items.get(key.lower())

    def list(self) -> Dict[str, T]:
        return self.items


class BaseSingleton(Generic[T]):
    """Generic singleton pattern implementation."""
    _instance: T = None

    @classmethod
    def get_instance(cls) -> T:
        if cls._instance is None:
            cls._instance = cls._create_instance()
        return cls._instance

    @classmethod
    def _create_instance(cls) -> T:
        raise NotImplementedError

    @classmethod
    def reset_instance(cls):
        cls._instance = None


# Concrete Repositories
class PokemonRepository(BaseRepository[PokemonBase]):
    pass


class MoveRepository(BaseRepository[BaseMove]):
    pass


class PokemonAbilityRepository(BaseRepository[Ability]):
    pass


# Concrete Singletons
class PokemonRepositorySingleton(BaseSingleton[PokemonRepository]):
    @classmethod
    def _create_instance(cls) -> PokemonRepository:
        return PokemonRepository()


class MoveRepositorySingleton(BaseSingleton[MoveRepository]):
    @classmethod
    def _create_instance(cls) -> MoveRepository:
        return MoveRepository()


class PokemonAbilityRepositorySingleton(BaseSingleton[PokemonAbilityRepository]):
    @classmethod
    def _create_instance(cls) -> PokemonAbilityRepository:
        return PokemonAbilityRepository()


# Module-level instances
pokemon_repository = PokemonRepositorySingleton.get_instance()
ability_repository = PokemonAbilityRepositorySingleton.get_instance()
move_repository = MoveRepositorySingleton.get_instance()
