"""
共享数据类型定义 - 所有模块必须使用这些类型
三只龙虾的接口契约，不可修改！
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DamageType(Enum):
    PHYSICAL = "physical"
    MAGIC = "magic"
    FIRE = "fire"
    ICE = "ice"
    POISON = "poison"


class Rarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Vector2:
    x: float = 0.0
    y: float = 0.0


@dataclass
class Stats:
    hp: int = 100
    max_hp: int = 100
    mp: int = 50
    max_mp: int = 50
    attack: int = 10
    defense: int = 5
    speed: int = 10
    luck: int = 5


@dataclass
class StatusEffect:
    name: str
    duration: int  # turns remaining
    damage_per_turn: int = 0
    stat_modifier: dict = field(default_factory=dict)


@dataclass
class AttackResult:
    """战斗系统返回的标准攻击结果"""
    attacker_name: str
    target_name: str
    damage: int
    damage_type: DamageType
    is_critical: bool = False
    is_miss: bool = False
    status_applied: Optional[StatusEffect] = None
    message: str = ""


@dataclass
class MonsterTemplate:
    """怪物模板 - 由 MonsterSystem 定义"""
    name: str
    base_stats: Stats
    attacks: list  # list of attack names
    loot_table: list  # list of item names
    experience_reward: int
    gold_reward: int


@dataclass
class ItemTemplate:
    """物品模板 - 由 InventorySystem 定义"""
    name: str
    item_type: str  # "weapon", "armor", "potion", "scroll"
    rarity: Rarity
    description: str
    stat_bonus: dict = field(default_factory=dict)  # e.g. {"attack": 5}
    heal_amount: int = 0
    value: int = 0
