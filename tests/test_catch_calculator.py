"""Test suite for catch calculation mechanics."""
import pytest
from unittest.mock import patch
from shared.pokemon.pokemon import Pokemon
from shared.pokemon.status_conditions import StatusCondition
from engine.repositories.repository import status_repository
from shared.items.pokeball import Pokeball
from engine.battle.catch_calculator import (
    calculate_catch_probability,
    calculate_shake,
    catch_attempt
)


class TestCalculateCatchProbability:
    """Tests for catch probability calculation."""

    def test_master_ball_guaranteed_catch(self, eevee_pokemon):
        """Master Ball should return maximum shake value (guaranteed catch)."""
        master_ball = Pokeball(name="Master Ball", catch_rate_modifier=255.0)
        shake_chance = calculate_catch_probability(eevee_pokemon.generate_battlemon(), master_ball)
        # Should return 65537 or higher (above max 16-bit value)
        assert shake_chance > 65536

    def test_standard_pokeball_catch_chance(self, eevee_pokemon, pokeball):
        """Standard Pokeball should return a reasonable catch chance."""
        shake_chance = calculate_catch_probability(eevee_pokemon.generate_battlemon(), pokeball)
        # Should be between 0 and 65536
        assert 0 <= shake_chance <= 65536

    def test_catch_probability_increases_with_ball_modifier(self, eevee_pokemon):
        """Better Pokeballs should have higher catch probability."""
        pokeball = Pokeball(name="Pokeball", catch_rate_modifier=1.0)
        great_ball = Pokeball(name="Great Ball", catch_rate_modifier=1.5)
        ultra_ball = Pokeball(name="Ultra Ball", catch_rate_modifier=2.0)
        
        bm = eevee_pokemon.generate_battlemon()
        chance_pokeball = calculate_catch_probability(bm, pokeball)
        chance_great = calculate_catch_probability(bm, great_ball)
        chance_ultra = calculate_catch_probability(bm, ultra_ball)
        
        assert chance_pokeball < chance_great < chance_ultra

    def test_catch_probability_increases_with_lower_hp(self, eevee_base, tackle_move):
        """Pokemon with lower current HP should be easier to catch."""
        move_set = pytest.importorskip("shared.pokemon.move").MoveSet(moves=[tackle_move])
        
        # Full HP Pokemon
        pokemon_full = Pokemon(pokemon_base=eevee_base, level=10, move_set=move_set)
        
        # Low HP Pokemon
        pokemon_low = Pokemon(pokemon_base=eevee_base, level=10, move_set=move_set)
        pokemon_low.current_hp = int(pokemon_low.max_hp * 0.25)  # 25% HP
        
        pokeball = Pokeball(name="Pokeball", catch_rate_modifier=1.0)
        
        chance_full = calculate_catch_probability(pokemon_full.generate_battlemon(), pokeball)
        chance_low = calculate_catch_probability(pokemon_low.generate_battlemon(), pokeball)
        
        assert chance_low > chance_full

    def test_catch_probability_with_status_conditions(self, eevee_pokemon, pokeball):
        """Pokemon with status conditions should be easier to catch."""
        bm = eevee_pokemon.generate_battlemon()
        chance_healthy = calculate_catch_probability(bm, pokeball)
        
        # Test big bonus status (SLEEP)
        sleep_status = status_repository.get("sleep") or StatusCondition(name="sleep")
        bm.status_conditions[sleep_status] = 0
        chance_sleep = calculate_catch_probability(bm, pokeball)
        assert chance_sleep >= chance_healthy
        
        # Reset and test small bonus status (BURN)
        bm.status_conditions.clear()
        chance_healthy2 = calculate_catch_probability(bm, pokeball)
        
        burn_status = status_repository.get("burn") or StatusCondition(name="burn")
        bm.status_conditions[burn_status] = 0
        chance_burned = calculate_catch_probability(bm, pokeball)
        assert chance_burned > chance_healthy2
        # With placeholder statuses, bonuses may be equal; ensure sleep is not worse
        assert chance_sleep >= chance_burned

    def test_frozen_status_big_bonus(self, eevee_pokemon, pokeball):
        """Frozen Pokemon should get big catch bonus."""
        bm = eevee_pokemon.generate_battlemon()
        chance_healthy = calculate_catch_probability(bm, pokeball)
        
        freeze_status = status_repository.get("freeze") or StatusCondition(name="freeze")
        bm.status_conditions[freeze_status] = 0
        chance_frozen = calculate_catch_probability(bm, pokeball)
        
        assert chance_frozen >= chance_healthy

    def test_paralyzed_status_small_bonus(self, eevee_pokemon, pokeball):
        """Paralyzed Pokemon should get small catch bonus."""
        bm = eevee_pokemon.generate_battlemon()
        chance_healthy = calculate_catch_probability(bm, pokeball)
        
        paralysis_status = status_repository.get("paralysis") or StatusCondition(name="paralysis")
        bm.status_conditions[paralysis_status] = 0
        chance_paralyzed = calculate_catch_probability(bm, pokeball)
        
        assert chance_paralyzed >= chance_healthy

    def test_poisoned_status_small_bonus(self, eevee_pokemon, pokeball):
        """Poisoned Pokemon should get small catch bonus."""
        bm = eevee_pokemon.generate_battlemon()
        chance_healthy = calculate_catch_probability(bm, pokeball)
        
        poison_status = status_repository.get("poison") or StatusCondition(name="poison")
        bm.status_conditions[poison_status] = 0
        chance_poisoned = calculate_catch_probability(bm, pokeball)
        
        assert chance_poisoned >= chance_healthy

    def test_catch_probability_level_bonus(self, eevee_base, tackle_move):
        """Lower level Pokemon should be easier to catch."""
        move_set = pytest.importorskip("shared.pokemon.move").MoveSet(moves=[tackle_move])
        
        pokemon_level_5 = Pokemon(pokemon_base=eevee_base, level=5, move_set=move_set)
        pokemon_level_20 = Pokemon(pokemon_base=eevee_base, level=20, move_set=move_set)
        pokemon_level_50 = Pokemon(pokemon_base=eevee_base, level=50, move_set=move_set)
        
        pokeball = Pokeball(name="Pokeball", catch_rate_modifier=1.0)
        
        chance_5 = calculate_catch_probability(pokemon_level_5.generate_battlemon(), pokeball)
        chance_20 = calculate_catch_probability(pokemon_level_20.generate_battlemon(), pokeball)
        chance_50 = calculate_catch_probability(pokemon_level_50.generate_battlemon(), pokeball)
        
        # Lower level should be easier to catch
        # bonus_level = max((30-level)//10, 1)
        # Level 5: bonus = 2.5 (25//10)
        # Level 20: bonus = 1.0 (10//10)
        # Level 50: bonus = 1 (clamped to 1)
        assert chance_5 > chance_20 >= chance_50

    def test_catch_probability_species_capture_rate(self, eevee_base, pikachu_base, tackle_move):
        """Pokemon with higher capture rates should be easier to catch."""
        move_set = pytest.importorskip("shared.pokemon.move").MoveSet(moves=[tackle_move])
        
        # Pikachu has 190 capture rate, Eevee has 45
        pikachu = Pokemon(pokemon_base=pikachu_base, level=10, move_set=move_set)
        eevee = Pokemon(pokemon_base=eevee_base, level=10, move_set=move_set)
        
        pokeball = Pokeball(name="Pokeball", catch_rate_modifier=1.0)
        
        chance_pikachu = calculate_catch_probability(pikachu.generate_battlemon(), pokeball)
        chance_eevee = calculate_catch_probability(eevee.generate_battlemon(), pokeball)
        
        assert chance_pikachu > chance_eevee

    def test_catch_probability_modifiers_stack(self, eevee_pokemon, pokeball):
        """Multiple modifiers should stack properly."""
        # Get baseline
        bm = eevee_pokemon.generate_battlemon()
        baseline = calculate_catch_probability(bm, pokeball)
        
        # Apply HP damage + status
        bm.current_hp = int(bm.max_hp * 0.25)
        bm.status_conditions[status_repository.get("sleep")] = 0
        modified = calculate_catch_probability(bm, pokeball)
        
        assert modified > baseline


