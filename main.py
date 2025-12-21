from engine.battle.battle_manager import TrainerOpponent, WildPokemonOpponent, SingleBattleManager, SinglesBattlePosition
from engine.battle.opponent import TrainerOpponent, WildPokemonOpponent
from shared.pokemon.pokemon import Pokemon
from shared.pokemon.trainer import BattleTrainer
from shared.pokemon.team import Team
from shared.pokemon.move import MoveSet

from engine.pokemon.repositry_generator import generate_pokemon_repository_from_json, generate_abilities_repository_from_json, generate_move_repository_from_json
from engine.pokemon.repository import pokemon_repository, ability_repository, move_repository
import os

from direct.showbase.ShowBase import ShowBase


class Application(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)


# Generate Abilities Repository
abilities_file_path = "data/abilities.json"
generate_abilities_repository_from_json(abilities_file_path)

print ("\nGenerated Abilities Repository with the following Abilities:\n")
for index, ability in enumerate(ability_repository.abilities.values()):
    print (f"- {ability.name} : {ability.description}")
    if index >= 10:
        print ("...")
        break
print ("\n")


# Generate Moves Repository
moves_folder_path = "data/moves"
for subdir, _, files in os.walk(moves_folder_path):
    file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.json')]
    for file_path in file_paths:
        print (f"Generating moves from file: {file_path}")
        generate_move_repository_from_json(file_path)
        
        


# Generate Pokemon Repository
pokemon_folder_path = "data/pokemon"
# Generate repositories from JSON data files
for subdir, _, files in os.walk(pokemon_folder_path):
    file_paths = [os.path.join(subdir, file) for file in files if file.endswith('.json')]
    generate_pokemon_repository_from_json(file_paths)

print ("\nGenerated Pokemon Repository with the following Pokemon:\n")
for index, pokemon in enumerate(pokemon_repository.list_pokemons().values()):
    print (f"- {pokemon.name} (#{pokemon.pokedex_number})")
    if index >= 10:
        print ("...")
        break
print ("\n")



tackle = move_repository.get_move("tackle")
growl = move_repository.get_move("growl")


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






app = Application()
app.run()