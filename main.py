from engine.rendering.window import game_window
from engine.battle.battle_manager import TrainerOpponent, WildPokemonOpponent, SingleBattleManager, SinglesBattlePosition
from engine.battle.opponent import TrainerOpponent, WildPokemonOpponent
from shared.pokemon.pokemon import Pokemon, PokemonBase
from shared.pokemon.types import PokemonType
from shared.pokemon.trainer import BattleTrainer
from shared.pokemon.team import Team
from shared.pokemon.move import MoveSet, MoveCategory, BaseMove

from engine.pokemon.repositry_generator import generate_pokemon_repository_from_json, generate_abilities_repository_from_json
from engine.pokemon.repository import pokemon_repository
import os

def main():
    game_window()


os.listdir("data/pokemon")
# Generate repositories from JSON data files
for subdir, _, files in os.walk("data/pokemon"):
    file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.json')]
    generate_pokemon_repository_from_json(file_paths)

print ("\nGenerated Pokemon Repository with the following Pokemon:\n")
for pokemon in pokemon_repository.list_pokemons().values():
    print (f"- {pokemon.name} (#{pokemon.pokedex_number})")


tackle = BaseMove(
    name="Tackle",
    type=PokemonType.NORMAL,
    power=40,
    accuracy=100,
    pp=35,
    category=MoveCategory.PHYSICAL
)
default_move_set = MoveSet(moves=[tackle])

ashes_pickachu = Pokemon(pokemon=pokemon_repository.get_pokemon("pikachu"), level=15, move_set=default_move_set)
ashes_team = Team(pokemons=[ashes_pickachu])

trainer=BattleTrainer(name="Ash", team=ashes_team)
pokemon=Pokemon(pokemon=pokemon_repository.get_pokemon("eevee"), level=10, move_set=default_move_set)

opponent_1 = TrainerOpponent(trainer=trainer)
opponent_2 = WildPokemonOpponent(pokemon=pokemon)

battle_manager = SingleBattleManager(team_1=opponent_1, team_2=opponent_2)

battle_manager.init_battle()

# for _ in range(3):

battle_manager.start_turn()

battle_manager.use_move(
    user_position=SinglesBattlePosition.Team1_Pokemon1,
    move_index=0,
    target_position=SinglesBattlePosition.Team2_Pokemon1
)

battle_manager.use_move(
    move_index=0,
    user_position=SinglesBattlePosition.Team2_Pokemon1,
    target_position=SinglesBattlePosition.Team1_Pokemon1
)

battle_manager.end_turn()

battle_manager.start_turn()

#battle_manager.use_escape()

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







if __name__ == "__main__":
    main()