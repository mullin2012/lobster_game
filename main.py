"""
[LOBSTER] 龙虾大冒险 - 游戏入口
三只龙虾协作开发的游戏框架
"""
import random
import json
import os
from contracts.types import Stats, MonsterTemplate, ItemTemplate, Rarity, DamageType
from modules.battle_system import BattleSystem
from modules.monster_system import MonsterSystem
from modules.inventory_system import InventorySystem
from modules.scene_system import SceneSystem


# ============ 技能系统 ============
class SkillSystem:
    """技能系统"""
    
    # 技能定义
    SKILLS = {
        # 战士技能
        "冲锋": {
            "mp": 10, 
            "damage_mult": 1.5, 
            "description": "强力一击，伤害x1.5",
            "type": "attack"
        },
        "斩击": {
            "mp": 15, 
            "damage_mult": 2.0, 
            "description": "致命斩击，伤害x2.0",
            "type": "attack"
        },
        "怒吼": {
            "mp": 20, 
            "damage_mult": 0.5, 
            "description": "震怒咆哮，降低敌人防御",
            "type": "debuff"
        },
        # 法师技能
        "火球": {
            "mp": 15, 
            "damage_mult": 2.0, 
            "magic": True,
            "damage_type": "fire",
            "description": "魔法火球，伤害x2.0",
            "type": "magic_attack"
        },
        "冰霜": {
            "mp": 20, 
            "damage_mult": 1.8, 
            "magic": True,
            "damage_type": "ice",
            "description": "冰霜法术，有几率冰冻敌人",
            "type": "magic_attack"
        },
        "治疗": {
            "mp": 25, 
            "heal_amount": 50,
            "description": "恢复50点HP",
            "type": "heal"
        },
        # 盗贼技能
        "背刺": {
            "mp": 15, 
            "damage_mult": 2.5, 
            "description": "背刺弱点，伤害x2.5",
            "type": "attack"
        },
        "隐身": {
            "mp": 20, 
            "description": "下次攻击必定暴击",
            "type": "buff"
        },
        "投毒": {
            "mp": 10, 
            "damage_mult": 1.2, 
            "damage_type": "poison",
            "description": "毒刃攻击，每回合持续伤害",
            "type": "attack"
        },
    }
    
    # 职业对应技能
    CLASS_SKILLS = {
        "warrior": ["冲锋", "斩击", "怒吼"],
        "mage": ["火球", "冰霜", "治疗"],
        "rogue": ["背刺", "隐身", "投毒"],
    }
    
    @classmethod
    def get_skills_for_class(cls, player_class: str) -> list:
        """获取职业对应的技能列表"""
        return cls.CLASS_SKILLS.get(player_class.lower(), [])
    
    @classmethod
    def get_skill_info(cls, skill_name: str) -> dict:
        """获取技能信息"""
        return cls.SKILLS.get(skill_name, {})


