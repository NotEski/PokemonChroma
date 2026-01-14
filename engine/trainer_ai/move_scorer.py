from math import ceil
from shared.pokemon.move import BaseMove
from engine.repositories.repository import move_repository
from shared.pokemon.pokemon import BattleMon
from shared.battle.type_effectiveness import get_effectiveness_level, effectiveness_multiplier, EffectivenessLevel
from engine.battle.damage_calculator import get_stab_modifier




# TODO function_code need to be implimented with my system





def score_move_advanced(move: BaseMove, user: BattleMon, target: BattleMon, skill: int) -> int:
    base_score = 100

    if move in move_repository.damaging_moves:
        base_score += score_damage_potential(move, user, target, skill)
        base_score += score_type_effectiveness(move, user, target)
        base_score += score_stab_bonus(move, user)
        base_score += score_crit_potential(move, user, target)
    
    if move in move_repository.status_moves:
        base_score += score_status_utility(move, user, target, skill)
    
    if move.function_code.startswith("RaiseUser"):
        base_score += score_setup_value(move, user, target, skill)
    
    base_score += score_priority(move, user, target)
    base_score += score_accuracy(move, skill)
    base_score += score_recoil_risk(move, user)
    base_score += score_secondary_effects(move, user, target)
    
    return base_score


def score_damage_potential(move: BaseMove, user: BattleMon, target: BattleMon, skill: int) -> int:
    score = 0
    bp = calculate_effective_power(move, user, target)
    
    if bp > 0:
        score += ceil(bp / 10.0)
    
    if skill >= 60:
        rough_damage = calculate_rough_damage(move, user, target, bp)
        if rough_damage >= target.current_hp:
            score += 100
        elif rough_damage >= target.current_hp * 0.7:
            score += 50
        elif rough_damage >= target.current_hp * 0.4:
            score += 25
    
    return score


def score_type_effectiveness(move: BaseMove, target: BattleMon) -> int:
    type_mod: EffectivenessLevel = get_effectiveness_level(effectiveness_multiplier(move.type, target.types))
    
    if type_mod == EffectivenessLevel.SUPER_EFFECTIVE:
        return 40
    elif type_mod == EffectivenessLevel.NOT_EFFECTIVE:
        return -30
    elif type_mod == EffectivenessLevel.NO_EFFECT:
        return -200
    return 0


def score_stab_bonus(move: BaseMove, user: BattleMon) -> int:
    if get_stab_modifier(user, move) > 0:
        return 20
    return 0


def score_crit_potential(move: BaseMove, user: BattleMon, target: BattleMon) -> int:
    score = 0
    
    if target.abilities.has_active_ability("battle_armor") or target.abilities.has_active_ability("shell_armor"):
        return 0
    
    is_high_crit = move.high_critical_hit
    is_always_crit = move.always_critical_hit
    
    if user.effects.get("FocusEnergy", 0) > 0:
        if is_high_crit:
            score += 50
        elif not is_always_crit:
            score += 20
    elif is_high_crit:
        score += 15
    
    ignore_target_def = (target.stat_stages.defense > 0 and move.physical) or (target.stat_stages.special_defense > 0 and move.special)
    ignore_user_debuff = (user.stat_stages.attack < 0 and move.physical) or (user.stat_stages.special_attack < 0 and move.special)
    
    if ignore_target_def or ignore_user_debuff:
        score += 30
    
    return score


def score_status_utility(move: BaseMove, user: BattleMon, target: BattleMon, skill: int) -> int:
    score = 0
    
    function_code = move.function_code
    
    if function_code == "AddSpikesToFoeSide":
        score += 60
    elif function_code == "AddStealthRocksToFoeSide":
        score += 70
    elif function_code == "AddToxicSpikesToFoeSide":
        score += 50
    elif function_code == "AddStickyWebToFoeSide":
        score += 60
    elif function_code == "StartWeakenPhysicalDamageAgainstUserSide":
        score += 50
    elif function_code == "StartWeakenSpecialDamageAgainstUserSide":
        score += 50
    elif function_code == "StartWeakenDamageAgainstUserSideIfHail":
        score += 60
    elif function_code in ["HealUserHalfOfTotalHP", "HealUserDependingOnWeather"]:
        hp_percent = user.current_hp / user.max_hp
        if hp_percent < 0.3:
            score += 80
        elif hp_percent < 0.5:
            score += 50
        elif hp_percent < 0.7:
            score += 20
    elif function_code == "ParalyzeTarget":
        score += 40
    elif function_code == "BurnTarget":
        score += 50
    elif function_code in ["PoisonTarget", "BadPoisonTarget"]:
        score += 45
    elif function_code in ["LowerTargetAttack1", "LowerTargetAttack2"]:
        score += 30
    elif function_code in ["LowerTargetSpeed1", "LowerTargetSpeed2"]:
        score += 35
    elif function_code in ["LowerTargetDefense1", "LowerTargetDefense2"]:
        score += 25
    
    return score


