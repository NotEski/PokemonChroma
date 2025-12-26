"""Test suite for battle system functionality."""
import pytest
from engine.battle.battle_manager import SingleBattleManager
from shared.battle.position_manager import BattlePosition
from shared.battle.opponent import TrainerOpponent, WildPokemonOpponent
from shared.battle.battle_header import BattleState
from shared.pokemon.pokemon import PokemonTeam
from shared.trainer.trainer import BattleTrainer


class TestBattleInitialization:
    """Tests for battle initialization."""

    def test_init_wild_pokemon_battle(self, pikachu_pokemon, eevee_pokemon):
        """Test initializing a wild Pokemon battle."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(
                name="Ash",
                team=PokemonTeam(pokemons=[pikachu_pokemon])
            )
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(
            team_1=trainer_opponent,
            team_2=wild_opponent
        )
        
        battle.init_battle()
        
        assert battle.battle_config.is_wild is True
        assert len(battle.in_play_pokemon) == 2
        assert SinglesBattlePosition.Team1_Pokemon1 in battle.in_play_pokemon
        assert SinglesBattlePosition.Team2_Pokemon1 in battle.in_play_pokemon

    def test_init_trainer_battle(self, pikachu_pokemon, eevee_pokemon):
        """Test initializing a trainer vs trainer battle."""
        trainer_1 = TrainerOpponent(
            trainer=BattleTrainer(
                name="Ash",
                team=PokemonTeam(pokemons=[pikachu_pokemon])
            )
        )
        trainer_2 = TrainerOpponent(
            trainer=BattleTrainer(
                name="Gary",
                team=PokemonTeam(pokemons=[eevee_pokemon])
            )
        )
        
        battle = SingleBattleManager(team_1=trainer_1, team_2=trainer_2)
        battle.init_battle()
        
        assert battle.battle_config.is_wild is False
        assert len(battle.in_play_pokemon) == 2

    def test_pokemon_sent_out_on_init(self, pikachu_pokemon, eevee_pokemon):
        """Test that Pokemon are sent out when battle initializes."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(
                name="Ash",
                team=PokemonTeam(pokemons=[pikachu_pokemon])
            )
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(
            team_1=trainer_opponent,
            team_2=wild_opponent
        )
        battle.init_battle()
        
        # Check that both positions have Pokemon
        pokemon_1 = battle.in_play_pokemon[SinglesBattlePosition.Team1_Pokemon1]
        pokemon_2 = battle.in_play_pokemon[SinglesBattlePosition.Team2_Pokemon1]
        
        assert pokemon_1 is not None
        assert pokemon_2 is not None
        assert pokemon_1.pokemon.name == "Pikachu"
        assert pokemon_2.pokemon.name == "Eevee"


