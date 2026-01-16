from pydantic import BaseModel, Field
from typing import Dict, Optional, TypeVar, Generic

from shared.pokemon.hazard import EntryHazard
from shared.pokemon.pokemon import PokemonBase
from shared.pokemon.abilities import Ability
from shared.pokemon.move import BaseMove, MoveCategory, MoveTarget
from shared.pokemon.move_tags import *
from shared.items.items import Item
from shared.pokemon.status_conditions import StatusCondition
from shared.battle.field_effect import FieldEffect

T = TypeVar('T')


class BaseRepository(BaseModel, Generic[T]):
    """Generic base repository for managing entities."""
    items: Dict[str, T] = Field(default_factory=dict)

    def create(self, item: T, force: bool = False):
        if not hasattr(item, "name"):
            raise ValueError("Item must have a 'name' attribute.")
        elif not isinstance(item.name, str): # type: ignore
            raise ValueError("Item 'name' attribute must be of type str.")
        
        key: str = item.name.lower() # type: ignore
        if key in self.items and not force:
            raise ValueError(f"{type(item).__name__} with name '{item.name}' already exists.") # type: ignore
        self.items[key] = item

    def get(self, key: str) -> Optional[T]:
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
    _instance: Optional[T] = None

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
    def get(self, key: str) -> Optional[PokemonBase]:
        return super().get(key)


class MoveRepository(BaseRepository[BaseMove]):
    def get(self, key: str|int) -> Optional[BaseMove]:
        if isinstance(key, int):
            for move in self.items.values():
                if move.index == key:
                    return move
            return None
        elif isinstance(key, str): # type: ignore
            return self.items.get(str(key).lower())
        else:
            raise ValueError("Key must be a string (name) or integer (index).")
        
    @property
    def categories(self) -> "MoveCategories":
        """Lazy-load move categories on first access."""
        if self._categories is None: # type: ignore
            self._categories = MoveCategories()
            self._categories.build_all_categories()
        return self._categories

    def refresh_categories(self):
        """Refresh move categories."""
        self._categories = MoveCategories()
        self._categories.build_all_categories()

    @property
    def priority_moves(self) -> dict[BaseMove, int]:
        return self.categories.priority_moves
    @property
    def setup_moves(self) -> dict[BaseMove, list[StatChangeMove]]:
        return self.categories.setup_moves
    @property
    def hazard_moves(self) -> list[BaseMove]:
        return self.categories.hazard_moves
    @property
    def healing_moves(self) -> list[BaseMove]:
        return self.categories.healing_moves
    @property
    def ohko_moves(self) -> list[BaseMove]:
        return self.categories.ohko_moves
    @property
    def spread_moves(self) -> list[BaseMove]:
        return self.categories.spread_moves
    @property
    def protect_moves(self) -> list[BaseMove]:
        return self.categories.protect_moves
    @property
    def status_moves(self) -> list[BaseMove]:
        return self.categories.status_moves
    @property
    def screen_moves(self) -> list[BaseMove]:
        return self.categories.screen_moves
    @property
    def weather_moves(self) -> list[BaseMove]:
        return self.categories.weather_moves
    @property
    def terrain_moves(self) -> list[BaseMove]:
        return self.categories.terrain_moves
    @property
    def pivot_moves(self) -> list[BaseMove]:
        return self.categories.pivot_moves
    @property
    def damaging_moves(self) -> list[BaseMove]:
        return self.categories.damaging_moves
    
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


