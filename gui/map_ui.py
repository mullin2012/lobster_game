"""
【地图界面】- 龙虾大冒险 GUI 模块
场景选择、位置切换
"""
from typing import Callable, Optional

# ═══════════════════════════════════════════════════════════════
#  ║  ANSI 颜色常量                                               ║
# ═══════════════════════════════════════════════════════════════
C = {
    "RED":     "\033[91m",
    "GREEN":   "\033[92m",
    "YELLOW":  "\033[93m",
    "BLUE":    "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN":    "\033[96m",
    "WHITE":   "\033[97m",
    "BG_RED":  "\033[41m",
    "BG_GREEN": "\033[42m",
    "BG_YELLOW": "\033[43m",
    "BG_BLUE": "\033[44m",
    "BG_MAG":  "\033[45m",
    "BG_CYAN": "\033[46m",
    "BG_WHITE": "\033[47m",
    "BOLD":    "\033[1m",
    "DIM":     "\033[2m",
    "INVERT":  "\033[7m",
    "RESET":   "\033[0m",
    "CLR":     "\033[2J\033[H",   # 清屏+光标归位
}

# ═══════════════════════════════════════════════════════════════
#  ║  边框字符                                                   ║
# ═══════════════════════════════════════════════════════════════
BOX_THICK = {
    "tl": "╔", "tr": "╗",
    "bl": "╚", "br": "╝",
    "l":  "║", "r":  "║",
    "h":  "═",
}
BOX_THIN = {
    "tl": "┌", "tr": "┐",
    "bl": "└", "br": "┘",
    "l":  "│", "r":  "│",
    "h":  "─",
}

W = 48   # 界面宽度

# ═══════════════════════════════════════════════════════════════
#  ║  场景定义                                                   ║
# ═══════════════════════════════════════════════════════════════
LOCATIONS = {
    "town": {
        "name": "城镇",
        "icon": "🏘️",
        "description": "安全的避风港，可以休息和交易",
        "color": C["YELLOW"],
    },
    "forest": {
        "name": "森林",
        "icon": "🌲",
        "description": "危险的野外，充满野狼和怪物",
        "color": C["GREEN"],
    },
    "cave": {
        "name": "山洞",
        "icon": "🕳️",
        "description": "黑暗潮湿的洞穴，栖息着洞穴生物",
        "color": C["MAGENTA"],
    },
    "castle": {
        "name": "城堡",
        "icon": "🏰",
        "description": "邪恶的据点，强大的敌人等待着你",
        "color": C["RED"],
    },
}