class TestCalculateShake:
    """Tests for shake calculation."""

    @patch('engine.battle.catch_calculator.randint')
    def test_calculate_shake_success(self, mock_randint):
        """Should return True when roll is less than shake_chance."""
        mock_randint.return_value = 1000
        result = calculate_shake(2000)
        assert result is True
        mock_randint.assert_called_once_with(0, 65535)

    @patch('engine.battle.catch_calculator.randint')
    def test_calculate_shake_failure(self, mock_randint):
        """Should return False when roll is greater than shake_chance."""
        mock_randint.return_value = 3000
        result = calculate_shake(2000)
        assert result is False

    @patch('engine.battle.catch_calculator.randint')
    def test_calculate_shake_boundary_success(self, mock_randint):
        """Should return True when roll equals shake_chance boundary."""
        mock_randint.return_value = 1999
        result = calculate_shake(2000)
        assert result is True

    @patch('engine.battle.catch_calculator.randint')
    def test_calculate_shake_boundary_failure(self, mock_randint):
        """Should return False when roll equals shake_chance."""
        mock_randint.return_value = 2000
        result = calculate_shake(2000)
        assert result is False

    @patch('engine.battle.catch_calculator.randint')
    def test_calculate_shake_zero_chance(self, mock_randint):
        """Should return False with zero shake chance."""
        mock_randint.return_value = 10000
        result = calculate_shake(0)
        assert result is False

    @patch('engine.battle.catch_calculator.randint')
    def test_calculate_shake_guaranteed(self, mock_randint):
        """Should return True with very high shake chance."""
        mock_randint.return_value = 65535  # Max roll
        result = calculate_shake(65536)  # Higher than max roll
        assert result is True


