


class Move:
    def on_turn_start(self, battle, user):
        pass
    def can_move(self, battle, user):
        pass


class Ability:
    def on_entry(self, battle, pokemon):
        pass

    def on_defending_contact(self, battle, attacker, defender):
        pass

    def on_attacking_contact(self, battle, attacker, defender):
        pass

    def on_switch_out(self, battle, pokemon):
        pass


class Item:
    def on_entry(self, battle, pokemon):
        pass

class Pokemon:
    def __init__(self, name):
        self.name = name
        self.ability = Ability()
        self.item = Item()
    
    @property
    def is_fainted(self):
        return False

class BattleManager:
    def __init__(self):
        pass

    def start_turn(self):
        pass

    def end_turn(self):
        self.process_turn()

    def process_turn(self):
        # Quick Claw/Custap Berry announce their effects if applicable

        # If wild battle, display "Got away safely!"/"Can't escape!" message; if trainer battle, forfeit and fade out

        # Handle switches
        self.process_switch(None)

        # Handle rotation
        # unsure if rotation battles will be supported

        # Item usage (in-game only)
        self.process_item_usage(None)

        # Mega Evolution, Ultra Burst
        self.process_mega_evolution(None)

        # Focus Punch, Beak Blast, Shell Trap charging effects
        self.process_move_charging_effects(None)

        # Move usage in order
        turn_order = self.calculate_turn_order()
        for participant in turn_order:
            self.process_move(None, participant)

        # End of turn effects
        self.process_end_of_turn_effects()

    def process_switch(self, old_pokemon: Pokemon, new_pokemon: Pokemon):
        if not old_pokemon.is_fainted:
            old_pokemon.ability.on_switch_out(self, old_pokemon)
        # change_pokemon
        new_pokemon.ability.on_entry(self, new_pokemon)
        self.process_pokemon_entry(new_pokemon)

    def process_entry_hazards(self, pokemon: Pokemon):
        pass

    def announce_entry_abilities(self, pokemon: Pokemon):
        pass

    def process_move_charging_effects(self, move: Move):
        pass

    def process_move(self, move: Move, user):
        move.on_turn_start(self, user)
        move.can_move(self, user)
    
    def process_escape_attempt(self, user):
        success: bool = True

        if success:
            print(f"{user.name} escaped successfully!")
        else:
            print(f"{user.name} failed to escape!")

    def process_pokemon_entry(self, pokemon: Pokemon):
        # Pokeball Effects
        # Ribbon Effects
        # Entry healing (Healing Wish, Lunar Dance, Z-Momento, Z-Parting Shot)
        self.process_entry_hazards(pokemon)
        pokemon.ability.on_entry(self, pokemon)
        pokemon.item.on_entry(self, pokemon)

    def process_item_usage(self, pokemon: Pokemon):
        pass

    def process_mega_evolution(self, pokemon: Pokemon):
        pass

    def process_end_of_turn_effects(self):
        pass

    def calculate_turn_order(self, participants)->list:
        pass