def score_setup_value(move: BaseMove, user: BattleMon, target: BattleMon, skill: int) -> int:
    if skill < 55:
        return 0
    
    score = 0
    
    if is_safe_to_setup(user, target):
        total_boosts = 1
        if move.function_code.startswith("RaiseUser"):
            import re
            matches = re.findall(r'\d+', move.function_code)
            if matches:
                total_boosts = int(matches[-1])
        
        score += total_boosts * 20
        
        if user.current_hp > user.max_hp * 0.7:
            score += 30
    else:
        score -= 40
    
    return score


def score_priority(move: BaseMove, user: BattleMon, target: BattleMon) -> int:
    if move.priority <= 0:
        return 0
    
    score = move.priority * 15
    
    if user.current_hp <= user.max_hp * 0.33 and target.stat_speed > user.stat_speed:
        score += 40
    
    if move.priority > 0:
        score += 30 if target.stat_speed > user.stat_speed else 0
        
        rough_damage = calculate_rough_damage(move, user, target)
        if rough_damage >= target.current_hp:
            score += 40
    
    return score


def score_accuracy(move: BaseMove, skill: int) -> int:
    accuracy = move.accuracy
    if accuracy == 0:
        return 0
    
    if accuracy < 70:
        return -40
    elif accuracy < 85:
        return -20
    elif accuracy < 95:
        return -10
    
    return 0


def score_recoil_risk(move: BaseMove, user: BattleMon) -> int:
    if not move.recoil_move:
        return 0
    
    hp_percent = user.current_hp / user.max_hp
    
    if hp_percent < 0.3:
        return -50
    elif hp_percent < 0.5:
        return -25
    else:
        return -10


def score_secondary_effects(move: BaseMove, user: BattleMon, target: BattleMon) -> int:
    score = 0
    
    if move.base_move in move_repository.flinching_moves and user.stat_speed > target.stat_speed:
        score += 20
    
    if move.function_code.startswith("LowerTarget"):
        score += 20
    
    if any(code in move.function_code for code in ["ParalyzeTarget", "BurnTarget", "PoisonTarget", "SleepTarget", "FreezeTarget"]):
        score += move.additional_effect / 2
    
    return score


def calculate_rough_damage(move: BaseMove, user: BattleMon, target: BattleMon, override_bp: int = None) -> int:
    if not move.base_move in move_repository.damaging_moves:
        return 0
    
    bp = override_bp or move.power
    if bp == 0:
        return 0
    
    atk = user.stat_attack if move.physical else user.stat_special_attack
    defense = target.stat_defense if move.physical else target.stat_special_defense
    
    damage = ((2 * user.level / 5.0 + 2) * bp * atk / defense / 50 + 2)
    
    return int(damage)


def is_safe_to_setup(user: BattleMon, target: BattleMon) -> bool:
    if user.current_hp < user.max_hp * 0.5:
        return False
    
    if target.stat_speed > user.stat_speed * 1.5:
        return False
    
    for move in target.move_set.list_moves():
        if move.base_move in move_repository.damaging_moves:
            continue
        else:
            return True
        
    return False


def calculate_effective_power(move: BaseMove, user: BattleMon, target: BattleMon) -> int:
    bp = move.power
    if bp == 0:
        return 0
    
    if "AlwaysCriticalHit" in move.function_code:
        is_immune = (target.has_active_ability("battle_armor") or 
                     target.has_active_ability("shell_armor"))
        if not is_immune:
            bp = int(bp * 1.5)
    
    if move.multi_hit_move or move.function_code == "HitTwoTimes":
        if move.multi_hit_move:
            if user.has_active_ability("skill_link"):
                return bp * 5
            elif user.has_active_item("loaded_dice"):
                return bp * 4
            else:
                return bp * 3
        elif move.function_code == "HitTwoTimes":
            return bp * 2
    
    return bp
