# battle example

from engine.pokemon.repository import pokemon_repository, ability_repository, move_repository, item_repository

from engine.battle.battle_manager import TrainerOpponent, WildPokemonOpponent, SingleBattleManager, SinglesBattlePosition
from engine.battle.opponent import TrainerOpponent, WildPokemonOpponent
from shared.pokemon.pokemon import Pokemon
from shared.pokemon.trainer import BattleTrainer
from shared.pokemon.team import Team
from shared.pokemon.move import MoveSet


def moveset_from_names(move_names: list[str]) -> MoveSet:
    moves = []
    for name in move_names:
        move = move_repository.get(name)
        if move:
            moves.append(move)
    return MoveSet(moves=moves)


def pickachu_eevee_battle_example():

    pikachu_moveset = moveset_from_names(["tackle", "growl", "volt_tackle", "quick_attack"])
    eevee_moveset = moveset_from_names(["tackle", "tail_whip", "bite", "quick_attack"])

    ashes_pickachu = Pokemon(pokemon=pokemon_repository.get("pikachu"), level=15, move_set=pikachu_moveset)
    ashes_pickachu.nickname = "Pika"
    ashes_pickachu.held_item = item_repository.get("light_ball")
    ashes_team = Team(pokemons=[ashes_pickachu])


    trainer=BattleTrainer(name="Ash", team=ashes_team)
    pokemon=Pokemon(pokemon=pokemon_repository.get("eevee"), level=10, move_set=eevee_moveset)
    opponent_1 = TrainerOpponent(trainer=trainer)
    opponent_2 = WildPokemonOpponent(pokemon=pokemon)

    battle_manager = SingleBattleManager(team_1=opponent_1, team_2=opponent_2)

    battle_manager.init_battle()


    battle_manager.start_turn()

    battle_manager.use_move(
        user_position=SinglesBattlePosition.Team1_Pokemon1,
        move_index=33,
        target_position=SinglesBattlePosition.Team2_Pokemon1
    )

    battle_manager.use_move(
        move_index=98,
        user_position=SinglesBattlePosition.Team2_Pokemon1,
        target_position=SinglesBattlePosition.Team1_Pokemon1
    )

    battle_manager.end_turn()

    battle_manager.start_turn()

    #battle_manager.use_escape()

    battle_manager.use_move(
        user_position=SinglesBattlePosition.Team1_Pokemon1,
        move_index=33,
        target_position=SinglesBattlePosition.Team2_Pokemon1
    )

    battle_manager.use_move(
        user_position=SinglesBattlePosition.Team2_Pokemon1,
        move_index=33,
        target_position=SinglesBattlePosition.Team1_Pokemon1
    )
    battle_manager.end_turn()

    print ("\nBattle ended.\n\n")
