"""Pytest configuration and shared fixtures for the Pokemon Fan Game test suite."""
import pytest
from shared.pokemon.pokemon import Pokemon, PokemonBase
from shared.pokemon.types import PokemonType, MoveCategory, Nature, Gender
from shared.pokemon.move import MoveSet, BaseMove
from shared.pokemon.team import Team
from shared.pokemon.trainer import BattleTrainer


@pytest.fixture
def pikachu_base():
    """Basic Pikachu PokemonBase fixture."""
    return PokemonBase(
        name="Pikachu",
        types=[PokemonType.ELECTRIC],
        base_stats={
            "hp": 35,
            "attack": 55,
            "defense": 40,
            "special_attack": 50,
            "special_defense": 50,
            "speed": 90,
        },
        pokedex_number=25,
        catch_rate=190
    )


@pytest.fixture
def charizard_base():
    """Basic Charizard PokemonBase fixture."""
    return PokemonBase(
        name="Charizard",
        types=[PokemonType.FIRE, PokemonType.FLYING],
        base_stats={
            "hp": 78,
            "attack": 84,
            "defense": 78,
            "special_attack": 109,
            "special_defense": 85,
            "speed": 100,
        },
        pokedex_number=6,
        catch_rate=45
    )


@pytest.fixture
def eevee_base():
    """Basic Eevee PokemonBase fixture."""
    return PokemonBase(
        name="Eevee",
        types=[PokemonType.NORMAL],
        base_stats={
            "hp": 55,
            "attack": 55,
            "defense": 50,
            "special_attack": 45,
            "special_defense": 65,
            "speed": 55,
        },
        pokedex_number=133,
        catch_rate=45
    )


@pytest.fixture
def tackle_move():
    """Basic Tackle move fixture."""
    return BaseMove(
        name="Tackle",
        type=PokemonType.NORMAL,
        power=40,
        accuracy=100,
        pp=35,
        category=MoveCategory.PHYSICAL
    )


@pytest.fixture
def thunderbolt_move():
    """Basic Thunderbolt move fixture."""
    return BaseMove(
        name="Thunderbolt",
        type=PokemonType.ELECTRIC,
        power=90,
        accuracy=100,
        pp=15,
        category=MoveCategory.SPECIAL
    )


@pytest.fixture
def flamethrower_move():
    """Basic Flamethrower move fixture."""
    return BaseMove(
        name="Flamethrower",
        type=PokemonType.FIRE,
        power=90,
        accuracy=100,
        pp=15,
        category=MoveCategory.SPECIAL
    )


@pytest.fixture
def water_gun_move():
    """Basic Water Gun move fixture."""
    return BaseMove(
        name="Water Gun",
        type=PokemonType.WATER,
        power=40,
        accuracy=100,
        pp=25,
        category=MoveCategory.SPECIAL
    )


@pytest.fixture
def pikachu_pokemon(pikachu_base, tackle_move, thunderbolt_move):
    """Level 15 Pikachu with moves."""
    move_set = MoveSet(moves=[tackle_move, thunderbolt_move])
    return Pokemon(pokemon=pikachu_base, level=15, move_set=move_set)


@pytest.fixture
def charizard_pokemon(charizard_base, tackle_move, flamethrower_move):
    """Level 50 Charizard with moves."""
    move_set = MoveSet(moves=[tackle_move, flamethrower_move])
    return Pokemon(pokemon=charizard_base, level=50, move_set=move_set)


@pytest.fixture
def eevee_pokemon(eevee_base, tackle_move):
    """Level 10 Eevee with Tackle."""
    move_set = MoveSet(moves=[tackle_move])
    return Pokemon(pokemon=eevee_base, level=10, move_set=move_set)


@pytest.fixture
def basic_team(pikachu_pokemon):
    """Basic team with a single Pikachu."""
    return Team(pokemons=[pikachu_pokemon])


@pytest.fixture
def ash_trainer(basic_team):
    """Ash trainer with a basic team."""
    return BattleTrainer(name="Ash", team=basic_team)