class MoveCategories:
    """
    Categorizes all Moves for intelligent AI decisions
    
    Categories:
    - Priority Moves (Quick Attack, Aqua Jet, Mach Punch, etc.)
    - Setup Moves (Swords Dance, Nasty Plot, Dragon Dance, etc.)
    - Hazard Moves (Stealth Rock, Spikes, Sticky Web, etc.)
    - Healing Moves (Roost, Recover, Synthesis, etc.)
    - OHKO Moves (Fissure, Guillotine, Sheer Cold, etc.)
    - Spread Moves (Earthquake, Surf, Rock Slide, etc.)
    - Protect Moves (Protect, Detect, Spiky Shield, etc.)
    - Status Moves (Will-O-Wisp, Thunder Wave, Toxic, etc.)
    - Screen Moves (Light Screen, Reflect, Aurora Veil, etc.)
    - Weather Moves (Rain Dance, Sunny Day, Sandstorm, etc.)
    - Terrain Moves (Electric Terrain, Grassy Terrain, etc.)
    - Pivot Moves (U-turn, Volt Switch, Flip Turn, etc.)
    """

    priority_moves: dict[BaseMove, int] = {} # set of move indexes with priority other than 0
    setup_moves: list[BaseMove] = []
    hazard_moves: list[BaseMove] = []
    healing_moves: list[BaseMove] = []
    ohko_moves: list[BaseMove] = []
    spread_moves: list[BaseMove] = []
    protect_moves: list[BaseMove] = []
    status_moves: list[BaseMove] = []
    screen_moves: list[BaseMove] = []
    weather_moves: list[BaseMove] = []
    terrain_moves: list[BaseMove] = []
    pivot_moves: list[BaseMove] = []
    damaging_moves: list[BaseMove] = []


    def build_priority_moves(self):
        """Build the set of priority move categories from move repo."""
        for move in move_repository.items.values():
            if move.priority != 0:
                self.priority_moves[move] = move.priority
    
    def build_setup_moves(self):
        """Build the set of setup move categories from move repo."""
        for move in move_repository.items.values():
            new_setup_move: Optional[SetupMove] = None
            # setup_tag = move.has_any_tag([StatChangeReceivedMove, StatChangeReceivedMove]) # type: ignore
            # if not setup_tag: continue
            if move.has_tag(StatChangeReceivedMove):
                if new_setup_move is None:
                    new_setup_move = SetupMove()
                new_setup_move.stat_changes_received.append(move.get_tag(StatChangeReceivedMove)) # type: ignore
            if move.has_tag(StatChangeInflictedMove):
                if new_setup_move is None:
                    new_setup_move = SetupMove()
                new_setup_move.stat_changes_inflicted.append(move.get_tag(StatChangeInflictedMove)) # type: ignore

            if new_setup_move is None: # Can't be called a setup move without stat changes
                continue

            if move in self.damaging_moves:
                new_setup_move.damages_opponent = True
            # Check for recoil or self-damage
                if move.has_tag(DrainMove):
                    drain_move = move.get_tag(DrainMove) # type: ignore
                    if isinstance(drain_move, DrainMove):
                        if drain_move.drain_percentage < 0:
                            new_setup_move.recoil_percentage = abs(drain_move.drain_percentage)
                            new_setup_move.damages_user = True

            if move.has_tag(TrapOpponentMove):
                new_setup_move.trap_opponent = True
            if move.has_tag(TrapUserMove):
                new_setup_move.trap_user = True

            secondary_effects: list[MoveTag] = []
            for tag in move.move_tags:
                if not isinstance(tag, (StatChangeInflictedMove, StatChangeReceivedMove, TrapOpponentMove, TrapUserMove, DrainMove)):
                    secondary_effects.append(tag)

            move.add_tag(new_setup_move)
            self.setup_moves.append(move)

    def build_hazard_moves(self):
        """Build the set of hazard move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(HazardMove):
                self.hazard_moves.append(move)

    def build_healing_moves(self):
        """Build the set of healing move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(HealMove):
                self.healing_moves.append(move)
            elif move.has_tag(DrainMove) and move.get_tag(DrainMove).drain_percentage > 0: # type: ignore
                self.healing_moves.append(move)

    def build_ohko_moves(self):
        """Build the set of OHKO move categories from move repo."""
        for move in move_repository.items.values():
            if move.is_ohko:
                self.ohko_moves.append(move)

    def build_spread_moves(self):
        """Build the set of spread move categories from move repo."""
        for move in move_repository.items.values():
            if move.target in [MoveTarget.ALL_OPPONENTS, MoveTarget.ALL_OTHER_POKEMON, MoveTarget.ALL_POKEMON]:
                self.spread_moves.append(move)

    def build_protect_moves(self):
        """Build the set of protect move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(ProtectMove):
                self.protect_moves.append(move)

    def build_status_moves(self):
        """Build the set of status move categories from move repo."""
        for move in move_repository.items.values():
            if move.is_status_condition_move:
                self.status_moves.append(move)

    def build_screen_moves(self):
        """Build the set of screen move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(ScreenMove):
                self.screen_moves.append(move)

    def build_weather_moves(self):
        """Build the set of weather move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(WeatherMove):
                self.weather_moves.append(move)

    def build_terrain_moves(self):
        """Build the set of terrain move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(TerrainMove):
                self.terrain_moves.append(move)

    def build_pivot_moves(self):
        """Build the set of pivot move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(PivotMove):
                self.pivot_moves.append(move)

    def build_damaging_moves(self):
        """Build the set of damaging move categories from move repo."""
        for move in move_repository.items.values():
            if move.category in [MoveCategory.DAMAGE, MoveCategory.DAMAGE_HEAL, MoveCategory.DAMAGE_STATUS, MoveCategory.DAMAGE_LOWER, MoveCategory.DAMAGE_RAISE]:
                self.damaging_moves.append(move)

    def build_all_categories(self):
        """Build all move categories."""
        self.build_priority_moves()
        self.build_setup_moves()
        self.build_hazard_moves()
        self.build_healing_moves()
        self.build_ohko_moves()
        self.build_spread_moves()
        self.build_protect_moves()
        self.build_status_moves()
        self.build_screen_moves()
        self.build_weather_moves()
        self.build_terrain_moves()
        self.build_pivot_moves()


# Module-level instances
pokemon_repository = PokemonRepositorySingleton.get_instance()
ability_repository = PokemonAbilityRepositorySingleton.get_instance()
move_repository = MoveRepositorySingleton.get_instance()
item_repository = ItemRepositorySingleton.get_instance()
status_repository = StatusConditionRepositorySingleton.get_instance()
hazard_repository = HazardRepositorySingleton.get_instance()
field_effect_repository = FieldEffectRepositorySingleton.get_instance()