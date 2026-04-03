# 🦞 龙虾大冒险 - Git 版本控制指南

## ✅ 已完成配置

### 本地 Git 仓库
- ✅ Git 仓库已初始化
- ✅ .gitignore 已创建（排除 Python 缓存、游戏存档等）
- ✅ 首次提交完成（commit: 79e1241）
- ✅ 提交内容：20 个文件，3775 行代码

### 项目文档
- ✅ README.md - 项目说明文档
- ✅ DEVELOPMENT_LOG.md - 完整开发日志
- ✅ .gitignore - Git 忽略文件配置

### 已提交的文件
```
contracts/          # 接口契约（5 个文件）
modules/           # 游戏模块（5 个文件）
gui/               # 图形界面（5 个文件）
main.py           # 游戏主入口
test_game.py      # 测试脚本
.gitignore        # Git 配置
README.md         # 项目说明
DEVELOPMENT_LOG.md # 开发日志
```

---

## 📋 日常 Git 使用命令

### 1. 查看状态
```bash
# 查看哪些文件被修改了
git status
```

### 2. 添加文件到暂存区
```bash
# 添加所有修改
git add .

# 添加指定文件
git add main.py
git add modules/

# 添加所有 .py 文件
git add *.py
```

### 3. 提交更改
```bash
# 提交并写说明
git commit -m "添加了新功能：训练场系统"

# 详细格式
git commit -m "类型：简短描述

详细说明
- 修改了哪些功能
- 修复了哪些问题"

# 示例
git commit -m "feat: 添加训练场系统

- 实现 6 种训练项目（攻击、防御、速度、幸运、HP、MP）
- 添加训练费用计算
- 实现属性提升预览界面"
```

### 4. 查看提交历史
```bash
# 简洁版
git log --oneline

# 详细版
git log

# 图形化显示
git log --graph --oneline
```

### 5. 撤销更改
```bash
# 撤销工作区的修改（未 add）
git checkout -- 文件名

# 撤销暂存区的修改（已 add 未 commit）
git reset HEAD 文件名

# 撤销最后一次 commit
git reset --soft HEAD~1
```

---

## 🏷️ 提交信息规范

### 类型前缀
- `feat` - 新功能（feature）
- `fix` - 修复 bug（fix）
- `docs` - 文档更新（documentation）
- `style` - 代码格式（不影响功能）
- `refactor` - 重构（既不是新功能也不是 bug 修复）
- `test` - 测试相关
- `chore` - 构建过程或辅助工具变动

### 示例
```bash
# 新功能
git commit -m "feat: 添加 Boss 战机制"

# 修复 bug
git commit -m "fix: 修复战斗系统暴击计算错误"

# 文档更新
git commit -m "docs: 更新 README 添加安装说明"

# 重构
git commit -m "refactor: 优化战斗系统代码结构"

# 测试
git commit -m "test: 添加物品栏系统单元测试"
```

---

## 🌐 推送到 GitHub（可选）

### 第一步：在 GitHub 创建仓库
1. 访问 https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - Repository name: `lobster_game`
   - Description: "🦞 Lobster's Adventure - A turn-based RPG game"
   - 选择 "Public"（公开）
   - **不要** 勾选 "Initialize this repository with a README"
4. 点击 "Create repository"

### 第二步：关联远程仓库
```bash
# 替换为你的 GitHub 用户名
git remote add origin https://github.com/你的用户名/lobster_game.git

# 验证是否添加成功
git remote -v
```

### 第三步：推送代码
```bash
# 推送主分支到 GitHub
git push -u origin master

# 以后推送（简写）
git push
```

### 第四步：从 GitHub 拉取
```bash
# 拉取最新代码
git pull
```

---

## 📊 版本管理最佳实践

### 1. 频繁提交
```bash
# ✅ 好的习惯
- 完成一个小功能就提交一次
- 每天下班前提交
- 提交信息写清楚

# ❌ 不好的习惯
- 一周提交一次
- 提交信息写 "update" 或 "修改"
- 一次提交包含太多改动
```

### 2. 分支管理（进阶）
```bash
# 创建新分支（开发新功能）
git branch feature/new-skill-system

# 切换到新分支
git checkout feature/new-skill-system

# 合并分支到 master
git checkout master
git merge feature/new-skill-system

# 删除分支
git branch -d feature/new-skill-system
```

### 3. 打标签（发布版本）
```bash
# 创建版本标签
git tag -a v1.0.0 -m "Lobster's Adventure v1.0.0 - 首次发布"

# 查看所有标签
git tag

# 推送标签到 GitHub
git push origin v1.0.0
```

---

## 📁 项目文件结构

```
lobster_game/
├── .git/                  # Git 仓库（隐藏文件夹）
├── .gitignore            # Git 忽略配置
├── README.md             # 项目说明
├── DEVELOPMENT_LOG.md    # 开发日志
├── GIT_GUIDE.md          # 本文件
├── contracts/            # 接口定义
├── modules/              # 游戏模块
├── gui/                  # 图形界面
├── game_assets/          # 游戏素材（未提交）
├── main.py              # 游戏主入口
└── test_game.py         # 测试脚本
```

---

## 🎯 下一步行动

### 本地开发流程
1. 开发新功能
2. `git add .` - 添加修改
3. `git commit -m "描述"` - 提交
4. 重复 1-3 步

### 推送到 GitHub（推荐）
1. 在 GitHub 创建仓库
2. `git remote add origin https://github.com/用户名/lobster_game.git`
3. `git push -u origin master`
4. 以后每次开发后 `git push`

### 备份策略
- ✅ 本地 Git 仓库（版本历史）
- ✅ GitHub 远程仓库（云端备份）
- ✅ 定期导出压缩包（额外保险）

---

## 📞 常用 Git 命令速查表

| 命令 | 说明 |
|------|------|
| `git status` | 查看状态 |
| `git add 文件` | 添加文件到暂存区 |
| `git commit -m "信息"` | 提交更改 |
| `git log` | 查看提交历史 |
| `git push` | 推送到远程仓库 |
| `git pull` | 从远程拉取 |
| `git checkout -- 文件` | 撤销修改 |
| `git branch` | 查看分支 |
| `git tag` | 管理版本标签 |

---

## 🎓 学习资源

- **Git 官方文档**: https://git-scm.com/doc
- **GitHub 教程**: https://docs.github.com/cn/get-started
- **Git 入门教程**: https://www.runoob.com/git/git-tutorial.html
- **廖雪峰 Git 教程**: https://www.liaoxuefeng.com/wiki/896043488029600

---

**🦞 祝你开发顺利！**

*最后更新：2026-04-03*
