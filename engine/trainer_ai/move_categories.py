#===============================================================================
# Categorizes all Moves for intelligent AI decisions
#
# Categories:
# - Priority Moves (Quick Attack, Aqua Jet, Mach Punch, etc.)
# - Setup Moves (Swords Dance, Nasty Plot, Dragon Dance, etc.)
# - Hazard Moves (Stealth Rock, Spikes, Sticky Web, etc.)
# - Healing Moves (Roost, Recover, Synthesis, etc.)
# - OHKO Moves (Fissure, Guillotine, Sheer Cold, etc.)
# - Spread Moves (Earthquake, Surf, Rock Slide, etc.)
# - Protect Moves (Protect, Detect, Spiky Shield, etc.)
# - Status Moves (Will-O-Wisp, Thunder Wave, Toxic, etc.)
# - Screen Moves (Light Screen, Reflect, Aurora Veil, etc.)
# - Weather Moves (Rain Dance, Sunny Day, Sandstorm, etc.)
# - Terrain Moves (Electric Terrain, Grassy Terrain, etc.)
# - Pivot Moves (U-turn, Volt Switch, Flip Turn, etc.)
#===============================================================================

from engine.pokemon.repository import move_repository
from shared.pokemon.move import BaseMove, MoveCategory, MoveTarget
from shared.pokemon.move_tags import *


# this will need to be a singleton class


class MoveCategories:
    #===========================================================================
    # Priority Move Detection
    #===========================================================================
    PRIORITY_MOVES: dict[BaseMove, int] = {} # set of move indexes with priority other than 0
    SETUP_MOVES: dict[BaseMove, list[StatChangeMove]] = {}
    HAZARD_MOVES: dict[BaseMove, None] = {}
    HEALING_MOVES: dict[BaseMove, None] = {}
    OHKO_MOVES: list[BaseMove] = []
    SPREAD_MOVES: list[BaseMove] = []
    PROTECT_MOVES: list[BaseMove] = []
    STATUS_MOVES: list[BaseMove] = []
    SCREEN_MOVES: list[BaseMove] = []
    WEATHER_MOVES: list[BaseMove] = []
    TERRAIN_MOVES: list[BaseMove] = []
    PIVOT_MOVES: list[BaseMove] = []
    DAMAGING_MOVES: dict[BaseMove] = []



    def build_priority_moves(self):
        """Build the set of priority move categories from move repo."""
        for move in move_repository.items.values():
            if move.priority != 0:
                self.PRIORITY_MOVES[move] = move.priority
    
    def build_setup_moves(self):
        """Build the set of setup move categories from move repo."""
        for move in move_repository.items.values():
            stat_changes = []
            for effect in move.move_tags:
                if isinstance(effect, StatChangeMove):
                    stat_changes.append(effect)
            if stat_changes:
                self.SETUP_MOVES[move] = stat_changes

    def build_hazard_moves(self):
        """Build the set of hazard move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(EntryHazardMove):
                self.HAZARD_MOVES[move] = None

    def build_healing_moves(self):
        """Build the set of healing move categories from move repo."""
        for move in move_repository.items.values():
            stat_changes = []
            if move.has_tag(HealMove):
                stat_changes.append(move)
            elif move.has_tag(DrainMove) and move.get_tag(DrainMove)[0].drain_percentage > 0:
                stat_changes.append(move)
            if stat_changes:
                self.SETUP_MOVES[move] = stat_changes

    def build_ohko_moves(self):
        """Build the set of OHKO move categories from move repo."""
        for move in move_repository.items.values():
            if move.is_ohko:
                self.OHKO_MOVES.append(move)

    def build_spread_moves(self):
        """Build the set of spread move categories from move repo."""
        for move in move_repository.items.values():
            if move.target in [MoveTarget.ALL_OPPONENTS, MoveTarget.ALL_OTHER_POKEMON, MoveTarget.ALL_POKEMON]:
                self.SPREAD_MOVES.append(move)

    def build_protect_moves(self):
        """Build the set of protect move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(ProtectMove):
                self.PROTECT_MOVES.append(move)

    def build_status_moves(self):
        """Build the set of status move categories from move repo."""
        for move in move_repository.items.values():
            if move.is_status_condition_move:
                pass

    def build_screen_moves(self):
        """Build the set of screen move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(ScreenMove):
                self.SCREEN_MOVES.append(move)

    def build_weather_moves(self):
        """Build the set of weather move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(WeatherMove):
                self.WEATHER_MOVES.append(move)

    def build_terrain_moves(self):
        """Build the set of terrain move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(TerrainMove):
                self.TERRAIN_MOVES.append(move)

    def build_pivot_moves(self):
        """Build the set of pivot move categories from move repo."""
        for move in move_repository.items.values():
            if move.has_tag(PivotMove):
                self.PIVOT_MOVES.append(move)

    def build_damaging_moves(self):
        """Build the set of damaging move categories from move repo."""
        for move in move_repository.items.values():
            if move.category in [MoveCategory.DAMAGE, MoveCategory.DAMAGE_HEAL, MoveCategory.DAMAGE_STATUS, MoveCategory.DAMAGE_LOWER, MoveCategory.DAMAGE_RAISE]:
                self.DAMAGING_MOVES.append(move)

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
