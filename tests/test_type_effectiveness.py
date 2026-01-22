"""Test suite for type effectiveness system."""
from shared.battle.type_effectiveness import (
    TYPE_EFFECTIVENESS, offensive_effectiveness_all
)
from shared.pokemon.types import PokemonType


class TestTypeEffectivenessChart:
    """Tests for the type effectiveness chart."""

    def test_fire_super_effective_against_grass(self):
        """Test Fire is super effective against Grass."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.FIRE]
        assert effectiveness[PokemonType.GRASS] == 2.0

    def test_fire_not_very_effective_against_water(self):
        """Test Fire is not very effective against Water."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.FIRE]
        assert effectiveness[PokemonType.WATER] == 0.5

    def test_water_super_effective_against_fire(self):
        """Test Water is super effective against Fire."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.WATER]
        assert effectiveness[PokemonType.FIRE] == 2.0

    def test_water_not_very_effective_against_grass(self):
        """Test Water is not very effective against Grass."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.WATER]
        assert effectiveness[PokemonType.GRASS] == 0.5

    def test_grass_super_effective_against_water(self):
        """Test Grass is super effective against Water."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.GRASS]
        assert effectiveness[PokemonType.WATER] == 2.0

    def test_electric_no_effect_on_ground(self):
        """Test Electric has no effect on Ground."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.ELECTRIC]
        assert effectiveness[PokemonType.GROUND] == 0.0

    def test_ground_super_effective_against_electric(self):
        """Test Ground is super effective against Electric."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.GROUND]
        assert effectiveness[PokemonType.ELECTRIC] == 2.0

    def test_normal_no_effect_on_ghost(self):
        """Test Normal has no effect on Ghost."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.NORMAL]
        assert effectiveness[PokemonType.GHOST] == 0.0

    def test_ghost_no_effect_on_normal(self):
        """Test Ghost has no effect on Normal."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.GHOST]
        assert effectiveness[PokemonType.NORMAL] == 0.0

    def test_fighting_no_effect_on_ghost(self):
        """Test Fighting has no effect on Ghost."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.FIGHTING]
        assert effectiveness[PokemonType.GHOST] == 0.0

    def test_psychic_no_effect_on_dark(self):
        """Test Psychic has no effect on Dark."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.PSYCHIC]
        assert effectiveness[PokemonType.DARK] == 0.0

    def test_dragon_no_effect_on_fairy(self):
        """Test Dragon has no effect on Fairy."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.DRAGON]
        assert effectiveness[PokemonType.FAIRY] == 0.0


class TestComplexTypeMatchups:
    """Tests for more complex type matchups."""

    def test_ice_super_effective_against_dragon(self):
        """Test Ice is super effective against Dragon."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.ICE]
        assert effectiveness[PokemonType.DRAGON] == 2.0

    def test_fairy_super_effective_against_dragon(self):
        """Test Fairy is super effective against Dragon."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.FAIRY]
        assert effectiveness[PokemonType.DRAGON] == 2.0

    def test_fighting_super_effective_against_dark(self):
        """Test Fighting is super effective against Dark."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.FIGHTING]
        assert effectiveness[PokemonType.DARK] == 2.0

    def test_bug_super_effective_against_psychic(self):
        """Test Bug is super effective against Psychic."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.BUG]
        assert effectiveness[PokemonType.PSYCHIC] == 2.0

    def test_dark_super_effective_against_psychic(self):
        """Test Dark is super effective against Psychic."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.DARK]
        assert effectiveness[PokemonType.PSYCHIC] == 2.0

    def test_steel_resists_many_types(self):
        """Test Steel resists many types."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.STEEL]
        resistances = [t for t, mult in effectiveness.items() if mult == 0.5]
        
        # Steel should resist multiple types
        assert len(resistances) >= 3

    def test_fire_super_effective_against_steel(self):
        """Test Fire is super effective against Steel."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.FIRE]
        assert effectiveness[PokemonType.STEEL] == 2.0

    def test_rock_super_effective_against_flying(self):
        """Test Rock is super effective against Flying."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.ROCK]
        assert effectiveness[PokemonType.FLYING] == 2.0


