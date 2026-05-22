<div align="center">

# 🧠 HOMO-MemPalace

**DeepSeek 版 · 本地优先 AI 记忆系统**

> 零 API 调用 · 96.6% R@5 原始召回 · Wing-Room-Drawer 三层架构 · 29 个 MCP 工具  
> 数据永不离开你的机器 · 逐字存储 · 无摘要 · 无 paraphrase

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-4dc9f6?style=flat-square&logo=python&logoColor=4dc9f6)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-b0e8ff?style=flat-square)](LICENSE)
[![DeepSeek Ready](https://img.shields.io/badge/DeepSeek-Ready-4D6BFE?style=flat-square)](https://deepseek.com)

</div>

---

## 🌟 这是什么

**HOMO-MemPalace** 是 [MemPalace](https://github.com/MemPalace/mempalace) (52638⭐) 的中文增强版，专为 **DeepSeek 系列模型**优化的本地优先 AI 记忆系统。

它让你的 AI 助手拥有 **长期记忆**——每次对话不需要从头开始。所有数据存储在你的机器上，不需要任何 API 密钥。

### 核心理念

| 概念 | 说明 |
|------|------|
| **Wing（翼）** | 人/项目——记忆的最高分类 |
| **Room（房间）** | 时间线/主题——按日或按话题组织 |
| **Drawer（抽屉）** | 原始文本——逐字存储，绝不摘要 |
| **AAAK 索引** | LLM 可扫描的压缩索引层，秒级定位 |
| **知识图谱** | 时态实体关系图（SQLite 本地存储） |
| **4 层唤醒栈** | 每次唤醒仅 600-900 tokens，释放 95%+ 上下文 |

### 性能

| 基准 | 指标 | 分数 | 说明 |
|------|------|------|------|
| LongMemEval (raw) | R@5 | **96.6%** | 零 API、零 LLM |
| LongMemEval (hybrid) | R@5 | **98.4%** | 仅本地算法 |
| LoCoMo (hybrid) | R@10 | **88.9%** | 对话场景 |
| ConvoMem | Avg recall | **92.9%** | 全类别 |
| MemBench (ACL 2025) | R@5 | **80.3%** | 8500 项 |

---

## 🚀 快速开始

### 安装

```bash
# 推荐：使用 uv 安装原版 mempalace
uv tool install mempalace

# 克隆 HOMO 增强版
git clone https://github.com/sevenliuhu/homo-mempalace.git
cd homo-mempalace

# 安装适配层
pip install -e .
```

### 配置 DeepSeek

```bash
# 设置 DeepSeek 为默认 LLM（本地或 API）
homo-mempalace config set llm deepseek
homo-mempalace config set deepseek_api_key sk-your-key  # 可选：API 模式
```

### 摄入记忆

```bash
# 从项目文件摄入
homo-mempalace mine ~/projects/myapp

# 从对话记录摄入
homo-mempalace mine ~/.claude/projects/ --mode convos

# 设置自动保存钩子
homo-mempalace hooks install
```

### 搜索与唤醒

```bash
# 语义搜索
homo-mempalace search "为什么选择了 GraphQL？"

# 唤醒模式（L0+L1，~600-900 tokens）
homo-mempalace wake-up

# 按项目唤醒
homo-mempalace wake-up --wing myapp
```

---

## 🏗️ 架构详解

### Wing-Room-Drawer 三层存储

```
宫殿 (Palace)
├── WING: 用户 (person: 刘哥)
│   ├── ROOM: 2026-01-15
│   │   ├── DRAWER: "今天讨论项目架构..."
│   │   └── DRAWER: "决定使用 PostgreSQL..."
│   └── ROOM: 2026-02-20
│       └── DRAWER: "星河考试成绩出来了..."
├── WING: myapp (project)
│   ├── ROOM: backend
│   │   └── DRAWER: "API 设计文档..."
│   └── ROOM: decisions
│       └── DRAWER: "选择 GraphQL 的原因..."
└── WING: deepseek (agent)
    └── ROOM: diary
        └── DRAWER: "AAAK:今天完成记忆模块重构..."
```

### 4 层记忆唤醒栈

```
Layer 0: 身份层 (~100 tokens)   —— 始终加载：你是谁
Layer 1: 必要故事 (~500-800)    —— 始终加载：最重要的记忆
Layer 2: 按需检索 (~200-500)    —— 触发加载：按翼/房间过滤
Layer 3: 深度搜索 (无限制)       —— 语义搜索全部记忆
```

### AAAK 压缩索引

AAAK (Adaptive AI-Aware Key) 是一种紧凑的符号格式，让 LLM 可快速扫描数千条记录：

```
SESSION:2026-04-04|built.graph+diary.tools|ALC.req:agent.diaries|★★★
```

记忆使用星级标记重要性（★ = 一般，★★ = 重要，★★★ = 关键）。

### 知识图谱

时态实体关系图，支持事实的有效期追踪：

```
刘哥 ──father_of──→ 星河  [valid_from: 2015-04-01]
星河 ──does──→ 游泳     [valid_from: 2025-01-01]
我 ──works_on──→ myapp  [valid_from: 2026-03-01]
```

---

## 🔧 MCP 工具全表（29 个）

### 读取工具（8 个）
| 工具 | 功能 |
|------|------|
| `mempalace_status` | 宫殿总览：抽屉数、翼/房间统计 |
| `mempalace_list_wings` | 列出所有翼及抽屉数 |
| `mempalace_list_rooms` | 列出翼内房间 |
| `mempalace_get_taxonomy` | 完整分类树：翼→房间→抽屉数 |
| `mempalace_search` | 语义搜索（支持翼/房间过滤） |
| `mempalace_get_aaak_spec` | AAAK 压缩格式规范 |
| `mempalace_get_drawer` | 按 ID 获取单个抽屉 |
| `mempalace_list_drawers` | 分页列出抽屉 |

### 知识图谱工具（5 个）
| 工具 | 功能 |
|------|------|
| `mempalace_kg_query` | 查询实体关系 |
| `mempalace_kg_add` | 添加事实三元组 |
| `mempalace_kg_invalidate` | 标记事实失效 |
| `mempalace_kg_timeline` | 实体时间线 |
| `mempalace_kg_stats` | 知识图谱统计 |

### 写作工具（4 个）
| 工具 | 功能 |
|------|------|
| `mempalace_add_drawer` | 逐字写入抽屉 |
| `mempalace_update_drawer` | 更新抽屉内容 |
| `mempalace_delete_drawer` | 删除抽屉 |
| `mempalace_sync` | 同步（删除已删除源文件的抽屉） |

### 宫殿图工具（7 个）
| 工具 | 功能 |
|------|------|
| `mempalace_traverse` | 从房间出发遍历宫殿图 |
| `mempalace_find_tunnels` | 寻找跨翼通道 |
| `mempalace_graph_stats` | 宫殿图统计 |
| `mempalace_create_tunnel` | 创建跨翼通道 |
| `mempalace_list_tunnels` | 列出所有通道 |
| `mempalace_delete_tunnel` | 删除通道 |
| `mempalace_follow_tunnels` | 沿通道追踪 |

### 日记工具（2 个）
| 工具 | 功能 |
|------|------|
| `mempalace_diary_write` | 以 AAAK 格式写代理日记 |
| `mempalace_diary_read` | 读取最近的日记条目 |

### 其他工具（3 个）
| 工具 | 功能 |
|------|------|
| `mempalace_check_duplicate` | 检查内容是否重复 |
| `mempalace_hook_settings` | 钩子行为设置 |
| `mempalace_memories_filed_away` | 检查最近保存情况 |
| `mempalace_reconnect` | 强制重连数据库 |

---

## 🎯 HOMO 增强特性

相比原版 MemPalace，HOMO 版提供：

1. **中文优先** —— 完整的中文界面、文档和错误信息
2. **DeepSeek 适配** —— 针对 DeepSeek-V2/V3/R1 系列优化嵌入和检索
3. **本地推理** —— 内置 Ollama/LM Studio 配置，无缝使用本地模型
4. **AAAK 中文方言** —— AAAK 压缩格式支持中文实体编码
5. **一键钩子** —— 为 Claude Code / Gemini CLI 提供一键安装钩子
6. **中文实体检测** —— 智能识别中文人名、项目名、概念

---

## 📋 系统要求

- Python 3.9+
- 向量存储后端（默认 ChromaDB）
- 约 300 MB 磁盘空间（默认嵌入模型）
- **无需任何 API 密钥**

---

## 📞 联系方式

如有问题或合作意向，请联系：

- 📧 <16208204@qq.com>

---

## 📜 许可

MIT License

---

*HOMO-MemPalace：让你的 AI 拥有永不遗忘的记忆。*




---

## ⭐ Star 解锁专属工具

给本仓库点 Star，即可前往解锁页面获取独家数据/工具/模板：

👉 [**https://sevenliuhu.github.io/Homo-Ai/unlock.html**](https://sevenliuhu.github.io/Homo-Ai/unlock.html)

内容包括：A股量化模板 / 反爬指纹规则集 / 134技能索引 / 记忆系统配置 / 电商SKILL模板 / 中国风设计色板 等 12 份独家资源。

## 🤝 需要定制开发？

我们提供基于此项目的商业增强版和企业定制服务。

- **📧 邮件咨询**：16208204@qq.com

> 💼 **商业授权**：获取商业授权与付款信息，请填写[授权表单](https://sevenliuhu.github.io/Homo-Ai/unlock.html)或发邮件至 **16208204@qq.com**
- **💼 在 Fiverr 下单**：https://www.fiverr.com/sevenliuhu
- **🌐 HOMO 官方网站**：https://sevenliuhu.github.io/Homo-Ai/

> 💡 我们拥有 215 个 AI 智能体、15+ 专业部门，覆盖工程/设计/销售/市场/法律等全链路。无论你是需要定制开发、技术咨询，还是想把 AI 能力落地到你的业务中，我们都能帮你实现。
