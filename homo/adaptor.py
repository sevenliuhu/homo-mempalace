"""
HOMO Memory Adaptor — 记忆模块适配层

将 mempalace 的 Wing-Room-Drawer 架构适配为 HOMO 中文接口。
不包含 mempalace 核心代码，仅做封装和适配。

用法:
    from homo.adaptor import HomoPalace

    palace = HomoPalace()
    palace.mine("~/projects/myapp")
    results = palace.search("项目的后端架构")

架构:
    HOMO → HomoPalace → mempalace CLI/MCP → ChromaDB
        ↓
    HOMO 适配层 (中文提示词、DeepSeek 嵌入配置、AAAK 中文方言)
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Dict

from .config import get_config, HomoConfig

logger = logging.getLogger("homo")


class HomoPalace:
    """HOMO 记忆宫殿 —— Wing-Room-Drawer 架构的中文适配接口。

    封装 mempalace CLI 和 Python API，提供中文友好的接口。
    所有 LLM 操作默认指向 DeepSeek 系列模型（API 或本地）。
    """

    def __init__(self, palace_path: Optional[str] = None):
        self.config = get_config()
        self.palace_path = palace_path or self.config.palace_path
        self._memories_cache = []

    # ── 记忆摄入 ──────────────────────────────────────────

    def mine(self, path: str, mode: str = "files", wing: Optional[str] = None):
        """从指定路径摄入记忆。

        Args:
            path: 项目路径或对话路径
            mode: "files"（项目文件）或 "convos"（对话记录）
            wing: 可选，指定翼名
        """
        cmd = ["mempalace", "mine", path]
        if mode == "convos":
            cmd.extend(["--mode", "convos"])
        if wing:
            cmd.extend(["--wing", wing])
        return self._run(cmd)

    def add_memory(self, wing: str, room: str, content: str, source: str = "homo"):
        """直接添加一条记忆。

        Args:
            wing: 翼（人/项目名）
            room: 房间（主题/日期）
            content: 逐字内容
            source: 来源标记
        """
        cmd = [
            "mempalace-mcp", "--palace", self.palace_path,
            "add_drawer", wing, room, content,
        ]
        return self._run(cmd)

    # ── 搜索与检索 ────────────────────────────────────────

    def search(self, query: str, wing: Optional[str] = None,
               room: Optional[str] = None, n: int = 5) -> List[Dict]:
        """语义搜索记忆。

        Args:
            query: 搜索关键词（中文）
            wing: 可选，限定翼
            room: 可选，限定房间
            n: 返回结果数

        Returns:
            搜索结果列表，每项包含 text、wing、room、similarity
        """
        cmd = ["mempalace", "search", query, "--limit", str(n)]
        if wing:
            cmd.extend(["--wing", wing])
        if room:
            cmd.extend(["--room", room])
        output = self._run(cmd)

        # 解析 mempalace search 输出为结构化数据
        results = self._parse_search_output(output)
        return results

    def recall(self, wing: Optional[str] = None,
               room: Optional[str] = None, n: int = 10) -> str:
        """按需回忆（Layer 2）—— 按翼/房间过滤检索。

        Args:
            wing: 翼名
            room: 房间名
            n: 返回数量

        Returns:
            格式化的回忆文本
        """
        from mempalace.layers import MemoryStack
        try:
            stack = MemoryStack(palace_path=self.palace_path)
            return stack.recall(wing=wing, room=room, n_results=n)
        except ImportError:
            return self.search(
                query="",
                wing=wing,
                room=room,
                n=n,
            )

    def wake_up(self, wing: Optional[str] = None) -> str:
        """唤醒模式 —— 生成 L0（身份）+ L1（必要故事）文本。

        典型输出 ~600-900 tokens，可注入系统提示词或首条消息。

        Args:
            wing: 可选，按项目唤醒

        Returns:
            格式化的唤醒文本
        """
        from mempalace.layers import MemoryStack
        try:
            stack = MemoryStack(palace_path=self.palace_path)
            return stack.wake_up(wing=wing)
        except ImportError:
            return "## L0 — IDENTITY\n[HOMO 记忆系统已就绪]\n\n## L1 — ESSENTIAL STORY\n[请先运行 mempalace mine <dir> 摄入记忆]"

    # ── 知识图谱 ──────────────────────────────────────────

    def kg_query(self, entity: str, as_of: Optional[str] = None) -> List[Dict]:
        """查询知识图谱中的实体关系。

        Args:
            entity: 实体名（支持中文）
            as_of: 时间点（YYYY-MM-DD），查询在该时间点有效的事实

        Returns:
            实体关系列表
        """
        try:
            from mempalace.knowledge_graph import KnowledgeGraph

            kg_path = os.path.join(self.palace_path, "knowledge_graph.sqlite3")
            if not os.path.exists(kg_path):
                # 尝试默认路径
                kg_path = os.path.expanduser("~/.mempalace/knowledge_graph.sqlite3")

            if os.path.exists(kg_path):
                kg = KnowledgeGraph(db_path=kg_path)
                results = kg.query_entity(entity, as_of=as_of)
                return results
        except ImportError:
            logger.warning("knowledge_graph 模块不可用，请安装 mempalace")
        except Exception as e:
            logger.warning(f"知识图谱查询失败: {e}")
        return []

    def kg_add(self, subject: str, predicate: str, obj: str,
               valid_from: Optional[str] = None, valid_to: Optional[str] = None):
        """向知识图谱添加事实。

        Args:
            subject: 主体
            predicate: 关系类型
            obj: 客体
            valid_from: 事实开始时间
            valid_to: 事实结束时间
        """
        try:
            from mempalace.knowledge_graph import KnowledgeGraph

            kg_path = os.path.join(self.palace_path, "knowledge_graph.sqlite3")
            if not os.path.exists(kg_path):
                kg_path = os.path.expanduser("~/.mempalace/knowledge_graph.sqlite3")

            if os.path.exists(kg_path):
                kg = KnowledgeGraph(db_path=kg_path)
                kg.add_triple(subject, predicate, obj,
                              valid_from=valid_from, valid_to=valid_to)
                return True
        except ImportError:
            logger.warning("knowledge_graph 模块不可用")
        except Exception as e:
            logger.warning(f"添加事实失败: {e}")
        return False

    # ── 状态与统计 ────────────────────────────────────────

    def status(self) -> dict:
        """宫殿状态概览。"""
        try:
            result = subprocess.run(
                ["mempalace", "status"],
                capture_output=True, text=True, timeout=10,
            )
            return {
                "status": result.stdout.strip(),
                "error": result.stderr.strip() if result.stderr else None,
            }
        except FileNotFoundError:
            return {"status": "mempalace 未安装，请运行: uv tool install mempalace"}
        except subprocess.TimeoutExpired:
            return {"status": "查询超时"}

    def count_memories(self) -> int:
        """返回记忆总数。"""
        try:
            from mempalace.palace import get_collection
            col = get_collection(self.palace_path, create=False)
            return col.count()
        except Exception:
            return 0

    # ── 内部方法 ──────────────────────────────────────────

    def _run(self, cmd: list) -> str:
        """运行外部命令并返回输出。"""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                logger.warning(f"命令失败: {' '.join(cmd)}\n{result.stderr}")
            return result.stdout or result.stderr
        except FileNotFoundError:
            logger.error(f"命令未找到: {cmd[0]}，请安装 mempalace")
            return f"请先安装 mempalace: uv tool install mempalace"
        except subprocess.TimeoutExpired:
            return "命令超时"

    def _parse_search_output(self, output: str) -> List[Dict]:
        """解析 mempalace search 的输出。"""
        results = []
        for line in output.split("\n"):
            line = line.strip()
            if not line or line.startswith("##") or line.startswith("="):
                continue
            try:
                results.append({"text": line, "source": "mempalace"})
            except Exception:
                pass
        return results

    def __repr__(self):
        return f"<HomoPalace path={self.palace_path}>"
