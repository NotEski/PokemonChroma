"""Test suite for moves, teams, and trainer functionality."""
import pytest
from shared.pokemon.move import BaseMove, Move, MoveSet, StatChange, DamageClass, MoveCategory
from shared.pokemon.pokemon import PokemonTeam
from shared.trainer.trainer import Trainer
from shared.pokemon.types import PokemonType
from shared.pokemon.status_conditions import StatusCondition
from shared.pokemon.stats import Stat


class TestBaseMove:
    """Tests for BaseMove model."""

    def test_create_base_move(self, tackle_move):
        """Test creating a basic move."""
        assert tackle_move.name == "Tackle"
        assert tackle_move.type == PokemonType.NORMAL
        assert tackle_move.power == 40
        assert tackle_move.accuracy == 100
        assert tackle_move.pp == 35
        assert tackle_move.damage_class == DamageClass.PHYSICAL

    def test_move_with_different_categories(self, tackle_move, thunderbolt_move):
        """Test moves with different damage classes."""
        assert tackle_move.damage_class == DamageClass.PHYSICAL
        assert thunderbolt_move.damage_class == DamageClass.SPECIAL

    def test_move_power_can_be_none(self):
        """Test that move power can be None (status moves)."""
        status_move = BaseMove(
            name="Thunder Wave",
            index=2,
            type=PokemonType.ELECTRIC,
            power=None,
            accuracy=90,
            pp=20,
            damage_class=DamageClass.STATUS,
            category=MoveCategory.STATUS,
            status_condition=StatusCondition.PARALYSIS
        )
        assert status_move.power is None
        assert status_move.damage_class == DamageClass.STATUS

    def test_move_pp_validation(self):
        """Test that PP is within valid range (1-40)."""
        valid_move = BaseMove(
            name="Test Move",
            index=3,
            type=PokemonType.NORMAL,
            power=50,
            accuracy=100,
            pp=40  # Maximum PP
        )
        assert valid_move.pp == 40

        # Invalid PP
        with pytest.raises(Exception):
            BaseMove(
                name="Invalid Move",
                index=4,
                type=PokemonType.NORMAL,
                power=50,
                pp=0  # Too low
            )

    def test_move_with_status_condition(self):
        """Test move that inflicts status condition."""
        poison_move = BaseMove(
            name="Poison Sting",
            index=5,
            type=PokemonType.POISON,
            power=15,
            accuracy=100,
            pp=35,
            damage_class=DamageClass.PHYSICAL,
            category=MoveCategory.DAMAGE,
            status_condition=StatusCondition.POISON
        )
        assert poison_move.status_condition == StatusCondition.POISON


class TestMove:
    """Tests for Move instances (with current PP)."""

    def test_create_move_from_base(self, tackle_move):
        """Test creating a Move instance from BaseMove."""
        move = Move(base_move=tackle_move, current_pp=tackle_move.pp)
        
        assert move.current_pp == 35
        assert move.name == "Tackle"

    def test_move_pp_decreases(self, tackle_move):
        """Test that move PP can decrease."""
        move = Move(base_move=tackle_move, current_pp=tackle_move.pp)
        
        initial_pp = move.current_pp
        move.current_pp -= 1
        
        assert move.current_pp == initial_pp - 1

    def test_move_pp_reaches_zero(self, tackle_move):
        """Test that move PP can reach zero."""
        move = Move(base_move=tackle_move, current_pp=5)
        
        for _ in range(5):
            move.current_pp -= 1
        
        assert move.current_pp == 0


class TestMoveSet:
    """Tests for MoveSet model."""

    def test_create_moveset_with_moves(self, tackle_move, thunderbolt_move):
        """Test creating a moveset with moves."""
        moveset = MoveSet(moves=[tackle_move, thunderbolt_move])
        
        assert len(moveset.moves) == 2
        assert 1 in moveset.moves  # Tackle has index 1
        assert 24 in moveset.moves  # Thunderbolt has index 24

    def test_moveset_with_single_move(self, tackle_move):
        """Test creating a moveset with a single move."""
        moveset = MoveSet(moves=[tackle_move])
        
        assert len(moveset.moves) == 1
        assert moveset.moves[1].name == "Tackle"  # Tackle has index 1

    def test_moveset_max_four_moves(self, tackle_move, thunderbolt_move, water_gun_move, flamethrower_move):
        """Test that moveset can have up to 4 moves."""
        # Test creating moveset with 4 different moves (should work)
        moveset_4 = MoveSet(moves=[tackle_move, thunderbolt_move, water_gun_move, flamethrower_move])
        assert len(moveset_4.moves) == 4
        
        # Note: Validation for >4 moves may be handled elsewhere
        # This test verifies 4 moves works correctly

    def test_moveset_initializes_current_pp(self, tackle_move, thunderbolt_move):
        """Test that moveset initializes current PP from base PP."""
        moveset = MoveSet(moves=[tackle_move, thunderbolt_move])
        
        assert moveset.moves[1].current_pp == tackle_move.pp  # Tackle has index 1
        assert moveset.moves[24].current_pp == thunderbolt_move.pp  # Thunderbolt has index 24

    def test_empty_moveset(self):
        """Test creating an empty moveset."""
        moveset = MoveSet()
        assert len(moveset.moves) == 0

    def test_moveset_with_three_moves(self, tackle_move, thunderbolt_move, water_gun_move):
        """Test moveset with three moves."""
        moveset = MoveSet(moves=[tackle_move, thunderbolt_move, water_gun_move])
        
        assert len(moveset.moves) == 3


