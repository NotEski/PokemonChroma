# pick the move
# calculate the priority
# apply effects

from pydantic import BaseModel, Field
from typing import Optional, TypeVar, Generic
from abc import abstractmethod
from shared.pokemon.pokemon import Pokemon, PokemonBattleState
from shared.battle.battle_header import *
from shared.battle.battle_logs import BattleLogManager
from shared.battle.type_effectiveness import EffectivenessLevel, effectiveness_message, get_attack_multiplier, get_effectiveness_level
from shared.battle.opponent import Opponent, TrainerOpponent, WildPokemonOpponent

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

    battle_log: BattleLogManager = Field(default_factory=BattleLogManager)

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
        self.battle_log.turn_start(turn_number=self.battle_state.turn_number)

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

        if move_index not in self.in_play_pokemon[user_position].move_set.moves:
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
                self.battle_log.pokemon_switch_in(
                    switched_in_pokemon=new_pokemon,
                    posistion=position,
                    trainer=self.trainers[position.value // 2]
                )

                # TODO activate any abilities or items that trigger on switch-in

    def procress_priority_turn_order(self, turn_order: list[TPosition]) -> list[TPosition]:
        priority_moves: dict[TPosition, int] = {}

        for position in turn_order:
            action = self.this_turns_actions[position]
            if isinstance(action, ActionMove):
                move = action.move.base_move
                priority = move.priority
                priority_moves[position] = priority
        # Sort by priority first (higher goes first), then by speed (handled in turn_order)
        sorted_by_priority = sorted(priority_moves.keys(), key=lambda item: priority_moves[item], reverse=True)

        #first check if there are any ties in priority
        final_sorted_order: list[TPosition] = []
        for i in range(len(sorted_by_priority)):
            current_position = sorted_by_priority[i]
            current_priority = priority_moves[current_position]

            tied_positions = [current_position]

            # check for ties
            for j in range(i + 1, len(sorted_by_priority)):
                next_position = sorted_by_priority[j]
                next_priority = priority_moves[next_position]
                if next_priority == current_priority:
                    tied_positions.append(next_position)
                else:
                    break
            if len(tied_positions) > 1:
                # maintain original turn order for tied positions
                tied_positions_sorted = sorted(tied_positions, key=lambda item: turn_order.index(item))
                final_sorted_order.extend(tied_positions_sorted)
            else:
                final_sorted_order.append(current_position)
        return final_sorted_order

    def process_move(self, turn_order: list[TPosition]):
        # process priority move order
        priority_order = self.procress_priority_turn_order(turn_order)

        for position in priority_order:
            description_list = []

            action = self.this_turns_actions[position]
            if not isinstance(action, ActionMove): continue

            user_pokemon = self.in_play_pokemon[position]
            target_position = action.target_position
            target_pokemon = self.in_play_pokemon[target_position]

            description_list.append(f"{user_pokemon.nickname} used {action.move.base_move.name}!")

            is_critical = calculate_critical_hit(user_pokemon)
            used_move = action.move.base_move


            if used_move.accuracy is None:
                accuracy_check = 100.0
            else:
                accuracy_check = calculate_accuracy(used_move, user_pokemon, target_pokemon, self.battle_state)
            
            if not calculate_accuracy_hit(accuracy_check):
                description_list.append(f"But it missed!")
                damage = 0
                effectiveness_level = EffectivenessLevel.NORMAL_EFFECTIVE

            else:

                effectiveness_multiplier = get_attack_multiplier(used_move.type, target_pokemon.pokemon.types)
                effectiveness_level = get_effectiveness_level(effectiveness_multiplier)
                

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
                    description_list.append(effectiveness_message(EffectivenessLevel.NO_EFFECT))
                    continue
                else:
                    description_list.append(effectiveness_message(effectiveness_level))


                # show the amount of health the target has before applying damage
                # description_list.append(f"{target_pokemon.nickname} has {target_pokemon.current_hp}/{target_pokemon.max_hp} HP before the attack.")

                target_pokemon.current_hp -= damage

                description_list.append(f"It dealt {damage} damage!")
                # print if the hit was critical
                if is_critical:
                    description_list.append("A critical hit!")
                
                


                description_list.append(f"DEBUG: {user_pokemon.nickname} used {used_move.name} on {target_pokemon.nickname} dealing {damage} damage.")

            description = "\n".join(description_list)


            self.battle_log.move_used(
                move_name=used_move,
                user_pokemon=user_pokemon,
                target_pokemon=[target_pokemon],
                damage_dealt=damage,
                is_critical=is_critical,
                status_condition_applied=None,
                move_effectiveness=effectiveness_level,
                description=description
            )

            if target_pokemon.current_hp <= 0:
                target_pokemon.current_hp = 0
                description_list.append(f"{target_pokemon.nickname} fainted!")


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
                    self.battle_log.battle_end(
                        winning_trainer=None,
                        description=f"{escaping_pokemon.nickname} successfully escaped!"
                    )
                    self.end_battle()
                    return
                else:
                    print(f"{escaping_pokemon.nickname} couldn't escape!")


                

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
