# pick the move
# calculate the priority
# apply effects

from typing import TypeVar, Generic
from pydantic import BaseModel, Field
from abc import abstractmethod
from shared.battle.battle_actions import BattleAction, SwitchAction, MoveAction, EscapeAction
from shared.pokemon.pokemon import BattleMon, StatStages
from shared.battle.battle_header import *
from shared.battle.battle_logs import BattleLogManager
from shared.battle.type_effectiveness import EffectivenessLevel, effectiveness_message, get_attack_multiplier, get_effectiveness_level
from shared.battle.opponent import Opponent, TrainerOpponent
from shared.battle.position_manager import BattlePosition
from shared.pokemon.status_conditions import StatusCondition
from shared.pokemon.types import PokemonType

from .damage_calculator import calculate_damage, calculate_critical_hit
from .speed_calculator import calculate_speed
from .escape_calculator import calculate_escape_success
from .calculate_accuracy import calculate_accuracy, calculate_accuracy_hit


class BattleManager(BaseModel):
    position_manager: BattlePositionManager = Field(default_factory=BattlePositionManager)
    battle_config: BattleConfig = Field(default_factory=BattleConfig)
    battle_state: BattleState = Field(default_factory=BattleState)
    taking_actions: bool = Field(default=False)
    battle_log: BattleLogManager = Field(default_factory=BattleLogManager)
    active_battle: bool = Field(default=True)
    teams: dict[int, Opponent]|List[Opponent] = Field(default_factory=dict)


    def __init__(self, **data):
        super().__init__(**data)
        if isinstance(self.teams, list):
            teams_dict = {}
            for index, team in enumerate(self.teams):
                teams_dict[index + 1] = team
            self.teams = teams_dict
        elif isinstance(self.teams, dict):
            # validate keys are 1, 2, ...
            len_keys = len(self.teams.keys())
            for i in range(1, len_keys + 1):
                if i not in self.teams:
                    raise ValueError("Teams dictionary keys must be sequential integers starting from 1.")
                
        if len(self.teams) != 2: # only support 2 teams for now. probably will only ever need 2 teams
            raise ValueError("There must be exactly 2 teams for a battle.")
                
        self.position_manager.teams_count = len(self.teams)

        if self.battle_config.battle_type == BattleType.SINGLE:
            self.position_manager.pokemon_per_team = 1
        elif self.battle_config.battle_type == BattleType.DOUBLE:
            self.position_manager.pokemon_per_team = 2
        elif self.battle_config.battle_type == BattleType.TRIPLE:
            self.position_manager.pokemon_per_team = 3


    # region Abstract Methods
    def get_opponent_from_position(self, position: BattlePosition) -> Opponent:
        return self.teams[position.team_id]
    
    def get_opposite_position_from_position(self, position: BattlePosition) -> BattlePosition:
        return self.position_manager.get_direct_opponent_position(position)

    def clear_all_stat_stages(self):
        for pokemon in self.teams[1].get_all_battlemons() + self.teams[2].get_all_battlemons():
            self.clear_pokemon_stat_stages(pokemon)
    
    def init_battle(self):
        self.clear_all_stat_stages()

        for team_id in range(1, self.position_manager.teams_count + 1):
            for pokemon_index in range(1, self.position_manager.pokemon_per_team + 1):
                self.position_manager.register_pokemon(
                    pokemon=self.teams[team_id].get_active_battlemon(),
                    team_index=team_id,
                    pokemon_index=pokemon_index
                )

    def process_escape(self):
        for position, action in self.position_manager.position_actions().items():
            if isinstance(action, EscapeAction):
                escaping_pokemon = self.position_manager.get_pokemon_at_position(position)
                enemy_pokemon = self.position_manager.get_pokemon_at_position(self.get_opposite_position_from_position(position))
                
                success = calculate_escape_success(escaping_pokemon, enemy_pokemon, action.escape_attempts)
                if success:
                    self.battle_log.battle_end(
                        winning_trainer=None,
                        description=f"{escaping_pokemon.nickname} successfully escaped!"
                    )
                    self.end_battle()
                    return
                else:
                    self.battle_log.misc(
                        escaping_pokemon=escaping_pokemon,
                        description=f"{escaping_pokemon.nickname} failed to escape!"
                    )

    

    def clear_non_standard_variables(self):
        self.teams = {}
    # endregion

    # region Utility Methods
    def clear_pokemon_stat_stages(self, pokemon: BattleMon):
        pokemon.stat_stages = StatStages()

    def _has_actioned(self, position: BattlePosition) -> bool:
        return self.position_manager.get_position_action(position) is not None

    def get_taking_actions(self) -> bool:
        return self.taking_actions
    # endregion

    # region Action Submission
    def submit_action(self, action: BattleAction):
        if not self.taking_actions:
            raise ValueError("Not currently taking actions.")
        if isinstance(action, MoveAction):
            self.use_move(
                user_position=action.position,
                move_index=action.move_index,
                target_position=action.target_position
            )
        elif isinstance(action, SwitchAction):
            self.switch_pokemon(
                user_position=action.position,
                new_pokemon=action.switch_in_pokemon
            )
        else:
            raise ValueError("Invalid action type submitted.")
        
        self.position_manager.add_position_action(action.position, action)

    def use_escape(self, user_position: BattlePosition):
        if self._has_actioned(user_position): return
        if self.battle_config.is_wild is False:
            raise ValueError("Cannot escape from trainer battles!")
        
        opponent_escaping = self.get_opponent_from_position(user_position)
        opponent_escaping.escape_attempts += 1
        self.position_manager.add_position_action(user_position, EscapeAction(position=user_position, escape_attempts=opponent_escaping.escape_attempts))

    def use_move(self, user_position: BattlePosition, move_index: int, target_position: BattlePosition):
        if self._has_actioned(user_position): return

        if not isinstance(move_index, int):
            raise ValueError("Invalid move type.")

        if move_index not in self.position_manager.get_pokemon_at_position(user_position).move_set.moves:
            raise ValueError("Invalid move index.")

        user_pokemon = self.position_manager.get_pokemon_at_position(user_position)
        move = user_pokemon.move_set.moves[move_index]

        if move.current_pp <= 0:
            raise ValueError(f"{user_pokemon.nickname} has no PP left for {move.name}!")

        self.position_manager.add_position_action(user_position, MoveAction(move_index=move_index, position=user_position, target_position=target_position))

    def switch_pokemon(self, user_position: BattlePosition, new_pokemon: BattleMon):
        if self._has_actioned(user_position): return
        self.position_manager.add_position_action(user_position, SwitchAction(switch_in_position=new_pokemon))
    def cancel_action(self, user_position: BattlePosition):
        if self._has_actioned(user_position):
            self.position_manager.remove_position_action(user_position)

    def print_action_queue(self):
        print("Current Action Queue:")
        for position, action in self.position_manager.position_actions().items():
            print(f"Position: {position}, Action: {action}")
    # endregion

    # region Turn Management
    def start_turn(self):
        if not self.active_battle:
            raise ValueError("No active battle to submit actions to.")
        self.taking_actions = True
        self.battle_log.turn_start(turn_number=self.battle_state.turn_number)
        self.battle_state.turn_number += 1
        self.position_manager.clear_position_actions()

    def end_turn(self):    
        if self.position_manager.get_missing_actions() != []:
            raise UnfinishedTurnException("Not all positions have submitted actions.")

        turn_order = self.get_turn_orders()

        try:
            self.process_escape()
            if not self.taking_actions:
                return        

            self.process_switch()
            self.process_item_use()
            self.process_move(turn_order)

            self.process_damaging_status_conditions()
            self.process_weather()


            self.process_fainted_pokemon()

        except UnfinishedTurnException as e:
            print(e)
            return
        self.taking_actions = False
        return

    def end_battle(self):
        self.battle_log.battle_end(
            winning_trainer=None,
            description="The battle has ended"
        )
        self.active_battle = False

    def clear_battle(self):
        self.clear_all_stat_stages()
        self.position_manager.clear_position_actions()
        self.clear_non_standard_variables()
        self.position_manager.clear()
        self.taking_actions = False
        self.battle_config = None
        self.battle_state = None
    # endregion

    # region Turn Order
    def get_turn_orders(self) -> list[BattlePosition]:
        speed_dict: dict[BattlePosition, int] = {}

        for position in self.position_manager.position_actions().keys():
            pokemon = self.position_manager.get_pokemon_at_position(position)
            speed = calculate_speed(pokemon)
            speed_dict[position] = speed
        
        sorted_positions = sorted(speed_dict.items(), key=lambda item: item[1], reverse=True)
        return [position for position, speed in sorted_positions]

    def process_priority_turn_order(self, turn_order: list[BattlePosition]) -> list[BattlePosition]:
        marked_turn_order: dict[int, BattlePosition] = {}

        # first mark the turn order into a dict with order values
        for index, position in enumerate(turn_order):
            marked_turn_order[index] = position

        # create a dict prioritys with their value being a list of positions with that priority

        priority_positions: dict[int, list[BattlePosition]] = {}

        for position in turn_order:
            action = self.position_manager.get_position_action(position)
            if isinstance(action, MoveAction):
                user_pokemon = self.position_manager.get_pokemon_at_position(position)
                move = user_pokemon.move_set.moves.get(action.move_index)
                if move is not None:
                    priority = move.priority
                    if priority not in priority_positions:
                        priority_positions[priority] = []
                    priority_positions[priority].append(position)

        highest_priority: int = max(priority_positions.keys())
        lowest_priority: int = min(priority_positions.keys())
        sorted_by_priority: list[BattlePosition] = []

        for priority in range(highest_priority, lowest_priority - 1, -1):
            if priority in priority_positions:
                positions = priority_positions[priority]
                if len(positions) > 1:
                    # sort by turn order
                    positions_sorted = sorted(positions, key=lambda item: turn_order.index(item))
                    sorted_by_priority.extend(positions_sorted)
                else:
                    sorted_by_priority.extend(positions)

        return sorted_by_priority
    # endregion

    # region Process Actions
    def process_switch(self):
        for position, action in self.position_manager.position_actions().items():
            if isinstance(action, SwitchAction):
                new_pokemon = action.switch_in_pokemon
                self.position_manager.register_pokemon(new_pokemon, position.team_id, position.pokemon_index)
                self.battle_log.pokemon_switch_in(
                    switched_in_pokemon=new_pokemon,
                    posistion=position,
                    trainer=self.trainers[position.value // 2]
                )

    def process_weather(self):
        weather = self.battle_state.weather_turns.weather
        
        if weather == BattleWeather.NONE:
            return
        elif weather == BattleWeather.HAIL:
            for pokemon in self.position_manager.list_registered_pokemon():
                if PokemonType.ICE in pokemon.pokemon_base.types:
                    continue
                elif pokemon.abilities.has_any_ability(["snow_cloak", "ice_body", "forecast", "magic_guard", "overcoat"]):
                    continue
                elif pokemon.held_item.name in ["safety_goggles"]:
                    continue
                damage = max(1, pokemon.calculate_max_hp() // 16)
                pokemon.current_hp -= damage

        elif weather == BattleWeather.SANDSTORM:
            for pokemon in self.position_manager.list_registered_pokemon():
                if PokemonType.ROCK in pokemon.pokemon_base.types or \
                   PokemonType.GROUND in pokemon.pokemon_base.types or \
                   PokemonType.STEEL in pokemon.pokemon_base.types:
                    continue
                elif pokemon.abilities.has_any_ability(["sand_veil", "sand_rush", "sand_force", "magic_guard", "overcoat"]):
                    continue
                elif pokemon.held_item.name in ["safety_goggles"]:
                    continue
                damage = max(1, pokemon.calculate_max_hp() // 16)
                pokemon.current_hp -= damage

        self.battle_state.decrement_weather()
        if self.battle_state.weather_turns.weather == BattleWeather.NONE:
            self.battle_log.weather_end(
                description="The weather returned to normal."
            )

    def process_damaging_status_conditions(self):
        # loop through all the pokemon in play and apply damage from status conditions
        for pokemon in self.position_manager.list_registered_pokemon():
            for status_condition in pokemon.status_conditions.keys():
                if status_condition == StatusCondition.BURN:
                    damage = max(1, pokemon.calculate_max_hp() // 16)
                    pokemon.current_hp -= damage
                    self.battle_log.status_condition_damage(
                        description=f"{pokemon.nickname} is hurt by its burn!"
                    )
                if status_condition == StatusCondition.FROSTBITE:
                    damage = max(1, pokemon.calculate_max_hp() // 16)
                    pokemon.current_hp -= damage
                    self.battle_log.status_condition_damage(
                        description=f"{pokemon.nickname} is hurt by its frostbite!"
                    )
                if status_condition == StatusCondition.POISON:
                    damage = max(1, pokemon.calculate_max_hp() // 8)
                    pokemon.current_hp -= damage
                    self.battle_log.status_condition_damage(
                        description=f"{pokemon.nickname} is hurt by its poison!"
                    )
                if status_condition == StatusCondition.BADLY_POISON:
                    turns_poisoned = pokemon.status_conditions[StatusCondition.BADLY_POISON]
                    if turns_poisoned > 15:
                        turns_poisoned = 15
                    damage = max(1, (pokemon.calculate_max_hp() // 16) * turns_poisoned)
                    pokemon.current_hp -= damage
                    pokemon.status_conditions[StatusCondition.BADLY_POISON] += 1
                    self.battle_log.status_condition_damage(
                        description=f"{pokemon.nickname} is hurt by its poison!"
                    )

    def process_move(self, turn_order: list[BattlePosition]):
        priority_order = self.process_priority_turn_order(turn_order)

        for position in priority_order:
            if self.position_manager.check_fainted(position):
                self.battle_log.misc(
                    description=f"{self.position_manager.get_pokemon_at_position(position).nickname} is fainted and cannot move!"
                )
                continue  # skip fainted pokemon


            description_list = []

            action = self.position_manager.get_position_action(position)
            if not isinstance(action, MoveAction): continue


            # get pokemons move from moveactions moveindex

            user_pokemon = self.position_manager.get_pokemon_at_position(position)

            used_move = user_pokemon.move_set.get_move_by_index(action.move_index)
            if used_move is None:
                raise ValueError("Move not found in user's move set.")


            target_positions = self.position_manager.get_target_positions(
                user_position=position,
                move_target=used_move.target,
                selected_position=action.target_position
            )

            base_move = used_move.base_move
            base_move.on_use()
            
            for target_position in target_positions:

                target_pokemon = self.position_manager.get_pokemon_at_position(target_position)

                if self.position_manager.check_fainted(target_position):
                    description_list.append(f"{target_pokemon.nickname} is already fainted! The move failed.")
                    description = "\n".join(description_list)
                    self.battle_log.move_used(
                        move_name=None,
                        user_pokemon=user_pokemon,
                        target_pokemon=[target_pokemon],
                        damage_dealt=0,
                        is_critical=False,
                        status_condition_applied=None,
                        move_effectiveness=EffectivenessLevel.NORMAL_EFFECTIVE,
                        description=description
                    )
                    continue


                description_list.append(f"{user_pokemon.nickname} used {used_move.name}!")
                is_critical = calculate_critical_hit(user_pokemon)

                if used_move.accuracy is None:
                    accuracy_check = 100.0
                else:
                    accuracy_check = calculate_accuracy(used_move.base_move, user_pokemon, target_pokemon, self.battle_state)
                
                if not calculate_accuracy_hit(accuracy_check):
                    description_list.append(f"But it missed!")
                    damage = 0
                    effectiveness_level = EffectivenessLevel.NORMAL_EFFECTIVE
                else:
                    effectiveness_multiplier = get_attack_multiplier(used_move.type, target_pokemon.types)
                    effectiveness_level = get_effectiveness_level(effectiveness_multiplier)
                    
                    damage = calculate_damage(
                        attacking_pokemon=user_pokemon,
                        defending_pokemon=target_pokemon,
                        move=used_move.base_move,
                        critical_hit=is_critical,
                        battle_state=self.battle_state
                    )

                    used_move.current_pp -= 1

                    if damage <= 0:
                        description_list.append(effectiveness_message(EffectivenessLevel.NO_EFFECT))
                        continue
                    else:
                        description_list.append(effectiveness_message(effectiveness_level))

                    target_pokemon.current_hp -= damage
                    description_list.append(f"{target_pokemon.nickname} now has {max(0, target_pokemon.current_hp)}/{target_pokemon.calculate_max_hp()} HP.")
                    description_list.append(f"It dealt {damage} damage!")

                    if is_critical:
                        description_list.append("A critical hit!")

                        effectiveness_multiplier = get_attack_multiplier(used_move.type, target_pokemon.pokemon_base.types)

                    if target_pokemon.current_hp <= 0:
                        target_pokemon.current_hp = 0
                        description_list.append(f"{target_pokemon.nickname} fainted!")

                description = "\n".join(description_list)

                self.battle_log.move_used(
                    move_name=used_move.base_move,
                    user_pokemon=user_pokemon,
                    target_pokemon=[target_pokemon],
                    damage_dealt=damage,
                    is_critical=is_critical,
                    status_condition_applied=None,
                    move_effectiveness=effectiveness_level,
                    description=description
                )
    
    def process_fainted_pokemon(self):
        for position in self.position_manager.list_registered_positions():
            if self.position_manager.check_fainted(position):
                # check which opponent the pokemon belongs to
                # opponent = self.get_opponent_from_position(position)
                # if the opponent has usable pokemons, prompt for switch

                # if no usable pokemons, end battle

                self.end_battle()
                pass

    def process_item_use(self):
        pass

    # endregion