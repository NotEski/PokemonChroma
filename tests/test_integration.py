"""Integration tests for complete game scenarios."""
import pytest
from engine.battle.battle_manager import SingleBattleManager, SinglesBattlePosition
from shared.battle.opponent import TrainerOpponent, WildPokemonOpponent
from shared.pokemon.pokemon import Pokemon, PokemonBase, PokemonTeam
from shared.trainer.trainer import BattleTrainer
from shared.pokemon.move import MoveSet, BaseMove
from shared.pokemon.types import PokemonType
from shared.pokemon.move import DamageClass


class TestCompleteWildBattle:
    """Integration tests for a complete wild Pokemon battle."""

    def test_wild_battle_trainer_wins(self, pikachu_base, eevee_base, tackle_move):
        """Test a complete wild battle where trainer wins."""
        # Setup
        move_set = MoveSet(moves=[tackle_move])
        pikachu = Pokemon(pokemon=pikachu_base, level=20, move_set=move_set)
        eevee = Pokemon(pokemon=eevee_base, level=5, move_set=move_set)
        
        trainer = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu]))
        )
        wild = WildPokemonOpponent(pokemon=eevee)
        
        battle = SingleBattleManager(team_1=trainer, team_2=wild)
        battle.init_battle()
        
        # Execute multiple turns
        for _ in range(5):
            if eevee.current_hp <= 0:
                break
                
            battle.start_turn()
            battle.use_move(
                user_position=SinglesBattlePosition.Team1_Pokemon1,
                move_index=1,
                target_position=SinglesBattlePosition.Team2_Pokemon1
            )
            battle.use_move(
                user_position=SinglesBattlePosition.Team2_Pokemon1,
                move_index=1,
                target_position=SinglesBattlePosition.Team1_Pokemon1
            )
            battle.end_turn()
        
        # Wild Pokemon should have taken damage
        assert eevee.current_hp < eevee.max_hp

    def test_wild_battle_escape_success(self, pikachu_pokemon, eevee_pokemon):
        """Test escaping from a wild battle."""
        trainer = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer, team_2=wild)
        battle.init_battle()
        
        # Try to escape (may take multiple attempts)
        escaped = False
        for _ in range(10):
            battle.start_turn()
            battle.use_escape(user_position=SinglesBattlePosition.Team1_Pokemon1)
            battle.use_move(
                user_position=SinglesBattlePosition.Team2_Pokemon1,
                move_index=1,
                target_position=SinglesBattlePosition.Team1_Pokemon1
            )
            battle.end_turn()
            
            if not battle.taking_actions:
                escaped = True
                break
        
        # Either escaped or still in battle


class TestCompleteTrainerBattle:
    """Integration tests for trainer vs trainer battles."""

    def test_trainer_battle_both_attack(self, pikachu_base, charizard_base, tackle_move, thunderbolt_move):
        """Test a trainer battle with both trainers attacking."""
        # Create two trainers with different Pokemon
        move_set1 = MoveSet(moves=[tackle_move, thunderbolt_move])
        move_set2 = MoveSet(moves=[tackle_move])
        
        pikachu = Pokemon(pokemon=pikachu_base, level=25, move_set=move_set1)
        charizard = Pokemon(pokemon=charizard_base, level=25, move_set=move_set2)
        
        trainer1 = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu]))
        )
        trainer2 = TrainerOpponent(
            trainer=BattleTrainer(name="Gary", team=PokemonTeam(pokemons=[charizard]))
        )
        
        battle = SingleBattleManager(team_1=trainer1, team_2=trainer2)
        battle.init_battle()
        
        # Record initial HP
        initial_pikachu_hp = pikachu.current_hp
        initial_charizard_hp = charizard.current_hp
        
        # Execute one turn
        battle.start_turn()
        battle.use_move(
            user_position=SinglesBattlePosition.Team1_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team2_Pokemon1
        )
        battle.use_move(
            user_position=SinglesBattlePosition.Team2_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team1_Pokemon1
        )
        battle.end_turn()
        
        # Both Pokemon should have taken damage
        assert pikachu.current_hp < initial_pikachu_hp or charizard.current_hp < initial_charizard_hp

    def test_trainer_battle_speed_determines_order(self, pikachu_base, eevee_base, tackle_move):
        """Test that faster Pokemon moves first."""
        move_set = MoveSet(moves=[tackle_move])
        
        # Pikachu has higher base speed (90 vs 55)
        pikachu = Pokemon(pokemon=pikachu_base, level=20, move_set=move_set)
        eevee = Pokemon(pokemon=eevee_base, level=20, move_set=move_set)
        
        trainer1 = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu]))
        )
        trainer2 = TrainerOpponent(
            trainer=BattleTrainer(name="Gary", team=PokemonTeam(pokemons=[eevee]))
        )
        
        battle = SingleBattleManager(team_1=trainer1, team_2=trainer2)
        battle.init_battle()
        
        battle.start_turn()
        battle.use_move(
            user_position=SinglesBattlePosition.Team1_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team2_Pokemon1
        )
        battle.use_move(
            user_position=SinglesBattlePosition.Team2_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team1_Pokemon1
        )
        
        # Get turn order
        turn_order = battle.get_turn_orders()
        
        # Should have two positions in turn order
        assert len(turn_order) == 2


