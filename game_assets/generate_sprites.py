"""
【素材生成器】- 为龙虾大冒险创建简单的像素风格素材
使用 Pygame 绘制并保存为 PNG 文件
"""
import pygame
import os

# 初始化 Pygame
pygame.init()

# 颜色定义
COLORS = {
    "LOBSTER_RED": (220, 60, 60),
    "LOBSTER_ORANGE": (255, 140, 60),
    "LOBSTER_BROWN": (139, 69, 19),
    "SLIME_GREEN": (100, 200, 100),
    "GOBLIN_GREEN": (60, 120, 60),
    "DRAGON_RED": (200, 50, 50),
    "DRAGON_ORANGE": (255, 100, 50),
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "GRAY": (128, 128, 128),
    "BLUE": (50, 100, 200),
    "PURPLE": (150, 50, 200),
}


def draw_lobster_sprite(size=32):
    """绘制龙虾角色（简化像素风格）"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # 身体
    body_rect = pygame.Rect(size//4, size//3, size//2, size//3)
    pygame.draw.ellipse(surface, COLORS["LOBSTER_RED"], body_rect)
    
    # 钳子
    claw_left = [(size//4, size//3), (size//6, size//4), (size//5, size//2)]
    pygame.draw.polygon(surface, COLORS["LOBSTER_ORANGE"], claw_left)
    
    claw_right = [(3*size//4, size//3), (5*size//6, size//4), (4*size//5, size//2)]
    pygame.draw.polygon(surface, COLORS["LOBSTER_ORANGE"], claw_right)
    
    # 眼睛
    eye_size = size // 8
    pygame.draw.circle(surface, COLORS["WHITE"], (size//3, size//3), eye_size)
    pygame.draw.circle(surface, COLORS["WHITE"], (2*size//3, size//3), eye_size)
    pygame.draw.circle(surface, COLORS["BLACK"], (size//3, size//3), eye_size//2)
    pygame.draw.circle(surface, COLORS["BLACK"], (2*size//3, size//3), eye_size//2)
    
    # 触须
    pygame.draw.line(surface, COLORS["LOBSTER_ORANGE"], 
                    (size//3, size//4), (size//4, size//8), 2)
    pygame.draw.line(surface, COLORS["LOBSTER_ORANGE"], 
                    (2*size//3, size//4), (3*size//4, size//8), 2)
    
    return surface


def draw_slime_sprite(size=32):
    """绘制史莱姆"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # 身体（水滴形）
    points = [
        (size//2, size//8),
        (3*size//4, size//2),
        (5*size//6, 3*size//4),
        (size//6, 3*size//4),
        (size//4, size//2),
    ]
    pygame.draw.polygon(surface, COLORS["SLIME_GREEN"], points)
    pygame.draw.polygon(surface, COLORS["BLACK"], points, width=1)
    
    # 眼睛
    eye_size = size // 10
    pygame.draw.circle(surface, COLORS["BLACK"], (size//3, size//2), eye_size)
    pygame.draw.circle(surface, COLORS["BLACK"], (2*size//3, size//2), eye_size)
    
    # 高光
    pygame.draw.circle(surface, COLORS["WHITE"], (size//3 - 2, size//2 - 2), eye_size//2)
    
    return surface


def draw_goblin_sprite(size=32):
    """绘制哥布林"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # 身体
    body_rect = pygame.Rect(size//3, size//3, size//3, size//2)
    pygame.draw.ellipse(surface, COLORS["GOBLIN_GREEN"], body_rect)
    
    # 头
    head_rect = pygame.Rect(size//4, size//6, size//2, size//3)
    pygame.draw.ellipse(surface, COLORS["GOBLIN_GREEN"], head_rect)
    
    # 耳朵（尖的）
    ear_points_left = [(size//4, size//4), (size//8, size//6), (size//4, size//3)]
    pygame.draw.polygon(surface, COLORS["GOBLIN_GREEN"], ear_points_left)
    
    ear_points_right = [(3*size//4, size//4), (7*size//8, size//6), (3*size//4, size//3)]
    pygame.draw.polygon(surface, COLORS["GOBLIN_GREEN"], ear_points_right)
    
    # 眼睛
    eye_size = size // 10
    pygame.draw.circle(surface, COLORS["WHITE"], (size//3, size//3), eye_size)
    pygame.draw.circle(surface, COLORS["WHITE"], (2*size//3, size//3), eye_size)
    pygame.draw.circle(surface, COLORS["RED"], (size//3, size//3), eye_size//2)
    pygame.draw.circle(surface, COLORS["RED"], (2*size//3, size//3), eye_size//2)
    
    # 嘴巴
    pygame.draw.arc(surface, COLORS["BLACK"], 
                   (size//3, size//2, size//3, size//6), 3.14, 0, 2)
    
    return surface


def draw_dragon_sprite(size=48):
    """绘制火焰龙（Boss）"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # 身体
    body_rect = pygame.Rect(size//6, size//3, 2*size//3, size//2)
    pygame.draw.ellipse(surface, COLORS["DRAGON_RED"], body_rect)
    
    # 头
    head_rect = pygame.Rect(size//3, size//8, size//3, size//3)
    pygame.draw.ellipse(surface, COLORS["DRAGON_RED"], head_rect)
    
    # 翅膀
    wing_left = [(size//4, size//3), (size//8, size//6), (size//3, size//4)]
    pygame.draw.polygon(surface, COLORS["DRAGON_ORANGE"], wing_left)
    
    wing_right = [(3*size//4, size//3), (7*size//8, size//6), (2*size//3, size//4)]
    pygame.draw.polygon(surface, COLORS["DRAGON_ORANGE"], wing_right)
    
    # 眼睛
    eye_size = size // 12
    pygame.draw.circle(surface, COLORS["YELLOW"], (5*size//12, size//4), eye_size)
    pygame.draw.circle(surface, COLORS["YELLOW"], (7*size//12, size//4), eye_size)
    pygame.draw.circle(surface, COLORS["BLACK"], (5*size//12, size//4), eye_size//2)
    pygame.draw.circle(surface, COLORS["BLACK"], (7*size//12, size//4), eye_size//2)
    
    # 鼻孔
    pygame.draw.circle(surface, COLORS["BLACK"], (size//2, size//3), size//16)
    
    return surface


def draw_warrior_sprite(size=32):
    """绘制战士角色"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # 身体（盔甲）
    body_rect = pygame.Rect(size//3, size//3, size//3, size//2)
    pygame.draw.rect(surface, COLORS["BLUE"], body_rect)
    
    # 头
    head_rect = pygame.Rect(size//3, size//6, size//3, size//4)
    pygame.draw.ellipse(surface, COLORS["GRAY"], head_rect)
    
    # 头盔装饰
    pygame.draw.line(surface, COLORS["GRAY"], (size//2, size//8), (size//2, size//6), 2)
    
    # 剑
    pygame.draw.line(surface, COLORS["GRAY"], (2*size//3, size//2), (2*size//3, 3*size//4), 3)
    pygame.draw.line(surface, COLORS["GRAY"], (2*size//3 - size//8, 3*size//4), 
                    (2*size//3 + size//8, 3*size//4), 2)
    
    return surface


def draw_mage_sprite(size=32):
    """绘制法师角色"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # 身体（长袍）
    body_rect = pygame.Rect(size//3, size//3, size//3, size//2)
    pygame.draw.rect(surface, COLORS["PURPLE"], body_rect)
    
    # 头
    head_rect = pygame.Rect(size//3, size//6, size//3, size//4)
    pygame.draw.ellipse(surface, COLORS["GRAY"], head_rect)
    
    # 法师帽
    hat_points = [(size//2, size//12), (size//6, size//4), (5*size//6, size//4)]
    pygame.draw.polygon(surface, COLORS["PURPLE"], hat_points)
    
    # 法杖
    pygame.draw.line(surface, COLORS["BROWN"], (size//6, size//3), (size//6, 3*size//4), 2)
    pygame.draw.circle(surface, COLORS["BLUE"], (size//6, size//4), size//8)
    
    return surface


def draw_rogue_sprite(size=32):
    """绘制盗贼角色"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # 身体（皮甲）
    body_rect = pygame.Rect(size//3, size//3, size//3, size//2)
    pygame.draw.rect(surface, COLORS["GOBLIN_GREEN"], body_rect)
    
    # 头
    head_rect = pygame.Rect(size//3, size//6, size//3, size//4)
    pygame.draw.ellipse(surface, COLORS["GRAY"], head_rect)
    
    # 头巾
    pygame.draw.arc(surface, COLORS["GOBLIN_GREEN"], 
                   (size//4, size//8, size//2, size//4), 3.14, 0, 3)
    
    # 匕首
    pygame.draw.line(surface, COLORS["GRAY"], (5*size//6, size//2), (5*size//6, 2*size//3), 2)
    
    return surface


def save_sprite(surface, filename, folder):
    """保存精灵图"""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    pygame.image.save(surface, filepath)
    print(f"✓ 已保存：{filepath}")


def generate_all_sprites():
    """生成所有素材"""
    print("🦞 开始生成龙虾大冒险素材...\n")
    
    # 角色 sprites (32x32)
    characters_folder = "game_assets/sprites/characters"
    save_sprite(draw_lobster_sprite(32), "lobster.png", characters_folder)
    save_sprite(draw_warrior_sprite(32), "warrior.png", characters_folder)
    save_sprite(draw_mage_sprite(32), "mage.png", characters_folder)
    save_sprite(draw_rogue_sprite(32), "rogue.png", characters_folder)
    
    # 怪物 sprites
    monsters_folder = "game_assets/sprites/monsters"
    save_sprite(draw_slime_sprite(32), "slime.png", monsters_folder)
    save_sprite(draw_goblin_sprite(32), "goblin.png", monsters_folder)
    save_sprite(draw_dragon_sprite(48), "dragon.png", monsters_folder)
    
    print("\n✅ 素材生成完成！")


if __name__ == "__main__":
    generate_all_sprites()
    pygame.quit()
