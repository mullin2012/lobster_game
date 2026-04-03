"""
【龙虾大冒险】- 游戏主 GUI 框架
使用 Pygame 实现图形化界面
"""
import pygame
import sys
from typing import Optional, Callable

# 初始化 Pygame
pygame.init()

# ============ 常量定义 ============
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
COLORS = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "CYAN": (0, 255, 255),
    "MAGENTA": (255, 0, 255),
    "GRAY": (128, 128, 128),
    "DARK_GRAY": (64, 64, 64),
    "LIGHT_GRAY": (192, 192, 192),
    "GOLD": (255, 215, 0),
    "BROWN": (139, 69, 19),
    "PURPLE": (128, 0, 128),
}

# 字体
FONT_LARGE = None
FONT_MEDIUM = None
FONT_SMALL = None


class Button:
    """按钮类"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, callback: Callable = None,
                 color=COLORS["BLUE"], hover_color=COLORS["CYAN"]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.is_clicked = False
    
    def draw(self, screen):
        """绘制按钮"""
        color = self.hover_color if self.is_hovered else self.color
        
        # 绘制按钮背景
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLORS["WHITE"], self.rect, width=2, border_radius=8)
        
        # 绘制文字
        text_surface = FONT_MEDIUM.render(self.text, True, COLORS["WHITE"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.is_clicked = True
                if self.callback:
                    self.callback()
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_clicked = False
        
        return False


class GameGUI:
    """游戏主 GUI 类"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🦞 龙虾大冒险 - Lobster's Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_state = "menu"  # menu, game, battle, shop, inn, training
        
        # 游戏数据
        self.player = None
        self.game_data = None
        
        # UI 元素
        self.buttons = []
        self.setup_menu_buttons()
        
        # 背景
        self.background = None
        self._create_background()
    
    def _create_background(self):
        """创建渐变背景"""
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(30 + ratio * 20)
            g = int(50 + ratio * 30)
            b = int(80 + ratio * 40)
            pygame.draw.line(self.background, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def setup_menu_buttons(self):
        """设置主菜单按钮"""
        self.buttons = []
        button_width = 200
        button_height = 50
        start_x = (SCREEN_WIDTH - button_width) // 2
        
        self.buttons.append(Button(
            start_x, 200, button_width, button_height,
            "🎮 开始游戏",
            self.start_game
        ))
        
        self.buttons.append(Button(
            start_x, 270, button_width, button_height,
            "📂 继续游戏",
            self.continue_game
        ))
        
        self.buttons.append(Button(
            start_x, 340, button_width, button_height,
            "⚙️ 设置",
            self.show_settings
        ))
        
        self.buttons.append(Button(
            start_x, 410, button_width, button_height,
            "❌ 退出游戏",
            self.quit_game
        ))
    
    def start_game(self):
        """开始新游戏"""
        self.current_state = "game"
        print("[GUI] 开始新游戏")
    
    def continue_game(self):
        """继续游戏"""
        self.current_state = "game"
        print("[GUI] 继续游戏")
    
    def show_settings(self):
        """显示设置"""
        print("[GUI] 显示设置")
    
    def quit_game(self):
        """退出游戏"""
        self.running = False
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.current_state == "menu":
                for button in self.buttons:
                    if button.handle_event(event):
                        return
            
            elif self.current_state == "game":
                # 返回按钮点击检测
                if event.type == pygame.MOUSEBUTTONDOWN:
                    back_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, 400, 150, 40)
                    if back_button.collidepoint(event.pos):
                        self.current_state = "menu"
    
    def draw_menu(self):
        """绘制主菜单"""
        self.screen.blit(self.background, (0, 0))
        
        # 标题
        title_text = FONT_LARGE.render("🦞 龙虾大冒险", True, COLORS["GOLD"])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = FONT_MEDIUM.render("Lobster's Adventure", True, COLORS["WHITE"])
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # 按钮
        for button in self.buttons:
            button.draw(self.screen)
        
        # 版本信息
        version_text = FONT_SMALL.render("Version 1.0 - Made with 🦐 by Lobster Team", 
                                         True, COLORS["LIGHT_GRAY"])
        version_rect = version_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(version_text, version_rect)
    
    def draw_game(self):
        """绘制游戏主界面"""
        self.screen.blit(self.background, (0, 0))
        
        # 显示提示信息
        info_text = FONT_MEDIUM.render("游戏功能请使用命令行版", True, COLORS["WHITE"])
        text_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(info_text, text_rect)
        
        hint_text = FONT_SMALL.render("运行: python main.py", True, COLORS["LIGHT_GRAY"])
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(hint_text, hint_rect)
        
        # 返回按钮
        back_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, 400, 150, 40)
        pygame.draw.rect(self.screen, COLORS["RED"], back_button, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["WHITE"], back_button, width=2, border_radius=8)
        
        back_text = FONT_SMALL.render("返回菜单", True, COLORS["WHITE"])
        back_text_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_text_rect)
    
    def draw(self):
        """绘制当前状态"""
        if self.current_state == "menu":
            self.draw_menu()
        elif self.current_state == "game":
            self.draw_game()
        
        pygame.display.flip()
    
    def run(self):
        """运行主循环"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


# 初始化字体
def init_fonts():
    """初始化字体 - 使用系统中文字体"""
    global FONT_LARGE, FONT_MEDIUM, FONT_SMALL
    
    # 尝试使用系统中文字体
    chinese_fonts = ['simhei', 'microsoftyahei', 'simsun', 'fangsong', 'kaiti', 'Arial Unicode MS']
    
    font_name = None
    for name in chinese_fonts:
        try:
            test_font = pygame.font.SysFont(name, 24)
            if test_font:
                font_name = name
                break
        except:
            continue
    
    if font_name:
        try:
            FONT_LARGE = pygame.font.SysFont(font_name, 72)
            FONT_MEDIUM = pygame.font.SysFont(font_name, 48)
            FONT_SMALL = pygame.font.SysFont(font_name, 24)
            print(f"[GUI] 使用字体: {font_name}")
            return
        except:
            pass
    
    # 回退方案：使用默认字体
    try:
        FONT_LARGE = pygame.font.Font(None, 72)
        FONT_MEDIUM = pygame.font.Font(None, 48)
        FONT_SMALL = pygame.font.Font(None, 24)
        print("[GUI] 使用默认字体")
    except:
        FONT_LARGE = pygame.font.SysFont('arial', 72)
        FONT_MEDIUM = pygame.font.SysFont('arial', 48)
        FONT_SMALL = pygame.font.SysFont('arial', 24)


# 主函数
def main():
    """主函数"""
    init_fonts()
    gui = GameGUI()
    gui.run()


if __name__ == "__main__":
    main()