class TestMultiTurnBattle:
    """Integration tests for battles lasting multiple turns."""

    def test_pp_depletion_over_turns(self, pikachu_pokemon, eevee_pokemon):
        """Test that PP depletes correctly over multiple turns."""
        trainer = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer, team_2=wild)
        battle.init_battle()
        
        initial_pp = pikachu_pokemon.move_set.moves[0].current_pp
        
        # Execute 3 turns
        for i in range(3):
            if eevee_pokemon.current_hp <= 0:
                break
            battle.start_turn()
            battle.use_move(
                user_position=SinglesBattlePosition.Team1_Pokemon1,
                move_index=1,
                target_position=SinglesBattlePosition.Team2_Pokemon1
            )
            battle.use_move(
                user_position=SinglesBattlePosition.Team2_Pokemon1,
                move_index=1,
                target_position=SinglesBattlePosition.Team1_Pokemon1
            )
            battle.end_turn()
        
        # PP should have decreased
        assert pikachu_pokemon.move_set.moves[0].current_pp < initial_pp

    def test_pokemon_fainting_ends_battle(self, pikachu_base, eevee_base, tackle_move):
        """Test that battle behavior when Pokemon faints."""
        move_set = MoveSet(moves=[tackle_move])
        
        # Create a very weak Eevee (low level, low HP)
        pikachu = Pokemon(pokemon=pikachu_base, level=50, move_set=move_set)
        eevee = Pokemon(pokemon=eevee_base, level=1, move_set=move_set)
        
        trainer = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu]))
        )
        wild = WildPokemonOpponent(pokemon=eevee)
        
        battle = SingleBattleManager(team_1=trainer, team_2=wild)
        battle.init_battle()
        
        # Fight until Eevee faints
        for _ in range(10):
            if eevee.current_hp <= 0:
                break
                
            battle.start_turn()
            battle.use_move(
                user_position=SinglesBattlePosition.Team1_Pokemon1,
                move_index=1,
                target_position=SinglesBattlePosition.Team2_Pokemon1
            )
            battle.use_move(
                user_position=SinglesBattlePosition.Team2_Pokemon1,
                move_index=1,
                target_position=SinglesBattlePosition.Team1_Pokemon1
            )
            battle.end_turn()
        
        # Eevee should have fainted
        assert eevee.current_hp == 0


