from .generator import TestGenerateFromTiles


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


def test_tile_based_world_generation():
    generator = TestGenerateFromTiles()
    world_structure = generator.generate_world(TEST_WORLD_DATA)

    world_structure.print_tile_map()