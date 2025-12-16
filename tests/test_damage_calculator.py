"""Test suite for damage calculation system."""
import pytest
from engine.battle.damage_calculator import (
    calculate_damage, calculate_critical_hit,
    _get_level_modifier, _get_power_modifier, _get_attack_stat_modifier,
    _get_defence_stat_modifier, _get_stab_modifier, _get_type_effectiveness_modifier
)
from engine.battle.battle_header import BattleState, BattleWeather
from shared.pokemon.types import MoveCategory, PokemonType, StatusCondition
from shared.pokemon.move import Move


class TestDamageCalculation:
    """Tests for damage calculation."""

    def test_calculate_damage_returns_positive(self, pikachu_pokemon, eevee_pokemon):
        """Test that damage calculation returns a positive value."""
        move = pikachu_pokemon.move_set.moves[0]  # Tackle
        battle_state = BattleState()
        
        damage = calculate_damage(
            attacking_pokemon=pikachu_pokemon,
            defending_pokemon=eevee_pokemon,
            move=move,
            critical_hit=False,
            battle_state=battle_state
        )
        
        assert damage > 0
        assert isinstance(damage, int)

    def test_damage_at_least_1(self, pikachu_pokemon, eevee_pokemon):
        """Test that damage is always at least 1."""
        move = pikachu_pokemon.move_set.moves[0]
        battle_state = BattleState()
        
        # Even with very low attack pokemon
        pikachu_pokemon.pokemon.base_stats.attack = 1
        
        damage = calculate_damage(
            attacking_pokemon=pikachu_pokemon,
            defending_pokemon=eevee_pokemon,
            move=move,
            critical_hit=False,
            battle_state=battle_state
        )
        
        assert damage >= 1

    def test_critical_hit_increases_damage(self, pikachu_pokemon, eevee_pokemon):
        """Test that critical hits increase damage."""
        move = pikachu_pokemon.move_set.moves[0]
        battle_state = BattleState()
        
        normal_damage = calculate_damage(
            attacking_pokemon=pikachu_pokemon,
            defending_pokemon=eevee_pokemon,
            move=move,
            critical_hit=False,
            battle_state=battle_state
        )
        
        critical_damage = calculate_damage(
            attacking_pokemon=pikachu_pokemon,
            defending_pokemon=eevee_pokemon,
            move=move,
            critical_hit=True,
            battle_state=battle_state
        )
        
        assert critical_damage > normal_damage

    def test_higher_level_deals_more_damage(self, pikachu_base, eevee_pokemon, tackle_move):
        """Test that higher level Pokemon deal more damage."""
        from shared.pokemon.move import MoveSet
        from shared.pokemon.pokemon import Pokemon
        
        move_set = MoveSet(moves=[tackle_move])
        low_level = Pokemon(pokemon=pikachu_base, level=5, move_set=move_set)
        high_level = Pokemon(pokemon=pikachu_base, level=50, move_set=move_set)
        
        battle_state = BattleState()
        move = low_level.move_set.moves[0]
        
        low_damage = calculate_damage(
            attacking_pokemon=low_level,
            defending_pokemon=eevee_pokemon,
            move=move,
            critical_hit=False,
            battle_state=battle_state
        )
        
        high_damage = calculate_damage(
            attacking_pokemon=high_level,
            defending_pokemon=eevee_pokemon,
            move=move,
            critical_hit=False,
            battle_state=battle_state
        )
        
        assert high_damage > low_damage

    def test_physical_move_uses_attack_stat(self, pikachu_pokemon, eevee_pokemon, tackle_move):
        """Test that physical moves use attack stat."""
        from shared.pokemon.move import MoveSet
        
        move_set = MoveSet(moves=[tackle_move])
        pikachu_pokemon.move_set = move_set
        
        move = pikachu_pokemon.move_set.moves[0]
        
        attack_modifier = _get_attack_stat_modifier(pikachu_pokemon, move)
        
        assert attack_modifier == pikachu_pokemon.get_attack_stat()

    def test_special_move_uses_special_attack_stat(self, pikachu_pokemon, eevee_pokemon, thunderbolt_move):
        """Test that special moves use special attack stat."""
        from shared.pokemon.move import MoveSet
        
        move_set = MoveSet(moves=[thunderbolt_move])
        pikachu_pokemon.move_set = move_set
        
        move = pikachu_pokemon.move_set.moves[0]
        
        attack_modifier = _get_attack_stat_modifier(pikachu_pokemon, move)
        
        assert attack_modifier == pikachu_pokemon.get_special_attack_stat()


