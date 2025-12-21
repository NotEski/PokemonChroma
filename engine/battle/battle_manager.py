# pick the move
# calculate the priority
# apply effects

from pydantic import BaseModel, Field
from typing import Optional, TypeVar, Generic
from abc import abstractmethod
from shared.pokemon.pokemon import Pokemon, PokemonBattleState
from .battle_header import *
from .battle_logs import BattleLogEntry, BattleLogType
from .opponent import Opponent, TrainerOpponent, WildPokemonOpponent

from .damage_calculator import calculate_damage, calculate_critical_hit
from .speed_calculator import calculate_speed
from .escape_calculator import calculate_escape_success
from .calculate_accuracy import calculate_accuracy, calculate_accuracy_hit

TPosition = TypeVar('TPosition', bound=BattlePosition)



class BattleManager(BaseModel, Generic[TPosition]):
    battle_config: BattleConfig = Field(default_factory=BattleConfig)
    battle_state: BattleState = Field(default_factory=BattleState)

    in_play_pokemon: dict[TPosition, Pokemon] = Field(default_factory=dict)
    this_turns_actions: dict[TPosition, Action] = Field(default_factory=dict)
    taking_actions: bool = Field(default=False)

    @abstractmethod
    def get_opponent_from_position(self, position: TPosition) -> Opponent:
        pass

    def clear_pokemon_stat_stages(self, pokemon: Pokemon):
        pokemon.pokemon_battle_state = PokemonBattleState()
    
    @abstractmethod
    def clear_all_stat_stages(self):
        # Reset stat stages for all pokemon that are associated with the battle for the start of battle
        pass
    
    @abstractmethod
    def init_battle(self):
        pass

    @abstractmethod
    def send_out_first_pokemon(self):
        pass

    # region Turn Actions
    def start_turn(self):
        self.taking_actions = True
        print(f"Turn {self.battle_state.turn_number + 1} start!")
        self.battle_state.turn_number += 1
        self.this_turns_actions.clear()

    def use_escape(self, user_position: TPosition):
        if self._has_actioned(user_position): return
        if self.battle_config.is_wild is False:
            raise ValueError("Cannot escape from trainer battles!")
        
        opponent_escaping = self.get_opponent_from_position(user_position)
        opponent_escaping.escape_attempts += 1
        self.this_turns_actions[user_position] = ActionEscape(escape_attempts=opponent_escaping.escape_attempts)

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
        self.this_turns_actions[user_position] = ActionSwitch(switch_in_pokemon=new_pokemon)

    def cancel_action(self, user_position: TPosition):
        if self._has_actioned(user_position):
            del self.this_turns_actions[user_position]


    def get_turn_orders(self) -> list[TPosition]:
        # Placeholder for turn order calculation logic
        # For now, just return the positions in the order they acted

        speed_dict: dict[TPosition, int] = {}

        for position in self.this_turns_actions.keys():
            pokemon = self.in_play_pokemon[position]
            speed = calculate_speed(pokemon)
            speed_dict[position] = speed
        
        # Sort positions by speed in descending order
        sorted_positions = sorted(speed_dict.items(), key=lambda item: item[1], reverse=True)

        return [position for position, speed in sorted_positions]

    def end_turn(self):        
        if len(self.this_turns_actions) != 2:
            # get a list of missing positions
            missing_positions = [pos for pos in TPosition if pos not in self.this_turns_actions]
            raise UnfinishedTurnException("Both players must select an action before processing the turn. Missing actions for positions: " + ", ".join([str(pos) for pos in missing_positions]))
    
        print(f"Processing turn {self.battle_state.turn_number}...")    


        # get each pokemons speed and determine order of actions
        turn_order = self.get_turn_orders()



        try:
            # --- Process Action Order ---
            


            # Quick Claw/Custap Berry announce their effects if applicable
            
            # If wild battle, display "Got away safely!"/"Can't escape!" message; if trainer battle, forfeit and fade out
            self.process_escape()

            if not self.taking_actions:
                return

            # Handle switches
            self.switch_pokemon()
            
            # Handle rotation
            # NOTE only applicable in rotation battles which are not implemented yet
            
            # Item usage (in-game only)
            self.process_item_use()
            
            # Mega Evolution, Ultra Burst
            
            # Focus Punch, Beak Blast, Shell Trap charging effects
            
            # Move usage in order
            self.process_move(turn_order)
            
            # End of turn effects

            pass
        except UnfinishedTurnException as e:
            print(e)
            return
        self.taking_actions = False
        return
    #endregion

    #region Process Actions
    @abstractmethod
    def process_escape(self):
        pass

    def switch_pokemon(self):
        # Process all switch actions
        for position, action in self.this_turns_actions.items():
            if isinstance(action, ActionSwitch):
                old_pokemon = self.in_play_pokemon[position]
                new_pokemon = action.switch_in_pokemon
                self.in_play_pokemon[position] = new_pokemon
                print(f"{old_pokemon.nickname} was switched out for {new_pokemon.nickname}!")

                # TODO activate any abilities or items that trigger on switch-in

    @abstractmethod
    def process_move(self):
        pass

    @abstractmethod
    def process_item_use(self):
        pass
    #endregion


    def end_battle(self):
        self.clear_all_stat_stages()

        self.this_turns_actions.clear()
        
        self.clear_non_standard_variables()

        self.in_play_pokemon.clear()

        self.taking_actions = False
        self.battle_config = None
        self.battle_state = None
        
        
        
        

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
    
    def get_opponent_from_position(self, position: SinglesBattlePosition) -> Opponent:
        if position == SinglesBattlePosition.Team1_Pokemon1:
            return self.team_1
        elif position == SinglesBattlePosition.Team2_Pokemon1:
            return self.team_2
        else:
            raise ValueError("Invalid position for singles battle.")

    def get_opposite_position_from_position(self, position: SinglesBattlePosition) -> SinglesBattlePosition:
        if position == SinglesBattlePosition.Team1_Pokemon1:
            return SinglesBattlePosition.Team2_Pokemon1
        elif position == SinglesBattlePosition.Team2_Pokemon1:
            return SinglesBattlePosition.Team1_Pokemon1
        else:
            raise ValueError("Invalid position for singles battle.")

    def clear_all_stat_stages(self):
        for pokemon in self.team_1.get_all_pokemons() + self.team_2.get_all_pokemons():
            self.clear_pokemon_stat_stages(pokemon)

    def init_battle(self):
        self.clear_all_stat_stages()
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

    def process_escape(self):
        for position, action in self.this_turns_actions.items():
            if isinstance(action, ActionEscape):
                escaping_pokemon = self.in_play_pokemon[position]
                enemy_pokemon = self.in_play_pokemon[self.get_opposite_position_from_position(position)]
                
                success = calculate_escape_success(escaping_pokemon, enemy_pokemon, action.escape_attempts)
                if success:
                    print(f"{escaping_pokemon.nickname} got away safely!")
                    self.end_battle()
                    return
                else:
                    print(f"{escaping_pokemon.nickname} couldn't escape!")

    def process_move(self, turn_order: list[SinglesBattlePosition]):
        for position in turn_order:
            action = self.this_turns_actions[position]
            if isinstance(action, ActionMove):
                user_pokemon = self.in_play_pokemon[position]
                target_position = action.target_position
                target_pokemon = self.in_play_pokemon[target_position]

                is_critical = calculate_critical_hit(user_pokemon)
                used_move = action.move.base_move


                if used_move.accuracy is None:
                    print (used_move.name + " never misses!")
                    accuracy_check = 100.0
                else:
                    accuracy_check = calculate_accuracy(used_move, user_pokemon, target_pokemon, self.battle_state)
                
                    if not calculate_accuracy_hit(accuracy_check):
                        print (f"{user_pokemon.nickname} used {used_move.name}, but it missed!")
                        continue


                damage = calculate_damage(
                    attacking_pokemon=user_pokemon,
                    defending_pokemon=target_pokemon,
                    move=used_move,
                    critical_hit=is_critical,
                    battle_state=self.battle_state
                )

                action.move.current_pp -= 1

                # if damage is 0, the move had no effect
                if damage <= 0:
                    print (f"{user_pokemon.nickname} used {action.move.base_move.name}, but it had no effect on {target_pokemon.nickname}!")
                    continue


                # show the amount of health the target has before applying damage
                print (f"{target_pokemon.nickname} has {target_pokemon.current_hp}/{target_pokemon.max_hp} HP before the attack.")
                target_pokemon.current_hp -= damage
                print (f"{user_pokemon.nickname} used {action.move.base_move.name} on {target_pokemon.nickname} dealing {damage} damage!")
                # print if the hit was critical
                if is_critical:
                    print("A critical hit!")
                print (f"{target_pokemon.nickname} has {target_pokemon.current_hp}/{target_pokemon.max_hp} HP remaining.")

                BattleLogEntry(
                    turn_number=self.battle_state.turn_number,
                    log_type=BattleLogType.MOVE_USED,
                    description=f"{user_pokemon.nickname} used {action.move.base_move.name} on {target_pokemon.nickname} dealing {damage} damage."
                )

                if target_pokemon.current_hp <= 0:
                    target_pokemon.current_hp = 0
                    print(f"{target_pokemon.nickname} fainted!")
                

    def process_item_use(self):
        pass

    def clear_non_standard_variables(self):
        self.team_1 = None
        self.team_2 = None

    
        
    



# This is going to be more of a pain with what it has to handle
class DoubleBattleManager(BattleManager[DoublesBattlePosition]):
    team_1: Opponent
    team_1_2: Optional[Opponent] = Field(default=None)
    team_2: Opponent
    team_2_2: Optional[Opponent] = Field(default=None)