# ============ 存档系统 ============
class SaveSystem:
    """存档系统"""
    SAVE_FILE = "savegame.json"
    
    @classmethod
    def save_game(cls, game) -> bool:
        """保存游戏"""
        try:
            # 序列化玩家数据
            save_data = {
                "player": {
                    "name": game.player["name"],
                    "level": game.player["level"],
                    "experience": game.player["experience"],
                    "player_class": game.player.get("player_class", "warrior"),
                    "stats": {
                        "hp": game.player["stats"].hp,
                        "max_hp": game.player["stats"].max_hp,
                        "mp": game.player["stats"].mp,
                        "max_mp": game.player["stats"].max_mp,
                        "attack": game.player["stats"].attack,
                        "defense": game.player["stats"].defense,
                        "speed": game.player["stats"].speed,
                        "luck": game.player["stats"].luck,
                    },
                    "inventory": game.player["inventory"],
                    "equipped": {
                        "weapon": game.equipped.get("weapon", {}).get("name") if game.equipped.get("weapon") else None,
                        "armor": game.equipped.get("armor", {}).get("name") if game.equipped.get("armor") else None,
                    }
                },
                "floor": getattr(game, 'current_floor', 1),
            }
            
            with open(cls.SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"[SAVE] 游戏已保存到 {cls.SAVE_FILE}")
            return True
        except Exception as e:
            print(f"[ERROR] 保存失败: {e}")
            return False
    
    @classmethod
    def load_game(cls, game) -> bool:
        """加载游戏"""
        if not os.path.exists(cls.SAVE_FILE):
            print("[INFO] 没有找到存档文件")
            return False
            
        try:
            with open(cls.SAVE_FILE, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # 恢复玩家数据
            player_data = save_data["player"]
            game.player = {
                "name": player_data["name"],
                "level": player_data["level"],
                "experience": player_data["experience"],
                "player_class": player_data.get("player_class", "warrior"),
                "stats": Stats(
                    hp=player_data["stats"]["hp"],
                    max_hp=player_data["stats"]["max_hp"],
                    mp=player_data["stats"]["mp"],
                    max_mp=player_data["stats"]["max_mp"],
                    attack=player_data["stats"]["attack"],
                    defense=player_data["stats"]["defense"],
                    speed=player_data["stats"]["speed"],
                    luck=player_data["stats"]["luck"],
                ),
                "inventory": player_data["inventory"],
            }
            
            # 恢复装备状态
            equipped = player_data.get("equipped", {})
            game.equipped = {"weapon": None, "armor": None}
            
            # 重新装备物品
            if equipped.get("weapon"):
                game.equip_item(equipped["weapon"])
            if equipped.get("armor"):
                game.equip_item(equipped["armor"])
            
            game.current_floor = save_data.get("floor", 1)
            
            print(f"[LOAD] 游戏已从 {cls.SAVE_FILE} 加载")
            print(f"   玩家: {game.player['name']} (Lv.{game.player['level']})")
            print(f"   职业: {game.player.get('player_class', 'warrior')}")
            print(f"   当前层数: {game.current_floor}")
            return True
        except Exception as e:
            print(f"[ERROR] 加载失败: {e}")
            return False


# ============ 怪物模板 ============
MONSTER_TEMPLATES = [
    MonsterTemplate(
        name="史莱姆",
        base_stats=Stats(hp=30, max_hp=30, mp=10, max_mp=10, attack=5, defense=2, speed=8, luck=3),
        attacks=["撞击", "泡沫"],
        loot_table=["史莱姆凝胶", "小瓶药水"],
        experience_reward=10,
        gold_reward=5
    ),
    MonsterTemplate(
        name="哥布林",
        base_stats=Stats(hp=50, max_hp=50, mp=20, max_mp=20, attack=12, defense=5, speed=12, luck=5),
        attacks=["挥砍", "偷窃", "冲锋"],
        loot_table=["哥布林之刀", "金币袋", "中型药水"],
        experience_reward=25,
        gold_reward=15
    ),
    MonsterTemplate(
        name="火焰龙",
        base_stats=Stats(hp=150, max_hp=150, mp=80, max_mp=80, attack=25, defense=15, speed=18, luck=10),
        attacks=["火焰吐息", "龙爪", "甩尾"],
        loot_table=["龙鳞甲", "龙晶", "高级药水", "大量金币"],
        experience_reward=100,
        gold_reward=100
    ),
]

# ============ 物品模板 ============
ITEM_TEMPLATES = [
    ItemTemplate(name="新手剑", item_type="weapon", rarity=Rarity.COMMON, 
                 description="一把简陋的剑", stat_bonus={"attack": 5}, value=10),
    ItemTemplate(name="新手盾", item_type="armor", rarity=Rarity.COMMON,
                 description="简陋的盾牌", stat_bonus={"defense": 3}, value=10),
    ItemTemplate(name="小瓶药水", item_type="potion", rarity=Rarity.COMMON,
                 description="恢复30点HP", heal_amount=30, value=5),
    ItemTemplate(name="中瓶药水", item_type="potion", rarity=Rarity.UNCOMMON,
                 description="恢复60点HP", heal_amount=60, value=15),
    ItemTemplate(name="治疗卷轴", item_type="scroll", rarity=Rarity.RARE,
                 description="完全恢复HP", heal_amount=999, value=50),
]


class Game:
    def __init__(self):
        self.battle_system = BattleSystem()
        self.monster_system = MonsterSystem()
        self.inventory_system = InventorySystem()
        self.scene_system = SceneSystem()
        self.player = None
        self.equipped = {"weapon": None, "armor": None}
        
    def create_player(self, name: str):
        """创建玩家"""
        self.player = {
            "name": name,
            "level": 1,
            "experience": 0,
            "stats": Stats(hp=100, max_hp=100, mp=50, max_mp=50, attack=10, defense=5, speed=10, luck=5),
            "inventory": self.inventory_system.create_inventory(20)
        }
        # 送初始装备
        self.inventory_system.add_item(self.player["inventory"], 
            {"name": "新手剑", "item_type": "weapon", "rarity": "common", 
             "description": "一把简陋的剑", "stat_bonus": {"attack": 5}, "value": 10})
        self.inventory_system.add_item(self.player["inventory"],
            {"name": "小瓶药水", "item_type": "potion", "rarity": "common",
             "description": "恢复30点HP", "heal_amount": 30, "value": 5})
        self.equip_item("新手剑")
        
    def equip_item(self, item_name: str):
        """装备物品"""
        inv, stats, msg = self.inventory_system.equip_item(
            self.player["inventory"], item_name, self.player["stats"]
        )
        if inv:
            self.player["inventory"] = inv
            self.player["stats"] = stats
            # 更新装备状态
            for item in inv["items"]:
                if item["name"] == item_name:
                    if item["item_type"] == "weapon":
                        self.equipped["weapon"] = item
                    elif item["item_type"] == "armor":
                        self.equipped["armor"] = item
            print(f"[OK] {msg}")
        else:
            print(f"[X] {msg}")
            
    def use_item(self, item_name: str):
        """使用物品"""
        inv, stats, msg = self.inventory_system.use_item(
            self.player["inventory"], item_name, self.player["stats"]
        )
        if inv:
            self.player["inventory"] = inv
            self.player["stats"] = stats
            print(f"[OK] {msg}")
        else:
            print(f"[X] {msg}")
            
    def spawn_monster(self, difficulty: int = 1) -> dict:
        """生成怪物"""
        template = random.choice(MONSTER_TEMPLATES[:min(difficulty, len(MONSTER_TEMPLATES))])
        level = max(1, self.player["level"] + random.randint(-1, 1))
        return self.monster_system.create_monster(template, level)
        
    def battle(self, monster: dict) -> bool:
        """战斗回合，返回True则玩家获胜"""
        print(f"\n[FIGHT] 遭遇 {monster['name']} (Lv.{monster['level']})!")
        
        while True:
            # 显示状态
            p = self.player["stats"]
            m = monster["stats"]
            print(f"\n【{self.player['name']}】 HP:{p.hp}/{p.max_hp} MP:{p.mp}/{p.max_mp}")
            print(f"【{monster['name']}】   HP:{m['hp']}/{m['max_hp']} MP:{m['mp']}/{m['max_mp']}")
            
            # 玩家回合
            print("\n回合选择: [1]攻击 [2]使用物品 [3]查看背包 [4]逃跑")
            choice = input("> ").strip()
            
            if choice == "1":
                # 玩家攻击
                result = self.battle_system.perform_attack(
                    self.player["name"], 
                    {"attack": p.attack, "speed": p.speed, "luck": p.luck},
                    monster["name"],
                    {"defense": m['defense'], "speed": m['speed']},
                    "physical"
                )
                print(result.message)
                if result.is_miss:
                    pass
                else:
                    monster = self.monster_system.apply_damage_to_monster(
                        monster, result.damage, result.damage_type.value
                    )
                    
            elif choice == "2":
                # 使用物品
                print("\n背包物品:")
                items = self.player["inventory"]["items"]
                if not items:
                    print("背包为空！")
                else:
                    for i, item in enumerate(items, 1):
                        print(f"  [{i}] {item['name']} ({item.get('item_type', 'unknown')})")
                    try:
                        idx = int(input("选择物品编号> ")) - 1
                        if 0 <= idx < len(items):
                            self.use_item(items[idx]["name"])
                        else:
                            print("无效选择")
                    except ValueError:
                        print("输入错误")
                continue  # 不减少怪物HP
                
            elif choice == "3":
                print("\n" + self.inventory_system.get_inventory_summary(self.player["inventory"]))
                print(f"\n装备: 武器={self.equipped.get('weapon', {}).get('name', '无')} | 护甲={self.equipped.get('armor', {}).get('name', '无')}")
                continue
                
            elif choice == "4":
                if random.random() < 0.5:
                    print("逃跑成功！")
                    return False
                else:
                    print("逃跑失败！")
            else:
                print("无效选择")
                continue
                
            # 检查怪物是否死亡
            if not self.monster_system.is_monster_alive(monster):
                print(f"\n[WIN] 击败了 {monster['name']}!")
                exp = monster.get("experience_reward", 10)
                gold = monster.get("gold_reward", 5)
                self.player["experience"] += exp
                self.player["inventory"]["gold"] += gold
                print(f"获得 {exp} 经验, {gold} 金币!")
                
                # 掉落物品
                loot = self.monster_system.generate_loot(monster)
                for item_name in loot:
                    item = random.choice(ITEM_TEMPLATES)
                    item_copy = {**item.__dict__, "name": item_name}
                    if self.inventory_system.add_item(self.player["inventory"], item_copy):
                        print(f"获得物品: {item_name}")
                return True
                
            # 怪物回合
            print(f"\n>>> {monster['name']} 的回合!")
            attack_info = self.monster_system.get_monster_attack(monster, [self.player])
            result = self.battle_system.perform_attack(
                monster["name"],
                {"attack": m['attack'], "speed": m['speed'], "luck": m['luck']},
                self.player["name"],
                {"defense": p.defense, "speed": p.speed},
                "physical"
            )
            print(result.message)
            self.player["stats"].hp -= result.damage
            
            # 检查玩家是否死亡
            if self.player["stats"].hp <= 0:
                print(f"\n[DEAD] {self.player['name']} 倒下了!")
                return "dead"
                
    def check_level_up(self):
        """检查升级"""
        exp_needed = self.player["level"] * 50
        if self.player["experience"] >= exp_needed:
            self.player["level"] += 1
            self.player["experience"] -= exp_needed
            self.player["stats"].max_hp += 20
            self.player["stats"].hp = self.player["stats"].max_hp
            self.player["stats"].max_mp += 10
            self.player["stats"].mp = self.player["stats"].max_mp
            self.player["stats"].attack += 3
            self.player["stats"].defense += 2
            self.player["stats"].speed += 1
            self.player["stats"].luck += 1
            print(f"\n[LEVELUP] {self.player['name']} 升级到 Lv.{self.player['level']}!")
            print("   属性大幅提升!")
            
    def run(self):
        """游戏主循环"""
        print("=" * 50)
        print("  [LOBSTER] 龙虾大冒险 [LOBSTER]")
        print("  三只龙虾协作开发的RPG游戏")
        print("=" * 50)
        
        name = input("\n请输入你的名字: ").strip() or "冒险者"
        self.create_player(name)
        
        print(f"\n欢迎, {name}! 你的冒险开始!")
        print("目标: 击败火焰龙，成为传奇!")
        
        floor = 1
        while True:
            print(f"\n{'='*40}")
            print(f"  第 {floor} 层 - 准备战斗!")
            print(f"{'='*40}")
            
            monster = self.spawn_monster(difficulty=min(floor, 3))
            result = self.battle(monster)
            
            if result == "dead":
                print("\n" + "="*40)
                print("  GAME OVER")
                print(f"  到达第 {floor} 层")
                print("="*40)
                break
                
            self.check_level_up()
            
            # 战后恢复
            self.player["stats"].hp = min(
                self.player["stats"].hp + 10,
                self.player["stats"].max_hp
            )
            print(f"\n休息后 HP: {self.player['stats'].hp}/{self.player['stats'].max_hp}")
            
            # 下一层
            if floor >= 3 and result == True:
                print("\n" + "="*50)
                print("  [WIN] 恭喜通关!")
                print(f"  {name} 击败了火焰龙，成为传奇!")
                print("="*50)
                break
                
            cont = input("\n继续下一层? [y/n]: ").strip().lower()
            if cont != 'y':
                break
            floor += 1
            
        print(f"\n再见, {name}!")


if __name__ == "__main__":
    game = Game()
    game.run()

