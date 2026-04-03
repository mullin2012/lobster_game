"""
【训练场界面】- 龙虾大冒险 GUI 模块
提升属性、确认费用
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
def _stat_bar(label: str, current: int, maximum: int = None,
              filled_char="█", empty_char="░",
              color_current=None, width: int = 14) -> str:
    """生成单条属性条（可无上限）"""
    if maximum is not None and maximum > 0:
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
                f"{label} {current}")
    else:
        bar = filled_char * min(current, width)
        color = color_current or C["CYAN"]
        return f"{label} {color}{current}{C['RESET']}"


# ═══════════════════════════════════════════════════════════════
#  ║  TrainingUI 主类                                           ║
# ═══════════════════════════════════════════════════════════════
class TrainingUI:
    """
    训练场界面
    ────────────────────────────────────────────────────────────
    使用方式：
        ui = TrainingUI(player, training_cost, on_train_callback)
        ui.run()          # 进入交互循环（阻塞）
        ui.render()       # 仅渲染（用于嵌入）
    ────────────────────────────────────────────────────────────
    """

    # 训练项目配置
    TRAINING_OPTIONS = {
        "attack": {
            "name": "攻击训练",
            "icon": "⚔️",
            "stat_key": "attack",
            "cost_per_level": 50,
            "max_level": 10,
            "description": "提升攻击力",
        },
        "defense": {
            "name": "防御训练",
            "icon": "🛡️",
            "stat_key": "defense",
            "cost_per_level": 50,
            "max_level": 10,
            "description": "提升防御力",
        },
        "speed": {
            "name": "速度训练",
            "icon": "⚡",
            "stat_key": "speed",
            "cost_per_level": 40,
            "max_level": 10,
            "description": "提升速度",
        },
        "luck": {
            "name": "幸运训练",
            "icon": "🍀",
            "stat_key": "luck",
            "cost_per_level": 60,
            "max_level": 5,
            "description": "提升幸运值",
        },
        "max_hp": {
            "name": "体力训练",
            "icon": "❤️",
            "stat_key": "max_hp",
            "cost_per_level": 30,
            "max_level": 20,
            "description": "提升最大生命值",
        },
        "max_mp": {
            "name": "魔力训练",
            "icon": "💙",
            "stat_key": "max_mp",
            "cost_per_level": 30,
            "max_level": 20,
            "description": "提升最大魔法值",
        },
    }

    def __init__(
        self,
        player: dict,
        training_cost: int,
        on_train: Optional[Callable[[str, int], bool]] = None,
        on_close: Optional[Callable[[], None]] = None,
    ):
        """
        Args:
            player:       玩家字典，包含 stats 属性
            training_cost: 每次训练的基础费用
            on_train:    训练回调，参数为 (属性名, 训练次数)，返回 True=成功
            on_close:    关闭回调
        """
        self.player = player
        self.training_cost = training_cost
        self.on_train = on_train or (lambda _: True)
        self.on_close = on_close or (lambda: None)

        self._state = "menu"   # "menu" | "confirm" | "success" | "fail"
        self._selected_stat = None
        self._train_amount = 1
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
                "menu":    f"{C['CYAN']}➜ 选择训练项目 [1-6] [Q]离开: {C['RESET']}",
                "confirm": f"{C['YELLOW']}➜ 确认训练? [1-10]次数 [Y]确认 [N]取消: {C['RESET']}",
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
        if cmd in ("q", "quit", "exit"):
            return "close"

        # 数字选择
        stat_keys = list(self.TRAINING_OPTIONS.keys())
        if cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(stat_keys):
                self._selected_stat = stat_keys[idx]
                self._train_amount = 1
                self._state = "confirm"
                return "refresh"

        return "stay"

    def _handle_confirm(self, cmd: str) -> str:
        """处理确认状态输入"""
        # 数字输入 - 选择训练次数
        if cmd.isdigit():
            amount = int(cmd)
            if 1 <= amount <= 10:
                self._train_amount = amount
                return "refresh"
        
        # 确认训练
        if cmd in ("y", "yes", "是"):
            self._state = "menu"
            
            # 检查金币
            gold = self.player.get("inventory", {}).get("gold", 0)
            option = self.TRAINING_OPTIONS[self._selected_stat]
            total_cost = option["cost_per_level"] * self._train_amount
            
            if gold < total_cost:
                self._result_msg = f"💢 金币不足！需要 {total_cost} 金，当前 {gold} 金"
                self._state = "fail"
                return "refresh"
            
            # 执行训练
            success = self.on_train(self._selected_stat, self._train_amount)
            if success:
                self.player["inventory"]["gold"] = gold - total_cost
                stat_name = option["name"]
                gain = option["cost_per_level"] // 10 * self._train_amount  # 简化的增益计算
                self._result_msg = f"✅ {stat_name}完成！提升了 {gain} 点属性！"
                self._state = "success"
            else:
                self._result_msg = f"❌ 训练失败"
                self._state = "fail"
            self._selected_stat = None
            self._train_amount = 1
            return "refresh"

        # 取消
        elif cmd in ("n", "no", "否", "2"):
            self._selected_stat = None
            self._train_amount = 1
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
        lines.append(self._box_title(" ⚔️ 训 练 场  "))
        lines.append(self._box_hline())

        # ══ 训练师描述 ═════════════════════════════════════════════
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}训练师严肃地说：{C['RESET']}")
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}「只有经受住考验，才能变得更强！」{C['RESET']}")
        lines.append(self._box_hline())

        # ══ 玩家状态栏 ═════════════════════════════════════════════
        p = self.player
        stats = p.get("stats")
        if stats:
            atk_line = f"⚔️ 攻击: {C['RED']}{stats.attack}{C['RESET']}"
            def_line = f"🛡 防御: {C['BLUE']}{stats.defense}{C['RESET']}"
            spd_line = f"⚡ 速度: {C['YELLOW']}{stats.speed}{C['RESET']}"
            luk_line = f"🍀 幸运: {C['MAGENTA']}{stats.luck}{C['RESET']}"
            hp_line = f"❤️ HP: {C['GREEN']}{stats.hp}/{stats.max_hp}{C['RESET']}"
            mp_line = f"💙 MP: {C['CYAN']}{stats.mp}/{stats.max_mp}{C['RESET']}"
            
            lines.append(f"{BOX_THIN['l']}  {C['BOLD']}{p.get('name', '???')}{C['RESET']} Lv.{p.get('level', 1)}  {BOX_THIN['r']}")
            lines.append(f"{BOX_THIN['l']}  {atk_line}  {def_line}  {spd_line}  {BOX_THIN['r']}")
            lines.append(f"{BOX_THIN['l']}  {hp_line}  {mp_line}  {luk_line}  {BOX_THIN['r']}")
        
        gold = p.get("inventory", {}).get("gold", 0)
        lines.append(f"{BOX_THIN['l']}  {C['YELLOW']}💰 {gold} 金{C['RESET']}  {BOX_THIN['r']}")
        lines.append(self._box_hline())

        # ══ 训练项目列表 ═════════════════════════════════════════════
        lines.append(self._box_row(f"  📋 训 练 项 目  "))
        lines.append(self._box_hline())

        stat_keys = list(self.TRAINING_OPTIONS.keys())
        for i, stat_key in enumerate(stat_keys):
            option = self.TRAINING_OPTIONS[stat_key]
            current_val = getattr(stats, stat_key, 0) if stats else 0
            
            # 计算费用和增益
            cost = option["cost_per_level"]
            gain = cost // 10  # 每点费用提升10点属性（简化）
            
            lines.append(f"{BOX_THIN['l']}  {C['BOLD']}{i+1}{C['RESET']}. {option['icon']} {option['name']}")
            lines.append(f"{BOX_THIN['l']}      当前: {C['CYAN']}{current_val}{C['RESET']} "
                         f"  费用: {C['YELLOW']}{cost} 金{C['RESET']}/次 "
                         f"  提升: {C['GREEN']}+{gain}{C['RESET']}  {BOX_THIN['r']}")

        lines.append(self._box_hline())

        # ══ 底部操作提示 ════════════════════════════════════════
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}[1-6] 选择训练项目  [Q] 离开{C['RESET']}  {BOX_THIN['r']}")
        lines.append(self._box_close())

        return "\n".join(lines) + "\n"

    def _build_confirm_ui(self) -> str:
        option = self.TRAINING_OPTIONS[self._selected_stat]
        stats = self.player.get("stats")
        current_val = getattr(stats, self._selected_stat, 0) if stats else 0
        
        cost_per_level = option["cost_per_level"]
        total_cost = cost_per_level * self._train_amount
        gain_per_level = cost_per_level // 10
        total_gain = gain_per_level * self._train_amount
        
        gold = self.player.get("inventory", {}).get("gold", 0)
        can_afford = gold >= total_cost
        after_gold = gold - total_cost

        lines = []
        lines.append(C["CLR"])

        # 标题
        lines.append(self._box_open())
        lines.append(self._box_title(f" ⚠️ 确 认 {option['name']}  "))
        lines.append(self._box_hline())

        # 训练详情
        lines.append(f"{BOX_THIN['l']}  {option['icon']} 训练项目: {C['BOLD']}{option['name']}{C['RESET']}")
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}{option['description']}{C['RESET']}")
        lines.append(self._box_hline())

        # 属性变化预览
        lines.append(f"{BOX_THIN['l']}  📊 属性变化:")
        lines.append(f"{BOX_THIN['l']}      {option['icon']} {option['stat_key']}: "
                     f"{C['CYAN']}{current_val}{C['RESET']} → {C['GREEN']}{current_val + total_gain}{C['RESET']} "
                     f"({C['GREEN']}+{total_gain}{C['RESET']})  {BOX_THIN['r']}")
        lines.append(self._box_hline())

        # 费用
        lines.append(f"{BOX_THIN['l']}  💰 训练费用:")
        lines.append(f"{BOX_THIN['l']}      单次: {C['YELLOW']}{cost_per_level}{C['RESET']} 金")
        lines.append(f"{BOX_THIN['l']}      次数: {C['WHITE']}{self._train_amount}{C['RESET']} 次")
        lines.append(f"{BOX_THIN['l']}      总计: {C['YELLOW']}{total_cost}{C['RESET']} 金")
        lines.append(self._box_hline())

        # 金币状态
        price_color = C["GREEN"] if can_afford else C["RED"]
        lines.append(f"{BOX_THIN['l']}  当前金币: {C['YELLOW']}{gold}{C['RESET']} 金  {BOX_THIN['r']}")
        if can_afford:
            lines.append(f"{BOX_THIN['l']}  剩余金币: {C['CYAN']}{after_gold}{C['RESET']} 金  {BOX_THIN['r']}")
        else:
            lines.append(f"{BOX_THIN['l']}  {C['RED']}💢 金币不足，无法训练！{C['RESET']}  {BOX_THIN['r']}")

        lines.append(self._box_hline())

        # 选项
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}训练次数: 1-10{C['RESET']}")
        if can_afford:
            lines.append(f"{BOX_THIN['l']}  {C['GREEN']}[Y/Enter] 确认训练  [N] 取消  [1-10] 选择次数{C['RESET']}  {BOX_THIN['r']}")
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
        
        title = " ✅ 训 练 完 成 " if is_success else " ❌ 训 练 失 败 "
        lines.append(self._box_title(title))
        lines.append(self._box_hline())

        if is_success:
            stats = self.player.get("stats")
            lines.append(f"{BOX_THIN['l']}  {icon} {color}{self._result_msg}{C['RESET']}  {BOX_THIN['r']}")
            
            # 显示更新后的属性
            if stats:
                lines.append(self._box_hline())
                lines.append(f"{BOX_THIN['l']}  📊 当前属性:")
                lines.append(f"{BOX_THIN['l']}      ⚔️ 攻击: {C['RED']}{stats.attack}{C['RESET']}  "
                             f"🛡 防御: {C['BLUE']}{stats.defense}{C['RESET']}  {BOX_THIN['r']}")
                lines.append(f"{BOX_THIN['l']}      ⚡ 速度: {C['YELLOW']}{stats.speed}{C['RESET']}  "
                             f"🍀 幸运: {C['MAGENTA']}{stats.luck}{C['RESET']}  {BOX_THIN['r']}")
            
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