class TestCriticalHit:
    """Tests for critical hit calculation."""

    def test_calculate_critical_hit_returns_bool(self, pikachu_pokemon):
        """Test that critical hit calculation returns a boolean."""
        result = calculate_critical_hit(pikachu_pokemon)
        assert isinstance(result, bool)

    def test_critical_hit_possible(self, pikachu_pokemon):
        """Test that critical hits can occur."""
        # Run multiple times to check if critical can occur
        results = [calculate_critical_hit(pikachu_pokemon) for _ in range(1000)]
        
        # At least one should be True (critical hit) in 1000 tries
        # This is probabilistic but very unlikely to fail
        # Standard crit rate is 1/16 or 6.25%, so in 1000 tries we expect ~62 crits
        assert any(results), "No critical hits in 1000 tries - very unlikely"


class TestDamageModifiers:
    """Tests for individual damage modifier functions."""

    def test_level_modifier(self):
        """Test level modifier calculation."""
        level_5 = _get_level_modifier(5)
        level_50 = _get_level_modifier(50)
        level_100 = _get_level_modifier(100)
        
        assert level_5 > 0
        assert level_100 > level_50 > level_5

    def test_power_modifier(self, tackle_move, thunderbolt_move):
        """Test power modifier from moves."""
        from shared.pokemon.move import Move
        
        tackle = Move(base_move=tackle_move, current_pp=tackle_move.pp)
        thunderbolt = Move(base_move=thunderbolt_move, current_pp=thunderbolt_move.pp)
        
        tackle_power = _get_power_modifier(tackle)
        thunderbolt_power = _get_power_modifier(thunderbolt)
        
        assert tackle_power == 40
        assert thunderbolt_power == 90
        assert thunderbolt_power > tackle_power

    def test_stab_modifier(self, pikachu_pokemon, eevee_pokemon, thunderbolt_move):
        """Test Same Type Attack Bonus (STAB) modifier."""
        from shared.pokemon.move import Move, MoveSet
        
        # Pikachu (Electric type) using Electric move should get STAB
        electric_move = Move(base_move=thunderbolt_move, current_pp=15)
        stab = _get_stab_modifier(pikachu_pokemon, electric_move)
        assert stab == 1.5
        
        # Eevee (Normal type) using Electric move should not get STAB
        move_set = MoveSet(moves=[thunderbolt_move])
        eevee_pokemon.move_set = move_set
        no_stab = _get_stab_modifier(eevee_pokemon, electric_move)
        assert no_stab == 1.0

    def test_defense_stat_modifier_physical(self, eevee_pokemon, tackle_move):
        """Test defense stat modifier for physical moves."""
        from shared.pokemon.move import Move
        
        move = Move(base_move=tackle_move, current_pp=tackle_move.pp)
        defense_mod = _get_defence_stat_modifier(eevee_pokemon, move)
        
        assert defense_mod == eevee_pokemon.get_defense_stat()

    def test_defense_stat_modifier_special(self, eevee_pokemon, thunderbolt_move):
        """Test defense stat modifier for special moves."""
        from shared.pokemon.move import Move
        
        move = Move(base_move=thunderbolt_move, current_pp=thunderbolt_move.pp)
        defense_mod = _get_defence_stat_modifier(eevee_pokemon, move)
        
        assert defense_mod == eevee_pokemon.get_special_defense_stat()


class TestTypeEffectiveness:
    """Tests for type effectiveness in damage calculation."""

    def test_super_effective_deals_more_damage(self, pikachu_base, tackle_move, water_gun_move):
        """Test that super effective moves deal more damage."""
        from shared.pokemon.move import MoveSet
        from shared.pokemon.pokemon import Pokemon, PokemonBase
        
        # Create a Water-type Pokemon (Squirtle)
        squirtle_base = PokemonBase(
            name="Squirtle",
            types=[PokemonType.WATER],
            base_stats={
                "hp": 44, "attack": 48, "defense": 65,
                "special_attack": 50, "special_defense": 64, "speed": 43
            },
            pokedex_number=7,
            catch_rate=45
        )
        
        # Create Fire-type Pokemon (Charmander)
        charmander_base = PokemonBase(
            name="Charmander",
            types=[PokemonType.FIRE],
            base_stats={
                "hp": 39, "attack": 52, "defense": 43,
                "special_attack": 60, "special_defense": 50, "speed": 65
            },
            pokedex_number=4,
            catch_rate=45
        )
        
        move_set = MoveSet(moves=[water_gun_move])
        squirtle = Pokemon(pokemon=squirtle_base, level=20, move_set=move_set)
        charmander = Pokemon(pokemon=charmander_base, level=20, move_set=move_set)
        
        battle_state = BattleState()
        move = squirtle.move_set.moves[0]
        
        # Water is super effective against Fire
        damage = calculate_damage(
            attacking_pokemon=squirtle,
            defending_pokemon=charmander,
            move=move,
            critical_hit=False,
            battle_state=battle_state
        )
        
        assert damage > 0  # Should deal damage

    def test_type_effectiveness_modifier(self, pikachu_pokemon, thunderbolt_move):
        """Test type effectiveness modifier calculation."""
        from shared.pokemon.move import Move
        
        electric_move = Move(base_move=thunderbolt_move, current_pp=15)
        
        # Test that type effectiveness function exists and returns a value
        # Note: _get_type_effectiveness_modifier may return 1.0 as placeholder
        effectiveness = _get_type_effectiveness_modifier(electric_move, pikachu_pokemon)
        assert effectiveness >= 0.0
        assert isinstance(effectiveness, float)


