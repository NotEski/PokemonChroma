import random
from shared.pokemon.move import BaseMove, DamageClass
from shared.pokemon.pokemon import BattleMon
from shared.battle.battle_header import BattleState, BattleWeather
from engine.pokemon.repository import status_repository


def calculate_accuracy(base_move: BaseMove, user: BattleMon, target: BattleMon, battle_state: BattleState) -> float:
    # Placeholder for actual calculation logic

    # affection_bonus = 1.0  # Check user's affection level


    adjusted_accuracy_stage_modifier = _get_accuracy_stage_modifier(user, target)
    micle_berry = _get_micle_berry_modifier(user)
    other_modifiers = _get_other_modifiers(base_move, user, target, battle_state)


    accuracy_modified = base_move.accuracy * other_modifiers * adjusted_accuracy_stage_modifier * micle_berry # - affection_bonus
    return accuracy_modified
    

def _get_other_modifiers(base_move: BaseMove, user: BattleMon, target: BattleMon, battle_state: BattleState) -> float:
    modifier = 1.0

    # Gravity 1.67

    # Tangled Feet * 0.5
    if target.abilities.has_ability("tangled_feet"):
        if status_repository.get("confusion") in target.non_volatile_status_conditions:
            modifier *= 0.5

    # Hustle 0.8 - if the attacker has it and it's a physical move
    if user.abilities.has_ability("hustle"):
        if base_move.category == DamageClass.PHYSICAL:
            modifier *= 0.8

    # Sandveil 0.8 - if the target has it and the weather is sandstorm
    if target.abilities.has_ability("sandveil"):
        if battle_state.weather_turns.weather == BattleWeather.SANDSTORM:
            modifier *= 0.8

    # Snow Cloak 0.8 - if the target has it and the weather is hail or snow
    if target.abilities.has_ability("snow_cloak"):
        if battle_state.weather_turns.weather in [BattleWeather.HAIL, BattleWeather.SNOW]:
            modifier *= 0.8

    # Victory Star 1.1 - if the user or allies have it - this is multiplied per holder

    # Compound Eyes 1.3 - if the user has it (ability)
    if user.abilities.has_ability("compound_eyes"):
        modifier *= 1.3

    # Bright Powder 0.9 - if the target is holding it
    if target.held_item == "bright_powder":
        modifier *= 0.9

    # Lax Incense 0.9 - if the target is holding it
    if target.held_item == "lax_incense":
        modifier *= 0.9

    # Wide Lens 1.1 - if the user is holding it
    if user.held_item == "wide_lens":
        modifier *= 1.1

    # Zoom Lens 1.2 - if the user is holding it and moves after the target - requires turn order check which needs to implimented


    return modifier

def _get_accuracy_stage_modifier(user: BattleMon, target: BattleMon) -> float:
    accuracy_stage_target = target.evasion_stage
    accuracy_stage_user = user.accuracy_stage

    if accuracy_stage_user > 6:
        accuracy_stage_user = 6
    elif accuracy_stage_user < -6:
        accuracy_stage_user = -6
    if accuracy_stage_target > 6:
        accuracy_stage_target = 6
    elif accuracy_stage_target < -6:
        accuracy_stage_target = -6
    
    stage_difference = accuracy_stage_user - accuracy_stage_target

    match stage_difference:
        case 6:
            return 3.0
        case 5:
            return 2.5
        case 4:
            return 2.0
        case 3:
            return 1.67
        case 2:
            return 1.5
        case 1:
            return 1.33
        case 0:
            return 1.0
        case -1:
            return 0.75
        case -2:
            return 0.67
        case -3:
            return 0.5
        case -4:
            return 0.4
        case -5:
            return 0.33
        case -6:
            return 0.25
        case _:
            return 1.0
    return 1.0

def _get_micle_berry_modifier(user: BattleMon) -> float:
    # pokemon eating the micle berry
    if user.held_item == "micle_berry":
        if user.abilities.has_ability("guts"):
            if user.current_hp <= (user.max_hp / 2):
                print ("Micle Berry consumed to boost accuracy!")
                user.held_item = None  # Consume the berry
                return 1.2
        if user.current_hp <= (user.max_hp / 4):
            print ("Micle Berry consumed to boost accuracy!")
            user.held_item = None  # Consume the berry
            return 1.2
        
    return 1.0

def calculate_accuracy_hit(accuracy: float) -> bool:
    roll = random.randint(0, 100)
    return roll <= accuracy