class TestStatChange:
    """Tests for StatChange model."""

    def test_create_stat_change(self):
        """Test creating a stat change."""
        stat_change = StatChange(stat=Stat.ATTACK, change=1)
        
        assert stat_change.stat == Stat.ATTACK
        assert stat_change.change == 1

    def test_stat_change_positive(self):
        """Test positive stat change (boost)."""
        stat_change = StatChange(stat=Stat.SPEED, change=2)
        assert stat_change.change == 2

    def test_stat_change_negative(self):
        """Test negative stat change (reduction)."""
        stat_change = StatChange(stat=Stat.DEFENSE, change=-1)
        assert stat_change.change == -1


class TestTeam:
    """Tests for Team model."""

    def test_create_team_with_one_pokemon(self, pikachu_pokemon):
        """Test creating a team with one Pokemon."""
        team = PokemonTeam(pokemons=[pikachu_pokemon])
        
        assert len(team.pokemons) == 1
        assert team.pokemons[0] == pikachu_pokemon

    def test_create_team_with_multiple_pokemon(self, pikachu_pokemon, eevee_pokemon, charizard_pokemon):
        """Test creating a team with multiple Pokemon."""
        team = PokemonTeam(pokemons=[pikachu_pokemon, eevee_pokemon, charizard_pokemon])
        
        assert len(team.pokemons) == 3

    def test_team_max_six_pokemon(self, pikachu_pokemon):
        """Test that team cannot exceed 6 Pokemon."""
        with pytest.raises(Exception):
            PokemonTeam(pokemons=[pikachu_pokemon] * 7)

    def test_team_requires_at_least_one_pokemon(self):
        """Test that team requires at least one Pokemon."""
        with pytest.raises(Exception):
            PokemonTeam(pokemons=[])

    def test_get_all_pokemons(self, pikachu_pokemon, eevee_pokemon):
        """Test getting all Pokemon from team."""
        team = PokemonTeam(pokemons=[pikachu_pokemon, eevee_pokemon])
        all_pokemon = team.get_all_pokemons()
        
        assert len(all_pokemon) == 2
        assert pikachu_pokemon in all_pokemon
        assert eevee_pokemon in all_pokemon

    def test_team_with_six_pokemon(self, pikachu_pokemon, eevee_pokemon):
        """Test creating a full team of 6 Pokemon."""
        from shared.pokemon.pokemon import Pokemon
        
        # Create 6 different Pokemon instances
        team_of_six = [pikachu_pokemon, eevee_pokemon]
        # Add 4 more copies (in real game these would be different Pokemon)
        for i in range(4):
            team_of_six.append(pikachu_pokemon)
        
        team = PokemonTeam(pokemons=team_of_six)
        assert len(team.pokemons) == 6


class TestBattleTrainer:
    """Tests for BattleTrainer model."""

    def test_create_trainer(self, ash_trainer):
        """Test creating a trainer."""
        assert ash_trainer.name == "Ash"
        assert ash_trainer.team is not None

    def test_trainer_with_PokemonTeam(self, pikachu_pokemon):
        """Test trainer has a team of Pokemon."""
        team = PokemonTeam(pokemons=[pikachu_pokemon])
        trainer = Trainer(name="Misty", team=team)
        
        assert trainer.name == "Misty"
        assert len(trainer.team.pokemons) >= 1

    def test_trainer_team_access(self, ash_trainer, pikachu_pokemon):
        """Test accessing trainer's team."""
        all_pokemon = ash_trainer.team.get_all_pokemons()
        assert len(all_pokemon) >= 1

    def test_multiple_trainers(self, pikachu_pokemon, eevee_pokemon):
        """Test creating multiple trainers."""
        team1 = PokemonTeam(pokemons=[pikachu_pokemon])
        team2 = PokemonTeam(pokemons=[eevee_pokemon])
        
        trainer1 = Trainer(name="Ash", team=team1)
        trainer2 = Trainer(name="Gary", team=team2)
        
        assert trainer1.name == "Ash"
        assert trainer2.name == "Gary"
        assert trainer1.team != trainer2.team