class TestGetStrengths:
    """Tests for offensive strengths using provided effectiveness data."""

    def test_fire_strengths(self):
        """Test Fire type strengths."""
        chart = offensive_effectiveness_all(PokemonType.FIRE)
        strengths = [t for t, mult in chart.items() if mult == 2.0]
        assert PokemonType.GRASS in strengths
        assert PokemonType.ICE in strengths
        assert PokemonType.BUG in strengths
        assert PokemonType.STEEL in strengths

    def test_water_strengths(self):
        """Test Water type strengths."""
        chart = offensive_effectiveness_all(PokemonType.WATER)
        strengths = [t for t, mult in chart.items() if mult == 2.0]
        assert PokemonType.FIRE in strengths
        assert PokemonType.GROUND in strengths
        assert PokemonType.ROCK in strengths

    def test_electric_strengths(self):
        """Test Electric type strengths."""
        chart = offensive_effectiveness_all(PokemonType.ELECTRIC)
        strengths = [t for t, mult in chart.items() if mult == 2.0]
        assert PokemonType.WATER in strengths
        assert PokemonType.FLYING in strengths

    def test_grass_strengths(self):
        """Test Grass type strengths."""
        chart = offensive_effectiveness_all(PokemonType.GRASS)
        strengths = [t for t, mult in chart.items() if mult == 2.0]
        assert PokemonType.WATER in strengths
        assert PokemonType.GROUND in strengths
        assert PokemonType.ROCK in strengths

    def test_ice_strengths(self):
        """Test Ice type strengths."""
        chart = offensive_effectiveness_all(PokemonType.ICE)
        strengths = [t for t, mult in chart.items() if mult == 2.0]
        assert PokemonType.GRASS in strengths
        assert PokemonType.GROUND in strengths
        assert PokemonType.FLYING in strengths
        assert PokemonType.DRAGON in strengths

    def test_fighting_strengths(self):
        """Test Fighting type strengths."""
        chart = offensive_effectiveness_all(PokemonType.FIGHTING)
        strengths = [t for t, mult in chart.items() if mult == 2.0]
        assert PokemonType.NORMAL in strengths
        assert PokemonType.ICE in strengths
        assert PokemonType.ROCK in strengths
        assert PokemonType.DARK in strengths
        assert PokemonType.STEEL in strengths

    def test_poison_strengths(self):
        """Test Poison type strengths."""
        chart = offensive_effectiveness_all(PokemonType.POISON)
        strengths = [t for t, mult in chart.items() if mult == 2.0]
        assert PokemonType.GRASS in strengths
        assert PokemonType.FAIRY in strengths


class TestGetWeaknesses:
    """Tests for resistances via offensive chart (multiplier 0.5)."""

    def test_fire_weaknesses(self):
        """Test Fire type weaknesses (what resists Fire)."""
        chart = offensive_effectiveness_all(PokemonType.FIRE)
        weaknesses = [t for t, mult in chart.items() if mult == 0.5]
        assert PokemonType.FIRE in weaknesses
        assert PokemonType.WATER in weaknesses
        assert PokemonType.ROCK in weaknesses
        assert PokemonType.DRAGON in weaknesses

    def test_water_weaknesses(self):
        """Test Water type weaknesses (what resists Water)."""
        chart = offensive_effectiveness_all(PokemonType.WATER)
        weaknesses = [t for t, mult in chart.items() if mult == 0.5]
        assert PokemonType.WATER in weaknesses
        assert PokemonType.GRASS in weaknesses
        assert PokemonType.DRAGON in weaknesses

    def test_grass_weaknesses(self):
        """Test Grass type weaknesses (what resists Grass)."""
        chart = offensive_effectiveness_all(PokemonType.GRASS)
        weaknesses = [t for t, mult in chart.items() if mult == 0.5]
        assert PokemonType.FIRE in weaknesses
        assert PokemonType.POISON in weaknesses
        assert PokemonType.FLYING in weaknesses
        assert PokemonType.STEEL in weaknesses

    def test_steel_weaknesses(self):
        """Test Steel type weaknesses (what resists Steel)."""
        chart = offensive_effectiveness_all(PokemonType.STEEL)
        weaknesses = [t for t, mult in chart.items() if mult == 0.5]
        assert PokemonType.FIRE in weaknesses
        assert PokemonType.WATER in weaknesses
        # Steel resists many types
        assert len(weaknesses) >= 3


