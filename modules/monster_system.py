"""
怪物系统模块 - 龙虾2号实现
"""
import random
from copy import deepcopy
from contracts.imonster import IMonsterSystem
from contracts.types import Stats, MonsterTemplate, StatusEffect


class MonsterSystem(IMonsterSystem):
    """怪物系统实现"""
    
    def create_monster(self, template: MonsterTemplate, level: int) -> dict:
        """
        根据模板创建怪物实例，level会影响属性缩放
        每级增加约10%基础属性
        """
        # 等级缩放因子：每级增加10%
        level_scale = 1 + (level - 1) * 0.1
        
        # 缩放基础属性
        base_stats = template.base_stats
        scaled_stats = {
            'hp': int(base_stats.hp * level_scale),
            'max_hp': int(base_stats.hp * level_scale),
            'mp': int(base_stats.mp * level_scale),
            'max_mp': int(base_stats.mp * level_scale),
            'attack': int(base_stats.attack * level_scale),
            'defense': int(base_stats.defense * level_scale),
            'speed': int(base_stats.speed * level_scale),
            'luck': int(base_stats.luck * level_scale)
        }
        
        # 创建怪物实例
        monster = {
            'name': template.name,
            'level': level,
            'stats': scaled_stats,
            'attacks': deepcopy(template.attacks),
            'loot_table': deepcopy(template.loot_table),
            'experience_reward': int(template.experience_reward * level_scale),
            'gold_reward': int(template.gold_reward * level_scale),
            'status_effects': [],
            'is_alive': True
        }
        
        return monster
    
    def get_monster_attack(self, monster: dict, targets: list) -> dict:
        """
        怪物选择攻击方式
        AI决策：优先攻击HP最低的目标，或随机选择
        
        Args:
            monster: 怪物实例
            targets: 目标列表，每个目标包含 {'name': str, 'stats': dict}
        
        Returns:
            {'attack_name': str, 'target': dict}
        """
        if not targets:
            return {'attack_name': None, 'target': None}
        
        # 获取怪物可用的攻击
        attacks = monster.get('attacks', [])
        if not attacks:
            # 默认攻击
            attacks = ['普通攻击']
        
        # 随机选择攻击方式
        attack_name = random.choice(attacks)
        
        # AI决策：优先攻击HP最低的目标
        # 70%概率攻击HP最低的目标，30%概率随机选择
        if random.random() < 0.7 and len(targets) > 1:
            # 找到HP最低的目标
            target = min(targets, key=lambda t: t.get('stats', {}).get('hp', 100))
        else:
            # 随机选择目标
            target = random.choice(targets)
        
        return {
            'attack_name': attack_name,
            'target': target
        }
    
    def apply_damage_to_monster(self, monster: dict, damage: int,
                                 damage_type: str) -> dict:
        """
        对怪物造成伤害，返回更新后的怪物状态
        """
        # 深拷贝避免修改原数据
        updated_monster = deepcopy(monster)
        
        # 应用伤害
        stats = updated_monster.get('stats', {})
        current_hp = stats.get('hp', 0)
        
        # 计算实际伤害（考虑防御）
        # 这里简单处理，防御可以减少部分伤害
        defense = stats.get('defense', 0)
        actual_damage = max(1, damage - defense // 2)
        
        # 扣除HP
        new_hp = max(0, current_hp - actual_damage)
        stats['hp'] = new_hp
        
        # 检查是否死亡
        if new_hp <= 0:
            updated_monster['is_alive'] = False
        
        # 记录伤害信息
        updated_monster['last_damage'] = {
            'amount': actual_damage,
            'type': damage_type,
            'original_damage': damage
        }
        
        return updated_monster
    
    def is_monster_alive(self, monster: dict) -> bool:
        """
        判断怪物是否存活
        """
        # 优先检查显式的存活状态
        if 'is_alive' in monster:
            return monster['is_alive']
        
        # 兼容：检查HP
        stats = monster.get('stats', {})
        return stats.get('hp', 0) > 0
    
    def monster_die(self, monster: dict) -> dict:
        """
        怪物死亡处理，返回战利品信息
        {items: [], gold: int, xp: int}
        """
        # 标记死亡
        monster['is_alive'] = False
        
        # 生成战利品
        items = self.generate_loot(monster)
        
        # 获取金币和经验奖励
        gold = monster.get('gold_reward', 0)
        xp = monster.get('experience_reward', 0)
        
        return {
            'items': items,
            'gold': gold,
            'xp': xp
        }
    
    def generate_loot(self, monster: dict) -> list:
        """
        根据掉落表生成战利品
        基于概率系统，稀有物品掉率低
        """
        loot_table = monster.get('loot_table', [])
        dropped_items = []
        
        # 怪物等级影响掉落率
        level = monster.get('level', 1)
        level_bonus = 0.02 * (level - 1)  # 每级增加2%掉落率
        
        # 怪物幸运值影响掉落
        luck = monster.get('stats', {}).get('luck', 5)
        luck_bonus = luck * 0.01  # 每点幸运增加1%掉落率
        
        for loot_entry in loot_table:
            # 掉落表条目格式：
            # {'name': '物品名', 'rarity': 'common'/'rare'/'epic', 'drop_rate': 0.3}
            # 或者简单的字符串 '物品名'
            
            if isinstance(loot_entry, str):
                # 简单物品，默认20%掉率
                item_name = loot_entry
                base_drop_rate = 0.2
                item_rarity = 'common'
            elif isinstance(loot_entry, dict):
                item_name = loot_entry.get('name', '未知物品')
                base_drop_rate = loot_entry.get('drop_rate', 0.2)
                item_rarity = loot_entry.get('rarity', 'common')
            else:
                continue
            
            # 根据稀有度调整掉率
            rarity_multipliers = {
                'common': 1.0,
                'uncommon': 0.7,
                'rare': 0.4,
                'epic': 0.2,
                'legendary': 0.05
            }
            rarity_mult = rarity_multipliers.get(item_rarity, 1.0)
            
            # 最终掉率 = 基础掉率 * 稀有度系数 * 等级加成 * 幸运加成
            final_drop_rate = base_drop_rate * rarity_mult * (1 + level_bonus) * (1 + luck_bonus)
            final_drop_rate = min(1.0, final_drop_rate)  # 最高100%
            
            # 判定是否掉落
            if random.random() < final_drop_rate:
                dropped_items.append({
                    'name': item_name,
                    'rarity': item_rarity
                })
        
        return dropped_items


# ============ 预定义怪物模板 ============

def create_monster_templates():
    """创建一些预定义的怪物模板供游戏使用"""
    templates = {}
    
    # 史莱姆 - 最基础的怪物
    templates['slime'] = MonsterTemplate(
        name='史莱姆',
        base_stats=Stats(
            hp=30, max_hp=30,
            mp=0, max_mp=0,
            attack=5, defense=2,
            speed=5, luck=2
        ),
        attacks=['粘液攻击', '冲撞'],
        loot_table=[
            {'name': '粘液', 'rarity': 'common', 'drop_rate': 0.6},
            {'name': '小治疗药水', 'rarity': 'uncommon', 'drop_rate': 0.2}
        ],
        experience_reward=10,
        gold_reward=5
    )
    
    # 哥布林 - 常见怪物
    templates['goblin'] = MonsterTemplate(
        name='哥布林',
        base_stats=Stats(
            hp=50, max_hp=50,
            mp=10, max_mp=10,
            attack=12, defense=5,
            speed=12, luck=8
        ),
        attacks=['匕首刺击', '投石', '偷窃'],
        loot_table=[
            {'name': '破旧匕首', 'rarity': 'common', 'drop_rate': 0.4},
            {'name': '金币袋', 'rarity': 'common', 'drop_rate': 0.5},
            {'name': '小治疗药水', 'rarity': 'uncommon', 'drop_rate': 0.3}
        ],
        experience_reward=25,
        gold_reward=15
    )
    
    # 骷髅战士 - 不死生物
    templates['skeleton'] = MonsterTemplate(
        name='骷髅战士',
        base_stats=Stats(
            hp=70, max_hp=70,
            mp=5, max_mp=5,
            attack=18, defense=8,
            speed=8, luck=3
        ),
        attacks=['骨剑斩击', '骨盾防御', '死灵一击'],
        loot_table=[
            {'name': '骨头碎片', 'rarity': 'common', 'drop_rate': 0.7},
            {'name': '生锈铁剑', 'rarity': 'uncommon', 'drop_rate': 0.3},
            {'name': '骷髅护手', 'rarity': 'rare', 'drop_rate': 0.1}
        ],
        experience_reward=40,
        gold_reward=25
    )
    
    # 宝箱怪 - 惊喜怪物
    templates['mimic'] = MonsterTemplate(
        name='宝箱怪',
        base_stats=Stats(
            hp=100, max_hp=100,
            mp=20, max_mp=20,
            attack=25, defense=15,
            speed=5, luck=15
        ),
        attacks=['咬合', '舌鞭', '吞咽', '假死'],
        loot_table=[
            {'name': '宝藏钥匙', 'rarity': 'rare', 'drop_rate': 0.3},
            {'name': '随机卷轴', 'rarity': 'uncommon', 'drop_rate': 0.5},
            {'name': '神秘宝珠', 'rarity': 'epic', 'drop_rate': 0.15},
            {'name': '传说武器碎片', 'rarity': 'legendary', 'drop_rate': 0.02}
        ],
        experience_reward=100,
        gold_reward=80
    )
    
    # 火龙 - 强力BOSS
    templates['dragon'] = MonsterTemplate(
        name='火焰巨龙',
        base_stats=Stats(
            hp=500, max_hp=500,
            mp=200, max_mp=200,
            attack=80, defense=40,
            speed=15, luck=20
        ),
        attacks=['龙息', '龙爪', '尾击', '火焰吐息', '毁灭俯冲'],
        loot_table=[
            {'name': '龙鳞', 'rarity': 'rare', 'drop_rate': 0.8},
            {'name': '龙牙', 'rarity': 'epic', 'drop_rate': 0.4},
            {'name': '火焰精华', 'rarity': 'epic', 'drop_rate': 0.3},
            {'name': '龙之心', 'rarity': 'legendary', 'drop_rate': 0.1},
            {'name': '巨龙宝剑', 'rarity': 'legendary', 'drop_rate': 0.05}
        ],
        experience_reward=500,
        gold_reward=300
    )
    
    return templates


# 模块级单例模板库
MONSTER_TEMPLATES = create_monster_templates()
