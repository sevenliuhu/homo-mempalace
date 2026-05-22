"""
AAAK-ZH — 中文版 AAAK 压缩格式

AAAK (Adaptive AI-Aware Key) 是 MemPalace 的核心索引格式。
本模块提供中文适配版本，支持中文实体编码和语义标记。

格式规范:
  [SESSION|TOPIC]:YYYY-MM-DD|entity_codes|metadata|★emotion

示例:
  SESSION:2026-05-22|设计了.homo.架构+集成了.mempalace|★重要
  MEMORY:2026-04-15|星河.考试.成绩+家长会.安排|★★关键

实体编码规则:
  - 实体中文名使用 . 连接层级
  - 多实体用 + 分隔
  - 属性用 : 标记

星级标记:
  ★    一般 (routine)
  ★★   重要 (important)
  ★★★ 关键 (critical)

元数据标记:
  ALC = AI Learning Context
  REQ = Request/Requirement
  DEC = Decision
  QST = Question
  ANS = Answer
"""

import re
from datetime import date, datetime
from typing import Optional


class AAAK_ZH:
    """中文 AAAK 压缩格式工具。"""

    # 星级映射
    STARS = {
        1: "★",
        2: "★★",
        3: "★★★",
        0: "",
    }

    # 元数据类型
    META_TAGS = {
        "学习上下文": "ALC",
        "需求": "REQ",
        "决策": "DEC",
        "问题": "QST",
        "回答": "ANS",
        "项目": "PROJ",
    }

    @classmethod
    def encode(cls, session_type: str = "SESSION",
               date_str: Optional[str] = None,
               entities: Optional[list] = None,
               meta: Optional[dict] = None,
               importance: int = 1) -> str:
        """编码为 AAAK 格式。

        Args:
            session_type: 会话类型（SESSION/TOPIC/MEMORY）
            date_str: 日期字符串（默认今天）
            entities: 实体编码列表
            meta: 元数据字典
            importance: 重要性（0-3）

        Returns:
            AAAK 格式字符串
        """
        if date_str is None:
            date_str = date.today().isoformat()

        parts = [f"{session_type}:{date_str}"]

        # 实体部分
        if entities:
            entity_str = "+".join(entities)
            parts.append(entity_str)
        else:
            parts.append("general")

        # 元数据部分
        if meta:
            meta_str = "|".join(f"{k}:{v}" for k, v in meta.items())
            parts.append(meta_str)
        else:
            parts.append("")

        # 星级
        star = cls.STARS.get(importance, "")
        parts.append(star)

        return "|".join(p for p in parts if p)

    @classmethod
    def decode(cls, aaak_str: str) -> dict:
        """解码 AAAK 格式字符串。

        Returns:
            包含 session_type, date, entities, meta, importance 的字典
        """
        result = {
            "session_type": "",
            "date": "",
            "entities": [],
            "meta": {},
            "importance": 0,
        }

        if not aaak_str:
            return result

        parts = aaak_str.split("|")

        # 第一部分: SESSION:YYYY-MM-DD 或 TOPIC:YYYY-MM-DD
        if parts:
            first = parts[0]
            if ":" in first:
                stype, sdate = first.split(":", 1)
                result["session_type"] = stype
                result["date"] = sdate

        # 第二部分: 实体
        if len(parts) > 1:
            entity_str = parts[1]
            if entity_str and entity_str != "general":
                result["entities"] = entity_str.split("+")

        # 第三部分: 元数据
        if len(parts) > 2:
            meta_str = parts[2]
            if meta_str:
                for item in meta_str.split("|"):
                    if ":" in item:
                        k, v = item.split(":", 1)
                        result["meta"][k] = v

        # 第四部分: 星级
        if len(parts) > 3:
            star_str = parts[3]
            result["importance"] = len(star_str)

        return result

    @classmethod
    def entity_code(cls, *parts: str) -> str:
        """生成实体编码。

        Args:
            parts: 层级路径，如 "项目", "后端", "API设计"

        Returns:
            点分隔的编码，如 "项目.后端.API设计"
        """
        return ".".join(parts)

    @classmethod
    def make_diary(cls, date_str: str, work_items: list,
                   meta: Optional[dict] = None,
                   importance: int = 2) -> str:
        """生成日记格式的 AAAK 条目。

        Args:
            date_str: 日期
            work_items: 工作项列表
            meta: 元数据
            importance: 重要性

        Returns:
            AAAK 格式日记条目
        """
        return cls.encode(
            session_type="SESSION",
            date_str=date_str,
            entities=work_items,
            meta=meta,
            importance=importance,
        )


def aaak_encode(session_type="SESSION", entities=None,
                meta=None, importance=1) -> str:
    """快捷编码函数。"""
    return AAAK_ZH.encode(session_type, entities=entities,
                          meta=meta, importance=importance)


def aaak_decode(aaak_str: str) -> dict:
    """快捷解码函数。"""
    return AAAK_ZH.decode(aaak_str)