class MapUI:
    """
    地图界面
    ────────────────────────────────────────────────────────────
    使用方式：
        ui = MapUI(player, on_move_callback, on_close_callback)
        ui.run()          # 进入交互循环（阻塞）
        ui.render()       # 仅渲染（用于嵌入）
    ────────────────────────────────────────────────────────────
    """

    def __init__(
        self,
        player: dict,
        on_move: Optional[Callable[[str], bool]] = None,
        on_close: Optional[Callable[[], None]] = None,
    ):
        """
        Args:
            player:       玩家字典，需包含 'location' 字段
            on_move:      移动回调，返回 True=成功 False=失败
            on_close:     关闭回调
        """
        self.player = player
        self.on_move = on_move or (lambda _: True)
        self.on_close = on_close or (lambda: None)

        self._state = "menu"   # "menu" | "confirm" | "result"
        self._target_loc: str = ""
        self._result_msg: str = ""

    # ── 公开 API ────────────────────────────────────────────────

    def run(self):
        """进入交互循环（阻塞直到用户退出）"""
        while True:
            cmd = self._input_step()
            if cmd == "close":
                self.on_close()
                break

    def render(self) -> str:
        """仅返回当前界面的文本（不含 input 提示）"""
        return self._build_ui()

    # ── 内部状态机 ───────────────────────────────────────────────

    def _input_step(self) -> str:
        """读取一行输入并处理，返回 'close' 表示退出"""
        print(self._CLR + self._build_ui(), end="")

        while True:
            prompt_map = {
                "menu":    f"{C['CYAN']}➜ 输入编号选择目的地 / [Q]退出: {C['RESET']}",
                "confirm": f"{C['YELLOW']}➜ 确认前往? [Y]是 [N]否: {C['RESET']}",
                "result":  f"{C['GREEN']}➜ 按 Enter 继续... {C['RESET']}",
            }
            try:
                raw = input(prompt_map[self._state]).strip()
            except (EOFError, KeyboardInterrupt):
                raw = "q"

            cmd = raw.lower()

            if self._state == "menu":
                action = self._handle_menu(cmd)
            elif self._state == "confirm":
                action = self._handle_confirm(cmd)
            else:  # result
                action = "menu"

            if action != "stay":
                return action

    def _handle_menu(self, cmd: str) -> str:
        """处理菜单状态输入"""
        if cmd in ("q", "quit", "exit"):
            return "close"

        # 数字选择
        if cmd.isdigit():
            idx = int(cmd) - 1
            loc_ids = list(LOCATIONS.keys())
            if 0 <= idx < len(loc_ids):
                target = loc_ids[idx]
                current = self.player.get("location", "town")
                if target == current:
                    # 已在当前地点
                    self._result_msg = f"你已经在 {LOCATIONS[target]['name']} 了！"
                    self._state = "result"
                    return "refresh"
                self._target_loc = target
                self._state = "confirm"
                return "refresh"
            return "stay"

        return "stay"

    def _handle_confirm(self, cmd: str) -> str:
        """处理确认状态输入"""
        if cmd in ("y", "yes", "是", "1"):
            success = self.on_move(self._target_loc)
            if success:
                self.player["location"] = self._target_loc
                loc_info = LOCATIONS[self._target_loc]
                self._result_msg = f"✅ 成功前往 {loc_info['icon']} {loc_info['name']}！"
            else:
                self._result_msg = "❌ 无法前往该地点"
            self._state = "result"
            self._target_loc = ""
            return "refresh"

        elif cmd in ("n", "no", "否", "2"):
            self._target_loc = ""
            self._state = "menu"
            return "refresh"

        return "stay"

    # ── UI 渲染 ─────────────────────────────────────────────────

    @property
    def _CLR(self) -> str:
        return C["CLR"]

    def _build_ui(self) -> str:
        if self._state == "confirm":
            return self._build_confirm_ui()
        if self._state == "result":
            return self._build_result_ui()
        return self._build_menu_ui()

    def _build_menu_ui(self) -> str:
        lines = []
        lines.append(C["CLR"])

        # ══ 标题栏 ══════════════════════════════════════════════
        lines.append(self._box_open())
        lines.append(self._box_title(" 🗺️  地 图 导 航 "))
        lines.append(self._box_hline())

        # ══ 当前位置 ══════════════════════════════════════════════
        current = self.player.get("location", "town")
        current_info = LOCATIONS.get(current, LOCATIONS["town"])
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}当前位置: {C['RESET']}"
                     f"{current_info['color']}{current_info['icon']} {current_info['name']}{C['RESET']}  {BOX_THIN['r']}")
        lines.append(self._box_hline())

        # ══ 场景列表 ══════════════════════════════════════════════
        lines.append(self._box_row(f"  选 择 目 的 地  "))
        lines.append(self._box_hline())

        for i, (loc_id, loc_info) in enumerate(LOCATIONS.items()):
            is_current = (loc_id == current)
            prefix = f"  [{i+1}] "
            suffix = ""

            if is_current:
                prefix = f"  {C['BG_YELLOW']}{C['BOLD']}●{C['RESET']} "
                suffix = f" {C['YELLOW']}(当前){C['RESET']}"

            loc_name = f"{loc_info['icon']} {loc_info['name']}"
            loc_desc = loc_info['description']

            # 行1: 名称
            line1 = f"{prefix}{loc_info['color']}{C['BOLD']}{loc_name}{C['RESET']}{suffix}"
            lines.append(f"{BOX_THIN['l']}  {line1.ljust(W-4)}  {BOX_THIN['r']}")

            # 行2: 描述
            line2 = f"      {C['DIM']}{loc_desc}{C['RESET']}"
            lines.append(f"{BOX_THIN['l']}  {line2.ljust(W-4)}  {BOX_THIN['r']}")

            lines.append(self._box_hline())

        # ══ 操作提示 ════════════════════════════════════════════
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}[1-4] 选择目的地  [Q]退出{C['RESET']}  {BOX_THIN['r']}")
        lines.append(self._box_close())

        return "\n".join(lines) + "\n"

    def _build_confirm_ui(self) -> str:
        target_info = LOCATIONS[self._target_loc]
        current = self.player.get("location", "town")
        current_info = LOCATIONS.get(current, LOCATIONS["town"])

        lines = []
        lines.append(C["CLR"])

        # 标题
        lines.append(self._box_open())
        lines.append(self._box_title(" ⚠️  确 认 出 发 "))
        lines.append(self._box_hline())

        # 当前地点
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}当前地点:{C['RESET']} {current_info['icon']} {current_info['name']}  {BOX_THIN['r']}")

        # 箭头
        lines.append(f"{BOX_THIN['l']}  {C['CYAN']}      ↓ 前往 ↓{C['RESET']}  {BOX_THIN['r']}")

        # 目标地点
        lines.append(f"{BOX_THIN['l']}  {C['BOLD']}目标地点:{C['RESET']} {target_info['color']}{target_info['icon']} {target_info['name']}{C['RESET']}  {BOX_THIN['r']}")

        lines.append(self._box_hline())

        # 目标描述
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}{target_info['description']}{C['RESET']}  {BOX_THIN['r']}")
        lines.append(self._box_hline())

        # 选项
        lines.append(f"{BOX_THIN['l']}  {C['GREEN']}[Y] 确认前往{C['RESET']}   {C['RED']}[N] 取消{C['RESET']}  {BOX_THIN['r']}")
        lines.append(self._box_close())

        return "\n".join(lines) + "\n"

    def _build_result_ui(self) -> str:
        lines = []
        lines.append(C["CLR"])
        lines.append(self._box_open())
        lines.append(self._box_title(" 🗺️  地 图 导 航 "))
        lines.append(self._box_hline())

        # 结果消息
        is_success = "成功" in self._result_msg
        color = C["GREEN"] if is_success else C["RED"]
        lines.append(f"{BOX_THIN['l']}  {color}{self._result_msg}{C['RESET']}  {BOX_THIN['r']}")

        lines.append(self._box_hline())
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}按 Enter 继续...{C['RESET']}  {BOX_THIN['r']}")
        lines.append(self._box_close())

        return "\n".join(lines) + "\n"

    # ── 边框绘制辅助 ────────────────────────────────────────────

    def _box_open(self) -> str:
        return f"{BOX_THICK['tl']}{BOX_THICK['h']*W}{BOX_THICK['tr']}"

    def _box_close(self) -> str:
        return f"{BOX_THICK['bl']}{BOX_THICK['h']*W}{BOX_THICK['br']}"

    def _box_hline(self) -> str:
        return f"{BOX_THICK['l']}{' '*(W+2)}{BOX_THICK['r']}"

    def _box_title(self, title: str) -> str:
        return (f"{BOX_THICK['l']}  {C['BOLD']}{C['CYAN']}"
                f"{title.center(W)}{C['RESET']}  {BOX_THICK['r']}")

    def _box_row(self, content: str) -> str:
        pad = W - len(content) + 2
        return f"{BOX_THIN['l']}  {content}{' '*pad}{BOX_THIN['r']}"


# ═══════════════════════════════════════════════════════════════
#  ║  简易演示（可独立运行）                                      ║
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # 模拟玩家数据
    demo_player = {
        "name": "龙虾勇士",
        "level": 5,
        "location": "town",
    }

    def on_move(location: str) -> bool:
        """模拟移动回调"""
        print(f"\n>>> 正在前往 {location} ...")
        return True

    def on_close():
        print("\n>>> 退出地图")

    # 启动地图界面
    ui = MapUI(demo_player, on_move=on_move, on_close=on_close)
    ui.run()