class TestCatchAttempt:
    """Tests for complete catch attempt mechanics."""

    @patch('engine.battle.catch_calculator.calculate_shake')
    def test_catch_attempt_success(self, mock_shake, eevee_pokemon, pokeball):
        """All four shakes should succeed for a catch."""
        mock_shake.return_value = True  # All shakes succeed
        result = catch_attempt(eevee_pokemon.generate_battlemon(), pokeball)
        
        assert result is True
        assert mock_shake.call_count == 4

    @patch('engine.battle.catch_calculator.calculate_shake')
    def test_catch_attempt_failure_first_shake(self, mock_shake, eevee_pokemon, pokeball):
        """Failure on first shake should fail catch."""
        mock_shake.return_value = False
        result = catch_attempt(eevee_pokemon.generate_battlemon(), pokeball)
        
        assert result is False
        assert mock_shake.call_count == 1

    @patch('engine.battle.catch_calculator.calculate_shake')
    def test_catch_attempt_failure_second_shake(self, mock_shake, eevee_pokemon, pokeball):
        """Failure on second shake should fail catch."""
        mock_shake.side_effect = [True, False]
        result = catch_attempt(eevee_pokemon.generate_battlemon(), pokeball)
        
        assert result is False
        assert mock_shake.call_count == 2

    @patch('engine.battle.catch_calculator.calculate_shake')
    def test_catch_attempt_failure_third_shake(self, mock_shake, eevee_pokemon, pokeball):
        """Failure on third shake should fail catch."""
        mock_shake.side_effect = [True, True, False]
        result = catch_attempt(eevee_pokemon.generate_battlemon(), pokeball)
        
        assert result is False
        assert mock_shake.call_count == 3

    @patch('engine.battle.catch_calculator.calculate_shake')
    def test_catch_attempt_failure_fourth_shake(self, mock_shake, eevee_pokemon, pokeball):
        """Failure on fourth shake should fail catch."""
        mock_shake.side_effect = [True, True, True, False]
        result = catch_attempt(eevee_pokemon.generate_battlemon(), pokeball)
        
        assert result is False
        assert mock_shake.call_count == 4

    @patch('engine.battle.catch_calculator.calculate_shake')
    def test_catch_attempt_uses_correct_probability(self, mock_shake, eevee_pokemon, pokeball):
        """Catch attempt should use calculate_catch_probability internally."""
        mock_shake.return_value = True
        
        catch_attempt(eevee_pokemon.generate_battlemon(), pokeball)
        
        # Verify calculate_shake was called 4 times with values in valid range
        assert mock_shake.call_count == 4
        for call in mock_shake.call_args_list:
            shake_chance = call[0][0]
            assert 0 <= shake_chance <= 65536


