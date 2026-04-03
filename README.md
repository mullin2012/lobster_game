# 🦞 龙虾大冒险 (Lobster's Adventure)

一款用 Python + Pygame 开发的回合制 RPG 游戏

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Pygame](https://img.shields.io/badge/pygame-2.5+-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 🎮 游戏特色

- ⚔️ **经典回合制战斗** - 暴击、闪避、状态效果
- 🐉 **丰富的怪物系统** - 5+ 种怪物类型，智能 AI
- 🎒 **完整的物品装备** - 武器、防具、药水、卷轴
- 🗺️ **多场景探索** - 城镇、森林、山洞、城堡
- 🎯 **技能与职业** - 3 个职业，9 种技能
- 💾 **存档系统** - JSON 格式，安全保存
- 🖥️ **精美 GUI** - Pygame 图形界面 + ASCII 艺术风格

## 🚀 快速开始

### 安装依赖
```bash
pip install pygame
```

### 运行游戏
```bash
# 控制台版本
python main.py

# GUI 版本
python gui/main_gui.py
```

### 运行测试
```bash
python test_game.py
```

## 📁 项目结构

```
lobster_game/
├── contracts/           # 接口契约和数据类型
│   ├── types.py        # 数据类型定义
│   ├── ibattle.py      # 战斗系统接口
│   ├── imonster.py     # 怪物系统接口
│   └── iinventory.py   # 物品栏系统接口
├── modules/            # 游戏模块
│   ├── battle_system.py    # 战斗系统实现
│   ├── monster_system.py   # 怪物系统实现
│   ├── inventory_system.py # 物品栏系统实现
│   └── scene_system.py     # 场景系统实现
├── gui/                # 图形界面
│   ├── main_gui.py     # 主界面
│   ├── shop_ui.py      # 商店界面
│   ├── inn_ui.py       # 旅店界面
│   └── training_ui.py  # 训练场界面
├── game_assets/        # 游戏素材
├── main.py            # 游戏主入口
├── test_game.py       # 测试脚本
└── DEVELOPMENT_LOG.md # 开发日志
```

## 🎯 游戏系统

### 战斗系统
- 伤害计算：攻击×随机波动 - 防御×0.5
- 暴击机制：幸运值影响，最高 15%
- 闪避系统：速度差决定闪避率
- 状态效果：中毒、烧伤等持续伤害

### 怪物系统
- 5 种预定义怪物：史莱姆、哥布林、骷髅战士、宝箱怪、火焰巨龙
- 等级缩放：每级增加 10% 属性
- 智能 AI：优先攻击 HP 最低的目标
- 战利品掉落：基于稀有度和概率

### 物品系统
- 武器：增加攻击力
- 护甲：增加防御力
- 药水：恢复生命值
- 卷轴：临时属性加成

### 场景系统
- 城镇：商店、旅店、训练场
- 森林：初级怪物，草药采集
- 山洞：中级怪物，矿石采集
- 城堡：Boss 战，最终挑战

## 🛠️ 开发信息

- **开发语言**: Python 3.10+
- **游戏引擎**: Pygame 2.5+
- **开发周期**: 3 个月
- **代码量**: 3000+ 行
- **开发方式**: 100% 手工编码
- **版本控制**: Git + GitHub

## 📝 开发日志

详见 [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md)

## 🎨 游戏截图

（待添加）

## 📋 更新日志

### v1.0.0 (2026-04-03)
- ✅ 完整的战斗系统
- ✅ 完整的怪物系统
- ✅ 完整的物品栏系统
- ✅ 场景系统
- ✅ GUI 界面（主菜单、商店、旅店、训练场）
- ✅ 存档系统
- ✅ 技能系统

### 计划中
- [ ] 更多怪物种类
- [ ] 任务系统
- [ ] 战斗动画优化
- [ ] 多人游戏支持

## 🤝 贡献者

- **龙虾 1 号**: 战斗系统
- **龙虾 2 号**: 怪物系统
- **龙虾 3 号**: 物品栏系统
- **（你的名字）**: 项目统筹、GUI 开发

## 📄 许可证

MIT License

## 📧 联系方式

- GitHub: https://github.com/你的用户名/lobster_game
- Email: your-email@example.com

---

**🦞 祝你游戏愉快！**
