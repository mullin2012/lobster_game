"""
【启动器】- 龙虾大冒险
选择运行命令行版或 GUI 版
"""
import sys
import os

def check_pygame():
    """检查 Pygame 是否可用"""
    try:
        import pygame
        return True
    except ImportError:
        return False

def run_cli():
    """运行命令行版"""
    print("\n" + "="*50)
    print("  🦞 龙虾大冒险 - 命令行版 🦞")
    print("="*50 + "\n")
    
    # 导入并运行主游戏
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from main import Game
    
    game = Game()
    game.run()

def run_gui():
    """运行 GUI 版"""
    print("\n" + "="*50)
    print("  🦞 龙虾大冒险 - GUI 版 🦞")
    print("="*50 + "\n")
    
    if not check_pygame():
        print("❌ Pygame 未安装！")
        print("\n请先安装 Pygame:")
        print("  pip install pygame")
        print("\n或者运行命令行版 (无需安装):")
        print("  python launcher.py --cli")
        return
    
    # 检查素材
    assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                               "game_assets", "sprites")
    if not os.path.exists(assets_path) or not os.listdir(assets_path):
        print("⚠️  素材文件缺失，正在生成...")
        from game_assets.generate_sprites import generate_all_sprites
        import pygame
        pygame.init()
        generate_all_sprites()
        pygame.quit()
    
    # 导入并运行 GUI
    from gui.main_gui import main as gui_main
    gui_main()

def show_menu():
    """显示启动菜单"""
    print("\n" + "="*50)
    print("  🦞 龙虾大冒险 启动器 🦞")
    print("="*50)
    print("\n请选择运行模式:\n")
    print("  [1] 命令行版 (经典终端界面)")
    print("  [2] GUI 版 (图形界面，需要 Pygame)")
    print("  [3] 安装 Pygame")
    print("  [0] 退出")
    print()
    
    while True:
        choice = input("请输入选项 (0-3): ").strip()
        
        if choice == "1":
            run_cli()
            break
        elif choice == "2":
            run_gui()
            break
        elif choice == "3":
            print("\n正在安装 Pygame...")
            os.system("pip install pygame")
            print("\n安装完成！请重新启动启动器。")
            break
        elif choice == "0":
            print("\n再见！🦐")
            break
        else:
            print("无效选项，请重试。")

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--cli":
            run_cli()
        elif sys.argv[1] == "--gui":
            run_gui()
        else:
            print(f"未知参数：{sys.argv[1]}")
            print("用法：python launcher.py [--cli|--gui]")
    else:
        show_menu()