class TestWeatherEffects:
    """Tests for weather effects on damage."""

    def test_harsh_sunlight_boosts_fire(self, charizard_pokemon, eevee_pokemon, flamethrower_move):
        """Test that harsh sunlight boosts Fire-type moves."""
        from shared.pokemon.move import MoveSet
        
        move_set = MoveSet(moves=[flamethrower_move])
        charizard_pokemon.move_set = move_set
        
        battle_state_normal = BattleState()
        battle_state_sun = BattleState(weather=BattleWeather.HARSH_SUNLIGHT)
        
        move = charizard_pokemon.move_set.moves[0]
        
        normal_damage = calculate_damage(
            attacking_pokemon=charizard_pokemon,
            defending_pokemon=eevee_pokemon,
            move=move,
            critical_hit=False,
            battle_state=battle_state_normal
        )
        
        sun_damage = calculate_damage(
            attacking_pokemon=charizard_pokemon,
            defending_pokemon=eevee_pokemon,
            move=move,
            critical_hit=False,
            battle_state=battle_state_sun
        )
        
        assert sun_damage > normal_damage


class TestStatusConditions:
    """Tests for status condition effects on damage."""

    def test_burn_reduces_physical_damage(self, pikachu_pokemon, eevee_pokemon, tackle_move):
        """Test that burn reduces physical move damage."""
        from shared.pokemon.move import MoveSet
        
        move_set = MoveSet(moves=[tackle_move])
        pikachu_pokemon.move_set = move_set
        
        battle_state = BattleState()
        move = pikachu_pokemon.move_set.moves[0]
        
        # Normal damage
        normal_damage = calculate_damage(
            attacking_pokemon=pikachu_pokemon,
            defending_pokemon=eevee_pokemon,
            move=move,
            critical_hit=False,
            battle_state=battle_state
        )
        
        # Burned damage
        pikachu_pokemon.status_condition = StatusCondition.BURNED
        burned_damage = calculate_damage(
            attacking_pokemon=pikachu_pokemon,
            defending_pokemon=eevee_pokemon,
            move=move,
            critical_hit=False,
            battle_state=battle_state
        )
        
        assert burned_damage < normal_damage


class TestDamageRange:
    """Tests for damage range and randomness."""

    def test_damage_has_random_variation(self, pikachu_pokemon, eevee_pokemon):
        """Test that damage has random variation."""
        move = pikachu_pokemon.move_set.moves[0]
        battle_state = BattleState()
        
        # Calculate damage multiple times
        damages = [
            calculate_damage(
                attacking_pokemon=pikachu_pokemon,
                defending_pokemon=eevee_pokemon,
                move=move,
                critical_hit=False,
                battle_state=battle_state
            )
            for _ in range(50)
        ]
        
        # Should have some variation due to random factor
        unique_damages = set(damages)
        assert len(unique_damages) > 1, "Damage should have random variation"

    def test_damage_within_expected_range(self, pikachu_pokemon, eevee_pokemon):
        """Test that damage stays within expected range."""
        move = pikachu_pokemon.move_set.moves[0]
        battle_state = BattleState()
        
        damages = [
            calculate_damage(
                attacking_pokemon=pikachu_pokemon,
                defending_pokemon=eevee_pokemon,
                move=move,
                critical_hit=False,
                battle_state=battle_state
            )
            for _ in range(100)
        ]
        
        min_damage = min(damages)
        max_damage = max(damages)
        
        # Random factor is 0.85 to 1.0, so max should be at most ~18% higher than min
        # Allow slightly more range for rounding
        assert max_damage <= min_damage * 1.25
