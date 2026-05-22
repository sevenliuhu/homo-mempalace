"""
HOMO — DeepSeek 版记忆适配层

HOMO MemPalace 适配层，为 DeepSeek 系列模型优化的本地优先 AI 记忆系统。
提供 Wing-Room-Drawer 三层架构的中文接口。

核心原理：
  - Wing（翼）= 人/项目
  - Room（房间）= 时间线/主题
  - Drawer（抽屉）= 原始文本（逐字存储）
  - AAAK 索引 = LLM 可扫描的压缩索引
"""

__version__ = "1.0.0"