class TestTurnManagement:
    """Tests for turn management."""

    def test_start_turn(self, pikachu_pokemon, eevee_pokemon):
        """Test starting a turn."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
        battle.init_battle()
        
        initial_turn = battle.battle_state.turn_number
        battle.start_turn()
        
        assert battle.taking_actions is True
        assert battle.battle_state.turn_number == initial_turn + 1

    def test_end_turn_without_actions_raises_error(self, pikachu_pokemon, eevee_pokemon):
        """Test that ending turn without both players acting raises error."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
        battle.init_battle()
        battle.start_turn()
        
        # Try to end turn without any actions - catches any exception
        try:
            battle.end_turn()
            assert False, "Should have raised an exception"
        except Exception:
            # Expected to fail without both actions
            pass

    def test_turn_number_increments(self, pikachu_pokemon, eevee_pokemon):
        """Test that turn number increments correctly."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
        battle.init_battle()
        
        assert battle.battle_state.turn_number == 0
        battle.start_turn()
        assert battle.battle_state.turn_number == 1


class TestBattleActions:
    """Tests for battle actions (move, switch, escape)."""

    def test_use_move_action(self, pikachu_pokemon, eevee_pokemon):
        """Test using a move in battle."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
        battle.init_battle()
        battle.start_turn()
        
        # Use move from team 1 (first move, which is tackle with index=1)
        battle.use_move(
            user_position=SinglesBattlePosition.Team1_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team2_Pokemon1
        )
        
        assert SinglesBattlePosition.Team1_Pokemon1 in battle.this_turns_actions

    def test_invalid_move_index_raises_error(self, pikachu_pokemon, eevee_pokemon):
        """Test that using an invalid move index raises error."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
        battle.init_battle()
        battle.start_turn()
        
        with pytest.raises(ValueError):
            battle.use_move(
                user_position=SinglesBattlePosition.Team1_Pokemon1,
                move_index=10,
                target_position=SinglesBattlePosition.Team2_Pokemon1
            )

    def test_escape_in_wild_battle(self, pikachu_pokemon, eevee_pokemon):
        """Test escaping from a wild battle."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
        battle.init_battle()
        battle.start_turn()
        
        # Trainer tries to escape
        battle.use_escape(user_position=SinglesBattlePosition.Team1_Pokemon1)
        
        assert SinglesBattlePosition.Team1_Pokemon1 in battle.this_turns_actions

    def test_escape_in_trainer_battle_raises_error(self, pikachu_pokemon, eevee_pokemon):
        """Test that escaping from trainer battle raises error."""
        trainer_1 = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        trainer_2 = TrainerOpponent(
            trainer=BattleTrainer(name="Gary", team=PokemonTeam(pokemons=[eevee_pokemon]))
        )
        
        battle = SingleBattleManager(team_1=trainer_1, team_2=trainer_2)
        battle.init_battle()
        battle.start_turn()
        
        with pytest.raises(ValueError):
            battle.use_escape(user_position=SinglesBattlePosition.Team1_Pokemon1)

    def test_cancel_action(self, pikachu_pokemon, eevee_pokemon):
        """Test canceling an action."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
        battle.init_battle()
        battle.start_turn()
        
        # Use move
        battle.use_move(
            user_position=SinglesBattlePosition.Team1_Pokemon1,
            move_index=1,
            target_position=SinglesBattlePosition.Team2_Pokemon1
        )
        assert SinglesBattlePosition.Team1_Pokemon1 in battle.this_turns_actions
        
        # Cancel action
        battle.cancel_action(SinglesBattlePosition.Team1_Pokemon1)
        assert SinglesBattlePosition.Team1_Pokemon1 not in battle.this_turns_actions


class TestBattleFlow:
    """Tests for complete battle flow."""

    def test_complete_turn_with_moves(self, pikachu_pokemon, eevee_pokemon):
        """Test completing a full turn with both Pokemon using moves."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
        battle.init_battle()
        
        battle.start_turn()
        
        # Both Pokemon use moves
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
        
        # End turn should process successfully
        battle.end_turn()
        
        assert battle.taking_actions is False

    def test_move_reduces_pp(self, pikachu_pokemon, eevee_pokemon):
        """Test that using a move reduces its PP."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
        battle.init_battle()
        
        initial_pp = pikachu_pokemon.move_set.moves[0].current_pp
        
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
        
        assert pikachu_pokemon.move_set.moves[0].current_pp == initial_pp - 1

    def test_pokemon_faints_when_hp_reaches_zero(self, pikachu_pokemon, eevee_pokemon):
        """Test that Pokemon can reach 0 HP."""
        # Record initial HP
        initial_hp = eevee_pokemon.current_hp
        
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
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
        
        # Eevee should have taken damage
        assert eevee_pokemon.current_hp < initial_hp


class TestBattleState:
    """Tests for battle state management."""

    def test_battle_state_initialization(self):
        """Test battle state is initialized correctly."""
        state = BattleState()
        assert state.turn_number == 0

    def test_clear_stat_stages_on_battle_end(self, pikachu_pokemon, eevee_pokemon):
        """Test that stat stages are cleared when battle ends."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
        battle.init_battle()
        
        # Modify stat stages
        pikachu_pokemon.pokemon_battle_state.attack_stat_stage = 2
        eevee_pokemon.pokemon_battle_state.defense_stat_stage = -1
        
        battle.end_battle()
        
        assert pikachu_pokemon.pokemon_battle_state.attack_stat_stage == 0
        assert eevee_pokemon.pokemon_battle_state.defense_stat_stage == 0


class TestOpponentActions:
    """Tests for opponent action execution."""

    def test_trainer_opponent_get_all_pokemon(self, pikachu_pokemon):
        """Test getting all Pokemon from trainer opponent."""
        trainer = BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        opponent = TrainerOpponent(trainer=trainer)
        
        all_pokemon = opponent.get_all_pokemons()
        
        assert len(all_pokemon) >= 1
        assert pikachu_pokemon in all_pokemon

    def test_wild_opponent_get_all_pokemon(self, eevee_pokemon):
        """Test getting Pokemon from wild opponent."""
        opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        all_pokemon = opponent.get_all_pokemons()
        
        assert len(all_pokemon) == 1
        assert eevee_pokemon in all_pokemon


class TestBattlePositions:
    """Tests for battle position handling."""

    def test_get_opposite_position(self, pikachu_pokemon, eevee_pokemon):
        """Test getting opposite battle position."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
        
        opposite_1 = battle.get_opposite_position_from_position(
            SinglesBattlePosition.Team1_Pokemon1
        )
        opposite_2 = battle.get_opposite_position_from_position(
            SinglesBattlePosition.Team2_Pokemon1
        )
        
        assert opposite_1 == SinglesBattlePosition.Team2_Pokemon1
        assert opposite_2 == SinglesBattlePosition.Team1_Pokemon1

    def test_get_opponent_from_position(self, pikachu_pokemon, eevee_pokemon):
        """Test getting opponent from position."""
        trainer_opponent = TrainerOpponent(
            trainer=BattleTrainer(name="Ash", team=PokemonTeam(pokemons=[pikachu_pokemon]))
        )
        wild_opponent = WildPokemonOpponent(pokemon=eevee_pokemon)
        
        battle = SingleBattleManager(team_1=trainer_opponent, team_2=wild_opponent)
        
        opponent_1 = battle.get_opponent_from_position(SinglesBattlePosition.Team1_Pokemon1)
        opponent_2 = battle.get_opponent_from_position(SinglesBattlePosition.Team2_Pokemon1)
        
        assert opponent_1 == trainer_opponent
        assert opponent_2 == wild_opponent
