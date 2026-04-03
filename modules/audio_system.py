"""
音效系统模块 - 龙虾大冒险
支持背景音乐、战斗音效、UI音效
使用 pygame.mixer 作为音频引擎
"""
import json
import os
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path


class AudioCategory(Enum):
    """音频分类"""
    BGM = "bgm"          # 背景音乐
    BATTLE = "battle"    # 战斗音效
    UI = "ui"            # UI音效
    AMBIENT = "ambient"  # 环境音效


@dataclass
class AudioConfig:
    """音频配置"""
    enabled: bool = True
    master_volume: float = 1.0
    bgm_volume: float = 0.7
    sfx_volume: float = 0.8
    fade_time_ms: int = 1000  # 淡入淡出时间


class AudioSystem:
    """
    音效管理器
    
    功能：
    - 背景音乐播放/暂停/停止
    - 战斗音效播放
    - UI音效播放
    - 音量控制
    - 自动检测pygame可用性，不可用时降级为静默模式
    """
    
    _instance: Optional['AudioSystem'] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化音效系统"""
        if self._initialized:
            return
            
        self._initialized = True
        self.config = AudioConfig()
        self._pygame_available = False
        self._mixer_initialized = False
        self._current_bgm: Optional[str] = None
        self._loaded_sounds: Dict[str, Any] = {}
        self._assets_path = Path(__file__).parent.parent / "game_assets" / "audio"
        
        # 尝试初始化 pygame mixer
        self._init_pygame()
        
        # 加载配置
        self._load_config()
    
    def _init_pygame(self):
        """初始化 pygame mixer"""
        try:
            import pygame
            # 初始化 mixer
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=2,
                    buffer=512
                )
            self._pygame_available = True
            self._mixer_initialized = True
            print("[AudioSystem] Pygame mixer 初始化成功")
        except ImportError:
            print("[AudioSystem] Pygame 未安装，音效系统运行在静默模式")
            self._pygame_available = False
        except Exception as e:
            print(f"[AudioSystem] 初始化失败: {e}")
            self._pygame_available = False
    
    def _load_config(self):
        """从配置文件加载设置"""
        config_path = self._assets_path / "audio_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config.enabled = data.get('enabled', True)
                    self.config.master_volume = data.get('master_volume', 1.0)
                    self.config.bgm_volume = data.get('bgm_volume', 0.7)
                    self.config.sfx_volume = data.get('sfx_volume', 0.8)
                    self.config.fade_time_ms = data.get('fade_time_ms', 1000)
            except Exception as e:
                print(f"[AudioSystem] 加载配置失败: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        config_path = self._assets_path / "audio_config.json"
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'enabled': self.config.enabled,
                'master_volume': self.config.master_volume,
                'bgm_volume': self.config.bgm_volume,
                'sfx_volume': self.config.sfx_volume,
                'fade_time_ms': self.config.fade_time_ms
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[AudioSystem] 保存配置失败: {e}")
    
    # ==================== 音量控制 ====================
    
    def set_master_volume(self, volume: float):
        """设置主音量 (0.0 - 1.0)"""
        self.config.master_volume = max(0.0, min(1.0, volume))
        self._update_volumes()
    
    def set_bgm_volume(self, volume: float):
        """设置背景音乐音量 (0.0 - 1.0)"""
        self.config.bgm_volume = max(0.0, min(1.0, volume))
        if self._pygame_available:
            import pygame
            actual_volume = self.config.master_volume * self.config.bgm_volume
            pygame.mixer.music.set_volume(actual_volume)
    
    def set_sfx_volume(self, volume: float):
        """设置音效音量 (0.0 - 1.0)"""
        self.config.sfx_volume = max(0.0, min(1.0, volume))
    
    def _update_volumes(self):
        """更新所有音量"""
        if self._pygame_available:
            import pygame
            # 更新背景音乐音量
            actual_bgm_volume = self.config.master_volume * self.config.bgm_volume
            pygame.mixer.music.set_volume(actual_bgm_volume)
            
            # 更新已加载音效的音量
            actual_sfx_volume = self.config.master_volume * self.config.sfx_volume
            for sound in self._loaded_sounds.values():
                sound.set_volume(actual_sfx_volume)
    
    def mute(self):
        """静音"""
        self.config.enabled = False
        if self._pygame_available:
            import pygame
            pygame.mixer.music.set_volume(0)
    
    def unmute(self):
        """取消静音"""
        self.config.enabled = True
        self._update_volumes()
    
    def toggle_mute(self) -> bool:
        """切换静音状态，返回新的静音状态"""
        if self.config.enabled:
            self.mute()
        else:
            self.unmute()
        return not self.config.enabled
    
    # ==================== 背景音乐 ====================
    
    def play_bgm(self, bgm_name: str, loop: bool = True, fade_in: bool = True):
        """
        播放背景音乐
        
        Args:
            bgm_name: 音乐名称 (不含扩展名)
            loop: 是否循环播放
            fade_in: 是否淡入
        """
        if not self.config.enabled or not self._pygame_available:
            return
        
        import pygame
        
        # 查找音乐文件
        bgm_path = self._assets_path / "bgm" / f"{bgm_name}.ogg"
        if not bgm_path.exists():
            bgm_path = self._assets_path / "bgm" / f"{bgm_name}.mp3"
        if not bgm_path.exists():
            bgm_path = self._assets_path / "bgm" / f"{bgm_name}.wav"
        
        if not bgm_path.exists():
            print(f"[AudioSystem] 找不到背景音乐: {bgm_name}")
            return
        
        try:
            # 停止当前音乐
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(self.config.fade_time_ms)
                pygame.time.wait(self.config.fade_time_ms)
            
            # 加载并播放
            pygame.mixer.music.load(str(bgm_path))
            actual_volume = self.config.master_volume * self.config.bgm_volume
            
            if fade_in:
                pygame.mixer.music.set_volume(0)
                pygame.mixer.music.play(-1 if loop else 0)
                # 淡入效果
                fade_steps = 20
                for i in range(fade_steps + 1):
                    vol = actual_volume * (i / fade_steps)
                    pygame.mixer.music.set_volume(vol)
                    pygame.time.wait(self.config.fade_time_ms // fade_steps)
            else:
                pygame.mixer.music.set_volume(actual_volume)
                pygame.mixer.music.play(-1 if loop else 0)
            
            self._current_bgm = bgm_name
            print(f"[AudioSystem] 播放背景音乐: {bgm_name}")
            
        except Exception as e:
            print(f"[AudioSystem] 播放背景音乐失败: {e}")
    
    def stop_bgm(self, fade_out: bool = True):
        """停止背景音乐"""
        if not self._pygame_available:
            return
        
        import pygame
        
        if pygame.mixer.music.get_busy():
            if fade_out:
                pygame.mixer.music.fadeout(self.config.fade_time_ms)
            else:
                pygame.mixer.music.stop()
            self._current_bgm = None
    
    def pause_bgm(self):
        """暂停背景音乐"""
        if self._pygame_available:
            import pygame
            pygame.mixer.music.pause()
    
    def resume_bgm(self):
        """恢复背景音乐"""
        if self._pygame_available:
            import pygame
            pygame.mixer.music.unpause()
    
    def get_current_bgm(self) -> Optional[str]:
        """获取当前播放的背景音乐名称"""
        return self._current_bgm
    
    # ==================== 音效播放 ====================
    
    def _get_sound_path(self, category: AudioCategory, sound_name: str) -> Optional[Path]:
        """获取音效文件路径"""
        if category == AudioCategory.BGM:
            return self._assets_path / "bgm" / f"{sound_name}.ogg"
        else:
            return self._assets_path / "sfx" / category.value / f"{sound_name}.wav"
    
    def _load_sound(self, sound_path: Path) -> Optional[Any]:
        """加载音效文件"""
        if not self._pygame_available:
            return None
        
        import pygame
        
        # 检查缓存
        path_str = str(sound_path)
        if path_str in self._loaded_sounds:
            return self._loaded_sounds[path_str]
        
        # 尝试不同扩展名
        extensions = ['.wav', '.ogg', '.mp3']
        for ext in extensions:
            actual_path = sound_path.with_suffix(ext)
            if actual_path.exists():
                try:
                    sound = pygame.mixer.Sound(str(actual_path))
                    sound.set_volume(self.config.master_volume * self.config.sfx_volume)
                    self._loaded_sounds[path_str] = sound
                    return sound
                except Exception as e:
                    print(f"[AudioSystem] 加载音效失败 {actual_path}: {e}")
        
        return None
    
    def play_sfx(self, category: AudioCategory, sound_name: str):
        """
        播放音效
        
        Args:
            category: 音效类别
            sound_name: 音效名称
        """
        if not self.config.enabled or not self._pygame_available:
            return
        
        sound_path = self._get_sound_path(category, sound_name)
        sound = self._load_sound(sound_path)
        
        if sound:
            try:
                sound.play()
            except Exception as e:
                print(f"[AudioSystem] 播放音效失败: {e}")
        else:
            print(f"[AudioSystem] 找不到音效: {category.value}/{sound_name}")
    
    # ==================== 战斗音效 ====================
    
    def play_attack(self, attack_type: str = "normal"):
        """播放攻击音效"""
        sound_map = {
            "normal": "attack_normal",
            "critical": "attack_critical",
            "magic": "attack_magic",
            "fire": "attack_fire",
            "ice": "attack_ice",
            "poison": "attack_poison"
        }
        sound_name = sound_map.get(attack_type, "attack_normal")
        self.play_sfx(AudioCategory.BATTLE, sound_name)
    
    def play_hit(self, is_critical: bool = False):
        """播放命中音效"""
        sound_name = "hit_critical" if is_critical else "hit_normal"
        self.play_sfx(AudioCategory.BATTLE, sound_name)
    
    def play_miss(self):
        """播放闪避音效"""
        self.play_sfx(AudioCategory.BATTLE, "dodge")
    
    def play_death(self, is_boss: bool = False):
        """播放死亡音效"""
        sound_name = "boss_death" if is_boss else "enemy_death"
        self.play_sfx(AudioCategory.BATTLE, sound_name)
    
    def play_victory(self):
        """播放胜利音效"""
        self.play_sfx(AudioCategory.BATTLE, "victory")
    
    def play_defeat(self):
        """播放失败音效"""
        self.play_sfx(AudioCategory.BATTLE, "defeat")
    
    def play_level_up(self):
        """播放升级音效"""
        self.play_sfx(AudioCategory.BATTLE, "level_up")
    
    # ==================== UI音效 ====================
    
    def play_click(self):
        """播放点击音效"""
        self.play_sfx(AudioCategory.UI, "click")
    
    def play_hover(self):
        """播放悬停音效"""
        self.play_sfx(AudioCategory.UI, "hover")
    
    def play_confirm(self):
        """播放确认音效"""
        self.play_sfx(AudioCategory.UI, "confirm")
    
    def play_cancel(self):
        """播放取消音效"""
        self.play_sfx(AudioCategory.UI, "cancel")
    
    def play_error(self):
        """播放错误音效"""
        self.play_sfx(AudioCategory.UI, "error")
    
    def play_success(self):
        """播放成功音效"""
        self.play_sfx(AudioCategory.UI, "success")
    
    def play_item_pickup(self):
        """播放物品拾取音效"""
        self.play_sfx(AudioCategory.UI, "item_pickup")
    
    def play_coin(self):
        """播放金币音效"""
        self.play_sfx(AudioCategory.UI, "coin")
    
    def play_shop_open(self):
        """播放商店打开音效"""
        self.play_sfx(AudioCategory.UI, "shop_open")
    
    def play_inventory_open(self):
        """播放背包打开音效"""
        self.play_sfx(AudioCategory.UI, "inventory_open")
    
    # ==================== 环境音效 ====================
    
    def play_ambient(self, ambient_name: str, loop: bool = False):
        """播放环境音效"""
        # 环境音效通常较长，可以用channel单独处理
        self.play_sfx(AudioCategory.AMBIENT, ambient_name)
    
    # ==================== 场景音乐切换 ====================
    
    def play_scene_bgm(self, scene_name: str):
        """根据场景播放对应的背景音乐"""
        scene_bgm_map = {
            "town": "town_peaceful",
            "shop": "shop_theme",
            "inn": "inn_relaxing",
            "dungeon": "dungeon_adventure",
            "battle": "battle_intense",
            "boss": "boss_epic",
            "victory": "victory_fanfare",
            "game_over": "game_over_sad",
            "title": "title_theme"
        }
        bgm_name = scene_bgm_map.get(scene_name)
        if bgm_name:
            self.play_bgm(bgm_name)
        else:
            print(f"[AudioSystem] 未知场景: {scene_name}")
    
    # ==================== 工具方法 ====================
    
    def preload_sounds(self, sound_list: list):
        """
        预加载音效列表
        
        Args:
            sound_list: [(category, sound_name), ...] 格式的列表
        """
        for category, sound_name in sound_list:
            if isinstance(category, str):
                category = AudioCategory(category)
            sound_path = self._get_sound_path(category, sound_name)
            self._load_sound(sound_path)
    
    def clear_cache(self):
        """清除已加载的音效缓存"""
        self._loaded_sounds.clear()
    
    def is_available(self) -> bool:
        """检查音效系统是否可用"""
        return self._pygame_available and self.config.enabled
    
    def get_status(self) -> dict:
        """获取音效系统状态"""
        return {
            "available": self._pygame_available,
            "enabled": self.config.enabled,
            "muted": not self.config.enabled,
            "master_volume": self.config.master_volume,
            "bgm_volume": self.config.bgm_volume,
            "sfx_volume": self.config.sfx_volume,
            "current_bgm": self._current_bgm,
            "loaded_sounds": len(self._loaded_sounds)
        }
    
    def cleanup(self):
        """清理资源"""
        self.stop_bgm(fade_out=False)
        self.clear_cache()
        if self._pygame_available:
            try:
                import pygame
                pygame.mixer.quit()
            except:
                pass


# 全局实例
audio_system = AudioSystem()


# 便捷函数
def play_bgm(bgm_name: str, loop: bool = True):
    """播放背景音乐"""
    audio_system.play_bgm(bgm_name, loop)


def stop_bgm():
    """停止背景音乐"""
    audio_system.stop_bgm()


def play_sfx(category: str, sound_name: str):
    """播放音效"""
    try:
        cat = AudioCategory(category)
        audio_system.play_sfx(cat, sound_name)
    except ValueError:
        print(f"[AudioSystem] 未知的音效类别: {category}")


def set_volume(master: float = None, bgm: float = None, sfx: float = None):
    """设置音量"""
    if master is not None:
        audio_system.set_master_volume(master)
    if bgm is not None:
        audio_system.set_bgm_volume(bgm)
    if sfx is not None:
        audio_system.set_sfx_volume(sfx)


# 测试代码
if __name__ == "__main__":
    print("\n=== 音效系统测试 ===\n")
    
    # 获取状态
    status = audio_system.get_status()
    print(f"音效系统状态: {status}")
    
    # 测试静音切换
    print("\n测试静音切换...")
    is_muted = audio_system.toggle_mute()
    print(f"静音状态: {is_muted}")
    audio_system.toggle_mute()  # 恢复
    
    # 测试音量设置
    print("\n测试音量设置...")
    audio_system.set_master_volume(0.8)
    audio_system.set_bgm_volume(0.6)
    audio_system.set_sfx_volume(0.9)
    
    print(f"主音量: {audio_system.config.master_volume}")
    print(f"背景音乐音量: {audio_system.config.bgm_volume}")
    print(f"音效音量: {audio_system.config.sfx_volume}")
    
    # 测试场景音乐
    print("\n测试场景音乐...")
    audio_system.play_scene_bgm("town")  # 会提示找不到文件（正常）
    
    # 测试战斗音效
    print("\n测试战斗音效...")
    audio_system.play_attack("critical")
    audio_system.play_hit(is_critical=True)
    audio_system.play_victory()
    
    # 测试UI音效
    print("\n测试UI音效...")
    audio_system.play_click()
    audio_system.play_coin()
    
    print("\n=== 测试完成 ===")
    print("注意: 以上测试会提示找不到音频文件，这是正常的。")
    print("请添加实际的音频文件到 game_assets/audio/ 目录。")
