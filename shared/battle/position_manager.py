from pydantic import BaseModel, Field
from shared.battle.battle_actions import BattleAction, EscapeAction, SkipTurnAction, SwitchAction
from shared.pokemon.pokemon import BattleMon
from shared.battle.position import BattlePosition
from shared.pokemon.move import MoveTarget
from shared.pokemon.hazard import EntryHazard
from shared.battle.field_effect import FieldEffect
import random

class BattlePositionManager(BaseModel):
    positions: dict[tuple[int, int], BattleMon] = Field(default_factory=dict)
    actions: dict[BattlePosition, BattleAction] = Field(default_factory=dict)
    future_actions: dict[int, dict[BattlePosition, BattleAction]] = Field(default_factory=dict)
    switch_turn_actions: dict[BattlePosition, SwitchAction|SkipTurnAction] = Field(default_factory=dict)
    field_effects: dict[BattlePosition, dict[EntryHazard|FieldEffect, int]] = Field(default_factory=dict)
    teams_count: int = 2
    pokemon_per_team: int = 1

    def get_valid_positions(self) -> list[BattlePosition]:
        valid_positions = []
        for team_id in range(0, self.teams_count):
            for pokemon_index in range(0, self.pokemon_per_team):
                valid_positions.append(BattlePosition(team_id=team_id, pokemon_index=pokemon_index))
        return valid_positions

    def register_pokemon(self, pokemon: BattleMon, team_index: int, pokemon_index: int):
        pokemon.set_position(BattlePosition(team_id=team_index, pokemon_index=pokemon_index))
        self.positions[(team_index, pokemon_index)] = pokemon

    def check_position_validity(self, position: BattlePosition) -> bool:
        valid_positions = self.get_valid_positions()
        return position in valid_positions
    
    def get_missing_actions(self) -> list[BattlePosition]:
        missing_positions = []
        for position in self.list_registered_positions():
            if position not in self.actions:
                missing_positions.append(position)
        return missing_positions

    def get_pokemon_at_position(self, position: BattlePosition) -> BattleMon:
        return self.positions.get((position.team_id, position.pokemon_index))

    def position_actions(self):
        return self.actions

    def add_position_action(self, position: BattlePosition, action: BattleAction):
        # check if position is valid
        if not self.check_position_validity(position):
            raise ValueError("Invalid battle position.")
        
        if position in self.actions and type(self.actions[position]) == SkipTurnAction:
            print ("Position already has a SkipTurnAction, not overwriting.")
            return
        
        if type(action) not in [SwitchAction, EscapeAction]:
            # check if pokemon at position is fainted
            pokemon = self.get_pokemon_at_position(position)
            if pokemon is None or pokemon.is_fainted:
                raise ValueError("Cannot perform action with a fainted Pokémon.")

        self.actions[position] = action

    def add_future_position_action(self, turn_number: int, position: BattlePosition, action: BattleAction):
        if turn_number not in self.future_actions:
            self.future_actions[turn_number] = {}
        self.future_actions[turn_number][position] = action

    def get_future_position_actions(self, turn_number: int) -> dict[BattlePosition, BattleAction]:
        return self.future_actions.get(turn_number, {})
    
    def load_future_position_actions(self, turn_number: int):
        actions = self.get_future_position_actions(turn_number)
        for position, action in actions.items():
            self.add_position_action(position, action)
        if turn_number in self.future_actions:
            del self.future_actions[turn_number]

    def add_switch_turn_action(self, position: BattlePosition, action: SwitchAction|SkipTurnAction):
        self.switch_turn_actions[position] = action

    def load_switch_turn_actions(self):
        for position, action in self.switch_turn_actions.items():
            self.add_position_action(position, action)
        self.switch_turn_actions.clear()

    def remove_position_action(self, position: BattlePosition):
        if position in self.actions:
            del self.actions[position]
    
    def get_position_action(self, position: BattlePosition) -> BattleAction:
        return self.actions.get(position)
    
    def clear_position_actions(self):
        self.actions.clear()

    def get_direct_opponent_position(self, position: BattlePosition) -> BattlePosition:
        if position.team_id == 0:
            opponent_team_id = 1
        else:
            opponent_team_id = 0
        return BattlePosition(team_id=opponent_team_id, pokemon_index=position.pokemon_index)
    
    def clear(self):
        self.positions.clear()

    def list_registered_positions(self) -> list[BattlePosition]:
        return [BattlePosition(team_id=team_id, pokemon_index=pokemon_index) for (team_id, pokemon_index) in self.positions.keys()]
    
    def list_registered_pokemon(self) -> list[BattleMon]:
        return list(self.positions.values())
    
    def list_unregistered_positions(self) -> list[BattlePosition]:
        valid_positions = self.get_valid_positions()
        registered_positions = self.list_registered_positions()
        return [pos for pos in valid_positions if pos not in registered_positions]
    
    def check_fainted(self, position: BattlePosition) -> bool:
        pokemon = self.get_pokemon_at_position(position)
        if pokemon:
            return pokemon.is_fainted
        raise ValueError("No pokemon registered at the given position.")
    
    def get_opponent_teams(self, team_id: int) -> list[int]:
        return [tid for tid in range(1, self.teams_count + 1) if tid != team_id]
    
    def add_hazard(self, position: BattlePosition, hazard: EntryHazard, layers: int):
        if position not in self.field_effects:
            self.field_effects[position] = {}
        if hazard in self.field_effects[position]:
            self.field_effects[position][hazard] += layers
        else:
            self.field_effects[position][hazard] = layers
    
    def remove_hazard(self, position: BattlePosition, hazard: EntryHazard, layers: int):
        if position in self.field_effects and hazard in self.field_effects[position]:
            self.field_effects[position][hazard] -= layers
            if self.field_effects[position][hazard] <= 0:
                del self.field_effects[position][hazard]
            if not self.field_effects[position]:
                del self.field_effects[position]

    def add_field_effect(self, position: BattlePosition, effect: FieldEffect, turns: int):
        if position not in self.field_effects:
            self.field_effects[position] = {}
        self.field_effects[position][effect] = turns
    
    def remove_field_effect(self, position: BattlePosition, effect: FieldEffect):
        if position in self.field_effects and effect in self.field_effects[position]:
            del self.field_effects[position][effect]
            if not self.field_effects[position]:
                del self.field_effects[position]

    def decrement_field_effects(self):
        # Decrement duration of all field effects and remove those that expire
        # Exclude entry hazards from this process
        for position in list(self.field_effects.keys()):
            effects_to_remove = []
            for effect, duration in self.field_effects[position].items():
                if isinstance(effect, FieldEffect):
                    self.field_effects[position][effect] -= 1
                    if self.field_effects[position][effect] <= 0:
                        effects_to_remove.append(effect)
            for effect in effects_to_remove:
                del self.field_effects[position][effect]
            if not self.field_effects[position]:
                del self.field_effects[position]

    def get_target_positions(self, user_position: BattlePosition, move_target: MoveTarget, selected_position: BattlePosition = None) -> list[BattlePosition]:
        # For simplicity, only implement single target opponent logic
        if move_target == MoveTarget.ALL_ALLIES:
            team_id = user_position.team_id
            return [pos for pos in self.list_registered_positions() if pos.team_id == team_id and pos != user_position]
        
        elif move_target in [MoveTarget.ALL_OPPONENTS, MoveTarget.OPPONENTS_FIELD]:
            opponent_team_ids = self.get_opponent_teams(user_position.team_id)
            return [pos for pos in self.list_registered_positions() if pos.team_id in opponent_team_ids]
        
        elif move_target == MoveTarget.ALL_OTHER_POKEMON:
            return [pos for pos in self.list_registered_positions() if pos != user_position]
        
        elif move_target in [MoveTarget.ALL_POKEMON, MoveTarget.ENTIRE_FIELD]:
            return self.list_registered_positions()
        
        elif move_target == MoveTarget.ALLY:
            team_id = user_position.team_id
            return [pos for pos in self.list_registered_positions() if pos.team_id == team_id and pos != user_position]

        elif move_target == MoveTarget.FAINTING_POKEMON:
            # TODO target needs to be a fainted pokemon in the teams party not a position on the field but needs to be handled here kinda at least for now
            pass

        elif move_target == MoveTarget.RANDOM_OPPONENT:
            opponent_team_ids = self.get_opponent_teams(user_position.team_id)
            opponent_positions = [pos for pos in self.list_registered_positions() if pos.team_id in opponent_team_ids]
            if opponent_positions:
                return [random.choice(opponent_positions)]
            else:
                return []
            
        elif move_target == MoveTarget.SELECTED_POKEMON_ME_FIRST:
            # TODO will need to work with the priority or the move processing system, currently unsure
            target_position = selected_position

        elif move_target == MoveTarget.SELECTED_POKEMON:
            target_position = selected_position
            return [target_position]
        
        elif move_target == MoveTarget.SPECIFIC_MOVE:
            # from what I understand this usually targets the pokemon that hit the user last
            pass

        elif move_target == MoveTarget.USER_AND_ALLIES:
            team_id = user_position.team_id
            return [pos for pos in self.list_registered_positions() if pos.team_id == team_id]

        elif move_target == MoveTarget.USER_OR_ALLY:
            # Return the user after a check for validity
            if user_position.team_id == selected_position.team_id:
                return [selected_position]
            return ValueError("Selected position is not the user or an ally.")

        elif move_target in [MoveTarget.USER, MoveTarget.USERS_FIELD]:
            return [user_position]

        else:
            raise ValueError("Unsupported move target type.")

    def updated_battled_pokemon(self):
        for position, pokemon in self.positions.items():
            team_id, pokemon_index = position
            # Get the pokemon on the other team
            # Add all the battled pokemon to the pokemon's battled pokemon list
            opponent_team_ids = self.get_opponent_teams(team_id)
            for opponent_team_id in opponent_team_ids:
                for opponent_position in self.list_registered_positions():
                    if opponent_position.team_id == opponent_team_id:
                        opponent_pokemon = self.get_pokemon_at_position(opponent_position)
                        pokemon.add_pokemon_battled(opponent_pokemon)