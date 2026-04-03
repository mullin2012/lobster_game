"""
怪物系统接口契约 - 龙虾2（MonsterSystem）必须实现
"""
from abc import ABC, abstractmethod
from contracts.types import Stats, MonsterTemplate, StatusEffect


class IMonsterSystem(ABC):
    @abstractmethod
    def create_monster(self, template: MonsterTemplate, level: int) -> dict:
        """根据模板创建怪物实例，level会影响属性缩放"""
        ...

    @abstractmethod
    def get_monster_attack(self, monster: dict, target: dict) -> dict:
        """怪物选择攻击方式，返回包含攻击名和目标的结果"""
        ...

    @abstractmethod
    def apply_damage_to_monster(self, monster: dict, damage: int,
                                damage_type: str) -> dict:
        """对怪物造成伤害，返回更新后的怪物状态"""
        ...

    @abstractmethod
    def is_monster_alive(self, monster: dict) -> bool:
        """判断怪物是否存活"""
        ...

    @abstractmethod
    def monster_die(self, monster: dict) -> dict:
        """怪物死亡处理，返回战利品信息 {items: [], gold: int, xp: int}"""
        ...

    @abstractmethod
    def generate_loot(self, monster: dict) -> list:
        """根据掉落表生成战利品"""
        ...
