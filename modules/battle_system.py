"""
战斗系统模块 - 龙虾1号实现
"""
import random
from copy import deepcopy
from contracts.ibattle import IBattleSystem
from contracts.types import AttackResult, StatusEffect, DamageType


class BattleSystem(IBattleSystem):
    """战斗系统实现"""
    
    def calculate_damage(self, attacker_attack: int, defender_defense: int,
                         damage_type: str, is_critical: bool = False) -> int:
        """
        计算伤害值
        公式: 伤害 = 攻击方attack * (1 + rand(0,0.2)) - 防御方defense * 0.5
        暴击时 * 1.5，最低为1
        """
        # 随机波动因子 (0 到 0.2)
        random_factor = random.uniform(0, 0.2)
        
        # 基础伤害计算
        base_damage = attacker_attack * (1 + random_factor) - defender_defense * 0.5
        
        # 暴击加成
        if is_critical:
            base_damage *= 1.5
        
        # 最低伤害为1
        return max(1, int(base_damage))
    
    def perform_attack(self, attacker_name: str, attacker_stats: dict,
                       target_name: str, target_stats: dict,
                       damage_type: str) -> AttackResult:
        """
        执行完整攻击流程
        - 自动判定暴击
        - 根据speed差判定miss率
        - 生成AttackResult
        """
        # 解析伤害类型
        try:
            dmg_type = DamageType(damage_type.lower())
        except ValueError:
            dmg_type = DamageType.PHYSICAL
        
        # 获取属性值
        attacker_attack = attacker_stats.get('attack', 10)
        attacker_luck = attacker_stats.get('luck', 5)
        attacker_speed = attacker_stats.get('speed', 10)
        
        defender_defense = target_stats.get('defense', 5)
        defender_speed = target_stats.get('speed', 10)
        
        # 计算闪避率：速度差决定miss率
        # speed差越大，miss率越高（攻击方慢，防御方快容易闪避）
        speed_diff = defender_speed - attacker_speed
        # 基础miss率5%，每点速度差增加/减少2%，范围0%-30%
        miss_rate = 0.05 + speed_diff * 0.02
        miss_rate = max(0.0, min(0.30, miss_rate))
        
        # 判断是否miss
        is_miss = random.random() < miss_rate
        
        if is_miss:
            return AttackResult(
                attacker_name=attacker_name,
                target_name=target_name,
                damage=0,
                damage_type=dmg_type,
                is_critical=False,
                is_miss=True,
                status_applied=None,
                message=f"{attacker_name} 的攻击被 {target_name} 闪避了！"
            )
        
        # 判定暴击
        is_critical = self.check_critical(attacker_luck)
        
        # 计算伤害
        damage = self.calculate_damage(
            attacker_attack, defender_defense, damage_type, is_critical
        )
        
        # 生成消息
        if is_critical:
            message = f"{attacker_name} 对 {target_name} 发动了暴击！造成 {damage} 点{dmg_type.value}伤害！"
        else:
            message = f"{attacker_name} 对 {target_name} 造成了 {damage} 点{dmg_type.value}伤害。"
        
        return AttackResult(
            attacker_name=attacker_name,
            target_name=target_name,
            damage=damage,
            damage_type=dmg_type,
            is_critical=is_critical,
            is_miss=False,
            status_applied=None,
            message=message
        )
    
    def check_critical(self, luck: int) -> bool:
        """
        根据幸运值判断暴击
        公式: 暴击率 = luck * 0.5%，最高15%
        """
        critical_rate = luck * 0.005  # 0.5% = 0.005
        critical_rate = min(0.15, critical_rate)  # 最高15%
        
        return random.random() < critical_rate
    
    def apply_status(self, status: StatusEffect, target_stats: dict) -> dict:
        """
        将状态效果应用到目标属性
        返回修改后的stats副本
        """
        # 深拷贝避免修改原数据
        modified_stats = deepcopy(target_stats)
        
        # 应用属性修改器
        if status.stat_modifier:
            for stat_name, modifier in status.stat_modifier.items():
                if stat_name in modified_stats:
                    # modifier可以是加法或乘法，这里支持两种格式
                    if isinstance(modifier, dict):
                        if 'add' in modifier:
                            modified_stats[stat_name] += modifier['add']
                        if 'multiply' in modifier:
                            modified_stats[stat_name] = int(
                                modified_stats[stat_name] * modifier['multiply']
                            )
                    else:
                        # 简单数值直接加减
                        modified_stats[stat_name] += modifier
        
        return modified_stats
    
    def process_turn_effects(self, active_statuses: list) -> list:
        """
        每回合处理状态效果
        - 状态扣血（通过stat_modifier或damage_per_turn）
        - 持续时间减1
        - 返回仍存活的状态列表
        """
        surviving_statuses = []
        
        for status in active_statuses:
            # 持续时间减1
            status.duration -= 1
            
            # 如果还有剩余回合，保留状态
            if status.duration > 0:
                surviving_statuses.append(status)
        
        return surviving_statuses
