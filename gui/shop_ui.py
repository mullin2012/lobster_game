"""
【商店界面】- 龙虾大冒险 GUI 模块
物品展示、购买、货币显示
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
#  ║  稀有度颜色映射                                              ║
# ═══════════════════════════════════════════════════════════════
RARITY_COLORS = {
    "common":     C["WHITE"],
    "uncommon":   C["GREEN"],
    "rare":       C["BLUE"],
    "epic":       C["MAGENTA"],
    "legendary":  C["YELLOW"],
}

RARITY_EMOJI = {
    "common":     "⚪",
    "uncommon":   "🟢",
    "rare":       "🔵",
    "epic":       "🟣",
    "legendary":  "🟡",
}

ITEM_TYPE_ICON = {
    "weapon": "⚔️",
    "armor":  "🛡️",
    "potion": "🧪",
    "scroll": "📜",
    "accessory": "💍",
}

# ═══════════════════════════════════════════════════════════════
#  ║  边框字符（粗细两套）                                        ║
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
BOX_MIXED = {
    "tl": "╭", "tr": "╮",
    "bl": "╰", "br": "╯",
    "l":  "│",
    "r":  "│",
    "h":  "─",
}

W = 52   # 主框宽度
W2 = 22  # 副框宽度（半宽）


# ═══════════════════════════════════════════════════════════════
#  ║  内部辅助函数                                                ║
# ═══════════════════════════════════════════════════════════════

def _header_row(title: str, box=None) -> list[str]:
    """生成标题行（双线框）"""
    b = box or BOX_THICK
    line = f"{b['tl']}{b['h']*W}{b['tr']}"
    title_line = (f"{b['l']}  {C['BOLD']}{C['YELLOW']}{title.center(W)}{C['RESET']}  {b['r']}")
    return [line, title_line]


def _footer_row(box=None) -> str:
    b = box or BOX_THICK
    return f"{b['bl']}{b['h']*W}{b['br']}"


def _section(title: str, box=None) -> list[str]:
    """生成分隔标题行"""
    b = box or BOX_THIN
    return [
        f"{b['l']}  {C['BOLD']}{C['CYAN']}━━ {title} ━━{C['RESET']}".ljust(W + 2) + b['r'],
    ]


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


def _rarity_bar(rarity: str) -> str:
    """稀有度色条"""
    color = RARITY_COLORS.get(rarity, C["WHITE"])
    return f"{color}{'━'*16}{C['RESET']}"


def _stat_value(base: int, bonus: int, color: str = C["GREEN"]) -> str:
    """显示 基础+加成=总数值"""
    if bonus != 0:
        return f"{base} {C['DIM']}(+{bonus}){C['RESET']} {C['DIM']}→{C['RESET']} {color}{base+bonus}{C['RESET']}"
    return f"{base}"


# ═══════════════════════════════════════════════════════════════
#  ║  ShopUI 主类                                                ║
# ═══════════════════════════════════════════════════════════════
class ShopUI:
    """
    商店界面
    ────────────────────────────────────────────────────────────
    使用方式：
        ui = ShopUI(player, shop_items, on_buy_callback)
        ui.run()          # 进入交互循环（阻塞）
        ui.render()       # 仅渲染（用于嵌入）
    ────────────────────────────────────────────────────────────
    """

    # 分类标签
    CATEGORIES = {
        "全部":   ["weapon", "armor", "potion", "scroll", "accessory"],
        "武器":   ["weapon"],
        "防具":   ["armor"],
        "药水":   ["potion"],
        "卷轴":   ["scroll"],
        "饰品":   ["accessory"],
    }

    # 每页物品数量
    PAGE_SIZE = 5

    def __init__(
        self,
        player: dict,
        shop_items: list[dict],
        gold: int,
        on_buy: Optional[Callable[[dict], bool]] = None,
        on_close: Optional[Callable[[], None]] = None,
    ):
        """
        Args:
            player:       玩家字典
            shop_items:   商店物品列表 [{name, item_type, rarity, description, stat_bonus, heal_amount, value}, ...]
            gold:         当前金币数
            on_buy:       购买回调，返回 True=成功 False=失败/取消
            on_close:     关闭回调
        """
        self.player = player
        self.gold = gold
        self.shop_items = shop_items
        self.on_buy = on_buy or (lambda _: True)
        self.on_close = on_close or (lambda: None)

        self.category = "全部"
        self.page = 0
        self.selected = 0   # 选中项索引（0-based）
        self._state = "menu"   # "menu" | "confirm" | "success" | "fail"

        self._confirm_item: Optional[dict] = None
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

    def _filtered_items(self) -> list[dict]:
        types = self.CATEGORIES[self.category]
        return [it for it in self.shop_items if it.get("item_type") in types]

    def _paged_items(self) -> tuple[list[dict], int, int]:
        items = self._filtered_items()
        total = len(items)
        start = self.page * self.PAGE_SIZE
        end = min(start + self.PAGE_SIZE, total)
        return items[start:end], start + 1, end

    def _input_step(self) -> str:
        """读取一行输入并处理，返回 'close' 表示退出"""
        print(self._CLR + self._build_ui(), end="")

        while True:
            prompt_map = {
                "menu":    f"{C['CYAN']}➜ 输入编号/分类/←→翻页/Q退出: {C['RESET']}",
                "confirm": f"{C['YELLOW']}➜ 确认购买? [Y]是 [N]否: {C['RESET']}",
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

        # 分类切换
        if cmd in self.CATEGORIES:
            self.category = cmd
            self.page = 0
            self.selected = 0
            return "refresh"

        # 翻页
        if cmd in ("←", "left", "prev", "p"):
            self.page = max(0, self.page - 1)
            self.selected = 0
            return "refresh"
        if cmd in ("→", "right", "next", "n"):
            items = self._filtered_items()
            max_page = max(0, (len(items) - 1) // self.PAGE_SIZE)
            self.page = min(max_page, self.page + 1)
            self.selected = 0
            return "refresh"

        # 方向键/上下
        if cmd in ("↑", "up", "k", "w"):
            self.selected = max(0, self.selected - 1)
            return "refresh"
        if cmd in ("↓", "down", "s", "j"):
            self.selected = min(len(self._paged_items()[0]) - 1, self.selected + 1)
            return "refresh"

        # 数字选择
        if cmd.isdigit():
            idx = int(cmd) - 1
            page_items = self._paged_items()[0]
            if 0 <= idx < len(page_items):
                self.selected = idx
                self._confirm_item = page_items[idx]
                self._state = "confirm"
                return "refresh"
            return "stay"

        return "stay"

    def _handle_confirm(self, cmd: str) -> str:
        """处理确认状态输入"""
        if cmd in ("y", "yes", "是", "1"):
            self._state = "menu"
            item = self._confirm_item
            price = item.get("value", 0)
            if self.gold < price:
                self._result_msg = f"💢 金币不足！需要 {price} 金，当前 {self.gold} 金"
                self._state = "fail"
                return "refresh"
            success = self.on_buy(item)
            if success:
                self.gold -= price
                self._result_msg = f"✅ 购买成功！-{price} 金"
                self._state = "success"
            else:
                self._result_msg = f"❌ 购买失败，背包可能已满"
                self._state = "fail"
            self._confirm_item = None
            return "refresh"

        elif cmd in ("n", "no", "否", "2"):
            self._confirm_item = None
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
        lines.append(self._box_title(" ⚖️  商 店  "))
        lines.append(self._box_hline())

        # ══ 玩家状态栏 ══════════════════════════════════════════
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
        lines.append(f"{BOX_THIN['l']}  {C['YELLOW']}💰 {self.gold} 金{C['RESET']}"
                      f"  {C['DIM']}背包 {len(self.player.get('inventory', {}).get('items', []))}"
                      f"/{self.player.get('inventory', {}).get('capacity', 0)} 空位{C['RESET']}"
                      f"  {BOX_THIN['r']}")
        lines.append(self._box_hline())

        # ══ 分类标签 ═════════════════════════════════════════════
        cat_parts = []
        for name in self.CATEGORIES:
            if name == self.category:
                cat_parts.append(f"{C['INVERT']}{C['BOLD']} {name} {C['RESET']}")
            else:
                cat_parts.append(f"{C['CYAN']}{name}{C['RESET']}")
        cat_row = "  ".join(cat_parts)
        lines.append(f"{BOX_THIN['l']}  {cat_row}".ljust(W + 3) + BOX_THIN['r'])
        lines.append(self._box_hline())

        # ══ 商品列表 ═════════════════════════════════════════════
        page_items, start_idx, end_idx = self._paged_items()
        items_count = len(self._filtered_items())

        lines.append(self._box_row(f"  商品列表 ({start_idx}-{end_idx}/{items_count})  "))
        lines.append(self._box_hline())

        if not page_items:
            lines.append(self._box_row(f"  {C['DIM']}该分类暂无商品{C['RESET']}  "))
        else:
            for i, item in enumerate(page_items):
                is_sel = (i == self.selected)
                prefix = "  "
                suffix = "  "
                if is_sel:
                    prefix = f" {C['BG_CYAN']}{C['BOLD']}►{C['RESET']} "
                    suffix = f" {C['BG_CYAN']} {C['RESET']}"
                    bg = C['BG_CYAN']
                    inv = C['RESET']
                else:
                    bg = ""
                    inv = C['RESET']

                rarity = item.get("rarity", "common")
                rcolor = RARITY_COLORS.get(rarity, C["WHITE"])
                remoji = RARITY_EMOJI.get(rarity, "⚪")
                itype = item.get("item_type", "?")
                iicon = ITEM_TYPE_ICON.get(itype, "📦")
                name = item.get("name", "?")
                price = item.get("value", 0)
                desc = item.get("description", "")
                bonus = item.get("stat_bonus", {})
                heal = item.get("heal_amount", 0)

                # 价格颜色
                price_str = (f"{C['GREEN']}{price:>4}{C['RESET']}"
                             if self.gold >= price else f"{C['RED']}{price:>4}{C['RESET']}")

                # 物品效果描述
                effect_parts = []
                if itype == "weapon":
                    atk = bonus.get("attack", 0)
                    effect_parts.append(f"{C['RED']}⚔ ATK+{atk}{C['RESET']}")
                elif itype == "armor":
                    dfs = bonus.get("defense", 0)
                    effect_parts.append(f"{C['BLUE']}🛡 DEF+{dfs}{C['RESET']}")
                elif itype == "potion":
                    effect_parts.append(f"{C['GREEN']}❤ +{heal} HP{C['RESET']}")
                elif itype == "scroll":
                    effect_parts.append(f"{C['MAGENTA']}✨ 特殊{C['RESET']}")
                effect_str = "  ".join(effect_parts)

                line1 = (f"{prefix}{remoji} {C['BOLD']}{name}{C['RESET']}"
                         f"  {rcolor}【{rarity.upper()}】{C['RESET']}"
                         f"  💰 {price_str}金"
                         f"{suffix}")
                line1_padded = line1.rstrip()
                lines.append(f"{BOX_THIN['l']}{line1_padded.ljust(W+2)}{BOX_THIN['r']}")

                line2 = (f"{prefix}{iicon} {C['DIM']}{desc}{C['RESET']}"
                         f"  {effect_str}"
                         f"{suffix}")
                line2_padded = line2.rstrip()
                lines.append(f"{BOX_THIN['l']}{line2_padded.ljust(W+2)}{BOX_THIN['r']}")

                if is_sel:
                    lines.append(f"{BOX_THIN['l']}  {C['YELLOW']}↪ 输入编号 [Y]购买  [N]否  [↑↓]选择{C['RESET']}  {BOX_THIN['r']}")
                lines.append(self._box_hline())

        # ══ 分页提示 ═══════════════════════════════════════════
        max_page = max(0, (items_count - 1) // self.PAGE_SIZE)
        page_hint = (f"{C['DIM']}[←]上一页  [→]下一页{C['RESET']}"
                     if max_page > 0 else f"{C['DIM']}无可用分页{C['RESET']}")
        lines.append(f"{BOX_THIN['l']}  {page_hint}  页 {self.page+1}/{max(max_page,1)}  {BOX_THIN['r']}")
        lines.append(self._box_hline())

        # ══ 底部操作提示 ════════════════════════════════════════
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}[Q]关闭  [1-{min(len(page_items),9)}]购买选中物品{C['RESET']}  {BOX_THIN['r']}")
        lines.append(self._box_close())

        return "\n".join(lines) + "\n"

    def _build_confirm_ui(self) -> str:
        item = self._confirm_item
        rarity = item.get("rarity", "common")
        rcolor = RARITY_COLORS.get(rarity, C["WHITE"])
        price = item.get("value", 0)
        itype = item.get("item_type", "?")
        iicon = ITEM_TYPE_ICON.get(itype, "📦")
        name = item.get("name", "?")
        desc = item.get("description", "")
        bonus = item.get("stat_bonus", {})
        heal = item.get("heal_amount", 0)

        lines = []
        lines.append(C["CLR"])

        # 标题
        lines.append(self._box_open())
        lines.append(self._box_title(" ⚠️  确 认 购 买  "))
        lines.append(self._box_hline())

        # 商品预览
        lines.append(f"{BOX_THIN['l']}  {iicon} {C['BOLD']}{name}{C['RESET']}"
                     f"  {rcolor}【{rarity.upper()}】{C['RESET']}  {BOX_THIN['r']}")
        lines.append(f"{BOX_THIN['l']}  {C['DIM']}{desc}{C['RESET']}  {BOX_THIN['r']}")

        # 属性预览
        if itype == "weapon":
            atk = bonus.get("attack", 0)
            lines.append(f"{BOX_THIN['l']}  {C['RED']}⚔ 攻击力 +{atk}{C['RESET']}  {BOX_THIN['r']}")
        elif itype == "armor":
            dfs = bonus.get("defense", 0)
            lines.append(f"{BOX_THIN['l']}  {C['BLUE']}🛡 防御力 +{dfs}{C['RESET']}  {BOX_THIN['r']}")
        elif itype == "potion":
            lines.append(f"{BOX_THIN['l']}  {C['GREEN']}❤ 恢复 {heal} HP{C['RESET']}  {BOX_THIN['r']}")

        lines.append(self._box_hline())

        # 费用
        can_afford = self.gold >= price
        price_color = C["GREEN"] if can_afford else C["RED"]
        lines.append(f"{BOX_THIN['l']}  💰 所需金币: {price_color}{price}{C['RESET']}  "
                     f"  剩余: {C['YELLOW']}{self.gold}{C['RESET']}  {BOX_THIN['r']}")
        if can_afford:
            after = self.gold - price
            lines.append(f"{BOX_THIN['l']}  购买后余额: {C['CYAN']}{after}{C['RESET']}  {BOX_THIN['r']}")
        else:
            lines.append(f"{BOX_THIN['l']}  {C['RED']}💢 金币不足，无法购买！{C['RESET']}  {BOX_THIN['r']}")

        lines.append(self._box_hline())

        # 选项
        if can_afford:
            lines.append(f"{BOX_THIN['l']}  {C['GREEN']}[Y] 确认购买{C['RESET']}   {C['RED']}[N] 取消{C['RESET']}  {BOX_THIN['r']}")
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
        title = " ✅ 购 买 成 功 " if is_success else " ❌ 购 买 失 败 "
        lines.append(self._box_title(title))
        lines.append(self._box_hline())

        if is_success:
            item = self._confirm_item or {}
            lines.append(f"{BOX_THIN['l']}  {icon} {color}{self._result_msg}{C['RESET']}  {BOX_THIN['r']}")
            lines.append(f"{BOX_THIN['l']}  📦 物品已放入背包  {BOX_THIN['r']}")
            lines.append(f"{BOX_THIN['l']}  💰 剩余金币: {C['YELLOW']}{self.gold}{C['RESET']}  {BOX_THIN['r']}")
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
