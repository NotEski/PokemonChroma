from engine.rendering.window import game_window
from engine.battle.battle_manager import TrainerOpponent, WildPokemonOpponent, SingleBattleManager, SinglesBattlePosition
from shared.pokemon.pokemon import Pokemon, PokemonBase
from shared.pokemon.types import PokemonType
from shared.pokemon.trainer import BattleTrainer
from shared.pokemon.team import Team
from shared.pokemon.move import MoveSet, MoveCategory, BaseMove
from engine.battle.type_effectiveness import get_weaknesses

def main():
    game_window()



pickachu = PokemonBase(
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
eevee = PokemonBase(
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

tackle = BaseMove(
    name="Tackle",
    type=PokemonType.NORMAL,
    power=40,
    accuracy=100,
    pp=35,
    category=MoveCategory.PHYSICAL
)
default_move_set = MoveSet(moves=[tackle])

ashes_pickachu = Pokemon(pokemon=pickachu, level=15, move_set=default_move_set)
ashes_team = Team(pokemons=[ashes_pickachu])

trainer=BattleTrainer(name="Ash", team=ashes_team)
pokemon=Pokemon(pokemon=eevee, level=10, move_set=default_move_set)

opponent_1 = TrainerOpponent(trainer=trainer)
opponent_2 = WildPokemonOpponent(pokemon=pokemon)

battle_manager = SingleBattleManager(team_1=opponent_1, team_2=opponent_2)

battle_manager.init_battle()

for _ in range(3):
    print ("\n--- New Turn ---\n")
    battle_manager.start_turn()

    battle_manager.use_move(
        user_position=SinglesBattlePosition.Team1_Pokemon1,
        move_index=0,
        target_position=SinglesBattlePosition.Team2_Pokemon1
    )

    battle_manager.use_move(
        user_position=SinglesBattlePosition.Team2_Pokemon1,
        move_index=0,
        target_position=SinglesBattlePosition.Team1_Pokemon1
    )

    battle_manager.end_turn()


print ("\nBattle ended.\n\n")
print (get_weaknesses(PokemonType.FIRE))







if __name__ == "__main__":
    main()