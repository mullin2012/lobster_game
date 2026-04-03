"""
战斗系统接口契约 - 龙虾1（BattleSystem）必须实现
"""
from abc import ABC, abstractmethod
from contracts.types import AttackResult, StatusEffect


class IBattleSystem(ABC):
    @abstractmethod
    def calculate_damage(self, attacker_attack: int, defender_defense: int,
                         damage_type: str, is_critical: bool = False) -> int:
        """计算伤害值"""
        ...

    @abstractmethod
    def perform_attack(self, attacker_name: str, attacker_stats: dict,
                       target_name: str, target_stats: dict,
                       damage_type: str) -> AttackResult:
        """执行一次攻击，返回标准结果"""
        ...

    @abstractmethod
    def check_critical(self, luck: int) -> bool:
        """根据幸运值判断暴击"""
        ...

    @abstractmethod
    def apply_status(self, status: StatusEffect, target_stats: dict) -> dict:
        """给目标施加状态效果，返回修改后的 stats"""
        ...

    @abstractmethod
    def process_turn_effects(self, active_statuses: list) -> list:
        """处理一回合的状态效果（扣血、倒计时），返回仍有效的状态"""
        ...