class TestMoveUsageScenarios:
    """Tests for realistic move usage scenarios."""

    def test_pokemon_uses_all_pp(self, pikachu_pokemon):
        """Test Pokemon using all PP of a move."""
        move = pikachu_pokemon.move_set.moves[1]  # Tackle (index 1)
        initial_pp = move.current_pp
        
        # Use move until PP is depleted
        for _ in range(initial_pp):
            move.current_pp -= 1
        
        assert move.current_pp == 0

    def test_pokemon_with_multiple_moves_uses_each(self, pikachu_pokemon):
        """Test Pokemon using multiple different moves."""
        move1 = pikachu_pokemon.move_set.moves[1]  # Tackle
        move2 = pikachu_pokemon.move_set.moves[24]  # Thunderbolt
        
        initial_pp1 = move1.current_pp
        initial_pp2 = move2.current_pp
        
        # Use each move once
        move1.current_pp -= 1
        move2.current_pp -= 1
        
        assert move1.current_pp == initial_pp1 - 1
        assert move2.current_pp == initial_pp2 - 1

    def test_switching_pokemon_in_PokemonTeam(self, pikachu_pokemon, eevee_pokemon):
        """Test accessing different Pokemon in a team."""
        team = PokemonTeam(pokemons=[pikachu_pokemon, eevee_pokemon])
        
        first_pokemon = team.pokemons[0]
        second_pokemon = team.pokemons[1]
        
        assert first_pokemon.pokemon_base.name == "Pikachu"
        assert second_pokemon.pokemon_base.name == "Eevee"


class TestMoveProperties:
    """Tests for various move properties."""

    def test_high_power_move(self):
        """Test creating a high power move."""
        hyper_beam = BaseMove(
            name="Hyper Beam",
            index=63,
            type=PokemonType.NORMAL,
            power=150,
            accuracy=90,
            pp=5,
            damage_class=DamageClass.SPECIAL,
            category=MoveCategory.DAMAGE
        )
        assert hyper_beam.power == 150
        assert hyper_beam.pp == 5

    def test_low_accuracy_move(self):
        """Test creating a low accuracy move."""
        thunder = BaseMove(
            name="Thunder",
            index=25,
            type=PokemonType.ELECTRIC,
            power=110,
            accuracy=70,
            pp=10,
            damage_class=DamageClass.SPECIAL,
            category=MoveCategory.DAMAGE
        )
        assert thunder.accuracy == 70

    def test_different_type_moves(self):
        """Test creating moves of different types."""
        fire_move = BaseMove(
            name="Ember",
            index=6,
            type=PokemonType.FIRE,
            power=40,
            pp=25,
            damage_class=DamageClass.SPECIAL,
            category=MoveCategory.DAMAGE
        )
        
        water_move = BaseMove(
            name="Water Gun",
            index=55,
            type=PokemonType.WATER,
            power=40,
            pp=25,
            damage_class=DamageClass.SPECIAL,
            category=MoveCategory.DAMAGE
        )
        
        assert fire_move.type == PokemonType.FIRE
        assert water_move.type == PokemonType.WATER
        assert fire_move.type != water_move.type


class TestTeamManagement:
    """Tests for team management scenarios."""

    def test_team_with_mixed_levels(self, pikachu_base, tackle_move):
        """Test team with Pokemon of different levels."""
        from shared.pokemon.pokemon import Pokemon
        from shared.pokemon.move import MoveSet
        
        move_set = MoveSet(moves=[tackle_move])
        
        low_level = Pokemon(pokemon_base=pikachu_base, level=5, move_set=move_set)
        mid_level = Pokemon(pokemon_base=pikachu_base, level=25, move_set=move_set)
        high_level = Pokemon(pokemon_base=pikachu_base, level=50, move_set=move_set)
        
        team = PokemonTeam(pokemons=[low_level, mid_level, high_level])
        
        assert team.pokemons[0].level == 5
        assert team.pokemons[1].level == 25
        assert team.pokemons[2].level == 50

    def test_team_order_preserved(self, pikachu_pokemon, eevee_pokemon, charizard_pokemon):
        """Test that team order is preserved."""
        team = PokemonTeam(pokemons=[pikachu_pokemon, eevee_pokemon, charizard_pokemon])
        
        assert team.pokemons[0].pokemon_base.name == "Pikachu"
        assert team.pokemons[1].pokemon_base.name == "Eevee"
        assert team.pokemons[2].pokemon_base.name == "Charizard"
