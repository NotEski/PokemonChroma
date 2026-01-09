# How do I want this to work?
# The map will be a grid of tiles. but how do I split them up for management?
# a section will contain everything u puntil the loading spots


from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from enum import Enum
from pathlib import Path

from panda3d.core import (
    Vec2,
    Vec3,
)

class SlopeDir(Enum):
    NONE = "none"
    N = "north"
    S = "south"
    E = "east"
    W = "west"

class TileDef(BaseModel):
    id: str
    walkable: bool
    walkable: bool = True
    

TILE_REGISTRY: Dict[str, TileDef] = {
    "B": TileDef(id="B", walkable=False, height=0),
    "G": TileDef(id="G", walkable=True, height=0),
    "P": TileDef(id="P", walkable=True, height=0),
}

class Cell(BaseModel):
    tile_id: str
    slope: SlopeDir = SlopeDir.NONE

class Layer(BaseModel):
    """A single horizontal layer of tiles at fixed elevation."""
    elev: int
    cells: List[List[Cell]]  # 2D grid of cells

    def in_bounds(self, pos: Vec2) -> bool:
        return 0 <= pos.y < len(self.cells) and 0 <= pos.x < len(self.cells[0])
    
    def get_cell(self, pos: Vec2) -> Cell:
        if not self.in_bounds(pos):
            raise IndexError("Position out of bounds")
        return self.cells[pos.y][pos.x]
    
    def is_walkable(self, pos: Vec2) -> bool:
        if not self.in_bounds(pos):
            return False
        cell = self.get_cell(pos)
        tile = TILE_REGISTRY[cell.tile_id]
        return tile.walkable
    
    @property
    def width(self) -> int:
        return max((len(row) for row in self.cells), default=0)
    @property
    def height(self) -> int:
        return len(self.cells)
    
class GridSection(BaseModel):
    name: str = Field(default="Unnamed Section")
    section_type: str = Field(default="grid")
    layers: List[Layer]

    def get_layer(self, elev: int) -> Optional[Layer]:
        for layer in self.layers:
            if layer.elev == elev:
                return layer
        raise ValueError(f"No layer found at elevation {elev}")
    
    def is_walkable(self, pos: Vec2, elev: int) -> bool:
        layer = self.get_layer(elev)
        return layer.is_walkable(pos)
    
    def sample_height(self, pos: Vec2) -> Optional[int]:
        """Returns the elevation of the highest walkable layer at the given position."""
        walkable_layers = [layer for layer in self.layers if layer.is_walkable(pos)]
        if not walkable_layers:
            return None
        return max(layer.elev for layer in walkable_layers)
    
    def can_step(self, from_pos: Vec2, from_elev: int, to_pos: Vec2, to_elev: int) -> bool:
        if not self.is_walkable(to_pos, to_elev):
            return False
        dh = to_elev - from_elev
        return -1 <= dh <= 1
    
class MeshSection(BaseModel):
    name: str = Field(default="Unnamed Mesh Section")
    section_type: str = Field(default="mesh")
    mesh_path: Path # Path to the 3D mesh file

    # Optional metadata for artists/tooling
    origin: Optional[Vec2] = None
    scale: Optional[float] = None


Section = Union[GridSection, MeshSection]


TEST_WORLD_DATA = [
    "B"*20,
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "BG"+"P"*16+"GB",
    "B"*20,
]

def load_test_grid_section() -> GridSection:
    """Load a simple test grid section."""
    cells: List[List[Cell]] = []
    for row_str in TEST_WORLD_DATA:
        row: List[Cell] = []
        for ch in row_str:
            cell = Cell(tile_id=ch)
            row.append(cell)
        cells.append(row)
    layer = Layer(elev=0, cells=cells)
    section = GridSection(name="Test Grid Section", layers=[layer])
    return section

