from pydantic import BaseModel, Field
from abc import abstractmethod
from shared.battle.battle_actions import BattleAction
from shared.pokemon.pokemon import BattleMon
from shared.battle.position import BattlePosition 

class BattlePositionManager(BaseModel):
    positions: dict[tuple[int, int], BattleMon] = Field(default_factory=dict)
    actions: dict[BattlePosition, BattleAction] = Field(default_factory=dict)

    @abstractmethod
    def get_valid_positions(self) -> list[BattlePosition]:
        pass

    @abstractmethod
    def register_pokemon(self, pokemon: BattleMon, team_index: int, pokemon_index: int):
        pass

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

class SinglesBattlePositionManager(BattlePositionManager):
    

    def get_valid_positions(self) -> list[BattlePosition]:
        return [BattlePosition(team_id=1, pokemon_index=1), BattlePosition(team_id=2, pokemon_index=1)]

    def register_pokemon(self, pokemon: BattleMon, team_index: int, pokemon_index: int):
        pokemon.set_position(BattlePosition(team_id=team_index, pokemon_index=pokemon_index))
        self.positions[(team_index, pokemon_index)] = pokemon


class DoublesBattlePositionManager(BattlePositionManager):
    positions: dict[tuple[int, int], BattleMon] = Field(default_factory=dict)

    def get_valid_positions(self) -> list[BattlePosition]:
        return [
            BattlePosition(team_id=1, pokemon_index=1),
            BattlePosition(team_id=1, pokemon_index=2),
            BattlePosition(team_id=2, pokemon_index=1),
            BattlePosition(team_id=2, pokemon_index=2),
        ]

    def register_pokemon(self, pokemon: BattleMon, team_index: int, pokemon_index: int):
        self.positions[(team_index, pokemon_index)] = pokemon

    def get_pokemon_at_position(self, position: BattlePosition) -> BattleMon:
        return self.positions.get((position.team_id, position.pokemon_index))