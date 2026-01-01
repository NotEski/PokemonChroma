from pydantic import BaseModel, Field
from typing import Dict, TypeVar, Generic

from shared.pokemon.hazard import EntryHazard
from shared.pokemon.pokemon import PokemonBase
from shared.pokemon.abilities import Ability
from shared.pokemon.move import BaseMove
from shared.items.items import Item
from shared.pokemon.status_conditions import StatusCondition
from shared.battle.field_effect import FieldEffect

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
        return self.items.get(str(key).lower())

    def get_index_by_name(self, name: str) -> str:
        key = name.lower()
        if key in self.items:
            return key
        raise KeyError(f"{type(self).__name__} with name '{name}' not found.")
    
    def delete(self, key: str) -> None:
        key = key.lower()
        if key in self.items:
            del self.items[key]
        else:
            raise KeyError(f"{type(self).__name__} with name '{key}' not found.")

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
    def get(self, key: str|int) -> T:
        if isinstance(key, int):
            for move in self.items.values():
                if move.index == key:
                    return move
            return None
        elif isinstance(key, str):
            return self.items.get(str(key).lower())
        else:
            raise ValueError("Key must be a string (name) or integer (index).")


class PokemonAbilityRepository(BaseRepository[Ability]):
    pass

class ItemRepository(BaseRepository[Item]):
    pass

class StatusConditionRepository(BaseRepository[StatusCondition]):
    pass

class HazardRepository(BaseRepository[EntryHazard]):
    pass

class FieldEffectRepository(BaseRepository[FieldEffect]):
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

class ItemRepositorySingleton(BaseSingleton[ItemRepository]):
    @classmethod
    def _create_instance(cls) -> ItemRepository:
        return ItemRepository()
    
class StatusConditionRepositorySingleton(BaseSingleton[StatusConditionRepository]):
    @classmethod
    def _create_instance(cls) -> StatusConditionRepository:
        return StatusConditionRepository()
    
class HazardRepositorySingleton(BaseSingleton[HazardRepository]):
    @classmethod
    def _create_instance(cls) -> HazardRepository:
        return HazardRepository()
    
class FieldEffectRepositorySingleton(BaseSingleton[FieldEffectRepository]):
    @classmethod
    def _create_instance(cls) -> FieldEffectRepository:
        return FieldEffectRepository()

# Module-level instances
pokemon_repository = PokemonRepositorySingleton.get_instance()
ability_repository = PokemonAbilityRepositorySingleton.get_instance()
move_repository = MoveRepositorySingleton.get_instance()
item_repository = ItemRepositorySingleton.get_instance()
status_repository = StatusConditionRepositorySingleton.get_instance()
hazard_repository = HazardRepositorySingleton.get_instance()
field_effect_repository = FieldEffectRepositorySingleton.get_instance()