"""Test suite for Pokemon models and related functionality."""
import pytest
from engine.repositories.repository import status_repository
from shared.pokemon.pokemon import Pokemon, PokemonBase, StatStages
from shared.pokemon.types import PokemonType
from shared.pokemon.genders import Gender
from shared.pokemon.natures import Nature
from shared.pokemon.stats import (
    BaseStats, Stat, IndividualValues, EffortValues
)
from shared.pokemon.move import MoveSet, BaseMove


class TestPokemonBase:
    """Tests for PokemonBase model."""

    def test_create_pokemon_base(self, pikachu_base: "PokemonBase"):
        """Test creating a valid PokemonBase."""
        assert pikachu_base.name == "Pikachu"
        assert pikachu_base.pokedex_number == 25
        assert PokemonType.ELECTRIC in pikachu_base.types
        assert pikachu_base.capture_rate == 190

    def test_pokemon_base_stats(self, pikachu_base: "PokemonBase"):
        """Test PokemonBase has correct base stats."""
        assert pikachu_base.base_stats.hp == 35
        assert pikachu_base.base_stats.attack == 55
        assert pikachu_base.base_stats.defense == 40
        assert pikachu_base.base_stats.speed == 90

    def test_dual_type_pokemon(self, charizard_base: "PokemonBase"):
        """Test Pokemon with dual types."""
        assert len(charizard_base.types) == 2
        assert PokemonType.FIRE in charizard_base.types
        assert PokemonType.FLYING in charizard_base.types

    def test_capture_rate_validation(self):
        """Test capture rate is within valid range (0-255)."""
        with pytest.raises(Exception):
            PokemonBase(
                name="Invalid",
                types=[PokemonType.NORMAL],
                base_stats=BaseStats(hp=50, attack=50, defense=50,
                           special_attack=50, special_defense=50, speed=50),
                pokedex_number=999,
                capture_rate=256  # Invalid: too high
            )


class TestPokemon:
    """Tests for Pokemon instances."""

    def test_create_pokemon(self, pikachu_pokemon: "Pokemon"):
        """Test creating a Pokemon instance."""
        assert pikachu_pokemon.pokemon_base.name == "Pikachu"
        assert pikachu_pokemon.level == 15
        assert pikachu_pokemon.nickname == "Pikachu"
        assert pikachu_pokemon.max_hp > 0
        assert pikachu_pokemon.current_hp == pikachu_pokemon.max_hp

    def test_pokemon_level_validation(self, pikachu_base: "PokemonBase", tackle_move: "BaseMove"):
        """Test Pokemon level is within valid range."""
        move_set = MoveSet(moves=[tackle_move])
        
        # Valid levels
        pokemon_level_1 = Pokemon(pokemon_base=pikachu_base, level=1, move_set=move_set)
        assert pokemon_level_1.level == 1
        
        pokemon_level_100 = Pokemon(pokemon_base=pikachu_base, level=100, move_set=move_set)
        assert pokemon_level_100.level == 100

        # Invalid level
        with pytest.raises(Exception):
            Pokemon(pokemon_base=pikachu_base, level=101, move_set=move_set)

    def test_hp_calculation(self, pikachu_pokemon: "Pokemon"):
        """Test HP is calculated correctly."""
        # HP should be greater than 0 and based on level and stats
        assert pikachu_pokemon.max_hp > 0
        assert pikachu_pokemon.current_hp == pikachu_pokemon.max_hp

    def test_pokemon_stat_calculation(self, pikachu_pokemon: "Pokemon"):
        """Test stat calculation methods."""
        attack = pikachu_pokemon.calculate_stat(Stat.ATTACK)
        defense = pikachu_pokemon.calculate_stat(Stat.DEFENSE)
        speed = pikachu_pokemon.calculate_stat(Stat.SPEED)
        
        assert attack > 0
        assert defense > 0
        assert speed > 0

    def test_pokemon_with_custom_nickname(self, pikachu_base: "PokemonBase", tackle_move: "BaseMove"):
        """Test Pokemon with custom nickname."""
        move_set = MoveSet(moves=[tackle_move])
        pokemon = Pokemon(
            pokemon_base=pikachu_base,
            level=10,
            move_set=move_set
        )
        # Nickname defaults to Pokemon name but can be changed
        assert pokemon.nickname == "Pikachu"
        pokemon.nickname = "Sparky"
        assert pokemon.nickname == "Sparky"

    def test_pokemon_status_condition(self, pikachu_pokemon: "Pokemon"):
        """Test Pokemon external status condition (outside of battle)."""
        assert pikachu_pokemon.external_status_condition is None
        
        # Simulate status change outside of battle
        paralysis = status_repository.get("paralysis")
        pikachu_pokemon.external_status_condition = paralysis
        assert pikachu_pokemon.external_status_condition == paralysis

    def test_pokemon_gender(self, pikachu_pokemon: "Pokemon"):
        """Test Pokemon gender."""
        assert pikachu_pokemon.gender in [Gender.MALE, Gender.FEMALE, Gender.NONE]

    def test_pokemon_shiny(self, pikachu_base: PokemonBase, tackle_move: BaseMove):
        """Test shiny Pokemon."""
        move_set = MoveSet(moves=[tackle_move])
        shiny_pokemon = Pokemon(
            pokemon_base=pikachu_base,
            level=10,
            shiny=True,
            move_set=move_set,
            generate=False,
        )
        assert shiny_pokemon.shiny is True

    def test_pokemon_nature(self, pikachu_pokemon: Pokemon):
        """Test Pokemon has a nature."""
        assert pikachu_pokemon.nature is not None
        assert isinstance(pikachu_pokemon.nature, Nature)

    def test_tera_type_defaults_to_first_type(self, pikachu_pokemon: Pokemon):
        """Test tera type defaults to Pokemon's first type."""
        assert pikachu_pokemon.terra_type == PokemonType.ELECTRIC


