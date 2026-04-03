"""
物品栏系统 - 龙虾3号实现
提供背包管理、物品使用、装备等功能
"""
import random
from copy import deepcopy
from contracts.iinventory import IInventorySystem
from contracts.types import ItemTemplate, Rarity, Stats


class InventorySystem(IInventorySystem):
    """物品栏系统实现"""

    def create_inventory(self, capacity: int = 20) -> dict:
        """
        创建背包，返回库存字典 {items: [], capacity: int, gold: int}
        
        Args:
            capacity: 背包容量，默认20
            
        Returns:
            包含 items、capacity、gold 的字典
        """
        return {
            "items": [],
            "capacity": capacity,
            "gold": 0
        }

    def add_item(self, inventory: dict, item: dict) -> dict | None:
        """
        添加物品到背包，成功返回更新后的库存，满了返回None
        
        Args:
            inventory: 当前背包字典
            item: 要添加的物品字典（需要包含 name, item_type 等字段）
            
        Returns:
            更新后的背包，满了则返回 None
        """
        # 检查背包是否已满
        if len(inventory["items"]) >= inventory["capacity"]:
            return None
        
        # 深拷贝物品避免引用问题
        item_copy = deepcopy(item)
        
        # 添加到背包
        inventory["items"].append(item_copy)
        
        return inventory

    def remove_item(self, inventory: dict, item_name: str) -> tuple:
        """
        移除物品，返回 (updated_inventory, removed_item)
        
        Args:
            inventory: 当前背包字典
            item_name: 要移除的物品名称（精确匹配）
            
        Returns:
            (updated_inventory, removed_item) 或 (None, None) 如果物品不存在
        """
        # 深拷贝背包避免修改原数据
        updated_inventory = deepcopy(inventory)
        removed_item = None
        
        # 查找并移除物品
        for i, item in enumerate(updated_inventory["items"]):
            if item.get("name") == item_name:
                removed_item = updated_inventory["items"].pop(i)
                return (updated_inventory, removed_item)
        
        # 物品不存在
        return (None, None)

    def use_item(self, inventory: dict, item_name: str, player_stats: Stats) -> tuple:
        """
        使用物品（药水回血、卷轴施法等）
        返回 (updated_inventory, updated_stats, message)
        
        Args:
            inventory: 当前背包字典
            item_name: 要使用的物品名称
            player_stats: 玩家属性
            
        Returns:
            (updated_inventory, updated_stats, message)
        """
        # 深拷贝避免修改原数据
        updated_inventory = deepcopy(inventory)
        updated_stats = deepcopy(player_stats)
        
        # 查找物品
        item = None
        item_index = None
        for i, inv_item in enumerate(updated_inventory["items"]):
            if inv_item.get("name") == item_name:
                item = inv_item
                item_index = i
                break
        
        if item is None:
            return (None, None, f"背包中没有 '{item_name}' 这个物品。")
        
        item_type = item.get("item_type", "")
        message = ""
        
        # 根据物品类型执行不同效果
        if item_type == "potion":
            # 药水：回血
            heal_amount = item.get("heal_amount", 0)
            if heal_amount > 0:
                old_hp = updated_stats.hp
                updated_stats.hp = min(updated_stats.max_hp, updated_stats.hp + heal_amount)
                actual_heal = updated_stats.hp - old_hp
                message = f"使用了 {item['name']}，恢复了 {actual_heal} 点生命值！"
            else:
                message = f"使用了 {item['name']}，但它没有治疗效果。"
            
            # 药水使用后移除
            updated_inventory["items"].pop(item_index)
            
        elif item_type == "scroll":
            # 卷轴：随机效果（这里做一个简单的示例）
            effect = item.get("stat_bonus", {})
            effect_type = random.choice(["atk_up", "def_up", "heal"])
            
            if effect_type == "atk_up":
                bonus = random.randint(2, 5)
                updated_stats.attack += bonus
                message = f"使用了 {item['name']}，攻击力临时提升了 {bonus} 点！"
            elif effect_type == "def_up":
                bonus = random.randint(2, 5)
                updated_stats.defense += bonus
                message = f"使用了 {item['name']}，防御力临时提升了 {bonus} 点！"
            else:
                heal = random.randint(10, 20)
                updated_stats.hp = min(updated_stats.max_hp, updated_stats.hp + heal)
                message = f"使用了 {item['name']}，恢复了 {heal} 点生命值！"
            
            # 卷轴使用后移除
            updated_inventory["items"].pop(item_index)
            
        elif item_type in ["weapon", "armor"]:
            message = f"{item['name']} 是装备，请使用 equip_item 来装备它。"
            return (inventory, player_stats, message)
            
        else:
            message = f"无法使用类型为 '{item_type}' 的物品 '{item['name']}'。"
            return (inventory, player_stats, message)
        
        return (updated_inventory, updated_stats, message)

    def equip_item(self, inventory: dict, item_name: str, player_stats: Stats) -> tuple:
        """
        装备物品，将物品属性永久加到玩家属性
        返回 (updated_inventory, updated_stats, message)
        
        Args:
            inventory: 当前背包字典
            item_name: 要装备的物品名称
            player_stats: 玩家属性
            
        Returns:
            (updated_inventory, updated_stats, message)
        """
        # 深拷贝避免修改原数据
        updated_inventory = deepcopy(inventory)
        updated_stats = deepcopy(player_stats)
        
        # 查找物品
        item = None
        item_index = None
        for i, inv_item in enumerate(updated_inventory["items"]):
            if inv_item.get("name") == item_name:
                item = inv_item
                item_index = i
                break
        
        if item is None:
            return (None, None, f"背包中没有 '{item_name}' 这个物品。")
        
        item_type = item.get("item_type", "")
        stat_bonus = item.get("stat_bonus", {})
        message = ""
        
        # 只有武器和护甲可以装备
        if item_type == "weapon":
            # 武器：加攻击
            attack_bonus = stat_bonus.get("attack", 0)
            updated_stats.attack += attack_bonus
            message = f"装备了 {item['name']}，攻击力 +{attack_bonus}！"
            # 装备后从背包移除
            updated_inventory["items"].pop(item_index)
            
        elif item_type == "armor":
            # 护甲：加防御
            defense_bonus = stat_bonus.get("defense", 0)
            updated_stats.defense += defense_bonus
            message = f"装备了 {item['name']}，防御力 +{defense_bonus}！"
            # 装备后从背包移除
            updated_inventory["items"].pop(item_index)
            
        elif item_type == "potion":
            message = f"{item['name']} 是消耗品，请使用 use_item 来使用它。"
            return (inventory, player_stats, message)
            
        elif item_type == "scroll":
            message = f"{item['name']} 是消耗品，请使用 use_item 来使用它。"
            return (inventory, player_stats, message)
            
        else:
            message = f"无法装备类型为 '{item_type}' 的物品 '{item['name']}'。"
            return (inventory, player_stats, message)
        
        return (updated_inventory, updated_stats, message)

    def get_inventory_summary(self, inventory: dict) -> str:
        """
        返回背包的可读摘要字符串
        
        Args:
            inventory: 背包字典
            
        Returns:
            格式化的背包摘要字符串
        """
        items = inventory.get("items", [])
        capacity = inventory.get("capacity", 0)
        gold = inventory.get("gold", 0)
        
        # 头部信息
        summary_lines = [
            "=" * 30,
            f"📦 背包 ({len(items)}/{capacity})",
            f"💰 金币: {gold}",
            "=" * 30
        ]
        
        if not items:
            summary_lines.append("背包是空的，快去收集物品吧！")
        else:
            summary_lines.append("-" * 30)
            
            # 按物品类型分组显示
            weapons = []
            armors = []
            potions = []
            scrolls = []
            others = []
            
            for item in items:
                item_type = item.get("item_type", "unknown")
                if item_type == "weapon":
                    weapons.append(item)
                elif item_type == "armor":
                    armors.append(item)
                elif item_type == "potion":
                    potions.append(item)
                elif item_type == "scroll":
                    scrolls.append(item)
                else:
                    others.append(item)
            
            # 显示各类型物品
            if weapons:
                summary_lines.append(f"⚔️  武器 ({len(weapons)}):")
                for item in weapons:
                    rarity_emoji = self._get_rarity_emoji(item.get("rarity", "common"))
                    atk = item.get("stat_bonus", {}).get("attack", 0)
                    summary_lines.append(f"   {rarity_emoji} {item['name']} (攻击+{atk})")
            
            if armors:
                summary_lines.append(f"🛡️  护甲 ({len(armors)}):")
                for item in armors:
                    rarity_emoji = self._get_rarity_emoji(item.get("rarity", "common"))
                    defense = item.get("stat_bonus", {}).get("defense", 0)
                    summary_lines.append(f"   {rarity_emoji} {item['name']} (防御+{defense})")
            
            if potions:
                summary_lines.append(f"🧪 药水 ({len(potions)}):")
                for item in potions:
                    rarity_emoji = self._get_rarity_emoji(item.get("rarity", "common"))
                    heal = item.get("heal_amount", 0)
                    summary_lines.append(f"   {rarity_emoji} {item['name']} (恢复+{heal})")
            
            if scrolls:
                summary_lines.append(f"📜 卷轴 ({len(scrolls)}):")
                for item in scrolls:
                    rarity_emoji = self._get_rarity_emoji(item.get("rarity", "common"))
                    summary_lines.append(f"   {rarity_emoji} {item['name']}")
            
            if others:
                summary_lines.append(f"📦 其他 ({len(others)}):")
                for item in others:
                    rarity_emoji = self._get_rarity_emoji(item.get("rarity", "common"))
                    summary_lines.append(f"   {rarity_emoji} {item['name']}")
        
        summary_lines.append("=" * 30)
        
        return "\n".join(summary_lines)

    def _get_rarity_emoji(self, rarity: str) -> str:
        """
        根据稀有度返回对应的emoji
        """
        rarity_map = {
            "common": "⚪",
            "uncommon": "🟢",
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟡"
        }
        return rarity_map.get(rarity, "⚪")


