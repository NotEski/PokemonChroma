# pick the move
# calculate the priority
# apply effects

from pydantic import BaseModel, Field
from shared.battle.battle_actions import BattleAction, SwitchAction, MoveAction, EscapeAction
from shared.pokemon.move import BaseMove, MoveCategory, MoveCategoryCategories
from shared.pokemon.pokemon import BattleMon, StatStages
from shared.battle.battle_header import *
from shared.battle.battle_logs import BattleLogManager
from shared.battle.type_effectiveness import EffectivenessLevel, effectiveness_message, get_attack_multiplier, get_effectiveness_level
from shared.battle.opponent import Opponent
from shared.battle.position_manager import BattlePosition
from shared.pokemon.types import PokemonType
from shared.pokemon.status_conditions import StatusCondition
from shared.pokemon.move_tags import *

from .damage_calculator import calculate_damage, calculate_critical_hit
from .speed_calculator import calculate_speed
from .escape_calculator import calculate_escape_success
from .calculate_accuracy import calculate_accuracy, calculate_accuracy_hit
import random


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

        self.battle_state.position_manager_ref = self.position_manager


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

        try:
            self.process_turn()
        except UnfinishedTurnException as e:
            print(e)
            return
        self.taking_actions = False
        return


    
    def process_turn(self):
        # Quick Claw/Custap Berry announce their effects if applicable

        # If wild battle, display "Got away safely!"/"Can't escape!" message; if trainer battle, forfeit and fade out
        self.process_escape()
        if not self.taking_actions:
            return

        # Handle switches
        self.process_switch()

        # Handle rotation
        # unsure if rotation battles will be supported

        # Item usage (in-game only)
        self.process_item_use()

        # Mega Evolution, Ultra Burst
        self.process_mega_evolution()

        # Focus Punch, Beak Blast, Shell Trap charging effects
        self.process_move_charging_effects()

        # Move usage in order
        turn_order = self.get_turn_orders()
        priority_order = self.calculate_turn_order(turn_order)
        for participant in priority_order:
            self.process_move(participant)


        # End of turn effects
        self.process_end_of_turn_effects()

        self.process_fainted_pokemon()


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

        # Generate stable random tiebreakers
        tiebreakers = {position: random.random() for position in speed_dict.keys()}
        
        sorted_positions = sorted(
            speed_dict.items(), 
            key=lambda item: (item[1], tiebreakers[item[0]]), 
            reverse=True
        )
        return [position for position, speed in sorted_positions]

    def calculate_turn_order(self, turn_order: list[BattlePosition]) -> list[BattlePosition]:
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

    def process_end_of_turn_effects(self):
        self.process_weather()
        self.process_damaging_status_conditions()

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
                status_condition.on_turn_end(pokemon)

    def process_mega_evolution(self):
        pass

    def process_move_charging_effects(self):
        pass

    def process_move(self, position: BattlePosition):
        action = self.position_manager.get_position_action(position)
        if not isinstance(action, MoveAction): return

        if self.position_manager.check_fainted(position):
            self.battle_log.misc(
                description=f"{self.position_manager.get_pokemon_at_position(position).nickname} is fainted and cannot move!"
            )
            return  # skip fainted pokemon

        user_pokemon = self.position_manager.get_pokemon_at_position(position)
        target_pokemon = self.position_manager.get_pokemon_at_position(action.target_position)

        user_pokemon_status_conditions = list(user_pokemon.status_conditions.keys())
        can_move = self._can_move_check(user_pokemon_status_conditions, user_pokemon)
        if not can_move:
            return

        used_move = user_pokemon.move_set.get_move_by_index(action.move_index)
        if used_move is None:
            raise ValueError("Move not found in user's move set.")
        
        used_move.current_pp -= 1

        target_positions = self.position_manager.get_target_positions(
            user_position=position,
            move_target=used_move.target,
            selected_position=action.target_position
        )


        if used_move.accuracy is None:
            accuracy_check = 100.0
        else:
            accuracy_check = calculate_accuracy(used_move.base_move, user_pokemon, target_pokemon, self.battle_state)

        if not calculate_accuracy_hit(accuracy_check):
            damage = 0
            effectiveness_level = EffectivenessLevel.NORMAL_EFFECTIVE
            target_positions.clear()

        

        all_target_pokemon: list[BattleMon] = []
        for target_position in target_positions:
            target_pokemon = self.position_manager.get_pokemon_at_position(target_position)
            all_target_pokemon.append(target_pokemon)

            base_move = used_move.base_move

            is_critical = calculate_critical_hit(user_pokemon, base_move)

            effectiveness_level = EffectivenessLevel.NORMAL_EFFECTIVE


            if used_move.category in MoveCategoryCategories.DAMAGE_MOVES:
                print ("Processing damage move")
                effectiveness_level = self.process_damage_move(user_pokemon, target_pokemon, used_move.base_move, is_critical)
            
            if used_move.category in MoveCategoryCategories.STATUS_MOVES:
                print ("Processing status move")
                self.process_status_move(user_pokemon, target_pokemon, used_move.base_move)

            if used_move.category in MoveCategoryCategories.FIELD_EFFECT_MOVES:
                print ("Processing field effect move")
                self.process_field_effect_move(used_move.base_move, target_position)

            if used_move.category in MoveCategoryCategories.STAT_CHANGE_MOVES:
                print ("Processing stat change move")
                self.process_stat_change_move(user_pokemon, target_pokemon, used_move.base_move)

            if used_move.category == MoveCategory.HEAL:
                print ("Processing healing move")
                self.process_healing_move(user_pokemon, target_pokemon, used_move.base_move)

            if used_move.category == MoveCategory.OHKO:
                print ("Processing OHKO move")
                self.process_ohko_move(target_pokemon)


            # if target_pokemon.current_hp <= 0:
            #     self.battle_log.pokemon_fainted(
            #         fainted_pokemon=target_pokemon,
            #         pokemon_position=self.position_manager.get_position_of_pokemon(target_pokemon),
            #         trainer=self.get_opponent_from_position(self.position_manager.get_position_of_pokemon(target_pokemon)),
            #         description=f"{target_pokemon.nickname} has fainted!"
            #     )

        self.battle_log.move_used(
            move_name=used_move.base_move,
            user_pokemon=user_pokemon,
            target_pokemon=all_target_pokemon,
            damage_dealt=100,
            is_critical=is_critical,
            status_condition_applied=None,
            move_effectiveness=effectiveness_level,
            description="description goes here!"
        )

    def process_damage_move(self, user: BattleMon, target: BattleMon, move: BaseMove, is_critical: bool) -> EffectivenessLevel:
        """Process a damage-dealing move. Only called if the move is a damage move. Moves can also call other methods as needed for additional effects."""
        effectiveness_multiplier = get_attack_multiplier(move.type, target.types)
        effectiveness_level = get_effectiveness_level(effectiveness_multiplier)
        
        damage = calculate_damage(
            attacking_pokemon=user,
            defending_pokemon=target,
            move=move,
            critical_hit=is_critical,
            battle_state=self.battle_state
        )

        # If damage is less than or equal to 0, it means no damage was dealt (e.g., immune)
        if damage <= 0:
            return EffectivenessLevel.NO_EFFECT
        
        # Apply effectiveness message
        target.current_hp -= damage

        # Check for faint
        if target.current_hp <= 0:
            target.current_hp = 0

        if move.has_tag(ContactMove):
            user_abilities = list(user.abilities.get_all_active_abilities())
            for ability in user_abilities:
                ability.on_contact(target, user)

        return effectiveness_level


    def process_status_move(self, user: BattleMon, target: BattleMon, move: BaseMove):
        """Process a status move."""
        if move.has_tag(StatusConditionMove):
            status_condition = move.get_tag(StatusConditionMove).status_condition
            if status_condition is not None:
                target.add_status_condition(status_condition, status_condition._default_data_factory())

    def process_stat_change_move(self, user: BattleMon, target: BattleMon, move: BaseMove):
        """Process a stat-changing move."""
        if move.has_tag(StatChangeMove):
            stat_changes_received = move.get_stat_change_tags(StatChangeReceivedMove)
            for stat_change in stat_changes_received:
                if stat_change.chance >= random.randint(1, 100):
                    user.modify_stat_stage(stat_change.stat, stat_change.change)
            stat_changes_inflicted = move.get_stat_change_tags(StatChangeInflictedMove)
            for stat_change in stat_changes_inflicted:
                if stat_change.chance >= random.randint(1, 100):
                    target.modify_stat_stage(stat_change.stat, stat_change.change)

    def process_field_effect_move(self, move: BaseMove, position: BattlePosition):
        """Process a field-effect move."""
        if move.has_tag(FieldEffectMove):
            field_effect = move.get_tag(FieldEffectMove).field_effect
            turns = move.get_tag(FieldEffectMove).turns
            self.position_manager.add_field_effect(position, field_effect, turns)
        if move.has_tag(EntryHazardMove):
            hazard = move.get_tag(EntryHazardMove).entry_hazard
            layers = move.get_tag(EntryHazardMove).layers
            self.position_manager.add_hazard(position, hazard, layers)

    def process_healing_move(self, user: BattleMon, target: BattleMon, move: BaseMove):
        """Process a healing move."""
        pass

    def process_ohko_move(self, target: BattleMon):
        """Process a one-hit KO move."""
        target.current_hp = 0







    def _move_start_of_turn_effects(self, status_conditions: list[StatusCondition], user_pokemon: BattleMon):
        description_list = []
        for status_condition in status_conditions:
            if not isinstance(status_condition, StatusCondition):
                continue
            status_condition.on_turn_start(user_pokemon)
        return description_list
    
    def _can_move_check(self, status_conditions: list[StatusCondition], user_pokemon: BattleMon) -> bool:
        can_move = True
        for status_condition in status_conditions:
            if not isinstance(status_condition, StatusCondition):
                continue
            if not status_condition.can_move(user_pokemon):
                can_move = False
        return can_move

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
