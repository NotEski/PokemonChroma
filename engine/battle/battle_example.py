# battle example

from engine.pokemon.repository import pokemon_repository, ability_repository, move_repository, item_repository

from engine.battle.battle_manager import BattleManager
from shared.battle.position_manager import BattlePosition
from shared.battle.opponent import TrainerOpponent, WildPokemonOpponent
from shared.pokemon.pokemon import Pokemon, PokemonTeam
from shared.trainer.trainer import Trainer
from shared.pokemon.moves import MoveSet


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
    ashes_team = PokemonTeam(pokemons=[ashes_pickachu])


    trainer=Trainer(name="Ash", team=ashes_team)
    wild_pokemon=Pokemon(pokemon=pokemon_repository.get("eevee"), level=1, move_set=eevee_moveset)
    opponent_1 = TrainerOpponent(trainer=trainer)
    opponent_2 = WildPokemonOpponent(pokemon=wild_pokemon)

    battle_manager = BattleManager(teams=[opponent_1, opponent_2])
    

    battle_manager.init_battle()

    battle_manager.start_turn()

    quick_attack_action = ashes_pickachu.create_move_action(
        move="tackle",
        target_position=BattlePosition(team_id=2, pokemon_index=1)
    )
    wild_pokemon_action = wild_pokemon.create_move_action(
        move="quick_attack",
        target_position=BattlePosition(team_id=1, pokemon_index=1)
    )

    battle_manager.submit_action(quick_attack_action)
    battle_manager.submit_action(wild_pokemon_action)



    battle_manager.end_turn()

    print ("\n--- Turn 1 ended ---\n")

    battle_manager.start_turn()

    quick_attack_action_2 = ashes_pickachu.create_move_action(
        move="quick_attack",
        target_position=BattlePosition(team_id=2, pokemon_index=1)
    )
    wild_pokemon_action_2 = wild_pokemon.create_move_action(
        move="quick_attack",
        target_position=BattlePosition(team_id=1, pokemon_index=1)
    )

    battle_manager.submit_action(quick_attack_action_2)
    battle_manager.submit_action(wild_pokemon_action_2)

    battle_manager.end_turn()

    print ("\nBattle ended.\n\n")

    battle_manager.battle_log.print_log()