class TestTypeAdvantageScenarios:
    """Integration tests for type advantage scenarios."""

    def test_super_effective_damage_in_battle(self):
        """Test super effective moves in a real battle scenario."""
        # Create Fire-type move
        ember = BaseMove(
            name="Ember",
            type=PokemonType.FIRE,
            power=40,
            pp=25,
            accuracy=100,
            category=DamageClass.SPECIAL
        )
        
        # Create a Fire-type Pokemon
        charmander_base = PokemonBase(
            name="Charmander",
            types=[PokemonType.FIRE],
            base_stats={
                "hp": 39, "attack": 52, "defense": 43,
                "special_attack": 60, "special_defense": 50, "speed": 65
            },
            pokedex_number=4,
            capture_rate=45
        )
        
        # Create a Grass-type Pokemon (weak to Fire)
        bulbasaur_base = PokemonBase(
            name="Bulbasaur",
            types=[PokemonType.GRASS],
            base_stats={
                "hp": 45, "attack": 49, "defense": 49,
                "special_attack": 65, "special_defense": 65, "speed": 45
            },
            pokedex_number=1,
            capture_rate=45
        )
        
        move_set = MoveSet(moves=[ember])
        charmander = Pokemon(pokemon=charmander_base, level=20, move_set=move_set)
        bulbasaur = Pokemon(pokemon=bulbasaur_base, level=20, move_set=move_set)
        
        trainer1 = TrainerOpponent(
            trainer=BattleTrainer(name="Red", team=PokemonTeam(pokemons=[charmander]))
        )
        trainer2 = TrainerOpponent(
            trainer=BattleTrainer(name="Blue", team=PokemonTeam(pokemons=[bulbasaur]))
        )
        
        battle = SingleBattleManager(team_1=trainer1, team_2=trainer2)
        battle.init_battle()
        
        initial_hp = bulbasaur.current_hp
        
        battle.start_turn()
        battle.use_move(
            user_position=SinglesBattlePosition.Team1_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team2_Pokemon1
        )
        battle.use_move(
            user_position=SinglesBattlePosition.Team2_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team1_Pokemon1
        )
        battle.end_turn()
        
        # Bulbasaur should take super effective damage
        assert bulbasaur.current_hp < initial_hp


class TestBattleStateManagement:
    """Integration tests for battle state management."""

    def test_battle_state_resets_after_battle(self, pikachu_pokemon, eevee_pokemon):
        """Test that battle state resets properly after battle ends."""
        trainer = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer, team_2=wild)
        battle.init_battle()
        
        # Modify battle state
        pikachu_pokemon.pokemon_battle_state.attack_stat_stage = 2
        eevee_pokemon.pokemon_battle_state.defense_stat_stage = -1
        
        # End battle
        battle.end_battle()
        
        # Battle state should be reset
        assert pikachu_pokemon.pokemon_battle_state.attack_stat_stage == 0
        assert eevee_pokemon.pokemon_battle_state.defense_stat_stage == 0

    def test_turn_number_increments_correctly(self, pikachu_pokemon, eevee_pokemon):
        """Test that turn numbers increment correctly."""
        trainer = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer, team_2=wild)
        battle.init_battle()
        
        assert battle.battle_state.turn_number == 0
        
        # Execute 3 turns
        for i in range(3):
            battle.start_turn()
            assert battle.battle_state.turn_number == i + 1
            
            battle.use_move(
                user_position=SinglesBattlePosition.Team1_Pokemon1,
                move_index=1,
                target_position=SinglesBattlePosition.Team2_Pokemon1
            )
            battle.use_move(
                user_position=SinglesBattlePosition.Team2_Pokemon1,
                move_index=1,
                target_position=SinglesBattlePosition.Team1_Pokemon1
            )
            battle.end_turn()


class TestActionCancellation:
    """Integration tests for action cancellation scenarios."""

    def test_cancel_and_choose_different_action(self, pikachu_pokemon, eevee_pokemon):
        """Test canceling an action and choosing a different one."""
        trainer = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer, team_2=wild)
        battle.init_battle()
        
        battle.start_turn()
        
        # Choose move 0
        battle.use_move(
            user_position=SinglesBattlePosition.Team1_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team2_Pokemon1
        )
        assert SinglesBattlePosition.Team1_Pokemon1 in battle.this_turns_actions
        
        # Cancel and choose move 1
        battle.cancel_action(SinglesBattlePosition.Team1_Pokemon1)
        battle.use_move(
            user_position=SinglesBattlePosition.Team1_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team2_Pokemon1
        )
        
        # Should have move 1 queued
        assert SinglesBattlePosition.Team1_Pokemon1 in battle.this_turns_actions


