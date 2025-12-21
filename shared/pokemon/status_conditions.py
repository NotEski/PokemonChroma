from enum import Enum


class StatusCondition(Enum):
    NONE = "none"

    # Volatile status conditions
    CONFUSION = "confusion"
    CURSE = "curse"
    DISABLE = "disable"
    EMBARGO = "embargo"
    FLINCH = "flinch"
    HEAL_BLOCK = "heal_block"
    INFATUATION = "infatuation"
    INGRAIN = "ingrain"
    LEECH_SEED = "leech_seed"
    NIGHTMARE = "nightmare"
    NO_TYPE_IMMUNITY = "no_type_immunity"
    PERISH_SONG = "perish_song"
    SILENCE = "silence"
    TAR_SHOT = "tar_shot"
    TORMENT = "torment"
    TRAP = "trap"
    UNKNOWN = "unknown"
    YAWN = "yawn"

    # Non-volatile status conditions
    BURN = "burn"
    FREEZE = "freeze"
    PARALYSIS = "paralysis"
    POISON = "poison"
    BADLY_POISON = "badly_poison"
    SLEEP = "sleep"
    


volatile_status_conditions = {
    StatusCondition.CONFUSION,
    StatusCondition.FLINCH,
    StatusCondition.TRAP,
    StatusCondition.LEECH_SEED,
    StatusCondition.NIGHTMARE,
    StatusCondition.PERISH_SONG,
    StatusCondition.INFATUATION,
    StatusCondition.TORMENT,
    StatusCondition.CURSE,
    StatusCondition.INGRAIN,
    StatusCondition.HEAL_BLOCK,
    StatusCondition.YAWN,
    StatusCondition.EMBARGO,
    StatusCondition.SILENCE,
    StatusCondition.TAR_SHOT,
}
non_volatile_status_conditions = {
    StatusCondition.PARALYSIS,
    StatusCondition.POISON,
    StatusCondition.BADLY_POISON,
    StatusCondition.BURN,
    StatusCondition.FREEZE,
    StatusCondition.SLEEP,
}



# Non-volatile status conditions affect the Pokémon outside of battle as well,
# while volatile status conditions are removed when the Pokémon is switched out.