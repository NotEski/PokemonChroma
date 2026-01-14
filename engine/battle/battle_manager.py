from typing import Dict, Optional, List
from shared.battle.battle_actions import BattleAction, SwitchAction, MoveAction, EscapeAction, SkipTurnAction
from shared.pokemon.move import BaseMove, MoveCategory, MoveCategoryCategories
from shared.pokemon.pokemon import BattleMon, StatStages
from shared.battle.battle_header import *
from shared.battle.battle_logs import BattleLogManager
from shared.battle.type_effectiveness import EffectivenessLevel, get_attack_multiplier, get_effectiveness_level, effectiveness_message
from shared.battle.opponent import Opponent
from shared.battle.position_manager import BattlePosition
from shared.pokemon.types import PokemonType
from shared.pokemon.status_conditions import StatusCondition
from shared.pokemon.move_tags import *

from .damage_calculator import calculate_damage, calculate_critical_hit
from .speed_calculator import calculate_speed
from .escape_calculator import calculate_escape_success
from .calculate_accuracy import calculate_accuracy, calculate_accuracy_hit
from .calculate_experience import calculate_experience
from .multihit_check import multihit_check
import random


class BattleManager:
    position_manager: BattlePositionManager = BattlePositionManager()
    battle_config: BattleConfig = BattleConfig()
    battle_state: BattleState = BattleState()
    taking_actions: bool = False
    battle_log: BattleLogManager = BattleLogManager()
    active_battle: bool = True
    teams: dict[int, Opponent] = {}


    def __init__(self,
                 teams: Dict[int, Opponent] | List[Opponent],
                 battle_config: Optional[BattleConfig] = None ):
        if battle_config:
            self.battle_config = battle_config
        if isinstance(teams, list):
            teams_dict = {}
            for index, team in enumerate(teams):
                teams_dict[index] = team
            self.teams = teams_dict
        else:
            self.teams = teams
        # validate keys are 0, 1, 2, ...
        len_keys = len(self.teams.keys())
        for i in range(0, len_keys):
            if i not in self.teams:
                raise ValueError("Teams dictionary keys must be sequential integers starting from 0.")

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
        for pokemon in self.teams[0].get_all_battlemons() + self.teams[1].get_all_battlemons():
            self.clear_pokemon_stat_stages(pokemon)

    def init_battle(self):
        self.clear_all_stat_stages()

        for team_id in range(0, self.position_manager.teams_count):
            for pokemon_index in range(0, self.position_manager.pokemon_per_team):
                pokemon = self.teams[team_id].get_active_battlemon()
                if not pokemon:
                    raise ValueError(f"Team {team_id} does not have enough active Pokémon for the battle.")
                self.position_manager.register_pokemon(
                    pokemon=pokemon,
                    team_index=team_id,
                    pokemon_index=pokemon_index
                )

    def process_escape(self):
        for position, action in self.position_manager.position_actions().items():
            if isinstance(action, EscapeAction):
                escaping_pokemon = self.position_manager.get_pokemon_at_position(position)
                enemy_pokemon = self.position_manager.get_pokemon_at_position(self.get_opposite_position_from_position(position))
                if not escaping_pokemon or not enemy_pokemon:
                    continue
                success = calculate_escape_success(escaping_pokemon, enemy_pokemon, action.escape_attempts)
                if success:
                    self.battle_log.battle_end(
                        description=f"{escaping_pokemon.nickname} successfully escaped!"
                    )
                    self.end_battle()
                    return
                else:
                    self.battle_log.misc(
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
    
    def _has_fainted(self, position: BattlePosition) -> bool:
        output = self.position_manager.check_fainted(position)
        return output
    
    def get_switch_turn(self) -> bool:
        return self.battle_state.switch_turn

    def get_taking_actions(self) -> bool:
        return self.taking_actions
    # endregion

    # region Action Submission
    def submit_action(self, action: BattleAction):
        if not self.taking_actions:
            raise ValueError("Not currently taking actions.")
        
        if isinstance(action, SwitchAction):
            self.switch_pokemon(
                user_position=action.position,
                new_pokemon_index=action.switch_in_pokemon_index
            )
        elif isinstance(action, SkipTurnAction) and self.battle_state.switch_turn:
            # check if the position has a fainted pokemon, if so, do not allow skip
            if self._has_fainted(action.position):
                raise ValueError("Cannot skip turn with a fainted Pokémon.")
            self.position_manager.add_position_action(action.position, action)
        elif self.battle_state.switch_turn:
            raise ValueError("Cannot submit non-switch actions during a switch turn.")
        elif isinstance(action, MoveAction):
            target_position = action.target_position
            if not target_position:
                raise ValueError("Target position must be specified for move actions.")
            self.use_move(
                user_position=action.position,
                move_index=action.move_index,
                target_position=target_position
            )
        else:
            raise ValueError("Invalid action type submitted.")
        
        self.position_manager.add_position_action(action.position, action)

    def use_escape(self, user_position: BattlePosition):
        if self._has_actioned(user_position): return
        if self._has_fainted(user_position): return

        if self.battle_config.is_wild is False:
            raise ValueError("Cannot escape from trainer battles!")
        
        opponent_escaping = self.get_opponent_from_position(user_position)
        opponent_escaping.escape_attempts += 1
        self.position_manager.add_position_action(user_position, EscapeAction(position=user_position, escape_attempts=opponent_escaping.escape_attempts))

    def use_move(self, user_position: BattlePosition, move_index: int, target_position: BattlePosition):
        if self._has_actioned(user_position): return
        if self._has_fainted(user_position): return

        user_pokemon = self.position_manager.get_pokemon_at_position(user_position)
        if not user_pokemon:
            raise ValueError("No Pokémon found at the given user position.")
        if move_index not in user_pokemon.move_set.moves:
            raise ValueError("Invalid move index.")
        
        move = user_pokemon.move_set.moves[move_index]

        if move.current_pp <= 0 and move.max_pp >= 1:
            raise ValueError(f"{user_pokemon.nickname} has no PP left for {move.name}!")

        self.position_manager.add_position_action(user_position, MoveAction(move_index=move_index, position=user_position, target_position=target_position))

    def switch_pokemon(self, user_position: BattlePosition, new_pokemon_index: int):
        if self._has_actioned(user_position): return

        opponent = self.get_opponent_from_position(user_position)
        if new_pokemon_index < 0 or new_pokemon_index >= len(opponent.get_all_battlemons()):
            raise ValueError("Invalid Pokémon index for switch.")
        new_pokemon = opponent.get_battlemon_by_index(new_pokemon_index)
        if new_pokemon.is_fainted:
            raise ValueError("Cannot switch to a fainted Pokémon.")
        current_pokemon = self.position_manager.get_pokemon_at_position(user_position)
        if new_pokemon == current_pokemon:
            raise ValueError("Cannot switch to the same Pokémon.")

        self.position_manager.add_position_action(user_position, SwitchAction(position=user_position, switch_in_pokemon_index=new_pokemon_index))

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
        self.position_manager.clear_position_actions()
        if not self.battle_state.switch_turn:
            self.battle_state.turn_number += 1
        else:
            self.position_manager.load_switch_turn_actions()
        
        self.position_manager.updated_battled_pokemon()

    def end_turn(self):    
        if self.position_manager.get_missing_actions() != []:
            raise UnfinishedTurnException("Not all positions have submitted actions.")
        
        if self.battle_state.switch_turn:
            self.battle_state.switch_turn = False
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
        # Check if there are any moves to process
        if self.check_needs_turn_order_calculation():
            turn_order = self.get_turn_orders()
            priority_order = self.calculate_turn_order(turn_order)
            for participant in priority_order:
                self.process_move(participant)


        # End of turn effects
        self.process_end_of_turn_effects()

        self.process_fainted_pokemon()


    def end_battle(self):
        self.battle_log.battle_end(
            description="The battle has ended"
        )
        self.active_battle = False

    def clear_battle(self):
        self.clear_all_stat_stages()
        self.position_manager.clear_position_actions()
        self.clear_non_standard_variables()
        self.position_manager.clear()
        self.taking_actions = False
    # endregion

    # region Turn Order
    def check_needs_turn_order_calculation(self) -> bool:
        for action in self.position_manager.position_actions().values():
            if isinstance(action, MoveAction):
                return True
        return False

    def get_turn_orders(self) -> list[BattlePosition]:
        speed_dict: dict[BattlePosition, int] = {}

        for position in self.position_manager.position_actions().keys():
            user_pokemon = self.position_manager.get_pokemon_at_position(position)
            if not user_pokemon:
                continue
            speed = calculate_speed(user_pokemon)
            speed_dict[position] = speed

        # Generate stable random tiebreakers
        tiebreakers = {position: random.random() for position in speed_dict.keys()}
        
        sorted_positions = sorted(
            speed_dict.items(), 
            key=lambda item: (item[1], tiebreakers[item[0]]), 
            reverse=True
        )
        return [position for position, _ in sorted_positions]

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
                if not user_pokemon:
                    continue
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
                new_pokemon_index = action.switch_in_pokemon_index
                new_pokemon = self.get_opponent_from_position(position).get_battlemon_by_index(new_pokemon_index)
                self.position_manager.register_pokemon(new_pokemon, position.team_id, position.pokemon_index)
                self.battle_log.pokemon_switch_in(
                    switched_in_pokemon=new_pokemon,
                    posistion=position,
                    opponent=self.teams[position.team_id],
                    description=f"{new_pokemon.nickname} was switched in!"
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
                elif pokemon.held_item and pokemon.held_item.name in ["safety_goggles"]:
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
                elif pokemon.held_item and pokemon.held_item.name in ["safety_goggles"]:
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
        if not action: return
        if not isinstance(action, MoveAction): return

        user_pokemon = self.position_manager.get_pokemon_at_position(position)
        if not user_pokemon:
            raise ValueError("No Pokémon found at the given user position.")

        if self.position_manager.check_fainted(position):
            self.battle_log.misc(
                description=f"{user_pokemon.nickname} is fainted and cannot move!"
            )
            return  # skip fainted pokemon
        target_pokemon = self.position_manager.get_pokemon_at_position(action.target_position)
        if not target_pokemon:
            raise ValueError("No Pokémon found at the given target position.")

        user_pokemon_status_conditions = list(user_pokemon.status_conditions.keys())
        can_move = self._can_move_check(user_pokemon_status_conditions, user_pokemon)
        if not can_move:
            return

        used_move = user_pokemon.move_set.get_move_by_index(action.move_index)
        if used_move is None:
            raise ValueError("Move not found in user's move set.")
        
        # Is the move disabled?
        if action.move_index in user_pokemon.disabled_moves:
            self.battle_log.misc(
                description=f"{user_pokemon.nickname} tried to use a disabled move and failed!"
            )
            return
        
        user_pokemon.add_previous_move_used(used_move.base_move)

        if used_move.max_pp >= 1: 
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
        damage = 0
        effectiveness_level = EffectivenessLevel.NORMAL_EFFECTIVE

        if not calculate_accuracy_hit(accuracy_check):
            
            target_positions.clear()

        description_list: list[str] = []
        description_list.append(f"{user_pokemon.nickname} used {used_move.name}!")        

        all_target_pokemon: list[BattleMon] = []
        is_critical = False

        for target_position in target_positions:

            target_pokemon = self.position_manager.get_pokemon_at_position(target_position)
            if not target_pokemon:
                continue
            all_target_pokemon.append(target_pokemon)

            base_move = used_move.base_move

            is_critical = calculate_critical_hit(user_pokemon, base_move)

            effectiveness_level = EffectivenessLevel.NORMAL_EFFECTIVE
            damage = 0
            total_damage = 0

            # TODO Struggle Move needs special handling here to skip PP check and deduction

            # Calc multihit here if applicable
            num_hits = multihit_check(used_move.base_move, user_pokemon, target_pokemon)

            for _ in range(0, num_hits):
                if used_move.category in MoveCategoryCategories.DAMAGE_MOVES:
                    effectiveness_level, damage = self.process_damage_move(user_pokemon, target_pokemon, used_move.base_move, is_critical)
                    total_damage += damage
            if num_hits > 1:
                description_list.append(f"Hit {num_hits} time(s)!")
            
            if used_move.category in MoveCategoryCategories.STATUS_MOVES:
                self.process_status_move(user_pokemon, target_pokemon, used_move.base_move)

            if used_move.category in MoveCategoryCategories.FIELD_EFFECT_MOVES:
                self.process_field_effect_move(used_move.base_move, target_position)

            if used_move.category in MoveCategoryCategories.STAT_CHANGE_MOVES:
                self.process_stat_change_move(user_pokemon, target_pokemon, used_move.base_move)

            if used_move.category == MoveCategory.HEAL:
                self.process_healing_move(user_pokemon, target_pokemon, used_move.base_move)

            if used_move.category == MoveCategory.OHKO:
                self.process_ohko_move(target_pokemon)
            
            if used_move.base_move.has_tag(DrainMove):
                self.process_drain_move(user_pokemon, damage, used_move.base_move)
            
            if used_move.base_move.has_tag(WeatherMove):
                weather_move: WeatherMove = used_move.base_move.get_tag(WeatherMove) # type: ignore
                weather = weather_move.weather
                # run check here for item that extends weather duration
                self.battle_state.set_weather(weather, turns=5)
                description_list.append(f"The weather changed to {weather}!")

        if effectiveness_level != EffectivenessLevel.NORMAL_EFFECTIVE:
            description_list.append(effectiveness_message(effectiveness_level))

            # if target_pokemon.current_hp <= 0:
            #     self.battle_log.pokemon_fainted(
            #         fainted_pokemon=target_pokemon,
            #         pokemon_position=self.position_manager.get_position_of_pokemon(target_pokemon),
            #         trainer=self.get_opponent_from_position(self.position_manager.get_position_of_pokemon(target_pokemon)),
            #         description=f"{target_pokemon.nickname} has fainted!"
            #     )
        
        description =  "\n".join(description_list)

        self.battle_log.move_used(
            move_name=used_move.base_move,
            user_pokemon=user_pokemon,
            target_pokemon=all_target_pokemon,
            damage_dealt=100,
            is_critical=is_critical,
            description=description
        )

    def process_damage_move(self, user: BattleMon, target: BattleMon, move: BaseMove, is_critical: bool) -> tuple[EffectivenessLevel, int]:
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
            return EffectivenessLevel.NO_EFFECT, 0
        
        # Apply effectiveness message
        target.current_hp -= damage

        # Check for faint
        if target.current_hp <= 0:
            target.current_hp = 0

        if move.has_tag(ContactMove):
            user_abilities = list(user.abilities.get_all_active_abilities())
            for ability in user_abilities:
                ability.on_contact(target, user)

        return (effectiveness_level, damage)

    def process_status_move(self, user: BattleMon, target: BattleMon, move: BaseMove):
        """Process a status move."""
        if move.has_tag(StatusConditionMove):
            status_condition_move: StatusConditionMove = move.get_tag(StatusConditionMove) # type: ignore
            status_condition = status_condition_move.status_condition
            print ("Applying status condition:", status_condition)

            if status_condition is None: # type: ignore
                print ("No status condition found in move tag.")
                return
            previous_move = user.previous_move_used
            if not previous_move:
                print ("No previous move found for user.")
                return

            if status_condition.name == "disable":
                self.process_disable_move(target, move_index=previous_move.index, turns=4)
                return
            target.add_status_condition(status_condition, status_condition.default_data_factory())

    def process_disable_move(self, target: BattleMon, move_index: int, turns: int):
        last_move_used = target.previous_move_used if target.previous_move_used else None
        if last_move_used is None:
            return
        move_index = last_move_used.index
        target.disable_move(move_index, turns=4)
        return
    
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
            field_effect_move: FieldEffectMove = move.get_tag(FieldEffectMove) # type: ignore
            field_effect = field_effect_move.field_effect
            turns = field_effect_move.turns
            self.position_manager.add_field_effect(position, field_effect, turns)
        if move.has_tag(EntryHazardMove):
            entry_hazard_move: EntryHazardMove = move.get_tag(EntryHazardMove) # type: ignore
            hazard = entry_hazard_move.entry_hazard
            layers = entry_hazard_move.layers
            self.position_manager.add_hazard(position, hazard, layers)

    def process_healing_move(self, user: BattleMon, target: BattleMon, move: BaseMove):
        heal_move: HealMove = move.get_tag(HealMove) # type: ignore
        heal_percentage = heal_move.heal_percentage
        heal_amount = target.max_hp * heal_percentage // 100
        target.current_hp = min(target.calculate_max_hp(), target.current_hp + heal_amount)

    def process_ohko_move(self, target: BattleMon):
        """Process a one-hit KO move."""
        target.current_hp = 0

    def process_drain_move(self, user: BattleMon, damage_dealt: int, move: BaseMove):
        drain_move: DrainMove = move.get_tag(DrainMove) # type: ignore
        heal_amount = damage_dealt * drain_move.drain_percentage // 100
        user.current_hp = min(user.calculate_max_hp(), user.current_hp + heal_amount)

    def _move_start_of_turn_effects(self, status_conditions: list[StatusCondition], user_pokemon: BattleMon) -> list[str]:
        description_list: list[str] = []
        for status_condition in status_conditions:
            status_condition.on_turn_start(user_pokemon)
        return description_list
    
    def _can_move_check(self, status_conditions: list[StatusCondition], user_pokemon: BattleMon) -> bool:
        can_move = True
        for status_condition in status_conditions:
            if not status_condition.can_move(user_pokemon):
                can_move = False
        return can_move

    def process_item_use(self):
        pass

    def process_fainted_pokemon(self):
        # If this occurs we need to not track this as a turn end but rather a mid-turn event

        list_of_non_fainted_positions: list[BattlePosition] = []
        for position in self.position_manager.list_registered_positions():
            if self.position_manager.check_fainted(position):
                # check which opponent the pokemon belongs to
                opponent = self.get_opponent_from_position(position)
                fainted_pokemon = self.position_manager.get_pokemon_at_position(position)
                if not fainted_pokemon:
                    continue
                # for now just get the pokemon opposite the fainted pokemon
                battled_pokemon = self.position_manager.get_pokemon_at_position(self.get_opposite_position_from_position(position))
                if not battled_pokemon:
                    continue
                
                victorious_pokemon = battled_pokemon
                if self.battle_config.grant_exp:
                    experience_gained = calculate_experience(
                        defeated_pokemon=fainted_pokemon,
                        victorious_pokemon=battled_pokemon
                    )

                    print (f"{victorious_pokemon.nickname} gained {experience_gained} experience points!")

                self.battle_log.pokemon_fainted(
                    fainted_pokemon=fainted_pokemon,
                    pokemon_position=position,
                    opponent=opponent,
                    description=f"{fainted_pokemon.nickname} has fainted!"
                )
                # check if the opponent has usable pokemons
                if not opponent.has_viable_pokemons():
                    # if no usable pokemons, end battle
                    self.end_battle()
                    break
                continue
            list_of_non_fainted_positions.append(position)
        if len(list_of_non_fainted_positions) < len(self.position_manager.list_registered_positions()):
            self.taking_actions = True
            self.battle_state.switch_turn = True
            for position in list_of_non_fainted_positions:
                # check if battle switch type is switch or set. if set we skip their switch turn
                if self.battle_config.battle_switch_type == BattleSwitchType.SET:
                    self.position_manager.add_switch_turn_action(position, SkipTurnAction(position=position))
                    
    # endregion
