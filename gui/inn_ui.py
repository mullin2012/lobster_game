"""
【旅店界面】- 龙虾大冒险 GUI 模块
休息恢复HP、确认费用
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

W = 52   # 宽度


# ═══════════════════════════════════════════════════════════════
#  ║  内部辅助函数                                                ║
# ═══════════════════════════════════════════════════════════════
def _stat_bar(label: str, current: int, maximum: int,
              filled_char="█", empty_char="░",
              color_current=None, width: int = 18) -> str:
    """生成单条属性条"""
    if maximum <= 0:
        maximum = 1
    ratio = current / maximum
    filled = max(1, int(ratio * width))
    bar = filled_char * filled + empty_char * (width - filled)

    color = color_current or (
        C["GREEN"] if ratio > 0.5 else
        C["YELLOW"] if ratio > 0.25 else
        C["RED"]
    )
    return (f"{C['DIM']}[{C['RESET']}"
            f"{color}{bar}{C['RESET']}"
            f"{C['DIM']}]{C['RESET']} "
            f"{label} {current}/{maximum}")


# ═══════════════════════════════════════════════════════════════
#  ║  InnUI 主类                                                ║
# ═══════════════════════════════════════════════════════════════
class InnUI:
    """
    旅店界面
    ────────────────────────────────────────────────────────────
    使用方式：
        ui = InnUI(player, inn_cost, on_rest_callback)
        ui.run()          # 进入交互循环（阻塞）
        ui.render()       # 仅渲染（用于嵌入）
    ────────────────────────────────────────────────────────────
    """

    def __init__(
        self,
        player: dict,
        inn_cost: int,
        on_rest: Optional[Callable[[], bool]] = None,
        on_close: Optional[Callable[[], None]] = None,
    ):
        """
        Args:
            player:       玩家字典，包含 stats 属性
            inn_cost:     住宿费用
            on_rest:      休息回调，返回 True=成功 False=失败
            on_close:     关闭回调
        """
        self.player = player
        self.inn_cost = inn_cost
        self.on_rest = on_rest or (lambda: True)
        self.on_close = on_close or (lambda: None)

        self._state = "menu"   # "menu" | "confirm" | "success" | "fail"
        self._result_msg = ""

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

    # ── 内部状态机 ─────────────────────────────────────────────

    def _input_step(self) -> str:
        """读取一行输入并处理，返回 'close' 表示退出"""
        print(self._CLR + self._build_ui(), end="")

        while True:
            prompt_map = {
                "menu":    f"{C['CYAN']}➜ 选择服务 [1]休息 [2]查看背包 [Q]离开: {C['RESET']}",
                "confirm": f"{C['YELLOW']}➜ 确认休息? [Y]是 [N]否: {C['RESET']}",
                "success": f"{C['GREEN']}➜ 按 Enter 继续... {C['RESET']}",
                "fail":    f"{C['RED']}➜ 按 Enter 继续... {C['RESET']}",
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
            else:  # success / fail
                action = "menu"

            if action != "stay":
                return action  # "close" 或 "refresh"

    def _handle_menu(self, cmd: str) -> str:
        """处理菜单状态输入"""
        # 退出
        if cmd in ("q", "quit", "exit", "2", "背包"):
            return "close"

        # 休息选项
        if cmd in ("1", "休息"):
            self._state = "confirm"
            return "refresh"

        return "stay"

    def _handle_confirm(self, cmd: str) -> str:
        """处理确认状态输入"""
        if cmd in ("y", "yes", "是", "1"):
            self._state = "menu"
            
            # 检查金币
            gold = self.player.get("inventory", {}).get("gold", 0)
            if gold < self.inn_cost:
                self._result_msg = f"💢 金币不足！需要 {self.inn_cost} 金，当前 {gold} 金"
                self._state = "fail"
                return "refresh"
            
            # 检查是否满血
            stats = self.player.get("stats")
            if stats and stats.hp >= stats.max_hp:
                self._result_msg = f"💤 你的生命值已满，无需休息"
                self._state = "fail"
                return "refresh"
            
            # 执行休息
            success = self.on_rest()
            if success:
                # 更新本地金币显示
                self.player["inventory"]["gold"] = gold - self.inn_cost
                self._result_msg = f"✅ 休息完成！恢复了全部生命值！"
                self._state = "success"
            else:
                self._result_msg = f"❌ 休息失败"
                self._state = "fail"
            return "refresh"

        elif cmd in ("n", "no", "否", "2"):
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
        if self._state == "success":
            return self._build_result_ui(is_success=True)
        if self._state == "fail":
            return self._build_result_ui(is_success=False)
        return self._build_menu_ui()

    def _build_menu_ui(self) -> str:
        lines = []
        lines.append(C["CLR"])

        # ══ 标题栏 ══════════════════════════════════════════════
        lines.append(self._box_open())
        lines.append(self._box_title(" 🏠 旅 店  "))
        lines.append(self._box_hline())

        # ══ 旅店描述 ═════════════════════════════════════════════
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}旅店老板笑眯眯地招呼道：{C['RESET']}")
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}「客官，旅途劳顿，来歇歇脚吧！」{C['RESET']}")
        lines.append(self._box_hline())

        # ══ 玩家状态栏 ═════════════════════════════════════════════
        p = self.player
        stats = p.get("stats")
        if stats:
            hp_line = _stat_bar("❤ HP", stats.hp, stats.max_hp, width=14)
            mp_line = _stat_bar("✦ MP", stats.mp, stats.max_mp, width=14)
            stat_line = f"  {hp_line}  {mp_line}"
        else:
            stat_line = ""
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}冒险者: {C['RESET']}{C['BOLD']}{p.get('name', '???')}{C['RESET']}"
                      f"  Lv.{p.get('level', 1)}  {stat_line}  {BOX_THIN['r']}")
        
        gold = p.get("inventory", {}).get("gold", 0)
        lines.append(f"{BOX_THIN['l']}  {C['YELLOW']}💰 {gold} 金{C['RESET']}  {BOX_THIN['r']}")
        lines.append(self._box_hline())

        # ══ 服务选项 ═════════════════════════════════════════════
        lines.append(self._box_row(f"  📋 服 务 列 表  "))
        lines.append(self._box_hline())

        # 休息选项
        rest_needed = stats and stats.hp < stats.max_hp if stats else True
        rest_color = C["GREEN"] if rest_needed else C["DIM"]
        
        lines.append(f"{BOX_THIN['l']}  {C['BOLD']}1{C['RESET']}. 🛏️  休息（恢复全部HP）")
        lines.append(f"{BOX_THIN['l']}      费用: {C['YELLOW']}{self.inn_cost} 金{C['RESET']}"
                     f"  {rest_color}({'需要休息' if rest_needed else 'HP已满'}){C['RESET']}  {BOX_THIN['r']}")
        
        if rest_needed:
            heal_amount = stats.max_hp - stats.hp if stats else 0
            lines.append(f"{BOX_THIN['l']}      恢复: {C['GREEN']}+{heal_amount} HP{C['RESET']}  {BOX_THIN['r']}")
        
        lines.append(self._box_hline())

        # ══ 底部操作提示 ════════════════════════════════════════
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}[1] 休息  [2] 离开旅店{C['RESET']}  {BOX_THIN['r']}")
        lines.append(self._box_close())

        return "\n".join(lines) + "\n"

    def _build_confirm_ui(self) -> str:
        stats = self.player.get("stats")
        hp_before = stats.hp if stats else 0
        max_hp = stats.max_hp if stats else 100
        heal_amount = max_hp - hp_before
        
        gold = self.player.get("inventory", {}).get("gold", 0)
        can_afford = gold >= self.inn_cost
        after_gold = gold - self.inn_cost

        lines = []
        lines.append(C["CLR"])

        # 标题
        lines.append(self._box_open())
        lines.append(self._box_title(" ⚠️  确 认 休 息  "))
        lines.append(self._box_hline())

        # 服务详情
        lines.append(f"{BOX_THIN['l']}  🛏️  休息服务详情:")
        lines.append(self._box_hline())
        
        lines.append(f"{BOX_THIN['l']}  当前HP: {C['RED']}{hp_before}{C['RESET']} / {max_hp}  {BOX_THIN['r']}")
        lines.append(f"{BOX_THIN['l']}  恢复后: {C['GREEN']}{max_hp}{C['RESET']} / {max_hp}  {BOX_THIN['r']}")
        lines.append(f"{BOX_THIN['l']}  恢复量: {C['GREEN']}+{heal_amount} HP{C['RESET']}  {BOX_THIN['r']}")

        lines.append(self._box_hline())

        # 费用
        price_color = C["GREEN"] if can_afford else C["RED"]
        lines.append(f"{BOX_THIN['l']}  💰 所需费用: {price_color}{self.inn_cost}{C['RESET']} 金  {BOX_THIN['r']}")
        lines.append(f"{BOX_THIN['l']}  当前金币: {C['YELLOW']}{gold}{C['RESET']} 金  {BOX_THIN['r']}")
        if can_afford:
            lines.append(f"{BOX_THIN['l']}  剩余金币: {C['CYAN']}{after_gold}{C['RESET']} 金  {BOX_THIN['r']}")
        else:
            lines.append(f"{BOX_THIN['l']}  {C['RED']}💢 金币不足，无法休息！{C['RESET']}  {BOX_THIN['r']}")

        lines.append(self._box_hline())

        # 选项
        if can_afford and heal_amount > 0:
            lines.append(f"{BOX_THIN['l']}  {C['GREEN']}[Y] 确认休息{C['RESET']}   {C['RED']}[N] 取消{C['RESET']}  {BOX_THIN['r']}")
        elif heal_amount <= 0:
            lines.append(f"{BOX_THIN['l']}  {C['DIM']}[N] 返回 (HP已满){C['RESET']}  {BOX_THIN['r']}")
        else:
            lines.append(f"{BOX_THIN['l']}  {C['RED']}[N] 返回 (金币不足){C['RESET']}  {BOX_THIN['r']}")

        lines.append(self._box_close())
        return "\n".join(lines) + "\n"

    def _build_result_ui(self, is_success: bool) -> str:
        color = C["GREEN"] if is_success else C["RED"]
        icon = "✅" if is_success else "❌"
        lines = []
        lines.append(C["CLR"])
        lines.append(self._box_open())
        
        title = " ✅ 休 息 完 成 " if is_success else " ❌ 休 息 失 败 "
        lines.append(self._box_title(title))
        lines.append(self._box_hline())

        if is_success:
            stats = self.player.get("stats")
            max_hp = stats.max_hp if stats else 100
            lines.append(f"{BOX_THIN['l']}  {icon} {color}{self._result_msg}{C['RESET']}  {BOX_THIN['r']}")
            lines.append(f"{BOX_THIN['l']}  💤 生命值已恢复到 {C['GREEN']}{max_hp}{C['RESET']}  {BOX_THIN['r']}")
            gold = self.player.get("inventory", {}).get("gold", 0)
            lines.append(f"{BOX_THIN['l']}  💰 剩余金币: {C['YELLOW']}{gold}{C['RESET']} 金  {BOX_THIN['r']}")
        else:
            lines.append(f"{BOX_THIN['l']}  {icon} {color}{self._result_msg}{C['RESET']}  {BOX_THIN['r']}")

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
        return (f"{BOX_THICK['l']}  {C['BOLD']}{C['YELLOW']}"
                f"{title.center(W)}{C['RESET']}  {BOX_THICK['r']}")

    def _box_row(self, content: str) -> str:
        pad = W - len(content) + 2
        return f"{BOX_THIN['l']}  {content}{' '*pad}{BOX_THIN['r']}"