class TestTypeNeutralMatchups:
    """Tests for neutral type matchups (1.0 effectiveness)."""

    def test_normal_vs_normal_is_neutral(self):
        """Test Normal vs Normal is neutral."""
        effectiveness = TYPE_EFFECTIVENESS.get(PokemonType.NORMAL, {})
        # If not in dict, it's neutral (1.0)
        assert effectiveness.get(PokemonType.NORMAL, 1.0) == 1.0

    def test_fire_vs_electric_is_neutral(self):
        """Test Fire vs Electric is neutral."""
        effectiveness = TYPE_EFFECTIVENESS.get(PokemonType.FIRE, {})
        assert effectiveness.get(PokemonType.ELECTRIC, 1.0) == 1.0

    def test_water_vs_psychic_is_neutral(self):
        """Test Water vs Psychic is neutral."""
        effectiveness = TYPE_EFFECTIVENESS.get(PokemonType.WATER, {})
        assert effectiveness.get(PokemonType.PSYCHIC, 1.0) == 1.0


class TestAllPokemonTypes:
    """Tests to ensure all Pokemon types are covered."""

    def test_all_types_have_effectiveness_data(self):
        """Test that all Pokemon types have effectiveness data."""
        all_types = [
            PokemonType.NORMAL, PokemonType.FIRE, PokemonType.WATER,
            PokemonType.ELECTRIC, PokemonType.GRASS, PokemonType.ICE,
            PokemonType.FIGHTING, PokemonType.POISON, PokemonType.GROUND,
            PokemonType.FLYING, PokemonType.PSYCHIC, PokemonType.BUG,
            PokemonType.ROCK, PokemonType.GHOST, PokemonType.DRAGON,
            PokemonType.DARK, PokemonType.STEEL, PokemonType.FAIRY
        ]
        
        for pokemon_type in all_types:
            # Each type should be in the effectiveness chart
            assert pokemon_type in TYPE_EFFECTIVENESS

    def test_effectiveness_values_are_valid(self):
        """Test that all effectiveness values are valid."""
        valid_values = {0.0, 0.5, 1.0, 2.0}
        
        for attack_type, matchups in TYPE_EFFECTIVENESS.items():
            for defend_type, multiplier in matchups.items():
                assert multiplier in valid_values, \
                    f"Invalid effectiveness value {multiplier} for {attack_type} vs {defend_type}"


class TestDualTypeConsiderations:
    """Tests for dual-type Pokemon considerations."""

    def test_dual_type_weaknesses_stack(self):
        """Test understanding of how dual types would work."""
        # If a Pokemon is both Grass and Bug type
        # And Fire is super effective against both
        fire_effectiveness = TYPE_EFFECTIVENESS[PokemonType.FIRE]
        
        grass_mult = fire_effectiveness.get(PokemonType.GRASS, 1.0)
        bug_mult = fire_effectiveness.get(PokemonType.BUG, 1.0)
        
        # Both should be super effective
        assert grass_mult == 2.0
        assert bug_mult == 2.0
        
        # In actual game, this would be 4x (2.0 * 2.0)

    def test_dual_type_resistances_stack(self):
        """Test understanding of how dual type resistances work."""
        # If a Pokemon is both Steel and Psychic type
        # And Poison attacks it
        poison_effectiveness = TYPE_EFFECTIVENESS[PokemonType.POISON]
        
        steel_mult = poison_effectiveness.get(PokemonType.STEEL, 1.0)
        psychic_mult = poison_effectiveness.get(PokemonType.PSYCHIC, 1.0)
        
        # Check that Poison has some effectiveness against these types
        # Poison is immune (0.0) to Steel in Gen 6+
        assert steel_mult in [0.0, 0.5, 1.0]
        assert psychic_mult in [0.5, 1.0, 2.0]
        
        # In actual game with dual types, resistances would stack


class TestSpecialTypeInteractions:
    """Tests for special type interactions."""

    def test_ground_effectiveness(self):
        """Test Ground type effectiveness."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.GROUND]
        
        # Ground is super effective against
        assert effectiveness[PokemonType.FIRE] == 2.0
        assert effectiveness[PokemonType.ELECTRIC] == 2.0
        assert effectiveness[PokemonType.POISON] == 2.0
        assert effectiveness[PokemonType.ROCK] == 2.0
        assert effectiveness[PokemonType.STEEL] == 2.0

    def test_flying_effectiveness(self):
        """Test Flying type effectiveness."""
        effectiveness = TYPE_EFFECTIVENESS[PokemonType.FLYING]
        
        # Flying is super effective against
        assert effectiveness[PokemonType.GRASS] == 2.0
        assert effectiveness[PokemonType.FIGHTING] == 2.0
        assert effectiveness[PokemonType.BUG] == 2.0
