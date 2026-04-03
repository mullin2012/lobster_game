"""
物品栏系统接口契约 - 龙虾3（InventorySystem）必须实现
"""
from abc import ABC, abstractmethod
from contracts.types import ItemTemplate, Rarity, Stats


class IInventorySystem(ABC):
    @abstractmethod
    def create_inventory(self, capacity: int = 20) -> dict:
        """创建背包，返回库存字典 {items: [], capacity: int, gold: int}"""
        ...

    @abstractmethod
    def add_item(self, inventory: dict, item: dict) -> dict:
        """添加物品到背包，成功返回更新后的库存，满了返回None"""
        ...

    @abstractmethod
    def remove_item(self, inventory: dict, item_name: str) -> tuple:
        """移除物品，返回 (updated_inventory, removed_item) 或 (None, None)"""
        ...

    @abstractmethod
    def use_item(self, inventory: dict, item_name: str, player_stats: Stats) -> tuple:
        """使用物品（药水回血、卷轴施法等），返回 (updated_inventory, updated_stats, message)"""
        ...

    @abstractmethod
    def equip_item(self, inventory: dict, item_name: str, player_stats: Stats) -> tuple:
        """装备物品，返回 (updated_inventory, updated_stats, message)"""
        ...

    @abstractmethod
    def get_inventory_summary(self, inventory: dict) -> str:
        """返回背包的可读摘要字符串"""
        ...
