from engine.rendering.window import game_window
from engine.battle.battle_manager import TrainerOpponent, WildPokemonOpponent, SingleBattleManager, SinglesBattlePosition
from engine.battle.opponent import TrainerOpponent, WildPokemonOpponent
from shared.pokemon.pokemon import Pokemon, PokemonBase
from shared.pokemon.types import PokemonType
from shared.pokemon.trainer import BattleTrainer
from shared.pokemon.team import Team
from shared.pokemon.move import MoveSet, MoveCategory, BaseMove
from engine.battle.type_effectiveness import effectiveness

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


from shared.pokemon.pokeball import Pokeball

pokeball =  Pokeball(
    name="Pokeball",
    catch_rate_modifier=1.0
)
ultraball =  Pokeball(
    name="Ultraball",
    catch_rate_modifier=2.0
)

ultrabeastball =  Pokeball(
    name="Ultrabeast Ball",
    catch_rate_modifier=4.0,
    special_effect="higher catch rate for Ultra Beasts"
)

from engine.battle.catch_calculator import calculate_catch_probability, catch_attempt
catch_chance_pokeball = calculate_catch_probability(pokemon=pokemon, pokeball=pokeball)
catch_chance_ultraball = calculate_catch_probability(pokemon=pokemon, pokeball=ultraball)
catch_chance_ultrabeastball = calculate_catch_probability(pokemon=pokemon, pokeball=ultrabeastball)

print (f"\nCatch chance with Pokéball: {catch_chance_pokeball}/65536 each shake")
catch_attempt(pokemon=pokemon, pokeball=pokeball)
print (f"\nCatch chance with Ultra Ball: {catch_chance_ultraball}/65536 each shake")
catch_attempt(pokemon=pokemon, pokeball=ultraball)
print (f"\nCatch chance with Ultra Beast Ball: {catch_chance_ultrabeastball}/65536 each shake")
catch_attempt(pokemon=pokemon, pokeball=ultrabeastball)    




if __name__ == "__main__":
    main()