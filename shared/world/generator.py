from abc import ABC, abstractmethod
from typing import List

from .world_structure import WorldStructure, Node, Edge, Tile, TileDefinitions



class WorldGenerator(ABC):
    @abstractmethod
    def generate_world(self) -> WorldStructure:
        """Generate and return a world mesh."""
        pass

class TestGenerateFromTiles(WorldGenerator):
    """Tile-based world generation (RPG Maker style).
    
    Best for: Indoor areas, dungeons, structured layouts.
    Uses a 2D grid where each cell references a tile from a tileset.
    """
    
    def generate_world(self, tile_map: List[str]) -> WorldStructure:
        # Implementation for tile-based generation
        # Reads tile layout data (2D array of tile IDs)
        # Generates geometry from tileset based on layout
        # Returns complete mesh for rendering
        world_structure = WorldStructure()

        x_min, x_max, y_min, y_max = 0, 0, 0, 0

        for y, row in enumerate(tile_map):
            for x, tile_id in enumerate(row):
                # Example: Create nodes at walkable tile positions
                if tile_id != TileDefinitions.BARRIER.value:  # Assuming 'P' represents a walkable tile
                    node = Node(position={"x": x, "y": y, "z": 0}, direction={"x": 0, "y": 0, "z": -1})
                    world_structure.navigation_mesh.nodes.append(node)
                tile = Tile(tile_id=TileDefinitions(tile_id), position={"x": x, "y": y, "z": 0})
                world_structure.tiles.append(tile)
                x_min = min(x_min, x)
                x_max = max(x_max, x)
                y_min = min(y_min, y)
                y_max = max(y_max, y)

        # calc edges between nodes
        node_positions = {(node.x, node.y): node for node in world_structure.navigation_mesh.nodes}
        for node in world_structure.navigation_mesh.nodes:
            # Check adjacent positions (up, down, left, right)
            adjacent_positions = [
                (node.x + 1, node.y),
                (node.x - 1, node.y),
                (node.x, node.y + 1),
                (node.x, node.y - 1),
            ]
            for pos in adjacent_positions:
                if pos in node_positions:
                    edge = Edge(from_node=node, to_node=node_positions[pos])
                    world_structure.navigation_mesh.edges.append(edge)

        # this method is used in the event that the area we are loading isnt a perfect rectangle
        world_structure.width = x_max - x_min + 1
        world_structure.height = y_max - y_min + 1

        return world_structure

class GenerateFromTiles(WorldGenerator):
    """Tile-based world generation (RPG Maker style).
    
    Best for: Indoor areas, dungeons, structured layouts.
    Uses a 2D grid where each cell references a tile from a tileset.
    """
    
    def generate_world(self) -> WorldStructure:
        # Implementation for tile-based generation
        # Reads tile layout data (2D array of tile IDs)
        # Generates geometry from tileset based on layout
        # Returns complete mesh for rendering
        pass

class GenerateFromModel(WorldGenerator):
    """Model-based world generation from 3D files.
    
    Best for: Outdoor areas, organic terrain, custom-modeled spaces.
    Loads pre-made 3D models with collision and metadata.
    """
    
    def generate_world(self) -> WorldStructure:
        # Implementation for model-based generation
        # Loads .obj, .gltf, or other 3D model formats
        # Extracts geometry and collision data
        # Applies any procedural modifications if needed
        # Returns mesh for rendering
        pass

class GenerateHybrid(WorldGenerator):
    """Hybrid generation combining tiles and models.
    
    Best for: Complex worlds with both structured and organic areas.
    Typically: Indoor/dungeon areas use tiles, outdoor areas use models.
    Seamlessly blends both approaches in a single world.
    """
    
    def generate_world(self) -> WorldStructure:
        # Implementation for hybrid generation
        # Determines which regions use tiles vs models (via metadata)
        # Generates tile geometry for indoor/structured areas
        # Loads model geometry for outdoor/organic areas
        # Combines both into unified mesh
        # Returns complete mesh for rendering
        pass