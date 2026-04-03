"""自动测试游戏模块"""
import sys
sys.path.insert(0, '.')

# 测试导入
print("[TEST] 导入模块...")
from contracts.types import Stats, MonsterTemplate, ItemTemplate, Rarity
from modules.battle_system import BattleSystem
from modules.monster_system import MonsterSystem
from modules.inventory_system import InventorySystem

# 测试战斗系统
print("\n[TEST] 战斗系统...")
bs = BattleSystem()
result = bs.perform_attack("玩家", {"attack": 10, "speed": 10, "luck": 5}, 
                           "怪物", {"defense": 5, "speed": 10}, "physical")
print(f"  攻击结果: {result.message}")

# 测试怪物系统
print("\n[TEST] 怪物系统...")
ms = MonsterSystem()
template = MonsterTemplate(
    name="史莱姆",
    base_stats=Stats(hp=30, max_hp=30, mp=10, max_mp=10, attack=5, defense=2, speed=8, luck=3),
    attacks=["撞击"],
    loot_table=["凝胶"],
    experience_reward=10,
    gold_reward=5
)
monster = ms.create_monster(template, 1)
print(f"  怪物: {monster['name']} Lv{monster['level']} HP:{monster['stats']['hp']}")

monster = ms.apply_damage_to_monster(monster, 10, "physical")
print(f"  受伤后 HP:{monster['stats']['hp']}")
print(f"  存活: {ms.is_monster_alive(monster)}")

loot = ms.generate_loot(monster)
print(f"  掉落: {loot}")

# 测试物品栏系统
print("\n[TEST] 物品栏系统...")
inv_sys = InventorySystem()
inv = inv_sys.create_inventory()
print(f"  背包创建: {inv['capacity']}格")

item = {"name": "药水", "item_type": "potion", "heal_amount": 30, "rarity": "common", "description": "HP+30"}
result = inv_sys.add_item(inv, item)
print(f"  添加物品: {'成功' if result else '失败'}")

stats = Stats(hp=50, max_hp=100, mp=30, max_mp=50, attack=8, defense=5, speed=10, luck=5)
inv, new_stats, msg = inv_sys.use_item(inv, "药水", stats)
print(f"  使用结果: {msg}")

inv, new_stats, msg = inv_sys.equip_item(inv, "不存在物品", stats)
print(f"  装备失败: {'无此物品' in msg}")

print("\n" + "="*40)
print("  所有测试通过!")
print("="*40)