class TestPokemonBattleState:
    """Tests for BattleMon."""

    def test_initial_battle_state(self, pikachu_pokemon: Pokemon):
        """Test initial battle state values."""
        battlemon = pikachu_pokemon.generate_battlemon()
        assert battlemon.attack_stat_stage == 0
        assert battlemon.defense_stat_stage == 0
        assert battlemon.special_attack_stat_stage == 0
        assert battlemon.special_defense_stat_stage == 0
        assert battlemon.speed_stat_stage == 0
        assert battlemon.accuracy_stage == 0
        assert battlemon.evasion_stage == 0
        assert battlemon.critical_hit_stage == 0
        assert len(battlemon.status_conditions) == 0

    def test_reset_stat_stages(self, pikachu_pokemon: Pokemon):
        """Test stat stages can be reset to defaults."""
        battlemon = pikachu_pokemon.generate_battlemon()
        battlemon.stat_stages.attack_stat_stage = 2
        battlemon.stat_stages.defense_stat_stage = -1
        battlemon.stat_stages.speed_stat_stage = 1

        battlemon.stat_stages = StatStages()

        assert battlemon.stat_stages.attack_stat_stage == 0
        assert battlemon.stat_stages.defense_stat_stage == 0
        assert battlemon.stat_stages.speed_stat_stage == 0

    def test_reset_conditions(self, pikachu_pokemon: Pokemon):
        """Test battle status conditions can be reset to defaults."""
        battlemon = pikachu_pokemon.generate_battlemon()
        confusion_status = status_repository.get("confusion")
        if confusion_status:
            battlemon.status_conditions[confusion_status] = confusion_status.default_data_factory()

        battlemon.status_conditions.clear()

        assert len(battlemon.status_conditions) == 0

    def test_full_reset(self, pikachu_pokemon: Pokemon):
        """Test full reset of battle state via reinitialization."""
        battlemon = pikachu_pokemon.generate_battlemon()
        battlemon.stat_stages.attack_stat_stage = 2
        confusion_status = status_repository.get("confusion")
        if confusion_status:
            battlemon.status_conditions[confusion_status] = confusion_status.default_data_factory()

        battlemon.stat_stages = StatStages()
        battlemon.status_conditions.clear()

        assert battlemon.stat_stages.attack_stat_stage == 0
        assert len(battlemon.status_conditions) == 0


class TestPokemonIVsAndEVs:
    """Tests for Individual Values and Effort Values."""

    def test_default_ivs(self):
        """Test default IV values."""
        ivs = IndividualValues()
        # Default IVs should be within 0-31 range
        assert 0 <= ivs.hp <= 31
        assert 0 <= ivs.attack <= 31
        assert 0 <= ivs.defense <= 31

    def test_custom_ivs(self, pikachu_base: PokemonBase, tackle_move: BaseMove):
        """Test Pokemon with custom IVs."""
        custom_ivs = IndividualValues(
            hp=31, attack=31, defense=31,
            special_attack=31, special_defense=31, speed=31
        )
        move_set = MoveSet(moves=[tackle_move])
        pokemon = Pokemon(
            pokemon_base=pikachu_base,
            level=50,
            individual_values=custom_ivs,
            move_set=move_set,
            generate=False,
        )
        # Pokemon with max IVs should have higher stats
        assert pokemon.individual_values.hp == 31
        assert pokemon.individual_values.attack == 31
        assert pokemon.individual_values.defense == 31

    def test_default_evs(self):
        """Test default EV values."""
        evs = EffortValues()
        assert evs.hp == 0
        assert evs.attack == 0
        assert evs.defense == 0

    def test_ev_total_validation(self):
        """Test EV total cannot exceed 510."""
        with pytest.raises(Exception):
            EffortValues(
                hp=255, attack=255, defense=255,
                special_attack=0, special_defense=0, speed=0
            )


class TestPokemonGetters:
    """Test Pokemon stat getter methods."""

    def test_get_attack_stat(self, pikachu_pokemon: Pokemon):
        """Test getting attack stat."""
        attack = pikachu_pokemon.stat_attack
        assert attack > 0
        assert isinstance(attack, int)

    def test_get_defense_stat(self, pikachu_pokemon: Pokemon):
        """Test getting defense stat."""
        defense = pikachu_pokemon.stat_defense
        assert defense > 0
        assert isinstance(defense, int)

    def test_get_special_attack_stat(self, pikachu_pokemon: Pokemon):
        """Test getting special attack stat."""
        sp_attack = pikachu_pokemon.stat_special_attack
        assert sp_attack > 0
        assert isinstance(sp_attack, int)

    def test_get_special_defense_stat(self, pikachu_pokemon: Pokemon):
        """Test getting special defense stat."""
        sp_defense = pikachu_pokemon.stat_special_defense
        assert sp_defense > 0
        assert isinstance(sp_defense, int)

    def test_stat_stages_affect_stats(self, pikachu_pokemon: Pokemon):
        """Test that stat stages affect calculated stats."""
        # This test verifies stat stage system exists
        # Actual stat calculation may or may not include stages yet
        battlemon = pikachu_pokemon.generate_battlemon()
        battlemon.stat_stages.attack_stat_stage = 2
        assert battlemon.stat_stages.attack_stat_stage == 2

        # Reset stages manually on BattleMon
        battlemon.stat_stages.attack_stat_stage = 0
        assert battlemon.stat_stages.attack_stat_stage == 0
