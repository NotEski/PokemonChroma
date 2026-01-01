from pydantic import BaseModel, Field
from shared.battle.battle_actions import BattleAction
from shared.pokemon.pokemon import BattleMon
from shared.battle.position import BattlePosition
from shared.pokemon.move import MoveTarget
from shared.pokemon.hazard import EntryHazard
from shared.battle.field_effect import FieldEffect
import random

class BattlePositionManager(BaseModel):
    positions: dict[tuple[int, int], BattleMon] = Field(default_factory=dict)
    actions: dict[BattlePosition, BattleAction] = Field(default_factory=dict)
    field_effects: dict[BattlePosition, dict[EntryHazard|FieldEffect, int]] = Field(default_factory=dict)
    teams_count: int = 2
    pokemon_per_team: int = 1


    def get_valid_positions(self) -> list[BattlePosition]:
        valid_positions = []
        for team_id in range(1, self.teams_count + 1):
            for pokemon_index in range(1, self.pokemon_per_team + 1):
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

        self.actions[position] = action

    def remove_position_action(self, position: BattlePosition):
        if position in self.actions:
            del self.actions[position]
    
    def get_position_action(self, position: BattlePosition) -> BattleAction:
        return self.actions.get(position)
    
    def clear_position_actions(self):
        self.actions.clear()

    def get_direct_opponent_position(self, position: BattlePosition) -> BattlePosition:
        if position.team_id == 1 and position.pokemon_index == 1:
            return BattlePosition(team_id=2, pokemon_index=1)
        elif position.team_id == 2 and position.pokemon_index == 1:
            return BattlePosition(team_id=1, pokemon_index=1)
        else:
            raise ValueError("Invalid position for singles battle.")
    
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
