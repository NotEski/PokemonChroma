from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ItemAttribute(Enum):
    CONSUMABLE = "consumable"
    COUNTABLE = "countable"
    HOLDABLE_ACTIVE = "holdable_active"
    HOLDABLE_PASSIVE = "holdable_passive"
    HOLDABLE = "holdable"
    UNDERGROUND = "underground"
    USABLE_IN_BATTLE = "usable_in_battle"
    USABLE_OVERWORLD = "usable_overworld"

class ItemCategory(Enum):
    ALL_MACHINES = "all_machines"
    ALL_MAIL = "all_mail"
    APRICORN_BALLS = "apricorn_balls"
    APRICORN_BOX = "apricorn_box"
    BAD_HELD_ITEMS = "bad_held_items"
    BAKING_ONLY = "baking_only"
    CATCHING_BONUS = "catching_bonus"
    CATCHING_ONLY = "catching_only"
    CHOICE = "choice"
    COLLECTIBLES = "collectibles"
    CURRY_INGREDIENTS = "curry_ingredients"
    DATA_CARDS = "data_cards"
    DEX_COMPLETION = "dex_completion"
    DYNAMAX_CRYSTALS = "dynamax_crystals"
    EFFORT_DROP = "effort_drop"
    EFFORT_TRAINING = "effort_training"
    EVENT_ITEMS = "event_items"
    EVOLUTION = "evolution"
    FLUTES = "flutes"
    GAMEPLAY = "gameplay"
    HEALING = "healing"
    HELD_ITEMS = "held_items"
    IN_A_PINCH = "in_a_pinch"
    JEWELS = "jewels"
    LOOT = "loot"
    MEDICINE = "medicine"
    MEGA_STONES = "mega_stones"
    MEMORIES = "memories"
    MIRACLE_SHOOTER = "miracle_shooter"
    MULCH = "mulch"
    NATURE_MINTS = "nature_mints"
    OTHER = "other"
    PICKY_HEALING = "picky_healing"
    PICNIC = "picnic"
    PLATES = "plates"
    PLOT_ADVANCEMENT = "plot_advancement"
    PP_RECOVERY = "pp_recovery"
    REVIVAL = "revival"
    SANDWICH_INGREDIENTS = "sandwich_ingredients"
    SCARVES = "scarves"
    SPECIAL_BALLS = "special_balls"
    SPECIES_CANDIES = "species_candies"
    SPECIES_SPECIFIC = "species_specific"
    SPELUNKING = "spelunking"
    STANDARD_BALLS = "standard_balls"
    STAT_BOOSTS = "stat_boosts"
    STATUS_CURES = "status_cures"
    TERA_SHARD = "tera_shard"
    TM_MATERIALS = "tm_materials"
    TRAINING = "training"
    TYPE_ENHANCEMENT = "type_enhancement"
    TYPE_PROTECTION = "type_protection"
    UNUSED = "unused"
    VITAMINS = "vitamins"
    Z_CRYSTALS = "z_crystals"

class ItemPocket(Enum):
    BATTLE = "battle"
    BERRIES = "berries"
    KEY = "key"
    MACHINES = "machines"
    MAIL = "mail"
    MEDICINE = "medicine"
    MISC = "misc"
    POKEBALLS = "pokeballs"

class ItemFlingEffect(Enum):
    BADLY_POISON = "badly_poison"
    BERRY_EFFECT = "berry_effect"
    BURN = "burn"
    FLINCH = "flinch"
    HERB_EFFECT = "herb_effect"
    PARALYZE = "paralyze"
    POISON = "poison"

class Item(BaseModel):
    name: str
    display_name: str
    index: int
    description: str
    cost: int = Field(ge=0, default=0)
    attributes: List[ItemAttribute] = Field(default_factory=list)
    fling_effect: Optional[ItemFlingEffect] = None
    fling_power: Optional[int] = None
    baby_trigger_for: Optional[int] = None
    category: ItemCategory
    held_by_pokemon: List[str] = Field(default_factory=list)
    pocket: Optional[ItemPocket] = None

    def after_move_effect(self, pokemon, move, target) -> None:
        """Called after the Pokémon uses a move."""
        pass

    def on_consume(self, pokemon) -> None:
        """Called when the item is consumed by the Pokémon."""
        pass

    def on_switch_in(self, pokemon) -> None:
        """Called when the Pokémon switches in."""
        pass

    def on_switch_out(self, pokemon) -> None:
        """Called when the Pokémon switches out."""
        pass

    def on_faint(self, pokemon) -> None:
        """Called when the Pokémon faints."""
        pass

    def on_damage_taken(self, pokemon, damage) -> Optional[int]:
        """Called when the Pokémon takes damage."""
        return None
    
    def on_contact(self, pokemon, attacker) -> None:
        """Called when the Pokémon is hit by a contact move."""
        pass

    def modify_stat(self, pokemon, stat_name: str, amount: int) -> Optional[int]:
        """Modify the specified stat of the Pokémon."""
        return None