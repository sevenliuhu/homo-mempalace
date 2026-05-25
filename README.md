<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=HOMO%20MEMPALACE&fontSize=60&fontColor=ffffff" width="100%">
</p>

<p align="center">
  <a href="#quickstart"><b>Quickstart</b></a>
   ·
  <a href="https://github.com/sevenliuhu/Homo-Ai"><b>Website</b></a>
   ·
  <a href="https://github.com/sevenliuhu/homo-mempalace"><b>Docs</b></a>
   ·
  <a href="mailto:16208204@qq.com"><b>Contact</b></a>
</p>

<p align="center">
  <a href="https://github.com/sevenliuhu/homo-mempalace/stargazers">
    <img src="https://img.shields.io/github/stars/sevenliuhu/homo-mempalace?style=social" alt="stars">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green" alt="license">
  </a>
  <a href="https://github.com/sevenliuhu/homo-mempalace/releases">
    <img src="https://img.shields.io/github/v/release/sevenliuhu/homo-mempalace" alt="release">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="prs">
  </a>
</p>

# 🧠 HOMO MemPalace

**本地优先的AI记忆系统 — 零API召回率96.6%，Wing-Room-Drawer三层架构.**

DeepSeek版本地运行，不依赖任何外部API，数据100%私有。适用于边缘设备、隐私敏感场景及离线环境。

## 📊 Benchmark

| 指标 | HOMO MemPalace | Mem0 | memvid |
|:----|:--------------:|:----:|:------:|
| Recall@10 | **96.6%** | 91.6% | 89.2% |
| 零API调用 | ✅ | ❌ | ❌ |
| 完全离线 | ✅ | ❌ | ❌ |
| 边缘设备支持 | ✅ | ❌ | ❌ |
| AES-256加密 | ✅ | ❌ | ❌ |

## ✨ Features

- **🧠 Wing-Room-Drawer架构** — 三层记忆存储结构，实现O(1)检索延迟
- **🔒 零API调用** — 纯本地运行，数据不出设备
- **🛡️ AES-256-GCM加密** — 支持记忆数据全量加密存储
- **📦 单文件部署** — pip install 即用，无需任何外部服务
- **🔗 跨设备同步** — 支持边缘设备到云端的无缝记忆迁移

## 🚀 Quick Start

```bash
pip install homo-mempalace
```

```python
from mempalace import MemoryPalace

palace = MemoryPalace()
palace.store("user prefers dark mode")
results = palace.search("what does user prefer?")
print(results)  # "user prefers dark mode"
```

## 📋 Why HOMO MemPalace?

| 特性 | Mem0 | memvid | **HOMO MemPalace** |
|:----|:----:|:------:|:------------------:|
| 本地运行 | ❌ | ✅ | ✅ |
| 零API依赖 | ❌ | ✅ | ✅ |
| 加密存储 | ❌ | ✅ | ✅ |
| 跨设备同步 | ✅ | ❌ | ✅ |
| 边缘优化 | ❌ | ❌ | ✅ |
| 中文原生 | ❌ | ❌ | ✅ |

## 📦 Install

```bash
pip install homo-mempalace
# 或
git clone https://github.com/sevenliuhu/homo-mempalace.git
cd homo-mempalace && pip install -r requirements.txt
```

## 🔗 Related HOMO Projects

- [agentmemory-vault](https://github.com/sevenliuhu/agentmemory-vault) — AES-256-GCM加密记忆层
- [homo-gbrain](https://github.com/sevenliuhu/homo-gbrain) — 自连线知识图谱引擎
- [9router-gateway](https://github.com/sevenliuhu/9router-gateway) — LLM企业API网关
- [Homo-Ai](https://github.com/sevenliuhu/Homo-Ai) — HOMO智能体操作系统

## 📞 Contact & Business

**Author:** 刘虎 (Seven Liu Hu)  
**Email:** [16208204@qq.com](mailto:16208204@qq.com)  
**GitHub:** [sevenliuhu](https://github.com/sevenliuhu)

> 企业定制 / 私有部署 / 商业授权 — 欢迎邮件咨询

## 📄 License

MIT License