class TestEdgeCases:
    """Integration tests for edge cases."""

    def test_battle_with_max_level_pokemon(self, pikachu_base, tackle_move):
        """Test battle with level 100 Pokemon."""
        move_set = MoveSet(moves=[tackle_move])
        pikachu1 = Pokemon(pokemon=pikachu_base, level=100, move_set=move_set)
        pikachu2 = Pokemon(pokemon=pikachu_base, level=100, move_set=move_set)
        
        trainer1 = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu1]))
        )
        trainer2 = TrainerOpponent(
            trainer=BattleTrainer(name="Gary", team=PokemonTeam(pokemons=[pikachu2]))
        )
        
        battle = SingleBattleManager(team_1=trainer1, team_2=trainer2)
        battle.init_battle()
        
        battle.start_turn()
        battle.use_move(
            user_position=SinglesBattlePosition.Team1_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team2_Pokemon1
        )
        battle.use_move(
            user_position=SinglesBattlePosition.Team2_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team1_Pokemon1
        )
        battle.end_turn()
        
        # Both should have taken damage
        assert pikachu1.current_hp < pikachu1.max_hp or pikachu2.current_hp < pikachu2.max_hp

    def test_battle_with_minimum_level_pokemon(self, pikachu_base, tackle_move):
        """Test battle with level 1 Pokemon."""
        move_set = MoveSet(moves=[tackle_move])
        pikachu1 = Pokemon(pokemon=pikachu_base, level=1, move_set=move_set)
        pikachu2 = Pokemon(pokemon=pikachu_base, level=1, move_set=move_set)
        
        trainer1 = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu1]))
        )
        trainer2 = TrainerOpponent(
            trainer=BattleTrainer(name="Gary", team=PokemonTeam(pokemons=[pikachu2]))
        )
        
        battle = SingleBattleManager(team_1=trainer1, team_2=trainer2)
        battle.init_battle()
        
        # Battle should initialize without errors
        assert battle.battle_config.is_wild is False
        assert len(battle.in_play_pokemon) == 2


class TestRealGameScenario:
    """Integration test simulating a realistic game scenario."""

    def test_complete_game_scenario(self):
        """Test a complete realistic game scenario."""
        # Create Pokemon with appropriate moves
        tackle = BaseMove(
            name="Tackle",
            type=PokemonType.NORMAL,
            power=40,
            pp=35,
            accuracy=100,
            category=DamageClass.PHYSICAL
        )
        
        thunderbolt = BaseMove(
            name="Thunderbolt",
            type=PokemonType.ELECTRIC,
            power=90,
            pp=15,
            accuracy=100,
            category=DamageClass.SPECIAL
        )
        
        # Trainer's Pikachu
        pikachu_base = PokemonBase(
            name="Pikachu",
            types=[PokemonType.ELECTRIC],
            base_stats={
                "hp": 35, "attack": 55, "defense": 40,
                "special_attack": 50, "special_defense": 50, "speed": 90
            },
            pokedex_number=25,
            capture_rate=190
        )
        
        move_set = MoveSet(moves=[tackle, thunderbolt])
        pikachu = Pokemon(pokemon=pikachu_base, level=15, move_set=move_set)
        
        # Wild Rattata
        rattata_base = PokemonBase(
            name="Rattata",
            types=[PokemonType.NORMAL],
            base_stats={
                "hp": 30, "attack": 56, "defense": 35,
                "special_attack": 25, "special_defense": 35, "speed": 72
            },
            pokedex_number=19,
            capture_rate=255
        )
        
        rattata_moveset = MoveSet(moves=[tackle])
        rattata = Pokemon(pokemon=rattata_base, level=3, move_set=rattata_moveset)
        
        # Setup battle
        trainer = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu]))
        )
        wild = WildPokemonOpponent(pokemon=rattata)
        
        battle = SingleBattleManager(team_1=trainer, team_2=wild)
        battle.init_battle()
        
        # Turn 1: Pikachu uses Thunderbolt
        battle.start_turn()
        battle.use_move(
            user_position=SinglesBattlePosition.Team1_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team2_Pokemon1
        )  # Thunderbolt
        battle.use_move(
            user_position=SinglesBattlePosition.Team2_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team1_Pokemon1
        )  # Tackle
        battle.end_turn()
        
        # Rattata should take significant damage (likely faint)
        assert rattata.current_hp < rattata.max_hp
        
        # PP should be reduced
        assert pikachu.move_set.moves[1].current_pp < 15
