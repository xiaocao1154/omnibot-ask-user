# 🤖 ask-user — AI Agent 智能需求澄清 Skill

> 让 AI Agent 像人一样提问：填空题收集事实，选择题确认偏好，一问一答精准高效。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OmniBot Skill](https://img.shields.io/badge/OmniBot-Skill-blueviolet.svg)](https://github.com/xiaocao1154)

---

## 👨‍💻 关于开发者

我是 **xiaocao1154**，一个热爱 AI Agent 和自动化的独立开发者。

这是我的 **第二个 Skill 作品**。我的第一个作品是 [xiaocao-shop](https://github.com/xiaocao1154/xiaocao-shop)。

我的开发理念很简单：**AI 不应该猜用户想要什么，而应该主动问清楚再动手。**

在使用各种 AI Agent（OpenCode、Hermes、Claude、ChatGPT）的过程中，我发现一个共同的痛点——你给一个模糊的需求，Agent 就开始猜测执行，结果往往不是你想要的。于是我开始思考：能不能让 Agent 先像人一样提问，把需求搞清楚了再干活？

这就是 `ask-user` 的由来。

---

## 🎯 它是干什么的

`ask-user` 是一个 **OmniBot Skill 插件**，核心功能只有一件事：**在 Agent 执行任务之前，智能地向用户提问以补全需求信息。**

它支持两种提问模式：

### 模式一：原生对话提问（主功能）

Agent 在聊天中自动识别模糊需求，逐题向用户提问，用户直接回复：

```
用户: 帮我做个网站
Agent: ❓ Q1/5 — 网站主题/用途是什么？
用户: 产品汇报
Agent: ❓ Q2/5 — 目标受众是谁？
用户: 给领导
Agent: ❓ Q3/5 — 想要什么风格？
      A) 🍎 苹果风  B) 💻 终端风  C) 📊 PPT风  D) 🎵 抖音风
用户: C
Agent: 📝 需求确认：产品汇报 / 给领导 / PPT风
       回复"确认"我立即开始。
```

### 模式二：HTML 交互问卷（可选）

生成可交互的暗色主题网页表单，用户点击选择后一键提交：

```bash
python3 scripts/gen_form.py task="帮我做一个网站"
# → 生成交互式问卷 HTML
```

---

## 🌟 实际实现的效果

### ✅ 之前（没有 ask-user）

```
用户: 帮我做个网站
Agent: [直接开始写代码，做了一个完全不是你想要的网站]
用户: 😤 不是这样的，我要的是...
```

### ✅ 之后（使用 ask-user）

```
用户: 帮我做个网站
Agent: ❓ Q1/5 — 网站主题/用途？
用户: 产品汇报
Agent: ❓ Q2/5 — 目标受众？
用户: 领导
Agent: ❓ Q3/5 — 视觉风格？
      A) 苹果风  B) 终端风  C) PPT风  D) 抖音风
用户: C
Agent: ❓ Q4/5 — 页面数量？
用户: 3-5页
Agent: ❓ Q5/5 — 需要后端？
用户: 不需要
Agent: 📝 确认：产品汇报网站 / 领导 / PPT风 / 3-5页 / 静态
       确认后立即执行 ✅
用户: 确认
Agent: [按照确认的需求精准执行]
```

**效果：交互次数从 2-3 轮混乱对话，变成 5-6 轮精准问答。**

---

## 🔧 它适用于哪些 Agent

| Agent | 兼容性 | 说明 |
|-------|--------|------|
| **OmniBot** | ✅ 完美 | 原生 Skill 格式，直接安装使用 |
| **Claude Code** | ✅ 完美 | SKILL.md 格式完全兼容 |
| **Hermes** | ✅ 兼容 | 支持 SKILL.md 的 Agent 均可 |
| **OpenCode** | ✅ 兼容 | 支持 SKILL.md 的 Agent 均可 |
| **其他 AI Agent** | ⚠️ 通用 | 只要 Agent 支持自定义指令/Skill 机制即可 |

**核心原理**：`ask-user` 的核心是一个 SKILL.md 文件，它定义了一套 Agent 行为协议。任何能读取并遵循 Markdown 指令的 AI Agent 都可以使用。

---

## 🚀 如何快速安装

### 方式一：手动安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/xiaocao1154/omnibot-ask-user.git

# 2. 复制到你的 Skills 目录
cp -r omnibot-ask-user/skills/ask-user /你的/.omnibot/skills/

# 3. 验证安装
python3 /你的/.omnibot/skills/ask-user/scripts/verify.py
```

### 方式二：直接复制

只需要把 `skills/ask-user/SKILL.md` 复制到你的 Agent 的 Skills 目录即可。**SKILL.md 是核心**，脚本是可选的。

### 方式三：仅使用 SKILL.md

如果你的 Agent 不需要 HTML 问卷功能，**只需要 SKILL.md 一个文件**：

```
你的 Agent Skills 目录/
└── ask-user/
    └── SKILL.md    ← 复制这一个文件就够了
```

---

## 📁 仓库结构

```
omnibot-ask-user/
├── README.md                          # 本文件
├── LICENSE                            # MIT License
├── .gitignore
└── skills/
    └── ask-user/
        ├── SKILL.md                   # 核心协议（Agent 读取后自动生效）
        └── scripts/
            ├── gen_form.py            # HTML 问卷生成器（6 套内置模板）
            └── verify.py              # 安装验证脚本
```

---

## 🧠 技术原理

`ask-user` 本质上是一份 **Agent 行为协议**。当你把它放入 Agent 的 Skills 目录后：

1. Agent 读取 SKILL.md 中的指令
2. 当检测到用户需求模糊时（缺少 ≥2 个关键信息），自动触发提问流程
3. 按照协议定义的格式（填空题/选择题）逐题提问
4. 自动解析用户的回复（支持字母、数字、关键词、自然语言）
5. 收集完毕后输出结构化确认
6. 用户确认后执行任务

**不需要额外的运行时、不需要 API Key、不需要网络连接。**

---

## 📋 八种提问策略

| 策略 | 适用场景 | 示例 |
|------|----------|------|
| 多选 | 有 2-5 个明确方向 | 风格选择、格式选择 |
| 大输入框 | 信息严重不足 | "做个网站"但没说做什么 |
| 分维度追问 | 复杂项目 | 功能/风格/约束/成功标准 |
| 渐进式 | 需要逐步深入 | 每次只问 1 个问题 |
| 假设确认 | 有最优路径 | "我建议用 Python，可以吗？" |
| 决策树 | 有明确分支 | "需要前端+后端还是只要前端？" |
| 结果导向 | 目标不清晰 | "你最终想要达到什么效果？" |
| 控件描述 | 需要精确参数 | 尺寸/颜色/数量等精确规格 |

---

## 📝 内置场景模板

| 场景 | 触发词 | 问题数 |
|------|--------|--------|
| 做网站 | 网站/web/site | 5 题 |
| 写邮件 | 邮件/mail/email | 4 题 |
| 做海报 | 海报/poster | 4 题 |
| 写脚本 | 脚本/script/代码 | 4 题 |
| 做 PPT | PPT/ppt/汇报 | 5 题 |
| 写文档 | 文档/document/report | 4 题 |
| 通用默认 | 其他任何模糊需求 | 3 题 |

---

## 🤝 贡献

欢迎 Issue 和 PR！如果你有更好的提问场景模板，欢迎提交。

## 📄 License

[MIT License](LICENSE)

---

> 💡 **如果你觉得这个 Skill 有用，请给个 ⭐ Star 支持一下！**