# ============================================================================
# 测试代码
# ============================================================================
if __name__ == "__main__":
    print("🧪 开始测试物品栏系统...\n")
    
    # 创建物品栏系统实例
    inv_system = InventorySystem()
    
    # 1. 测试创建背包
    print("【测试1】创建背包")
    inventory = inv_system.create_inventory(capacity=5)
    print(f"背包容量: {inventory['capacity']}, 初始金币: {inventory['gold']}")
    print(f"初始物品数量: {len(inventory['items'])}")
    print("✅ 通过\n")
    
    # 2. 测试添加物品
    print("【测试2】添加物品")
    test_items = [
        {"name": "铁剑", "item_type": "weapon", "rarity": "common", 
         "stat_bonus": {"attack": 10}, "value": 50},
        {"name": "皮甲", "item_type": "armor", "rarity": "uncommon", 
         "stat_bonus": {"defense": 8}, "value": 80},
        {"name": "生命药水", "item_type": "potion", "rarity": "common", 
         "heal_amount": 30, "value": 20},
        {"name": "魔法卷轴", "item_type": "scroll", "rarity": "rare", 
         "value": 100},
    ]
    
    for item in test_items:
        result = inv_system.add_item(inventory, item)
        if result:
            print(f"  ✅ 添加 {item['name']} 成功")
        else:
            print(f"  ❌ 添加 {item['name']} 失败（背包已满）")
    
    # 3. 测试背包容量限制
    print("\n【测试3】背包容量限制")
    extra_item = {"name": "多余物品", "item_type": "potion", "rarity": "common", 
                  "heal_amount": 10, "value": 5}
    result = inv_system.add_item(inventory, extra_item)
    if result is None:
        print("  ✅ 容量已满，正确拒绝添加")
    else:
        print("  ❌ 应该拒绝但成功了")
    
    # 显示背包状态
    print("\n背包当前状态:")
    print(inv_system.get_inventory_summary(inventory))
    
    # 4. 测试使用药水
    print("\n【测试4】使用药水")
    player_stats = Stats(hp=50, max_hp=100, mp=30, max_mp=50, 
                         attack=15, defense=10, speed=12, luck=8)
    print(f"使用前 HP: {player_stats.hp}/{player_stats.max_hp}")
    
    updated_inv, updated_stats, msg = inv_system.use_item(inventory, "生命药水", player_stats)
    print(f"  {msg}")
    print(f"使用后 HP: {updated_stats.hp}/{updated_stats.max_hp}")
    
    # 5. 测试使用卷轴
    print("\n【测试5】使用卷轴")
    print(f"使用前 攻击: {updated_stats.attack}, 防御: {updated_stats.defense}")
    
    # 重新获取背包（因为上面已经用了药水）
    if updated_inv:
        inventory = updated_inv
    updated_inv, updated_stats2, msg2 = inv_system.use_item(inventory, "魔法卷轴", updated_stats)
    print(f"  {msg2}")
    print(f"使用后 攻击: {updated_stats2.attack}, 防御: {updated_stats2.defense}")
    
    # 6. 测试装备武器
    print("\n【测试6】装备武器")
    print(f"装备前 攻击: {updated_stats2.attack}")
    
    if updated_inv:
        inventory = updated_inv
    updated_inv, updated_stats3, msg3 = inv_system.equip_item(inventory, "铁剑", updated_stats2)
    print(f"  {msg3}")
    print(f"装备后 攻击: {updated_stats3.attack}")
    
    # 7. 测试装备护甲
    print("\n【测试7】装备护甲")
    print(f"装备前 防御: {updated_stats3.defense}")
    
    if updated_inv:
        inventory = updated_inv
    updated_inv, updated_stats4, msg4 = inv_system.equip_item(inventory, "皮甲", updated_stats3)
    print(f"  {msg4}")
    print(f"装备后 防御: {updated_stats4.defense}")
    
    # 8. 测试移除物品
    print("\n【测试8】移除物品")
    new_inv = inv_system.create_inventory()
    inv_system.add_item(new_inv, {"name": "测试物品", "item_type": "potion", "heal_amount": 10})
    updated_new_inv, removed = inv_system.remove_item(new_inv, "测试物品")
    if removed and updated_new_inv is not None:
        print(f"  ✅ 成功移除: {removed['name']}")
        print(f"  剩余物品数: {len(updated_new_inv['items'])}")
    else:
        print("  ❌ 移除失败")
    
    # 9. 最终背包状态
    print("\n【最终背包状态】")
    if updated_inv:
        print(inv_system.get_inventory_summary(updated_inv))
    
    print("\n✅ 所有测试完成！")