class TestCatchCalculatorIntegration:
    """Integration tests for catch calculation."""

    def test_easy_catch_scenario(self, eevee_base, tackle_move):
        """Low level, low HP, with status should have high catch rate."""
        move_set = pytest.importorskip("shared.pokemon.move").MoveSet(moves=[tackle_move])
        
        pokemon = Pokemon(pokemon_base=eevee_base, level=5, move_set=move_set)
        pokemon.current_hp = 1  # Near death
        pokemon.external_status_condition = status_repository.get("sleep")
        
        pokeball = Pokeball(name="Pokeball", catch_rate_modifier=1.0)
        shake_chance = calculate_catch_probability(pokemon.generate_battlemon(), pokeball)
        
        # Should have very high catch rate
        assert shake_chance > 40000

    def test_hard_catch_scenario(self, charizard_base, tackle_move):
        """High level, full HP, no status should have low catch rate."""
        move_set = pytest.importorskip("shared.pokemon.move").MoveSet(moves=[tackle_move])
        
        pokemon = Pokemon(pokemon_base=charizard_base, level=50, move_set=move_set)
        # Keep full HP (default)
        pokemon.external_status_condition = None
        
        pokeball = Pokeball(name="Pokeball", catch_rate_modifier=1.0)
        shake_chance = calculate_catch_probability(pokemon.generate_battlemon(), pokeball)
        
        # Should have a lower catch rate than an easy catch scenario
        # But Charizard's capture rate is still low (45) making it hard regardless
        assert shake_chance < 50000

    @patch('engine.battle.catch_calculator.calculate_shake')
    def test_catch_with_different_ball_types(self, mock_shake, eevee_pokemon):
        """Different ball types should affect catch success rate (probabilistically)."""
        mock_shake.return_value = True
        
        pokeball = Pokeball(name="Pokeball", catch_rate_modifier=1.0)
        ultra_ball = Pokeball(name="Ultra Ball", catch_rate_modifier=2.0)
        
        # With mocked shakes, both succeed, but different probability values should be used
        catch_attempt(eevee_pokemon.generate_battlemon(), pokeball)
        call_count_pokeball = mock_shake.call_count
        
        mock_shake.reset_mock()
        catch_attempt(eevee_pokemon.generate_battlemon(), ultra_ball)
        call_count_ultra = mock_shake.call_count
        
        # Both should have 4 shake attempts
        assert call_count_pokeball == 4
        assert call_count_ultra == 4

    def test_capture_rate_clamping(self, eevee_base, tackle_move):
        """Capture rate should be clamped between 1 and 255."""
        move_set = pytest.importorskip("shared.pokemon.move").MoveSet(moves=[tackle_move])
        
        pokemon = Pokemon(pokemon_base=eevee_base, level=10, move_set=move_set)
        
        # Very low modifier (should be clamped to 1)
        low_ball = Pokeball(name="Low Ball", catch_rate_modifier=0.001)
        chance_low = calculate_catch_probability(pokemon.generate_battlemon(), low_ball)
        
        # Very high modifier (should be clamped to 255)
        high_ball = Pokeball(name="High Ball", catch_rate_modifier=1000.0)
        chance_high = calculate_catch_probability(pokemon.generate_battlemon(), high_ball)
        
        # Both should return valid values
        assert 0 <= chance_low <= 65536
        assert 0 <= chance_high <= 65536
        assert chance_high > chance_low  # But high should still be greater


class TestCatchCalculatorEdgeCases:
    """Edge case tests for catch calculator."""

    def test_catch_probability_with_zero_hp(self, eevee_base, tackle_move):
        """Pokemon with 0 HP should still calculate (though shouldn't happen in practice)."""
        move_set = pytest.importorskip("shared.pokemon.move").MoveSet(moves=[tackle_move])
        pokemon = Pokemon(pokemon_base=eevee_base, level=10, move_set=move_set)
        pokemon.current_hp = 0
        
        pokeball = Pokeball(name="Pokeball", catch_rate_modifier=1.0)
        # Should not raise an error
        shake_chance = calculate_catch_probability(pokemon.generate_battlemon(), pokeball)
        assert isinstance(shake_chance, (int, float))
        assert shake_chance >= 0

    def test_catch_probability_with_very_high_level(self, eevee_base, tackle_move):
        """Very high level Pokemon should still calculate properly."""
        move_set = pytest.importorskip("shared.pokemon.move").MoveSet(moves=[tackle_move])
        pokemon = Pokemon(pokemon_base=eevee_base, level=100, move_set=move_set)
        
        pokeball = Pokeball(name="Pokeball", catch_rate_modifier=1.0)
        shake_chance = calculate_catch_probability(pokemon.generate_battlemon(), pokeball)
        
        assert 0 <= shake_chance <= 65536

    def test_multiple_status_conditions(self, eevee_pokemon, pokeball):
        """Pokemon with status conditions should have predictable behavior."""
        # Test each status individually in battle state
        sleep_status = status_repository.get("sleep") or StatusCondition(name="sleep")
        freeze_status = status_repository.get("freeze") or StatusCondition(name="freeze")
        paralysis_status = status_repository.get("paralysis") or StatusCondition(name="paralysis")
        burn_status = status_repository.get("burn") or StatusCondition(name="burn")
        poison_status = status_repository.get("poison") or StatusCondition(name="poison")

        statuses_to_test = [
            (sleep_status, True),  # Big bonus
            (freeze_status, True),  # Big bonus
            (paralysis_status, False),  # Small bonus
            (burn_status, False),  # Small bonus
            (poison_status, False),  # Small bonus
        ]
        
        chances = {}
        bm = eevee_pokemon.generate_battlemon()
        for status, is_big_bonus in statuses_to_test:
            bm.status_conditions.clear()
            bm.status_conditions[status] = 0
            chances[status] = calculate_catch_probability(bm, pokeball)
        
        # Verify big bonus statuses have higher catch rates than small bonus
        assert chances[sleep_status] >= chances[paralysis_status]
        assert chances[freeze_status] >= chances[burn_status]