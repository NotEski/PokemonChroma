# How do I want this to work?
# The map will be a grid of tiles. but how do I split them up for management?
# a section will contain everything u puntil the loading spots


from pydantic import BaseModel
from enum import Enum

from panda3d.core import (
    Geom,
    Vec3
)

class Vector3(BaseModel):
    x: float
    y: float
    z: float

    @property
    def Vec3(self) -> Vec3:
        return Vec3(self.x, self.y, self.z)

class TileDefinitions(Enum):
    """Definitions for tile types used in tile-based world generation."""
    BARRIER = "B"
    PATH = "P"
    GRASS = "G"

class Node(BaseModel):
    """A point in the navigation network."""
    position: Vector3
    direction: Vector3

    @property
    def x(self) -> float:
        return self.position.x
    @x.setter
    def x(self, value: float) -> None:
        self.position.x = value
    @property
    def y(self) -> float:
        return self.position.y
    @y.setter
    def y(self, value: float) -> None:
        self.position.y = value
    @property
    def z(self) -> float:
        return self.position.z
    @z.setter
    def z(self, value: float) -> None:
        self.position.z = value

class Edge(BaseModel):
    """A connection between two nodes in the navigation network."""
    from_node: Node
    shape: list[Vector3] = [] # if empty, the shape is a linear connection between the nodes
    to_node: Node

    def generate_shape(self):
        pass


class Tile(BaseModel):
    """A single tile in the world grid."""
    tile_id: TileDefinitions
    position: Vector3

class NavigationMesh(BaseModel):
    """Navigation mesh for pathfinding."""
    nodes: list[Node] = []
    edges: list[Edge] = []

class WorldStructure(BaseModel):
    """Defines the structure of the world for generation purposes."""
    tiles: list[Tile] = []
    width: int = 0
    height: int = 0

    navigation_mesh: NavigationMesh = NavigationMesh()



    def print_tile_map(self) -> None:
        tile_map = [[" " for _ in range(self.width)] for _ in range(self.height)]
        for tile in self.tiles:
            x = int(tile.position.x)
            y = int(tile.position.y)
            tile_map[y][x] = tile.tile_id.value
        for row in tile_map:
            print("".join(row))