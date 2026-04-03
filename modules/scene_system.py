"""
[模块] 场景系统
提供地图、场景和导航功能
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Scene:
    """场景类"""
    name: str                          # 场景名称
    description: str                   # 场景描述
    options: List[str]                  # 可用选项
    connected_scenes: Dict[str, str]  # 场景名 -> 场景ID
    enemies: List[str]                 # 该场景的敌人列表
    items: List[str] = field(default_factory=list)  # 该场景的物品
    is_town: bool = False              # 是否为城镇
    shop_items: List[str] = field(default_factory=list)  # 商店物品
    inn_cost: int = 10                # 旅店费用
    training_cost: int = 50           # 训练费用


class SceneSystem:
    """场景系统管理器"""
    
    def __init__(self):
        self.scenes: Dict[str, Scene] = {}
        self.current_scene_id: str = "town"
        self._init_scenes()
        
    def _init_scenes(self):
        """初始化所有场景"""
        # 起始城镇
        self.scenes["town"] = Scene(
            name="起始城镇",
            description="这是一个和平的小镇，商贩们正在叫卖，旅店的炊烟袅袅升起。\n北边是森林，东边有山洞，西边则是黑暗城堡...",
            options=["1.商店", "2.旅店", "3.训练场", "4.探索", "5.状态"],
            connected_scenes={"森林": "forest", "山洞": "cave", "城堡": "castle"},
            enemies=[], items=[],
            is_town=True,
            shop_items=["新手剑", "新手盾", "小瓶药水", "中瓶药水", "治疗卷轴"],
            inn_cost=10,
            training_cost=50
        )
        
        # 森林
        self.scenes["forest"] = Scene(
            name="幽暗森林",
            description="树木遮天蔽日，空气中弥漫着潮湿的气息。\n偶尔传来不知名的鸟兽叫声...",
            options=["1.探索", "2.休息", "3.背包", "4.状态", "5.返回城镇"],
            connected_scenes={"城镇": "town", "山洞": "cave", "城堡": "castle"},
            enemies=["史莱姆", "哥布林"],
            items=["草药", "野果"]
        )
        
        # 山洞
        self.scenes["cave"] = Scene(
            name="阴暗山洞",
            description="洞穴深处滴水声回荡，墙壁上闪烁着诡异的光芒。\n空气中带着一股霉味...",
            options=["1.探索", "2.休息", "3.背包", "4.状态", "5.返回"],
            connected_scenes={"森林": "forest", "城镇": "town", "城堡": "castle"},
            enemies=["哥布林", "洞穴蝙蝠", "岩石怪"],
            items=["铁矿石", "发光蘑菇"]
        )
        
        # 城堡
        self.scenes["castle"] = Scene(
            name="黑暗城堡",
            description="城堡大门紧锁，散发着一股令人窒息的压迫感。\n这里似乎藏着最终的秘密...",
            options=["1.挑战Boss", "2.探索", "3.休息", "4.背包", "5.状态", "6.返回"],
            connected_scenes={"森林": "forest", "山洞": "cave", "城镇": "town"},
            enemies=["火焰龙", "骷髅战士", "暗影刺客"],
            items=["城堡钥匙", "古老卷轴"]
        )
    
    def get_current_scene(self) -> Scene:
        """获取当前场景"""
        return self.scenes[self.current_scene_id]
    
    def move_to(self, scene_name: str) -> bool:
        """移动到指定场景"""
        current = self.get_current_scene()
        if scene_name in current.connected_scenes:
            self.current_scene_id = current.connected_scenes[scene_name]
            return True
        return False
    
    def get_available_exits(self) -> List[str]:
        """获取可用出口列表"""
        current = self.get_current_scene()
        return list(current.connected_scenes.keys())
    
    def show_scene_info(self) -> str:
        """显示当前场景信息"""
        scene = self.get_current_scene()
        info = f"""
╔══════════════════════════════════════════╗
║        🗺️  当前场景: {scene.name}             ║
╠══════════════════════════════════════════╣
║                                          ║
║  {scene.description}
║                                          ║
║  ───────────────────────────────────────  ║
║  可移动区域: {', '.join(scene.connected_scenes.keys())}   ║
╚══════════════════════════════════════════╝
"""
        return info
