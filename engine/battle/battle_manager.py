# pick the move
# calculate the priority
# apply effects

from pydantic import BaseModel, Field
from typing import Optional, TypeVar, Generic
from abc import abstractmethod
from shared.pokemon.pokemon import Pokemon
from .battle_header import *

from .damage_calculator import calculate_damage, calculate_critical_hit

TPosition = TypeVar('TPosition', bound=BattlePosition)

class BattleManager(BaseModel, Generic[TPosition]):
    battle_config: BattleConfig = Field(default_factory=BattleConfig)
    battle_state: BattleState = Field(default_factory=BattleState)

    in_play_pokemon: dict[TPosition, Pokemon] = Field(default_factory=dict)
    this_turns_actions: dict[TPosition, Action] = Field(default_factory=dict)
    taking_actions: bool = Field(default=False)
    
    @abstractmethod
    def init_battle(self):
        pass

    @abstractmethod
    def send_out_first_pokemon(self):
        pass

    @abstractmethod
    def process_turn(self):
        pass

    # region Turn Actions
    def start_turn(self):
        self.taking_actions = True
        print(f"Turn {self.battle_state.turn_number + 1} start!")
        self.battle_state.turn_number += 1
        self.this_turns_actions.clear()

    def use_move(self, user_position: TPosition, move_index: int, target_position: TPosition):
        if self._has_actioned(user_position): return
        # check if move index is valid

        if move_index < 0 or move_index >= len(self.in_play_pokemon[user_position].move_set.moves):
            raise ValueError("Invalid move index.")

        user_pokemon = self.in_play_pokemon[user_position]
        move = user_pokemon.move_set.moves[move_index]

        if move.current_pp <= 0:
            raise ValueError(f"{user_pokemon.nickname} has no PP left for {move.name}!")

        self.this_turns_actions[user_position] = ActionMove(move=move, target_position=target_position)

    def switch_pokemon(self, user_position: TPosition, new_pokemon: Pokemon):
        if self._has_actioned(user_position): return
        # check if new_pokemon is in team and not fainted
        self.this_turns_actions[user_position] = ActionSwitch()

    def cancel_action(self, user_position: TPosition):
        if self._has_actioned(user_position):
            del self.this_turns_actions[user_position]

    def end_turn(self) -> bool:
        try:
            self.process_turn()
        except UnfinishedTurnException as e:
            print(e)
            return False
        self.taking_actions = False
        return True
    #endregion

    def end_battle(self):
        self.taking_actions = False
        self.battle_config = None
        self.battle_state = None
        self.in_play_pokemon.clear()
        self.this_turns_actions.clear()
        self.clear_non_standard_variables()
    
    @abstractmethod
    def clear_non_standard_variables(self):
        pass

    def get_taking_actions(self) -> bool:
        return self.taking_actions

    def _has_actioned(self, position: TPosition) -> bool:
        return position in self.this_turns_actions

    @property
    def get_in_play_pokemon(self) -> dict[TPosition, Pokemon]:
        return self.in_play_pokemon
    

class SingleBattleManager(BattleManager[SinglesBattlePosition]):
    team_1: Opponent
    team_2: Opponent

    def __init__(self, **data):
        super().__init__(**data)
        # Check if battle is against a wild pokemon
        if isinstance(self.team_1, TrainerOpponent) and isinstance(self.team_2, TrainerOpponent):
            self.battle_config.is_wild = False
        else:
            self.battle_config.is_wild = True

    def init_battle(self):
        self.send_out_first_pokemon()
        # activate any abilities or items that trigger on switch-in

    def send_out_first_pokemon(self):
        if isinstance(self.team_1, TrainerOpponent):
            pokemon_1 = self.team_1.trainer.team.pokemons[0]
            self.in_play_pokemon[SinglesBattlePosition.Team1_Pokemon1] = pokemon_1
            print(f"{self.team_1.trainer.name} sent out {pokemon_1.nickname}!")

        elif isinstance(self.team_1, WildPokemonOpponent):
            pokemon_1 = self.team_1.pokemon
            self.in_play_pokemon[SinglesBattlePosition.Team1_Pokemon1] = pokemon_1
            print(f"A wild {pokemon_1.nickname} appeared!")

        if isinstance(self.team_2, TrainerOpponent):
            pokemon_2 = self.team_2.trainer.team.pokemons[0]
            self.in_play_pokemon[SinglesBattlePosition.Team2_Pokemon1] = pokemon_2
            print(f"{self.team_2.trainer.name} sent out {pokemon_2.nickname}!")
        elif isinstance(self.team_2, WildPokemonOpponent):
            pokemon_2 = self.team_2.pokemon
            self.in_play_pokemon[SinglesBattlePosition.Team2_Pokemon1] = pokemon_2
            print(f"A wild {pokemon_2.nickname} appeared!")

    def process_turn(self):
        # Placeholder for turn processing logic
        # this will require the moves to already be passed in from both sides

        if len(self.this_turns_actions) != 2:
            # get a list of missing positions
            missing_positions = [pos for pos in SinglesBattlePosition if pos not in self.this_turns_actions]
            raise UnfinishedTurnException("Both players must select an action before processing the turn. Missing actions for positions: " + ", ".join([str(pos) for pos in missing_positions]))
    
        print(f"Processing turn {self.battle_state.turn_number}...")
        # For now, just print out the actions
        # print (f"Actions this turn: {self.this_turns_actions}")

        # Determine action order based on move priority and speed


        # For the moment we will just process in order that they were added
        for position, action in self.this_turns_actions.items():
            if isinstance(action, ActionMove):
                user_pokemon = self.in_play_pokemon[position]
                target_position = action.target_position
                target_pokemon = self.in_play_pokemon[target_position]

                is_critical = calculate_critical_hit(user_pokemon)

                damage = calculate_damage(
                    attacking_pokemon=user_pokemon,
                    defending_pokemon=target_pokemon,
                    move=action.move,
                    critical_hit=is_critical,
                    battle_state=self.battle_state
                )

                # show the amount of health the target has before applying damage
                print (f"{target_pokemon.nickname} has {target_pokemon.current_hp}/{target_pokemon.max_hp} HP before the attack.")
                target_pokemon.current_hp -= damage
                print (f"{user_pokemon.nickname} used {action.move.base_move.name} on {target_pokemon.nickname} dealing {damage} damage!")
                # print if the hit was critical
                if is_critical:
                    print("A critical hit!")
                print (f"{target_pokemon.nickname} has {target_pokemon.current_hp}/{target_pokemon.max_hp} HP remaining.")

                if target_pokemon.current_hp <= 0:
                    target_pokemon.current_hp = 0
                    print(f"{target_pokemon.nickname} fainted!")

    def clear_non_standard_variables(self):
        self.team_1 = None
        self.team_2 = None



# This is going to be more of a pain with what it has to handle
class DoubleBattleManager(BattleManager[DoublesBattlePosition]):
    team_1: Opponent
    team_1_2: Optional[Opponent] = Field(default=None)
    team_2: Opponent
    team_2_2: Optional[Opponent] = Field(default=None)
